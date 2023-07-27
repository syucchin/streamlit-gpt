import os
import openai
import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

# ユーザー情報の取得
headers = _get_websocket_headers()
principal_name = headers.get("X-Ms-Client-Principal-Name")

with st.sidebar:
    if principal_name is not None:
        st.markdown('ようこそ ' + principal_name + 'さん')

st.title("ChatGPT-like clone")

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT_FQDN")

#OpenAI上必要な変数設定を実装する
openai.api_type = "azure"                     #APITYPEの指定をAzure用に指定
openai.api_key = API_KEY                      #APIキーを指定
openai.api_base = RESOURCE_ENDPOINT         #アクセスエンドポイントを指定
openai.api_version = "2023-03-15-preview"     #適合するAPIバージョンを指定

if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"
#     st.session_state["openai_model"] = "gpt-4-32k"
    st.session_state["openai_model"] = "gpt-4"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": "ギャル語で話して"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "system":
            continue
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("入力してください"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            # model = st.session_state["openai_model"],
            engine = st.session_state["openai_model"],
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

print(st.session_state)
