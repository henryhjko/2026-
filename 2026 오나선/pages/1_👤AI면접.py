#코드 실행하기:     cd "C:\Users\Family\Desktop\2026 오나선"     작성 후
#       python -m streamlit run app.py    작성

import json
import csv
import os
import time
import streamlit as st

from gemini_api import ask_gemini
from prompt import SYSTEM_PROMPT
from questions import get_questions
# -----------------------------------
# CSV 저장 함수
# -----------------------------------

CSV_FILE = "interview_results.csv"
# -----------------------------------
# CSV 읽기
# -----------------------------------

def load_results():

    if not os.path.exists(CSV_FILE):
        return []

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig"
    ) as f:

        reader = csv.DictReader(f)

        data = list(reader)

    return data

def save_result(name, questions, answers, result):

    file_exists = os.path.exists(CSV_FILE)

    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        if not file_exists:

            writer.writerow([
                "이름",
                "총점",
                "등급",
                "창의성",
                "문제해결력",
                "협업",
                "플레이어중심",
                "강점",
                "보완점",
                "총평",
                "질문1",
                "답변1",
                "질문2",
                "답변2",
                "질문3",
                "답변3",
                "질문4",
                "답변4",
                "질문5",
                "답변5"
            ])

        row = [
            name,
            result["total"],
            result["grade"],
            result["creativity"],
            result["problem_solving"],
            result["communication"],
            result["player_focus"],
            result["strength"],
            result["improvement"],
            result["summary"]
        ]

        for q, a in zip(questions, answers):
            row.append(q)
            row.append(a)

        writer.writerow(row)
# -----------------------------------
# 페이지 설정
# -----------------------------------

st.set_page_config(
    page_icon="🎮",
    layout="centered"
)
# -----------------------------------
# 현재 페이지
# -----------------------------------

if "page" not in st.session_state:
    st.session_state.page = "home"
# -----------------------------------
# 사이드바
# -----------------------------------

st.sidebar.title("🎮 면접 정보")

st.sidebar.write("AI 게임 개발자 채용")

st.sidebar.divider()

st.sidebar.write("📄 출제 문항")
st.sidebar.write("🎮 게임 기획 : 3문항")
st.sidebar.write("🤝 인성·가치관 : 2문항")

st.sidebar.divider()

st.sidebar.info(
    "고현준이 직접 만든 AI가 답변을 분석하여\n"
    "창의성, 문제 해결력,\n"
    "협업 능력, 플레이어 중심 사고를\n"
    "평가합니다."
)
# -----------------------------------
# 질문 생성 (처음 한 번만)
# -----------------------------------

if "questions" not in st.session_state:
    st.session_state.questions = get_questions()

# -----------------------------------
# 제목
# -----------------------------------
# -----------------------------------
# 페이지 선택
# -----------------------------------

if "page" not in st.session_state:
    st.session_state.page = "home"
if st.session_state.page == "home":

    st.title("🎮 AI가 심사하는 모의면접 체험하기")
    st.subheader("30402 고현준 30502 정우성 오나선 ")
    st.divider()

    # -----------------------------------
    # 실시간 랭킹
    # -----------------------------------

    ranking = load_results()
    # -----------------------------------
    # 학생 목록
    # -----------------------------------

    student_names = []

    for student in ranking:

        if student["이름"] not in student_names:

            student_names.append(student["이름"])
    if len(ranking) > 0:

        ranking.sort(
            key=lambda x: int(x["총점"]),
            reverse=True
        )

        st.sidebar.title("🏆 실시간 랭킹")

        top = ranking[:10]

        medals = ["🥇", "🥈", "🥉"]

        for i, student in enumerate(top):

            if i < 3:
                icon = medals[i]
            else:
                icon = f"{i+1}."

            st.sidebar.write(
                f"{icon} {student['이름']}  ({student['총점']}점)"
            )
    if len(ranking) > 0:

        avg = sum(
            int(x["총점"])
            for x in ranking
        ) / len(ranking)

        st.sidebar.divider()

        st.sidebar.metric(
            "📊 평균 점수",
            f"{avg:.1f}점"
        )
        st.sidebar.divider()

        selected_student = st.sidebar.selectbox(
            "📂 학생 기록 조회",
            student_names
        )
        
        show_record = st.sidebar.button(
        "📄 기록 보기",
        use_container_width=True
        )

    # -----------------------------------
    # 이름 입력
    # -----------------------------------

    name = st.text_input(
        "👤 이름을 입력하세요.",
        placeholder="예) 고현준"
    )

    st.header("📋 AI 면접")
    st.info("""
    AI 면접에 오신 것을 환영합니다.

    게임 개발자의 핵심 역량인

    • 창의성
    • 문제 해결력
    • 협업 능력
    • 플레이어 중심 사고

    를 AI가 종합적으로 평가합니다.
    """)
    st.write("다음 질문에 자유롭게 답변해주세요.")

    answers = []

    # -----------------------------------
    # 질문 출력
    # -----------------------------------

    for i, question in enumerate(st.session_state.questions):

        st.subheader(f"질문 {i+1}")

        st.info(question)

        answer = st.text_area(
            "답변",
            key=f"answer_{i}",
            height=150
        )

        answers.append(answer)

    # -----------------------------------
    # 면접 시작 버튼
    # -----------------------------------

    if st.button("🚀 AI 면접 시작", use_container_width=True):

        # 빈 답변 확인
        for answer in answers:

            if answer.strip() == "":
                st.warning("모든 질문에 답변해주세요.")
                st.stop()

        # Gemini에게 보낼 면접 내용 생성
        interview = ""

        for i in range(len(st.session_state.questions)):

            interview += f"""
    질문 {i+1}

    {st.session_state.questions[i]}

    답변

    {answers[i]}

    ----------------------------------------
    """

        with st.spinner("🤖 AI가 답변을 분석하는 중입니다..."):
            time.sleep(2)
            prompt = SYSTEM_PROMPT.replace(
                "{interview}",
                interview
            )

            response = ask_gemini(prompt)

            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

            try:

                result = json.loads(response)

            except Exception:

                st.error("JSON 파싱 실패")

                st.code(response)

                st.stop()
        save_result(
            name,
            st.session_state.questions,
            answers,
            result
        )
        # -----------------------------------
        # 결과 출력
        # -----------------------------------

        st.success("평가 완료!")

        st.divider()

        st.header("🏆 AI 면접 결과")
        grade = result["grade"]

        if grade == "A":

            st.success("🏆 A등급 · 최종 합격")

        elif grade == "B":

            st.warning("🥈 B등급 · 예비 합격")

        else:

            st.error("📌 C등급 · 보완 필요")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("총점", f"{result['total']}점")

        with col2:
            st.metric("등급", result["grade"])

        st.subheader("📊 항목별 점수")

        st.progress(result["creativity"] / 30)
        st.write(f"💡 창의성 : {result['creativity']} / 30")

        st.progress(result["problem_solving"] / 30)
        st.write(f"🛠 문제 해결력 : {result['problem_solving']} / 30")

        st.progress(result["communication"] / 20)
        st.write(f"🤝 협업 및 소통 : {result['communication']} / 20")

        st.progress(result["player_focus"] / 20)
        st.write(f"🎮 플레이어 중심 사고 : {result['player_focus']} / 20")

        st.divider()

        st.subheader("💪 강점")
        st.success(result["strength"])

        st.subheader("📝 보완점")
        st.warning(result["improvement"])

        st.subheader("📄 총평")
        st.info(result["summary"])

    # -----------------------------------
    # 새로운 면접
    # -----------------------------------

    st.divider()
    # -----------------------------------
    # 학생 기록 조회
    # -----------------------------------

    if len(ranking) > 0:

        selected = None

        for student in ranking:

            if student["이름"] == selected_student:

                selected = student

                break
            
    # -----------------------------------
    # 학생 기록 조회
    # -----------------------------------

    if len(ranking) > 0 and show_record:

        selected = None

        for student in ranking:

            if student["이름"] == selected_student:

                selected = student

                break

        if selected:

            st.divider()

            with st.expander(
                f"📂 {selected_student} 면접 기록",
                expanded=True
            ):

                st.metric(
                    "총점",
                    f"{selected['총점']}점"
                )

                st.metric(
                    "등급",
                    selected["등급"]
                )

                st.divider()

                for i in range(1, 6):

                    st.subheader(f"질문 {i}")

                    st.info(selected[f"질문{i}"])

                    st.write("**답변**")

                    st.success(selected[f"답변{i}"])

                st.divider()

                st.subheader("💪 강점")

                st.success(selected["강점"])

                st.subheader("📝 보완점")

                st.warning(selected["보완점"])

                st.subheader("📄 AI 총평")

                st.info(selected["총평"])        

    if st.button("🔄 새로운 면접 시작"):

        st.session_state.questions = get_questions()

        for key in list(st.session_state.keys()):

            if key.startswith("answer_"):
                del st.session_state[key]

        st.rerun()