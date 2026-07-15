import streamlit as st

st.set_page_config(
    page_title="AI 면접 시스템",
    page_icon="🎮",
    layout="centered"
)

st.title("🎮 AI가 심사하는 모의면접 체험하기")
st.subheader("30402 고현준 30502 정우성 오나선")

st.divider()

st.markdown("""
### 환영합니다!

생성형 AI가 게임회사 면접을 평가하는 프로그램입니다.

왼쪽 사이드바에서 원하는 페이지를 선택하세요. (오나선 참여 학생들은 "👤AI면접" 선택)

- 👤 AI면접
- 🛠 관리자
""")

#cd "C:\Users\Family\Desktop\2026 오나선"
#python -m streamlit run app.py