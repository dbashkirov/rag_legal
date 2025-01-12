import streamlit as st
import requests
from datetime import datetime

st.title("Legal AI Assistant")


URL = "http://localhost:8181"


def wrapper(s):
    for data in s:
        yield data.decode()


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "fb_k" not in st.session_state:
    st.session_state["fb_k"] = None

if prompt := st.chat_input("Какой у вас вопрос?"):
    print(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with requests.post(f"{URL}/saiga_law", json={"text": prompt}, stream=True) as s:

            response = st.write_stream(wrapper(s))

    with st.sidebar:
        res = requests.get(f"{URL}/source_law", json={"text": prompt})
        st.write(res.json())

    st.session_state.messages.append({"role": "assistant", "content": response})

    selected = st.feedback("thumbs", key="fb_k")

if st.session_state["fb_k"] is not None:
    print(st.session_state["fb_k"])
    print(st.session_state.messages[-2], st.session_state.messages[-1])
