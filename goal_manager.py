# goal_manager.py
import database
import learning_setup
from datetime import datetime, timedelta


def create_goal(learner_id, goal_text, duration_days):
    """
    Create a new learning goal and generate a topic plan.
    - Deactivates any previous active goals for this learner.
    - Inserts a new goal with start_date = today, deadline = today + duration_days.
    - Generates a topic plan distributed evenly across the duration.
    Returns the new goal_id.
    """
    # Deactivate old active goals
    database.execute_query(
        "UPDATE learning_goals SET status = 'paused' WHERE learner_id = ? AND status = 'active'",
        (learner_id,)
    )

    start_date = datetime.now().date()
    deadline = start_date + timedelta(days=duration_days)

    goal_id = database.execute_query(
        "INSERT INTO learning_goals (learner_id, goal_text, start_date, deadline, status) VALUES (?, ?, ?, ?, 'active')",
        (learner_id, goal_text, start_date.isoformat(), deadline.isoformat())
    )

    topics = learning_setup.get_topics()
    generate_learning_plan(goal_id, topics, duration_days)

    return goal_id


def generate_learning_plan(goal_id, topics, duration_days):
    """
    Distribute topics evenly across the available days.
    Example: 5 topics over 10 days → Day 1, Day 3, Day 5, Day 7, Day 9.
    """
    if not topics:
        return

    start_date = datetime.now().date()
    num_topics = len(topics)

    # Distribute evenly: spacing = duration / num_topics
    if num_topics >= duration_days:
        spacing = 1
    else:
        spacing = duration_days / num_topics

    for i, topic in enumerate(topics):
        day_offset = int(round(i * spacing))
        target_date = start_date + timedelta(days=day_offset)
        database.execute_query(
            "INSERT INTO learning_topics (goal_id, topic_name, target_date, completed, score) VALUES (?, ?, ?, 0, 0)",
            (goal_id, topic, target_date.isoformat())
        )


def get_active_goal(learner_id):
    """Return the current active goal for a learner, or None."""
    rows = database.fetch_query(
        "SELECT * FROM learning_goals WHERE learner_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1",
        (learner_id,)
    )
    return dict(rows[0]) if rows else None


def get_goal_topics(goal_id):
    """Return all topics for a goal with their completion status."""
    rows = database.fetch_query(
        "SELECT * FROM learning_topics WHERE goal_id = ? ORDER BY target_date",
        (goal_id,)
    )
    return [dict(r) for r in rows]


def get_current_topic(goal_id):
    """Return the next incomplete topic name, or None if all done."""
    rows = database.fetch_query(
        "SELECT topic_name FROM learning_topics WHERE goal_id = ? AND completed = 0 ORDER BY target_date LIMIT 1",
        (goal_id,)
    )
    return rows[0]["topic_name"] if rows else None


def mark_topic_completed(goal_id, topic_name, score):
    """
    Mark a topic as completed if score >= 70.
    Also stores the score regardless.
    """
    # Always store the score
    database.execute_query(
        "UPDATE learning_topics SET score = ? WHERE goal_id = ? AND topic_name = ?",
        (score, goal_id, topic_name)
    )

    if score >= 70:
        database.execute_query(
            "UPDATE learning_topics SET completed = 1 WHERE goal_id = ? AND topic_name = ?",
            (goal_id, topic_name)
        )

    # Check if all topics are done → mark goal complete
    remaining = database.fetch_query(
        "SELECT COUNT(*) as cnt FROM learning_topics WHERE goal_id = ? AND completed = 0",
        (goal_id,)
    )
    if remaining and remaining[0]["cnt"] == 0:
        database.execute_query(
            "UPDATE learning_goals SET status = 'completed' WHERE id = ?",
            (goal_id,)
        )


def calculate_progress(goal_id):
    """Return progress as a percentage (0–100)."""
    total = database.fetch_query(
        "SELECT COUNT(*) as cnt FROM learning_topics WHERE goal_id = ?",
        (goal_id,)
    )
    completed = database.fetch_query(
        "SELECT COUNT(*) as cnt FROM learning_topics WHERE goal_id = ? AND completed = 1",
        (goal_id,)
    )

    total_count = total[0]["cnt"] if total else 0
    completed_count = completed[0]["cnt"] if completed else 0

    if total_count == 0:
        return 0

    return int((completed_count / total_count) * 100)


def check_schedule_status(goal_id):
    """
    Compare expected progress vs actual progress.
    Returns: 'on_track', 'behind_schedule', or 'ahead_of_schedule'.
    """
    goal = database.fetch_query(
        "SELECT start_date, deadline FROM learning_goals WHERE id = ?",
        (goal_id,)
    )
    if not goal:
        return "on_track"

    start_date = datetime.strptime(goal[0]["start_date"], "%Y-%m-%d").date()
    deadline = datetime.strptime(goal[0]["deadline"], "%Y-%m-%d").date()
    today = datetime.now().date()

    total_days = (deadline - start_date).days
    if total_days <= 0:
        return "on_track"

    elapsed_days = (today - start_date).days
    expected_progress = min(elapsed_days / total_days, 1.0)

    # Actual progress
    total = database.fetch_query(
        "SELECT COUNT(*) as cnt FROM learning_topics WHERE goal_id = ?",
        (goal_id,)
    )
    completed = database.fetch_query(
        "SELECT COUNT(*) as cnt FROM learning_topics WHERE goal_id = ? AND completed = 1",
        (goal_id,)
    )
    total_count = total[0]["cnt"] if total else 0
    completed_count = completed[0]["cnt"] if completed else 0
    actual_progress = (completed_count / total_count) if total_count > 0 else 0

    gap = actual_progress - expected_progress

    if gap < -0.15:
        return "behind_schedule"
    elif gap > 0.15:
        return "ahead_of_schedule"
    else:
        return "on_track"


def adjust_learning_plan(goal_id, status):
    """
    Adjust topic target dates based on schedule status.
    - behind_schedule: extend remaining deadlines by +2 days each
    - ahead_of_schedule: compress remaining deadlines by -1 day each
    """
    if status == "on_track":
        return

    remaining_topics = database.fetch_query(
        "SELECT id, target_date FROM learning_topics WHERE goal_id = ? AND completed = 0 ORDER BY target_date",
        (goal_id,)
    )

    for topic_row in remaining_topics:
        try:
            current_date = datetime.strptime(topic_row["target_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        if status == "behind_schedule":
            new_date = current_date + timedelta(days=2)
        elif status == "ahead_of_schedule":
            new_date = current_date - timedelta(days=1)
            # Don't schedule before today
            if new_date < datetime.now().date():
                new_date = datetime.now().date()
        else:
            continue

        database.execute_query(
            "UPDATE learning_topics SET target_date = ? WHERE id = ?",
            (new_date.isoformat(), topic_row["id"])
        )

    # If behind, also extend the goal deadline
    if status == "behind_schedule":
        goal = database.fetch_query(
            "SELECT deadline FROM learning_goals WHERE id = ?",
            (goal_id,)
        )
        if goal:
            old_deadline = datetime.strptime(goal[0]["deadline"], "%Y-%m-%d").date()
            new_deadline = old_deadline + timedelta(days=2)
            database.execute_query(
                "UPDATE learning_goals SET deadline = ? WHERE id = ?",
                (new_deadline.isoformat(), goal_id)
            )


def log_progress_to_db(learner_id, topic, score):
    """Insert a progress record into the progress_history table."""
    database.execute_query(
        "INSERT INTO progress_history (learner_id, topic, score) VALUES (?, ?, ?)",
        (learner_id, topic, score)
    )


def log_mistake_to_db(learner_id, mistake_type):
    """Increment mistake count in the DB mistake_history table."""
    existing = database.fetch_query(
        "SELECT id, count FROM mistake_history WHERE learner_id = ? AND mistake_type = ?",
        (learner_id, mistake_type)
    )
    if existing:
        database.execute_query(
            "UPDATE mistake_history SET count = count + 1 WHERE id = ?",
            (existing[0]["id"],)
        )
    else:
        database.execute_query(
            "INSERT INTO mistake_history (learner_id, mistake_type, count) VALUES (?, ?, 1)",
            (learner_id, mistake_type)
        )
