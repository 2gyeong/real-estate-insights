import streamlit as st
from openai import OpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA


# 초기 설정

key = st.secrets["OPENAI_API_KEY"]
chat_model1 = OpenAI(api_key=key).chat.completions
chat_model2 = ChatOpenAI(model="gpt-3.5-turbo", api_key=key)
hf = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")
my_dictionary = "DB"
vectorDB = Chroma(persist_directory=my_dictionary, embedding_function=hf)

my_retriever = vectorDB.as_retriever(
    search_type="mmr",
    search_kwargs={"fetch_k": 10, "k": 3, "lambda_mult": 0.1},
    filter={"for": "질문"},
)

R_QA = RetrievalQA.from_chain_type(
    llm=chat_model2,
    chain_type="stuff",
    retriever=my_retriever,
    return_source_documents=True,
)


# 구분 모델


def AI1(inp):
    return (
        chat_model1.create(
            model="ft:gpt-3.5-turbo-0125:fininsight::BByIChMO",
            messages=[
                {
                    "role": "system",
                    "content": '사용자의 입력을 질문과 매물 추천 요청으로 구분하여 각각 "질문", "추천"만을 출력합니다.',
                },
                {"role": "user", "content": inp},
            ],
        )
        .choices[0]
        .message.content
    )


# 구분 결과로 출력 생성 모델
def AI2(inp):
    classify = AI1(inp)
    if classify == "질문":
        answer = R_QA.invoke(inp)["result"]
        return answer
    if classify == "추천":
        recommends = vectorDB.max_marginal_relevance_search(
            inp, fetch_k=50, k=2, lambda_mult=0.1, filter={"for": "추천"}
        )
        return [re.metadata["이름"] for re in recommends]
