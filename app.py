import streamlit as st
import learning_setup
import difficulty_mapper
import learner_model
import question_agent
import mistake_agent
import content_agent
import roadmap_agent
import resource_agent
import goal_agent
import database
import goal_manager

st.set_page_config(page_title="Autonomous Learning Coach", layout="wide")

# --- Initialize SQLite database on startup ---
database.initialize_db()

# --- Session State Management ---
if "step" not in st.session_state:
    st.session_state.step = "goal_setting"  # goal_setting, path_review, setup, quiz, result
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "selected_level" not in st.session_state:
    st.session_state.selected_level = None
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = "Medium"
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "learning_objective" not in st.session_state:
    st.session_state.learning_objective = None
if "generated_path" not in st.session_state:
    st.session_state.generated_path = None
if "active_goal_id" not in st.session_state:
    st.session_state.active_goal_id = None
if "goal_duration" not in st.session_state:
    st.session_state.goal_duration = 14

# --- UI Layout ---
st.title("🎓 Autonomous Learning Coach")

# --- STEP 0: GOAL SETTING ---
if st.session_state.step == "goal_setting":
    st.subheader("🎯 What is your learning objective today?")
    st.markdown("Let me help you build a personalized path to mastery.")
    
    goal = st.text_input("Enter your goal (e.g., 'Master Python for data engineering', 'Learn Data Structures for placements')")
    level = st.selectbox("Select Your Current Level", learning_setup.get_levels())
    duration = st.slider("⏱️ Goal Duration (days)", min_value=7, max_value=90, value=14, step=7)
    
    if st.button("Generate Learning Path"):
        if goal:
            st.session_state.learning_objective = goal
            st.session_state.selected_level = level
            st.session_state.goal_duration = duration
            learner_model.update_goal(goal)
            learner_model.update_level(level)
            # Create goal in SQLite and generate topic plan
            new_goal_id = goal_manager.create_goal(1, goal, duration)
            st.session_state.active_goal_id = new_goal_id
            with st.spinner("Analyzing your goal and building a personalized roadmap..."):
                st.session_state.generated_path = goal_agent.generate_learning_path(goal)
                st.session_state.step = "path_review"
                st.rerun()
        else:
            st.warning("Please enter a learning goal to proceed.")

# --- STEP 0.5: PATH REVIEW ---
elif st.session_state.step == "path_review":
    st.subheader(f"🗺️ Your Custom Path: {st.session_state.learning_objective}")
    path_data = st.session_state.generated_path
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 1. Personalized Learning Path
        st.markdown("### 🧭 Personalized Learning Path")
        plp = path_data.get("personalized_learning_path", {})
        
        st.markdown(f"**Recommended Order:** {plp.get('learning_order', '')}")
        st.markdown(f"**Prerequisites:** {', '.join(plp.get('prerequisites', []))}")
        st.markdown(f"**Difficulty Level:** {plp.get('difficulty', '')}")
        st.markdown(f"**Estimated Time:** {plp.get('estimated_time', '')}")
        st.info(f"💡 **Key Success Tip:** {plp.get('key_success_tip', '')}")
        
        # Topic Tags
        st.markdown("**Topics to Cover:**")
        topics = plp.get('recommended_topics', ['Topic'])[:4]
        if topics:
            cols = st.columns(len(topics))
            for i, t in enumerate(topics):
                cols[i].button(t, disabled=True, key=f"topic_tag_{i}")
            
    with col2:
        # 2. Suggested Starting Topic
        starting_topic = path_data.get("suggested_starting_topic", "Fundamentals")
        st.markdown("### 🤖 Auto Topic Suggestion")
        st.success(f"**I recommend starting with:**\n### {starting_topic}")
        
        st.markdown("---")
        # 3. Weekly Milestones
        st.markdown("### 📅 Weekly Milestones")
        miles = path_data.get("weekly_milestones", {})
        st.markdown(f"- **Week 1:** {miles.get('week_1_focus', '')}")
        st.markdown(f"- **Week 2:** {miles.get('week_2_focus', '')}")

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        # 4. Practice Recommendations
        st.markdown("### 🎯 Practice Recommendations")
        prac = path_data.get("practice_recommendations", {})
        st.markdown(f"- **Platform:** {prac.get('platform', '')}")
        st.markdown(f"- **Project Idea:** {prac.get('project_idea', '')}")
        st.markdown(f"- **Real-World use:** {prac.get('real_world_app', '')}")
        
    with col4:
        # 5. Career Relevance
        st.markdown("### 💼 Career / Interview Context")
        st.markdown(path_data.get("career_relevance", ""))
        
    st.markdown("---")
    st.markdown("### ready to begin?")
    
    # Merge the new topic into our tracked topics if it's not there
    active_topics = learning_setup.get_topics()
    if starting_topic not in active_topics:
        active_topics.insert(0, starting_topic)
        
    selected = st.selectbox("Confirm or Change your starting topic:", active_topics, index=0)

    # Detect topic change and reset quiz state
    if st.session_state.selected_topic != selected:
        st.session_state.selected_topic = selected
        st.session_state.current_question = None
        st.session_state.user_answer = None
    
    col_start, col_back = st.columns([1, 5])
    with col_start:
        if st.button("🚀 Start Assessment"):
            # Reset previous quiz state
            st.session_state.current_question = None
            st.session_state.user_answer = None

            # Use goal-based topic if an active goal exists
            if st.session_state.active_goal_id:
                goal_topic = goal_manager.get_current_topic(st.session_state.active_goal_id)
                if goal_topic:
                    selected = goal_topic
            st.session_state.selected_topic = selected
            st.session_state.current_difficulty = difficulty_mapper.map_level_to_difficulty(st.session_state.selected_level)
            
            with st.spinner(f"Generating question on {selected}..."):
                q_data = question_agent.generate_question(selected, st.session_state.current_difficulty)
                if q_data and isinstance(q_data, dict) and "question" in q_data:
                    st.session_state.current_question = q_data
                    st.session_state.step = "quiz"
                    st.rerun()
                else:
                    st.error("Failed to generate question.")
    with col_back:
        if st.button("Go Back"):
            st.session_state.step = "goal_setting"
            st.rerun()

# --- STEP 1: SETUP (Legacy, bypassed via Goal Setting usually) ---
elif st.session_state.step == "setup":
    # Bypassed via Goal setting, keeping just in case.
    st.session_state.step = "goal_setting"
    st.rerun()

# --- STEP 2: QUIZ ---
elif st.session_state.step == "quiz":
    q = st.session_state.current_question
    st.subheader(f"Quiz: {st.session_state.selected_topic}")
    st.progress(50)
    
    st.markdown(f"### {q['question']}")
    
    options = q.get('options', {})
    choice = st.radio("Choose your answer:", options.keys(), index=None, format_func=lambda x: f"{x}: {options[x]}")
    
    if st.button("Submit Answer"):
        st.session_state.user_answer = choice
        st.session_state.step = "result"
        st.rerun()

# --- STEP 3: RESULT ---
elif st.session_state.step == "result":
    st.subheader("Assessment Result")
    st.progress(100)
    
    q = st.session_state.current_question
    user_ans = st.session_state.user_answer
    correct_ans = q.get('correct_answer', 'A')
    
    # 1. Evaluate
    is_correct = (user_ans == correct_ans)
    
    
    DIFFICULTY_LEVELS = ["Easy", "Easy-Medium", "Medium", "Hard"]
    current_diff = st.session_state.current_difficulty
    if current_diff not in DIFFICULTY_LEVELS:
        current_diff = difficulty_mapper.map_level_to_difficulty(st.session_state.selected_level)
        st.session_state.current_difficulty = current_diff
    current_idx = DIFFICULTY_LEVELS.index(current_diff)

    if is_correct:
        st.success(f"✅ Correct! The answer was {correct_ans}.")
        score = 100
        mistake_type = "None (Correct Answer)"
        learner_model.update_progress(st.session_state.selected_topic, score)
        
        # Increase Difficulty
        if current_idx < len(DIFFICULTY_LEVELS) - 1:
            new_diff = DIFFICULTY_LEVELS[current_idx + 1]
            st.session_state.current_difficulty = new_diff
            st.toast(f"📈 Performance Strong! Increasing difficulty to **{new_diff}**.")
        else:
            st.toast("🏆 You are at Max Difficulty!")
            
    else:
        st.error(f"❌ Incorrect. You chose {user_ans}, but the correct answer was {correct_ans}.")
        score = 0
        learner_model.update_progress(st.session_state.selected_topic, score)
        
        # Decrease Difficulty
        if current_idx > 0:
            new_diff = DIFFICULTY_LEVELS[current_idx - 1]
            st.session_state.current_difficulty = new_diff
            st.toast(f"📉 Adjusting difficulty to **{new_diff}** to reinforce concepts.")
        else:
            st.toast("🛡️ reinforcing basics at Easy level.")
        
        # 2. Mistake Analysis
        mistake_type = mistake_agent.classify_mistake(q['question'], user_ans, correct_ans)
        mistake_type = learner_model.normalize_mistake_key(mistake_type)
        learner_model.update_mistake(mistake_type)
        # Log mistake to SQLite
        goal_manager.log_mistake_to_db(1, mistake_type)
        st.warning(f"⚠️ **Mistake Analysis:** {mistake_type}")

    # --- Goal-based tracking: mark topic + log progress + schedule check ---
    goal_manager.log_progress_to_db(1, st.session_state.selected_topic, score)
    if st.session_state.active_goal_id:
        goal_manager.mark_topic_completed(
            st.session_state.active_goal_id,
            st.session_state.selected_topic,
            score
        )
        schedule_status = goal_manager.check_schedule_status(st.session_state.active_goal_id)
        if schedule_status != "on_track":
            goal_manager.adjust_learning_plan(st.session_state.active_goal_id, schedule_status)
            status_label = schedule_status.replace('_', ' ').title()
            st.toast(f"📅 Schedule: **{status_label}** — plan adjusted automatically.")


    # 3. AI Tutor Feedback (Run Unconditionally)
    st.markdown("---")
    st.subheader("🤖 AI Tutor Analysis")
    
    with st.spinner("Analyzing your thought process..."):
        explanation_data = content_agent.generate_explanation(
            st.session_state.selected_topic, 
            mistake_type, 
            st.session_state.selected_level
        )
    
    # 1️⃣ Learning Focus
    st.error(f"**1️⃣ Learning Focus:** {explanation_data.get('learning_focus', 'Topic Mastery')}")
    
    # 2️⃣ Knowledge Gap Profile & 3️⃣ Why This Mistake Happens
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**2️⃣ Knowledge Gap Profile:**")
        for gap in explanation_data.get('knowledge_gap_profile', []):
            st.markdown(f"- {gap}")
    with c2:
        st.markdown(f"**3️⃣ Why This Mistake Happens:**\n{explanation_data.get('why_mistake_happens', 'N/A')}")
        
    # 4️⃣ AI Explanation (with Sample Code)
    st.markdown("### 4️⃣ AI Explanation")
    ai_exp = explanation_data.get('ai_explanation', {})
    st.info(f"**Explanation:** {ai_exp.get('beginner_explanation', 'N/A')}")

    # --- Correction Steps: handle both string and list-of-dicts ---
    raw_steps = ai_exp.get('step_by_step_correction', 'N/A')
    if isinstance(raw_steps, list):
        st.markdown("**Correction Steps:**")
        for step_item in raw_steps:
            if isinstance(step_item, dict):
                for key, val in step_item.items():
                    st.markdown(f"- **{key}:** {val}")
            else:
                st.markdown(f"- {step_item}")
    else:
        st.markdown(f"**Correction Steps:** {raw_steps}")
    
    with st.expander("📝 **Sample Code & Comments**", expanded=True):
        # --- Sample Code: handle list-of-dicts with 'Code Snippet' keys ---
        raw_code = ai_exp.get('sample_code', '# No code generated')
        if isinstance(raw_code, list):
            for code_item in raw_code:
                if isinstance(code_item, dict):
                    for key, snippet in code_item.items():
                        st.code(snippet, language='python')
                else:
                    st.code(str(code_item), language='python')
        else:
            st.code(raw_code, language='python')

        # --- Code Comments: handle list-of-dicts ---
        raw_comments = ai_exp.get('code_comments', '')
        if isinstance(raw_comments, list):
            for comment_item in raw_comments:
                if isinstance(comment_item, dict):
                    for key, val in comment_item.items():
                        st.caption(f"💬 {val}")
                else:
                    st.caption(str(comment_item))
        else:
            st.caption(raw_comments)
        
    st.warning(f"💡 **Practical Tip:** {ai_exp.get('practical_tip', 'N/A')}")
    
    # 8️⃣ Why This Matters
    st.success(f"**8️⃣ Why This Matters:** {explanation_data.get('why_this_matters', 'N/A')}")

    # 4. Personalized Readiness & Roadmap (Run Unconditionally)
    st.markdown("---")
    st.subheader("🚀 Readiness & Next Steps")
    
    with st.spinner("Constructing personalized learning path..."):
        roadmap_data = roadmap_agent.generate_roadmap(
            st.session_state.selected_topic, 
            score, 
            mistake_type, 
            st.session_state.selected_level
        )
        resource_data = resource_agent.recommend_resources(
            st.session_state.selected_topic, 
            mistake_type, 
            st.session_state.selected_level
        )

        # --- Track current focus from roadmap output ---
        nsg_focus = roadmap_data.get('next_step_guidance', {})
        focus_next = nsg_focus.get('next_step', '') if isinstance(nsg_focus, dict) else ''
        learner_model.update_focus(st.session_state.selected_topic, focus_next)
        
        # 🔟 Readiness Decision
        raw_decision = roadmap_data.get('readiness_decision', 'CONTINUE LEARNING')
        if isinstance(raw_decision, dict):
            decision = str(list(raw_decision.values())[0]) if raw_decision else "CONTINUE LEARNING"
        else:
            decision = str(raw_decision)

        if "ADVANCE" in decision.upper():
            st.success(f"**🔟 DECISION: {decision}**")
        elif "REMEDIATE" in decision.upper() or "REINFORCE" in decision.upper():
            st.error(f"**🔟 DECISION: {decision}**")
        else:
            st.warning(f"**🔟 DECISION: {decision}**")
            
        st.info(f"**Reasoning:** {roadmap_data.get('reason', 'Based on your recent performance.')}")
        
        c_rm, c_mst = st.columns([2, 1])
        with c_rm:
            # 5️⃣ Personalized Learning Roadmap
            st.markdown("### 5️⃣ Personalized Learning Roadmap")
            for i, step in enumerate(roadmap_data.get('learning_roadmap', [])):
                st.markdown(f"**Step {i+1}:** {step.get('action', '')}")
                st.markdown(f"*{step.get('why_it_matters', '')}*")
                st.markdown(f"[Learn Here]({step.get('learn_here', '#')})")
        with c_mst:
            # 9️⃣ Mastery Prediction
            st.markdown("### 9️⃣ Mastery Prediction")
            st.markdown(f"**Predicted Range:** {roadmap_data.get('mastery_prediction', 'N/A')}")
            
            # 1️⃣1️⃣ Next Step Guidance
            nsg = roadmap_data.get('next_step_guidance', {})
            st.markdown("### 1️⃣1️⃣ Next Step Guidance")
            st.markdown(f"**Next:** {nsg.get('next_step', '')}")
            st.markdown(f"*{nsg.get('explanation', '')}*")

    # 5. Resources and Practice
    st.markdown("---")
    c_res, c_prac = st.columns(2)
    
    with c_res:
        # 6️⃣ Smart Resources
        st.markdown("### 6️⃣ Smart Resources")
        st.info(f"**AI Advice:** {resource_data.get('resource_advice', 'Review the topic conceptually before practicing.')}")
        for link_obj in resource_data.get('dynamic_links', []):
            st.markdown(f"- {link_obj['icon']} **[{link_obj['title']}]({link_obj['url']})**")
            
    with c_prac:
        # 7️⃣ Targeted Practice Exercise
        prac = resource_data.get('targeted_practice', {})
        st.markdown("### 7️⃣ Targeted Practice")
        st.markdown(f"**Task:** {prac.get('task_description', '')}")
        st.markdown(f"**Skill Built:** {prac.get('skill_built', '')}")
        st.info(f"💡 **Hint:** {prac.get('hint', '')}")
        
    st.markdown("---")
    col_next, col_new, col_goal = st.columns([1, 1, 1])
    with col_next:
        if st.button("➡️ Next Question (Adaptive)"):
            st.session_state.step = "quiz"
            st.session_state.user_answer = None
            st.session_state.current_question = None
            
            # Use the UPDATED difficulty
            with st.spinner(f"Adapting to {st.session_state.current_difficulty}..."):
                q_data = question_agent.generate_question(st.session_state.selected_topic, st.session_state.current_difficulty)
                if q_data:
                    st.session_state.current_question = q_data
                    st.rerun()
                    
    with col_new:
        if st.button("📋 Review Path Dashboard"):
            st.session_state.step = "path_review"
            st.session_state.current_question = None
            st.session_state.user_answer = None
            st.session_state.current_difficulty = difficulty_mapper.map_level_to_difficulty(st.session_state.selected_level)
            st.rerun()
            
    with col_goal:
        if st.button("🔄 Change Learning Goal"):
            st.session_state.step = "goal_setting"
            st.session_state.current_question = None
            st.session_state.user_answer = None
            st.session_state.current_difficulty = difficulty_mapper.map_level_to_difficulty(st.session_state.selected_level)
            st.session_state.learning_objective = None
            st.session_state.generated_path = None
            st.session_state.active_goal_id = None
            st.rerun()

# --- Sidebar: Learner Analytics Dashboard ---
with st.sidebar:
    data = learner_model.load_data()

    # ── 👤 Learner Profile ──
    st.markdown("### 👤 Learner Profile")
    st.markdown(f"**Name:** {data.get('name', 'Learner')}")
    st.markdown(f"**Level:** {data.get('level', 'Beginner')}")
    goal = data.get('goal', '') or (st.session_state.learning_objective or '')
    if goal:
        st.markdown(f"**Goal:** {goal}")

    st.divider()

    # ── 📊 Learning Progress ──
    st.markdown("### 📊 Learning Progress")
    scores = data.get("topic_scores", {})
    if scores:
        # Show first 6 topics only to avoid sidebar clutter
        shown = dict(list(scores.items())[:6])
        for topic_name, pct in shown.items():
            pct_val = max(0, min(int(pct), 100))
            st.markdown(f"**{topic_name}** — {pct_val}%")
            st.progress(pct_val / 100)
        if len(scores) > 6:
            st.caption(f"+ {len(scores) - 6} more topics…")
    else:
        st.caption("No scores yet. Take a quiz to start tracking!")

    st.divider()

    # ── ⚠ Top Weak Areas ──
    st.markdown("### ⚠ Top Weak Areas")
    mistakes = data.get("mistake_history", {})
    if mistakes:
        # Sort by count descending so worst areas are first
        sorted_mistakes = sorted(mistakes.items(), key=lambda x: x[1], reverse=True)
        for m_type, m_count in sorted_mistakes:
            st.markdown(f"**{m_type}** — {m_count}")
    else:
        st.caption("No mistakes recorded yet. Keep learning!")

    st.divider()

    # ── 🎯 Current Focus ──
    st.markdown("### 🎯 Current Focus")
    focus = data.get("current_focus", {})
    focus_topic = focus.get("current_topic", "")
    focus_step = focus.get("next_step", "")
    if focus_topic:
        st.markdown(f"**Topic:** {focus_topic}")
        st.markdown(f"**Next Step:** {focus_step or 'Continue practicing this topic'}")
    else:
        st.caption("Start a quiz to set your learning focus.")

    st.divider()

    # ── 📋 Goal Dashboard ──
    st.markdown("### 📋 Goal Dashboard")

    # Recover active_goal_id from DB if session lost it
    if not st.session_state.active_goal_id:
        db_goal = goal_manager.get_active_goal(1)
        if db_goal:
            st.session_state.active_goal_id = db_goal["id"]

    if st.session_state.active_goal_id:
        active_goal = goal_manager.get_active_goal(1)
        if active_goal:
            st.markdown(f"**Goal:** {active_goal['goal_text']}")
            st.markdown(f"**Deadline:** {active_goal['deadline']}")

            progress_pct = goal_manager.calculate_progress(active_goal['id'])
            st.markdown(f"**Progress:** {progress_pct}%")
            st.progress(progress_pct / 100)

            sched = goal_manager.check_schedule_status(active_goal['id'])
            if sched == "on_track":
                st.success("✅ On Track")
            elif sched == "behind_schedule":
                st.error("⚠️ Behind Schedule")
            elif sched == "ahead_of_schedule":
                st.info("🚀 Ahead of Schedule")

            # Topic checklist
            st.markdown("**Topics:**")
            topics_list = goal_manager.get_goal_topics(active_goal['id'])
            for t in topics_list:
                icon = "✔" if t["completed"] else "◻"
                st.markdown(f"{icon} {t['topic_name']}")
        else:
            st.caption("No active goal. Set one to get started!")
    else:
        st.caption("No active goal. Set one to get started!")
