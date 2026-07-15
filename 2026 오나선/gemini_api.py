import streamlit as st
from google import genai

# 1. Streamlit Secrets에서 API 키를 안전하게 가져옵니다.
# (깃허브에 키가 노출되어 차단되는 것을 방지)
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# 2. 올바른 최신 표준 모델명으로 수정합니다.
MODEL = "gemini-3.5-flash"

def ask_gemini(prompt):
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI 호출 중 오류 발생: {str(e)}"
