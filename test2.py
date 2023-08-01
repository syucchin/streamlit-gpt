import os
import openai
import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

# ヘッダからユーザー情報を取得
headers = _get_websocket_headers()
principal_name = headers.get("X-Ms-Client-Principal-Name")

# スレッド番号がなければ1を入れる
st.session_state.setdefault("thread_num", "0")

# スレッドの選択。ボタンから呼ばれる
def select_thread(num):
    st.session_state["thread_num"] = num
    st.session_state.messages = st.session_state[f"thread{num}"].copy()

# 初期のスレッド名の設定
for i in range(0, 10):
    st.session_state.setdefault(f"thread_name{i}", "New Chat")

# 初期スレッドメッセージの設定
message_data = [{"role": "system", "content": "ギャル語で話して"}]

for i in range(0, 10):  # 1から10までループ
    key = f"thread{i}"  # キーを生成（messages1, messages2, ... , messages10）
    st.session_state.setdefault(key, message_data.copy())

with st.sidebar:
    # ヘッダからユーザー情報を取得できなければ、Guest として表示
    if principal_name is not None:
        st.markdown('ようこそ ' + principal_name + 'さん')
    else:
        st.markdown('ようこそ Guest さん')

    for i in range(0, 10):
        st.button(label=st.session_state[f"thread_name{i}"], key=i, on_click=select_thread, args=str(i))

st.title("Streamlit ChatKun")

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT_FQDN")

#OpenAIで必要な変数設定を実装する
openai.api_type = "azure"                     #APITYPEの指定をAzure用に指定
openai.api_key = API_KEY                      #APIキーを指定
openai.api_base = RESOURCE_ENDPOINT           #アクセスエンドポイントを指定
openai.api_version = "2023-03-15-preview"     #適合するAPIバージョンを指定

if "openai_model" not in st.session_state:
    # st.session_state["openai_model"] = "gpt-4"
    st.session_state["openai_model"] = "gpt-35-turbo-16k"

if "messages" not in st.session_state:
    st.session_state.messages = st.session_state[f"thread{st.session_state['thread_num']}"].copy()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "system":
            continue
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("入力してください"):
    # スレッドのタイトルが "New Chat" のままの場合は、入力から設定
    if st.session_state[f"thread_name{st.session_state['thread_num']}"] == "New Chat":
        st.session_state[f"thread_name{st.session_state['thread_num']}"] = prompt[:16]

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state[f"thread{st.session_state['thread_num']}"] = st.session_state.messages.copy()
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            engine = st.session_state["openai_model"],
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
        ):
            if len(response.choices) > 0:
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            else:
                print("No response generated")

            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# メッセージを現在のスレッドに保存
st.session_state[f"thread{st.session_state['thread_num']}"] = st.session_state.messages.copy()

print(st.session_state)
