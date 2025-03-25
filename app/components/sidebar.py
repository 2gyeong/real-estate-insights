import streamlit as st

def render_sidebar(last_map=None):
    
    # 세션 상태 초기화
    if "info_page" not in st.session_state:
        st.session_state["info_page"] = 0

    # 페이지 데이터 정의
    pages = [
        {
            "title": "📌 프로젝트 소개",
            "content": """
            **부동산 AI 챗봇**
            - 질문하고 매물 추천받기!
            - 지도에서 매물 위치 보기!
            - 부동산 지식 검색!
            """
        },
        {
            "title": "🛠️ 사용법",
            "content": """
            1. 원하는 부동산 관련 질문 입력
            2. 매물 추천 또는 지식 답변 확인
            3. 지도로 매물 위치 확인 가능
            """
        },
        {
            "title": "📍 개발 환경 및 정보",
            "content": """
            - Python 3.10
            - Streamlit
            - LangChain, OpenAI API
            - Folium 지도 시각화
            """
        }
    ]

    # 현재 페이지 인덱스 가져오기
    current_page = st.session_state["info_page"]

    # 페이지 타이틀
    st.sidebar.subheader(pages[current_page]["title"])

    # ✅ 고정 높이 삭제하고 가로 스크롤 차단 + 줄바꿈 처리

    st.sidebar.markdown(
    f"""
    <pre class="e1xss9yb2" style="
        background-color: #f0f2f6;
        padding: 12px 16px;
        border-radius: 5px;
        border: 1px solid rgba(49, 51, 63, 0.2);
        font-size: 0.9rem;
        line-height: 1.5;
        white-space: pre-wrap;   /* ✅ 줄바꿈 지원 */
        word-wrap: break-word;   /* ✅ 긴 단어 줄바꿈 */
        overflow-x: hidden;      /* ✅ 가로 스크롤 방지 */
        height: 300px;           /* ✅ 고정 높이 */
    ">
    {pages[current_page]["content"]}
    </pre>
    """,
    unsafe_allow_html=True
    )


    # 화살표 버튼 배치
    col1, col2, col3 = st.sidebar.columns([1, 2, 1])

    # 이전 페이지 버튼
    with col1:
        if st.button("◀", key="prev"):
            st.session_state["info_page"] = (current_page - 1) % len(pages)

    # 페이지 인덱스 표시 (1/3)
    with col2:
        st.markdown(f"<p style='text-align: center;'>{current_page + 1} / {len(pages)}</p>", unsafe_allow_html=True)

    # 다음 페이지 버튼
    with col3:
        if st.button("▶", key="next"):
            st.session_state["info_page"] = (current_page + 1) % len(pages)


