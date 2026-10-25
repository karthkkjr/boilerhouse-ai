import streamlit as st
from hermes_main import new_conversation, stream_reply_sync
st.title("🏠 BoilerHouse AI")
st.caption("Purdue housing assistant, running 100% locally")

if "messages" not in st.session_state:
    st.session_state.messages = new_conversation()

for m in st.session_state.messages:
    if m["role"] in ("user", "assistant") and m.get("content"):
        st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("Ask about Purdue housing"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        thoughts = st.expander("🧠 Thought process")
        thought_box, thinking = thoughts.empty(), ""
        answer_box, answer = st.empty(), ""
        for kind, text in stream_reply_sync(st.session_state.messages):
            if kind == "thinking":
                thinking += text
                thought_box.markdown(thinking)
            elif kind == "tool":
                st.caption("🔧 " + text)
            else:
                answer += text
                answer_box.markdown(answer)
