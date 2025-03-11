# 파이널 프로젝트
### 폴더 구조

```
real-estate-insights/
│
├── app/                         # Streamlit 앱 메인 디렉터리
│   ├── main.py                  # Streamlit 앱 실행 엔트리 포인트
│   ├── pages/                   # 멀티 페이지 관리 (Streamlit pages 지원)
│   │   ├── map_visualization.py # 지도 기반 매물 시각화 페이지
│   │   └── chatbot.py           # 챗봇 인터페이스 페이지
│   │
│   └── components/          # 공통 컴포넌트 모음 (UI 위젯 등)
│       ├── card.py          # 매물 정보를 보여주는 카드 (이미지+설명+가격+버튼)
│       ├── loader.py        # 로딩 스피너, 상태 표시기
│       ├── map_display.py   # 지도 시각화 함수 (folium/pydeck 등)
│       └── chatbot_ui.py    # 챗봇 메시지 박스, 버튼 등 UI 정의
│
├── config/                  # 설정 파일 모음
│   └── config.yaml          # 프로젝트 전역 설정
│
│
├── data/                    # 데이터 파일 및 벡터 저장소
│   ├── embeddings/          # RAG용 벡터 DB 저장소 (FAISS/Chroma)
│   ├── processed/           # 전처리된 데이터
│   └── raw/                 # 원본 데이터 (매물 데이터, 학습 데이터)
│
├── llm/                     # LLM 관련 모듈 (Fine-tune/RAG)
│   ├── fine_tune/           # Fine-tuning 관련 스크립트 및 모델
│   │   ├── train.py         # 파인튜닝 실행 스크립트
│   │   ├── dataset/         # 파인튜닝용 데이터셋
│   │   └── model/           # 파인튜닝한 모델 저장소
│   │
│   ├── rag/                 # RAG 시스템 구현 모듈
│   │   ├── retriever.py     # 벡터 검색기 구현 (FAISS/Chroma 등)
│   │   ├── reader.py        # 문서 Reader 또는 LLM QA
│   │   └── indexing.py      # 문서 전처리 및 임베딩 처리
│   │
│   └── utils/               # 공통 유틸리티 (토크나이저, 로깅 등)
│       └──  logger.py
│
├── modules/                 # 비즈니스 로직 및 서비스 모듈
│   ├── chatbot/             # 챗봇 기능 모듈
│   │   ├── __init__.py
│   │   ├── rag_pipeline.py  # RAG 기반 검색/생성 파이프라인
│   │   ├── prompt_engine.py # LLM 프롬프트 템플릿 정의 및 관리
│   │   └── qa_engine.py     # 질의응답 처리 및 결과 반환 로직
│   │
│   └── map/                 # 지도 시각화 및 매물 추천 모듈
│       ├── __init__.py
│       ├── data_loader.py   # 지도 및 매물 데이터 로드
│       └── map_renderer.py  # 지도 생성 및 매물 마커 출력
│
├── tests/                   # 테스트 코드
│   ├── test_chatbot.py
│   ├── test_map.py
│   └── test_rag.py
│
├── .gitignore               # Git 관리 제외 항목
├── README.md                # 프로젝트 소개
└── requirements.txt         # 패키지 의존성 목록
```