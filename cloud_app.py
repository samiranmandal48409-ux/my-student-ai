import streamlit as st
from groq import Groq

# 1. Page Setup
st.set_page_config(page_title="Student Coding AI", page_icon="🎓")

# 2. Groq Client
client = Groq(api_key="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")

SYSTEM_PROMPT = "You are a coding assistant for students. Be concise. Give short, clear code with brief explanations."

MAX_HISTORY = 4  # Only last 2 exchanges

def get_trimmed_messages():
    return st.session_state.messages[-MAX_HISTORY:]

st.title("🎓 Student Coding AI")
st.subheader("Get code and help instantly - 100% Free!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you want to build today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *get_trimmed_messages()
                    ],
                    model="llama-3.3-70b-versatile",  # ✅ Higher free TPM limit
                    max_tokens=512,  # ✅ Keep responses short
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Cloud Error: {e}")
