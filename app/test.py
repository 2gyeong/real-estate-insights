from mo import *
from mo2 import *
import streamlit as st
from langchain.memory import ConversationBufferMemory
# -----------mo------------
from openai import OpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# -----------mo2------------
import json
import pandas as pd
from haversine import haversine

# ----------사이드바-----------
from sidebar import render_sidebar

render_sidebar(last_map=None)

# ----------로고 상태 관리------
from logo import get_base64_image, render_logo

if "logo_small" not in st.session_state:
    st.session_state.logo_small = False
image_base64 = get_base64_image("logo.png")
render_logo(image_base64)

# ---------페이지 컨텐츠 영역-----
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ✅ CSS 커스터마이징
st.markdown(
    """
    <style>
        .ek8upll0 {
            display: flex;
            justify-content: center;
            align-items: center;
            }
        .st-emotion-cache-1d2o6qs { max-width: 1400px !important; }
        .st-emotion-cache-1104ytp p { font-size : 20px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------인터페이스-----------

if "pre_meomory" not in st.session_state:
    st.session_state.pre_memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True
    )

# ✅ 메시지 렌더링 (지도 포함)
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("map_data") is not None:
            display_map_and_list(msg["map_data"])


# 사용자 질문 입력
user_prompt = st.chat_input("부동산 관련 고민이 있으신가요?")

if user_prompt:
    st.session_state.logo_small = True  # 로고 작게 전환

    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("답변을 준비 중입니다..."):
            try:
                question_type = AI1(user_prompt)

                if question_type == "추천":
                    ai_response = AI2(user_prompt)
                    recommended_maemul = RecommendInfo(ai_response)
                    display_map_and_list(recommended_maemul)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": '',
                            "map_data": recommended_maemul
                        }
                    )

                elif question_type == "질문":
                    ai_response = AI2(user_prompt)

                    st.write(ai_response)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": ai_response}
                    )

            except Exception as e:
                st.error(f"에러 발생: {e}")
