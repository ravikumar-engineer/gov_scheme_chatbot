import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

# ---------------- ENV ----------------
load_dotenv()

# ---------------- HF CLIENT ----------------
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=os.getenv("HF_TOKEN")
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Gov Scheme Chatbot 2026",
    page_icon="🇮🇳",
    layout="centered"
)

# ---------------- TITLE ----------------
st.title("🇮🇳 Government Scheme Advisor")
st.caption("Brutally honest. Actually useful.")

# ---------------- SESSION STATE ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- SIDEBAR ----------------
st.sidebar.header("Tell me about yourself")

with st.sidebar.form(key="user_form"):
    age = st.number_input("Your Age", min_value=18, max_value=100, step=1)
    occupation = st.selectbox(
        "Occupation",
        (
            "Student",
            "Farmer",
            "Private Job",
            "Government Job",
            "Self Employed",
            "Unemployed"
        )
    )
    income = st.number_input("Monthly Income (₹)", min_value=0, step=1000)
    state = st.text_input("State (e.g. Uttar Pradesh)")
    category = st.selectbox("Category", ("General", "OBC", "SC", "ST"))

    submitted = st.form_submit_button("Find My Schemes")

# ---------------- CORE FUNCTION ----------------
def recommend_schemes(age, occupation, income, state, category):
    system_prompt = """
You are a brutal but helpful Indian Government Scheme Advisor.
STRICT RULES:
- Be honest and direct
- Clearly explain eligibility or rejection
- Recommend only REAL Indian government schemes
- Prefer Central schemes, then State schemes
- Use bullet points
- No sugarcoating
- Plain text output
"""

    user_prompt = f"""
User Profile:
Age: {age}
Occupation: {occupation}
Monthly Income: ₹{income}
State: {state}
Category: {category}

Task:
Recommend the most suitable government schemes.
Explain eligibility, benefits, and application steps.
"""

    response = client.chat_completion(
        inputs=f"{system_prompt}\n{user_prompt}",
        max_new_tokens=800,
        temperature=0.3
    )

    return response.generated_text.strip()

# ---------------- CLEAR HISTORY ----------------
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []
    st.experimental_rerun()

# ---------------- SIDEBAR HISTORY ----------------
if st.session_state.chat_history:
    st.sidebar.divider()
    st.sidebar.header("Previous Queries")
    for idx, chat in enumerate(reversed(st.session_state.chat_history), 1):
        st.sidebar.markdown(f"**Query {idx}:** {chat['user']}")
        st.sidebar.markdown(f"**Response:** {chat['assistant']}")
        st.sidebar.markdown("---")

# ---------------- MAIN CHAT AREA ----------------
st.divider()

# Initial form submission
if submitted:
    user_input = (
        f"Age: {age}, "
        f"Occupation: {occupation}, "
        f"Income: {income}, "
        f"State: {state}, "
        f"Category: {category}"
    )

    with st.spinner("Thinking like a government officer... 🇮🇳"):
        response = recommend_schemes(
            age, occupation, income, state, category
        )

    st.session_state.chat_history.append(
        {"user": user_input, "assistant": response}
    )

    st.chat_message("assistant").markdown(response)

# ---------------- CHATBOX FOR FOLLOW-UP QUESTIONS ----------------
user_question = st.chat_input("Ask about a scheme...")

if user_question:
    # Prepare a combined prompt including previous conversation
    conversation_context = "You are a brutal but helpful Indian Government Scheme Advisor. Be honest and direct. Recommend only REAL Indian government schemes.\n\n"

    for chat in st.session_state.chat_history:
        conversation_context += f"User: {chat['user']}\nAssistant: {chat['assistant']}\n"

    conversation_context += f"User: {user_question}\nAssistant:"

    with st.spinner("Consulting the government database... 🇮🇳"):
        response = client.chat_completion(
            inputs=conversation_context,
            max_new_tokens=800,
            temperature=0.3
        ).generated_text.strip()

    st.session_state.chat_history.append(
        {"user": user_question, "assistant": response}
    )

    st.chat_message("assistant").markdown(response)

# ---------------- FOOTER ----------------
st.divider()
st.caption("⚠️ This is an AI-based advisor. Always verify from official government portals.")
