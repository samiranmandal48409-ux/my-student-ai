import streamlit as st
from groq import Groq

# 1. Page Setup
st.set_page_config(page_title="Student Coding AI", page_icon="🎓")

# 2. ENTER YOUR GROQ KEY HERE
client = Groq(api_key="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")

SYSTEM_PROMPT = """
You are an expert AI Coding Partner for students.
Help them learn and build. Provide full code when asked and explain it simply.
"""

st.title("🎓 Student Coding AI")
st.subheader("Get code and help instantly - 100% Free!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you want to build today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Cloud Brain is thinking..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *st.session_state.messages
                    ],
                    model="llama-3.1-8b-instant",  # ✅ Fixed: replaced decommissioned model
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Cloud Error: {e}")
