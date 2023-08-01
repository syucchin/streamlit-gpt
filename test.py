import os
import openai
import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

# ヘッダからユーザー情報を取得
headers = _get_websocket_headers()
principal_name = headers.get("X-Ms-Client-Principal-Name")

# スレッド番号がなければ1を入れる
st.session_state.setdefault("thread_num", "1")

# スレッドの選択。ボタンから呼ばれる
def select_thread(num):
    st.session_state["thread_num"] = num
    st.session_state.messages = st.session_state[f"messages{num}"]


# 初期のタイトル設定
for i in range(1, 11):
    st.session_state.setdefault(f"title{i}", "New Chat")

# 初期スレッドメッセージの設定
message_data = []

for i in range(1, 11):  # 1から10までループ
    key = f"messages{i}"  # キーを生成（messages1, messages2, ... , messages10）
    st.session_state.setdefault(key, message_data)

with st.sidebar:
    # ヘッダからユーザー情報を取得できなければ、Guest として表示
    if principal_name is not None:
        st.markdown('ようこそ ' + principal_name + 'さん')
    else:
        st.markdown('ようこそ Guest さん')

    for i in range(1, 11):
        st.button(label=st.session_state[f"title{i}"], key=i, on_click=select_thread, args=str(i))

st.title("Streamlit ChatKun")

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT_FQDN")

#OpenAIで必要な変数設定を実装する
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
    print(st.session_state.messages)

i = st.session_state["thread_num"]
key = f"messages{i}"  # キーを生成
if key in st.session_state:
    st.session_state[key] = st.session_state.messages.copy()
    # st.session_state.messages.extend(st.session_state[key])
    print(st.session_state.messages)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "system":
            continue
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("入力してください"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state[f"messages{st.session_state['thread_num']}"] = st.session_state.messages
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

st.session_state[key] = st.session_state.messages

print(st.session_state)
