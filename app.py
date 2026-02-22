import streamlit as st
import learning_setup
import difficulty_mapper
import learner_model
import question_agent
import mistake_agent
import content_agent
import roadmap_agent
import resource_agent

st.set_page_config(page_title="Autonomous Learning Coach", layout="wide")

# --- Session State Management ---
if "step" not in st.session_state:
    st.session_state.step = "setup"  # setup, quiz, result
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

# --- UI Layout ---
st.title("🎓 Autonomous Learning Coach")

# --- STEP 1: SETUP ---
if st.session_state.step == "setup":
    st.subheader("Start Your Learning Session")
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.selectbox("Select Topic", learning_setup.get_topics())
    with col2:
        level = st.selectbox("Select Your Level", learning_setup.get_levels())
    
        # Initialize difficulty based on level for the first question
        st.session_state.selected_topic = topic
        st.session_state.selected_level = level
        st.session_state.current_difficulty = difficulty_mapper.map_level_to_difficulty(level)
        
        with st.spinner(f"Generating question ({st.session_state.current_difficulty})..."):
            q_data = question_agent.generate_question(topic, st.session_state.current_difficulty)
            
            if q_data and "question" in q_data:
                st.session_state.current_question = q_data
                st.session_state.step = "quiz"
                st.rerun()
            else:
                st.error("Failed to generate question. Please try again.")

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
    
    # Row 1: Focus & Root Cause
    c1, c2 = st.columns(2)
    with c1:
        st.error(f"**Learning Focus:** {explanation_data.get('learning_focus', 'Topic Mastery')}")
        st.markdown(f"**Why this happens:** {explanation_data.get('root_cause', 'N/A')}")
    with c2:
        st.info(f"**Concept:** {explanation_data.get('concept_explanation', 'N/A')}")
        st.warning(f"💡 **Tip:** {explanation_data.get('practical_tip', 'N/A')}")

    # Row 2: Code Example
    with st.expander("📝 **Code Solution & Explanation**", expanded=True):
        st.code(explanation_data.get('code_snippet', '# No code generated'), language='python')
        st.caption(explanation_data.get('code_explanation', ''))

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
        
        # 1. Decision Banner
        decision = roadmap_data.get('decision', 'CONTINUE LEARNING')
        if "ADVANCE" in decision.upper():
            st.success(f"**DECISION: {decision}**")
        elif "REMEDIATE" in decision.upper() or "REINFORCE" in decision.upper():
            st.error(f"**DECISION: {decision}**")
        else:
            st.warning(f"**DECISION: {decision}**")
            
        st.info(f"**Reasoning:** {roadmap_data.get('reason', 'Based on your recent performance.')}")
        
        # 2. Detailed Steps & Advice
        c1, c2 = st.columns(2)
        advice = roadmap_data.get('next_step_advice', {})
        
        with c1:
            st.markdown(f"**🎯 Next Objective:** {advice.get('next_topic', 'Current Topic')}")
            st.markdown(f"**⚡ Action:** {advice.get('action', 'Review')}")
        with c2:
            st.markdown(f"**🔥 Challenge:** {advice.get('tip_or_challenge', 'Keep coding!')}")
        
        # 3. Decision-Tailored Resources
        st.markdown("### 📚 Tailored Resources")
        decision_resources = roadmap_data.get('resources', [])
        
        if decision_resources:
            for res in decision_resources:
                if isinstance(res, dict):
                    st.markdown(f"- **[{res.get('title', 'Resource')}]({res.get('url', '#')})**: {res.get('reason', 'Helpful link')}")
                elif isinstance(res, str):
                    st.markdown(f"- **[Resource]({res})**: Recommended link")
                else:
                    st.caption(f"Invalid resource format: {res}")
        else:
            # Fallback
            fallback_res = resource_agent.recommend_resources(
                st.session_state.selected_topic, mistake_type, st.session_state.selected_level
            ).get('resources', [])
            for res in fallback_res:
                    st.markdown(f"- [{res['title']}]({res['url']})")
        
    col_next, col_new = st.columns([1, 1])
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
        if st.button("🔄 Start Fresh Topic"):
            st.session_state.step = "setup"
            st.session_state.current_question = None
            st.session_state.current_difficulty = None # Reset difficulty for new topic
            st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.header("Learner Profile")
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
