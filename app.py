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
    
    if st.button("Start Quiz"):
        st.session_state.selected_topic = topic
        st.session_state.selected_level = level
        
        with st.spinner("Generating adaptive question..."):
            difficulty = difficulty_mapper.map_level_to_difficulty(level)
            q_data = question_agent.generate_question(topic, difficulty)
            
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
    
    if is_correct:
        st.success(f"✅ Correct! The answer was {correct_ans}.")
        score = 100
        learner_model.update_score(st.session_state.selected_topic, score)
    else:
        st.error(f"❌ Incorrect. You chose {user_ans}, but the correct answer was {correct_ans}.")
        score = 0
        learner_model.update_score(st.session_state.selected_topic, score)
        
        # 2. Mistake Analysis
        mistake_type = mistake_agent.classify_mistake(q['question'], user_ans, correct_ans)
        learner_model.log_mistake(mistake_type)
        st.warning(f"⚠️ **Mistake Analysis:** {mistake_type}")
        
        # 3. Content Explanation
        with st.expander("💡 AI Explanation"):
            explanation = content_agent.generate_explanation(st.session_state.selected_topic, mistake_type)
            st.write(explanation)

    # 4. Roadmap & Resources
    col1, col2 = st.columns(2)
    with col1:
        st.info("🗺️ **Recommended Roadmap**")
        roadmap = roadmap_agent.generate_roadmap(st.session_state.selected_topic, score)
        for step in roadmap:
            st.write(f"- {step}")

    with col2:
        st.info("📚 **Resources**")
        resources = resource_agent.recommend_resources(st.session_state.selected_topic)
        for res in resources:
            st.markdown(f"- {res}")
            
    if st.button("Start New Session"):
        st.session_state.step = "setup"
        st.session_state.current_question = None
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
