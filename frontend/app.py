import streamlit as st
import uuid
import requests

# Constants
API_URL = "http://localhost:8000/chat"

# --- Page Config & Styling ---
st.set_page_config(
    page_title="Mutual Fund Assistant",
    page_icon="📈",
    layout="centered"
)

# Custom CSS matching the aesthetic guidelines and hiding unnecessary streamlit elements
st.markdown("""
    <style>
    .disclaimer {
        color: #ff4b4b;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        padding: 10px;
        border: 1px solid #ff4b4b;
        border-radius: 5px;
        background-color: #ffdce0;
    }
    </style>
""", unsafe_allow_html=True)


# --- Initialization ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI Setup ---
st.title("Mutual Fund FAQ Assistant")
st.markdown('<div class="disclaimer">⚠️ Facts-only. No investment advice.</div>', unsafe_allow_html=True)
st.write("Welcome! I can answer factual questions about our supported mutual fund schemes based exclusively on official documents.")

# Example Questions
st.subheader("Try asking:")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("What is the exit load for HDFC Large Cap?"):
        st.session_state.example_q = "What is the exit load for HDFC Large Cap?"
with col2:
    if st.button("What is the lock-in period for ELSS?"):
        st.session_state.example_q = "What is the lock-in period for ELSS?"
with col3:
    if st.button("Should I invest in HDFC Mid-Cap?"):
        st.session_state.example_q = "Should I invest in HDFC Mid-Cap?"

# --- Chat Rendering ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input Area ---
# Check if an example question was clicked
if "example_q" in st.session_state and st.session_state.example_q:
    user_input = st.session_state.example_q
    st.session_state.example_q = None # Reset
else:
    user_input = st.chat_input("Ask a factual question about a mutual fund...")

if user_input:
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. Call Backend API
    with st.chat_message("assistant"):
        with st.spinner("Searching official documents..."):
            try:
                response = requests.post(
                    API_URL, 
                    json={"session_id": st.session_state.session_id, "query": user_input},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    bot_text = data.get("response", "Error getting valid response.")
                else:
                    bot_text = f"Backend Error: {response.status_code}"
            except requests.exceptions.ConnectionError:
                bot_text = "Cannot connect to the backend server. Is the API running on port 8000?"
            except Exception as e:
                bot_text = f"An error occurred: {str(e)}"
                
            st.markdown(bot_text)
    
    # 3. Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": bot_text})
    st.rerun()

