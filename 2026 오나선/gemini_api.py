import streamlit as st
from google import genai

# Streamlit Secrets에서 안전하게 API 키를 가져옵니다.
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# [수정] 대안 1-1: 가볍고 트래픽 과부하에 강한 최신 라이트 모델 적용
MODEL = "gemini-3.1-flash-lite"

def ask_gemini(prompt):
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        # 화면에 에러를 보여주되, 원인이 무엇인지 명확하게 알려줍니다.
        return f"AI 호출 중 오류 발생: {str(e)}"
