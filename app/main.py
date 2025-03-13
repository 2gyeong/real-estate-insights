import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 기본 설정
st.set_page_config(page_title="은퇴 챗봇 + 지도 추천", layout="wide")

# 예시 매물 데이터
sample_data = pd.DataFrame({
    'name': ['강남 아파트', '서초 아파트', '잠실 아파트'],
    'price': ['12억', '10억', '15억'],
    'desc': ['역세권 신축 아파트입니다.', '조용한 주택가에 위치한 아파트입니다.', '한강뷰 고층 아파트입니다.'],
    'lat': [37.4979, 37.4838, 37.5146],
    'lon': [127.0276, 127.0327, 127.1025]
})

# ✅ 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
    ]

if 'show_map' not in st.session_state:
    st.session_state.show_map = False  # 지도 기본 OFF 상태

# ✅ 이전 대화 출력
st.title("은퇴 설계 GPT 챗봇 🤖")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ✅ 사용자 입력 받기
user_prompt = st.chat_input("메시지를 입력하세요!", key="main_chat")

if user_prompt:
    # 사용자 입력 세션에 추가
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.write(user_prompt)

    # ✅ 매물 추천 키워드 감지 → 지도 보여주기
    if "매물 보여줘" in user_prompt:
        st.session_state.show_map = True  # 지도 ON
        bot_response = "네! 추천 매물을 보여드릴게요. 지도를 확인하세요!"
    
    # ✅ 다른 질문은 지도 OFF
    else:
        # 이전에 지도가 보여지고 있었다면 → 지도 숨기기!
        if st.session_state.show_map:
            st.session_state.show_map = False
        
        bot_response = "네! 궁금한 점을 계속 질문해주세요 😊"

    # 챗봇 응답 추가
    st.session_state.messages.append({"role": "assistant", "content": bot_response})

    with st.chat_message("assistant"):
        st.write(bot_response)

# ✅ 지도 시각화 (플래그가 True일 때만!)
if st.session_state.show_map:
    st.markdown("---")
    st.subheader("🗺️ 추천 매물 지도 시각화")

    # folium 지도 생성
    m = folium.Map(location=[sample_data['lat'].mean(), sample_data['lon'].mean()], zoom_start=13)

    # 매물 마커 추가
    for idx, row in sample_data.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"{row['name']} ({row['price']})"
        ).add_to(m)

    # Streamlit에 지도 출력
    st_folium(m, width=700, height=500)

    # 매물 정보 카드도 같이 보여주기
    st.subheader("🏠 추천 매물 리스트")
    for idx, row in sample_data.iterrows():
        with st.container(border=True):
            st.markdown(f"### {row['name']}")
            st.markdown(f"💰 **가격:** {row['price']}")
            st.markdown(f"📝 {row['desc']}")
            st.button("자세히 보기", key=f"detail_{idx}")

