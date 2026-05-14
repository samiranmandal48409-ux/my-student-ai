import streamlit as st
from groq import Groq
import time

st.set_page_config(page_title="Student Coding AI", page_icon="🎓")

client = Groq(api_key="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")

SYSTEM_PROMPT = "You are an expert AI Coding Partner for students. Help them learn and build. Provide full code when asked and explain it simply."

MAX_HISTORY = 4

def get_trimmed_messages():
    return st.session_state.messages[-MAX_HISTORY:]

st.title("🎓 Student Coding AI")
st.subheader("Get code and help instantly - 100% Free!")

if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

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
        # ✅ Auto-retry after 60 seconds if rate limited
        for attempt in range(3):  # Try 3 times max
            try:
                with st.spinner("Thinking..." if attempt == 0 else f"Rate limited, retrying in 60s... ⏳"):
                    if attempt > 0:
                        time.sleep(60)  # Wait 60 seconds before retry

                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            *get_trimmed_messages()
                        ],
                        model="llama-3.1-8b-instant",
                        max_tokens=512,
                    )
                    response = chat_completion.choices[0].message.content
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    break  # ✅ Success, stop retrying

            except Exception as e:
                if "rate_limit_exceeded" in str(e) and attempt < 2:
                    continue  # Try again after waiting
                else:
                    st.error(f"Failed after 3 attempts: {e}")
