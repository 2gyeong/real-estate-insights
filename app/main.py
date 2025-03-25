import streamlit as st
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from openai import OpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain_community.vectorstores import Chroma
from streamlit_folium import st_folium
import folium
import base64

# ---- 사이드바 ----
from components.sidebar import render_sidebar
render_sidebar(last_map=None)

# ---------------- 로고 상태 관리 ----------------
if "logo_small" not in st.session_state:
    st.session_state.logo_small = False

# ---------------- 데이터 로드 및 모델 설정 ----------------
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('jhgan/ko-sroberta-multitask')

@st.cache_data
def load_maemul_data():
    with open('../data/processed/maemul_clear.json', 'r', encoding='utf-8') as f:
        return pd.DataFrame(json.load(f))

@st.cache_resource
def build_faiss_index(data, _model):
    embeddings = _model.encode((data['이름'] + ' ' + data['유형']).tolist()).astype('float32')
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index

embedding_model = load_embedding_model()
maemul_df = load_maemul_data()
faiss_index = build_faiss_index(maemul_df, embedding_model)

embedding_function = OpenAIEmbeddings(api_key=st.secrets["OPENAI_API_KEY"])
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- Moderation ----------------
def moderate_message(message):
    response = client.moderations.create(
        model="text-moderation-latest",
        input=message
    )
    result = response.results[0]
    if result.flagged:
        categories = [cat for cat in result.categories.__dict__ if getattr(result.categories, cat)]
        return False, categories
    return True, None


class ModeratedLLMChain(LLMChain):
    def moderated_and_generate(self, user_input):
        is_safe, categories = moderate_message(user_input)
        if not is_safe:
            st.warning(f"부적절한 메시지로 차단됨: {categories}")
            return ""
        response = self.predict(question=user_input)
        is_safe_ai, categories_ai = moderate_message(response)
        if not is_safe_ai:
            st.warning(f"AI의 부적절 응답 차단됨: {categories_ai}")
            return ""
        return response

# ---------------- 부동산 지식 답변 ----------------
def answer_real_estate_question(question):
    relevant_docs = db.max_marginal_relevance_search(question, k=3)
    context = "\n\n".join([
        f"[출처: {doc.metadata.get('source', '알 수 없음')} 페이지: {doc.metadata.get('page', '알 수 없음')}]\n{doc.page_content}"
        for doc in relevant_docs
    ])

    prompt = f"""
    너는 대한민국 부동산 전문가로서, 사용자의 질문에 친절하고 명확하게 답변하는 AI 어시스턴트야.
    정보가 아예 없으면 '부동산 관련 질문을 해주세요.' 라고만 답변해.
    
    정보:
    {context}
    
    질문:
    {question}
    
    답변:
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

# ---------------- 매물 추천 및 지도 시각화 ----------------
def search_maemul(query, top_k=3):
    query_vec = embedding_model.encode([query]).astype('float32')
    _, indices = faiss_index.search(query_vec, top_k)
    return maemul_df.iloc[indices[0]]

def safe_value(value):
    if pd.isna(value) or value is None:
        return "정보 없음"
    return f"{int(value):,}" if isinstance(value, (int, float)) else str(value)

def display_map_and_list(coords_df):
    if coords_df.empty:
        st.warning("지도에 표시할 매물이 없습니다.")
        return None

    locations = list(zip(coords_df["위도"], coords_df["경도"]))
    col1, col2 = st.columns([2, 1])

    with col1:
        m = folium.Map(location=[coords_df["위도"].mean(), coords_df["경도"].mean()], zoom_start=15)

        for _, row in coords_df.iterrows():
            min_price = safe_value(row.get('최소 분양 가격') or row.get('최소 매매 가격'))
            max_price = safe_value(row.get('최대 분양 가격') or row.get('최대 매매 가격'))
            bunyang_date = safe_value(row.get('분양 연월') or row.get('준공 연월'))

            tooltip_text = (
                f"<b>매물명:</b> {row.get('이름')}<br>"
                f"<b>유형:</b> {row.get('유형')}<br>"
                f"<b>분양가격:</b> {min_price} ~ {max_price}만원<br>"
                f"<b>분양연월:</b> {bunyang_date}<br>"
            )

            folium.Marker(
                [row["위도"], row["경도"]],
                tooltip=tooltip_text,
                icon=folium.DivIcon(html=f"""<div style="font-size: 40px;">🏠</div>""")
            ).add_to(m)

        m.fit_bounds(locations)
        st_folium(m, width=700, height=500)

    with col2:
        st.markdown("### 📋 매물 리스트")
        for idx, row in coords_df.iterrows():
            min_price = safe_value(row.get('최소 분양 가격') or row.get('최소 매매 가격'))
            max_price = safe_value(row.get('최대 분양 가격') or row.get('최대 매매 가격'))
            bunyang_date = safe_value(row.get('분양 연월') or row.get('준공 연월'))

            if st.button(f"🏢 {row.get('이름')}", key=f"item_{idx}"):
                st.session_state["selected_idx"] = idx

            st.markdown(
                f"""
                <div style="padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:5px; background-color:#f9f9f9;">
                    📍 유형: {row.get('유형')}<br>
                    💰 가격: {min_price} ~ {max_price}만원<br>
                    🗓️ 분양연월: {bunyang_date}<br>
                </div>
                """, unsafe_allow_html=True
            )

# ---------------- 질문 유형 판단 ----------------
def classify_question(question):
    knowledge_keywords = ["전세사기", "청약", "세금", "법률", "계약", "등기", "해지"]
    property_keywords = ["추천", "매물", "집", "아파트", "빌라", "부동산", "위치"]

    if any(word in question for word in knowledge_keywords):
        return "knowledge"
    elif any(word in question for word in property_keywords):
        return "property"
    return "general"

# ---------------- Streamlit 인터페이스 ----------------
chat_model = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    api_key=st.secrets["OPENAI_API_KEY"],
    temperature=0.5
)

my_prompt = PromptTemplate(
    input_variables=["chat_history", "question"],
    template="""
    너는 서울시 송파구 부동산에 특화된 친절한 AI 어시스턴트야.
    이전 대화: {chat_history}
    사람: {question}
    AI 어시스턴트:
    """
)

if "pre_memory" not in st.session_state:
    st.session_state.pre_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

moderated_chain = ModeratedLLMChain(llm=chat_model, prompt=my_prompt, memory=st.session_state.pre_memory)

import streamlit as st
import base64

# ---------------- 로고 상태 관리 ----------------
if "logo_small" not in st.session_state:
    st.session_state.logo_small = False

# Base64 이미지 처리
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

image_base64 = get_base64_image("../data/image/logo.png")

# ---------------- CSS 정의 ----------------
st.markdown(f"""
    <style>
        /* 공통 로고 컨테이너 */
        .logo-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            transition: all 0.5s ease-in-out;
        }}

        /* 큰 로고 (중앙 배치) */
        .logo-big {{
            margin-top: 150px;
            position: relative;
        }}

        /* 작은 로고 (화면 고정) */
        .logo-small {{
            position: fixed;
            top: 20px;
            left: 20px;
            background-color: #ffffff;  /* 배경색 지정 */
            padding: 10px;
            margin-top:10px;
            border-radius: 8px;
            z-index: 9999;
            transition: all 0.5s ease-in-out;
        }}

        /* 본문과의 간격 확보 */
        .main-container {{
            transition: margin-top 0.5s ease-in-out;
            margin-top: { '150px' if not st.session_state.logo_small else '80px' };
        }}
    </style>
""", unsafe_allow_html=True)

# ---------------- 로고 렌더링 ----------------
if st.session_state.logo_small:
    logo_class = "logo-container logo-small"
    logo_width = 150
else:
    logo_class = "logo-container logo-big"
    logo_width = 600

st.markdown(f"""
    <div class="{logo_class}">
        <img src="data:image/png;base64,{image_base64}" width="{logo_width}">
    </div>
""", unsafe_allow_html=True)

# ---------------- 페이지 컨텐츠 영역 (예시) ----------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)




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
    unsafe_allow_html=True
)

# ✅ 메시지 렌더링 (지도 포함)
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("map_data") is not None:
            display_map_and_list(msg["map_data"])

# ✅ 사용자 질문 입력
user_prompt = st.chat_input("부동산 관련 질문을 입력하세요.")

if user_prompt:
    st.session_state.logo_small = True  # 로고 작게 전환

    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt
    })

    with st.chat_message("user"):
        st.write(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("답변을 준비 중입니다..."):
            try:
                question_type = classify_question(user_prompt)

                if question_type == "property":
                    ai_response = moderated_chain.moderated_and_generate(user_prompt)
                    recommended_maemul = search_maemul(user_prompt)

                    st.write(ai_response)

                    display_map_and_list(recommended_maemul)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_response,
                        "map_data": recommended_maemul
                    })

                elif question_type == "knowledge":
                    answer = answer_real_estate_question(user_prompt)

                    st.write(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                else:
                    ai_response = moderated_chain.moderated_and_generate(user_prompt)

                    st.write(ai_response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_response
                    })

            except Exception as e:
                st.error(f"에러 발생: {e}")