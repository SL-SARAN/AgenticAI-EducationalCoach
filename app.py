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

st.set_page_config(page_title="Autonomous Learning Coach", layout="wide")

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

# --- UI Layout ---
st.title("🎓 Autonomous Learning Coach")

# --- STEP 0: GOAL SETTING ---
if st.session_state.step == "goal_setting":
    st.subheader("🎯 What is your learning objective today?")
    st.markdown("Let me help you build a personalized path to mastery.")
    
    goal = st.text_input("Enter your goal (e.g., 'Master Python for data engineering', 'Learn Data Structures for placements')")
    level = st.selectbox("Select Your Current Level", learning_setup.get_levels())
    
    if st.button("Generate Learning Path"):
        if goal:
            st.session_state.learning_objective = goal
            st.session_state.selected_level = level
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
    
    col_start, col_back = st.columns([1, 5])
    with col_start:
        if st.button("🚀 Start Assessment"):
            st.session_state.selected_topic = selected
            st.session_state.current_difficulty = difficulty_mapper.map_level_to_difficulty(st.session_state.selected_level)
            
            with st.spinner(f"Generating question on {selected}..."):
                q_data = question_agent.generate_question(selected, st.session_state.current_difficulty)
                if q_data and "question" in q_data:
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
    current_idx = DIFFICULTY_LEVELS.index(current_diff) if current_diff in DIFFICULTY_LEVELS else 1

    if is_correct:
        st.success(f"✅ Correct! The answer was {correct_ans}.")
        score = 100
        mistake_type = "None (Correct Answer)"
        learner_model.update_score(st.session_state.selected_topic, score)
        
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
        learner_model.update_score(st.session_state.selected_topic, score)
        
        # Decrease Difficulty
        if current_idx > 0:
            new_diff = DIFFICULTY_LEVELS[current_idx - 1]
            st.session_state.current_difficulty = new_diff
            st.toast(f"📉 Adjusting difficulty to **{new_diff}** to reinforce concepts.")
        else:
            st.toast("🛡️ reinforcing basics at Easy level.")
        
        # 2. Mistake Analysis
        mistake_type = mistake_agent.classify_mistake(q['question'], user_ans, correct_ans)
        learner_model.log_mistake(mistake_type)
        st.warning(f"⚠️ **Mistake Analysis:** {mistake_type}")


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
    st.markdown(f"**Correction Steps:** {ai_exp.get('step_by_step_correction', 'N/A')}")
    
    with st.expander("📝 **Sample Code & Comments**", expanded=True):
        st.code(ai_exp.get('sample_code', '# No code generated'), language='python')
        st.caption(ai_exp.get('code_comments', ''))
        
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
            st.session_state.current_difficulty = None
            st.rerun()
            
    with col_goal:
        if st.button("🔄 Change Learning Goal"):
            st.session_state.step = "goal_setting"
            st.session_state.current_question = None
            st.session_state.current_difficulty = None
            st.session_state.learning_objective = None
            st.session_state.generated_path = None
            st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.header("Learner Profile")
    if st.session_state.learning_objective:
        st.success(f"**Current Goal:**\n{st.session_state.learning_objective}")
        
    data = learner_model.load_data()
    st.write(f"**Name:** {data.get('name', 'Learner')}")
    
    st.write("### 📊 Topic Scores")
    scores = data.get("topic_scores", {})
    if scores:
        for t, s in scores.items():
            st.write(f"**{t}**: {s}%")
            st.progress(s)
    else:
        st.caption("No scores yet.")
        
    st.write("### ⚠️ Mistake History")
    mistakes = data.get("mistake_history", {})
    if mistakes:
        for m, c in mistakes.items():
            st.write(f"- {m}: {c}")

