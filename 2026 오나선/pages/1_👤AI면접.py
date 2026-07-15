# 코드 실행하기:
# cd "C:\Users\Family\Desktop\2026 오나선"
# python -m streamlit run app.py

import json
import csv
import os
import time
import streamlit as st

from gemini_api import ask_gemini
from prompt import SYSTEM_PROMPT
from questions import get_questions

# -----------------------------------
# CSV 저장 설정
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

# -----------------------------------
# CSV 저장 함수 (중복 코드를 제거한 최종본)
# -----------------------------------
def save_result(name, questions, answers, result):
    file_exists = os.path.exists(CSV_FILE)
    
    # 1. Gemini가 준 feedbacks 리스트 가져오기 (만약 없으면 빈 값 대응)
    feedbacks = result.get("feedbacks", ["", "", "", "", ""])
    while len(feedbacks) < 5:
        feedbacks.append("")

    # 2. CSV 파일의 가로줄(헤더) 순서 정의
    fieldnames = [
        "이름", "총점", "등급", "창의성", "문제해결력", "협업", "플레이어중심", 
        "강점", "보완점", "총평", 
        "질문1", "답변1", "코멘트1",
        "질문2", "답변2", "코멘트2",
        "질문3", "답변3", "코멘트3",
        "질문4", "답변4", "코멘트4",
        "질문5", "답변5", "코멘트5"
    ]

    # 3. 데이터 매핑 생성 (Key-Value 매칭으로 밀림 방지)
    row_data = {
        "이름": name,
        "총점": result.get("total", 0),
        "등급": result.get("grade", "C"),
        "창의성": result.get("creativity", 0),
        "문제해결력": result.get("problem_solving", 0),
        "협업": result.get("communication", 0),
        "플레이어중심": result.get("player_focus", 0),
        "강점": result.get("strength", ""),
        "보완점": result.get("improvement", ""),
        "총평": result.get("summary", "")
    }

    # 4. 질문, 답변, 코멘트 세트를 순서대로 매핑해서 집어넣음
    for i in range(5):
        q_val = questions[i] if i < len(questions) else ""
        a_val = answers[i] if i < len(answers) else ""
        c_val = feedbacks[i] if i < len(feedbacks) else ""
        
        row_data[f"질문{i+1}"] = q_val
        row_data[f"답변{i+1}"] = a_val
        row_data[f"코멘트{i+1}"] = c_val

    # 5. DictWriter를 사용해 단 한 번만 깨끗하게 작성 (★과거 중복 코드 제거됨)
    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_data)

# -----------------------------------
# 페이지 설정
# -----------------------------------
st.set_page_config(
    page_icon="🎮",
    layout="centered"
)

# -----------------------------------
# 현재 페이지 세션 초기화
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
    "고현준이 직접 구성한 AI가 답변을 분석하여\n"
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
# 홈 페이지 내용
# -----------------------------------
if st.session_state.page == "home":
    st.title("🎮 AI가 심사하는 모의면접 체험하기")
    st.subheader("30402 고현준 30502 정우성 오나선 ")
    st.divider()

    # 실시간 랭킹 및 학생 목록 로드
    ranking = load_results()
    student_names = []
    for student in ranking:
        if student.get("이름") and student["이름"] not in student_names:
            student_names.append(student["이름"])

    # 사이드바 실시간 랭킹 노출
    if len(ranking) > 0:
        # 안전한 정렬을 위해 총점을 정수로 변환하여 비교
        ranking.sort(
            key=lambda x: int(x.get("총점", 0)) if str(x.get("총점", "")).isdigit() else 0,
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
                f"{icon} {student['이름']}  ({student.get('총점', 0)}점)"
            )

        # 평균 점수 계산 및 노출
        valid_scores = [int(x["총점"]) for x in ranking if str(x.get("총점", "")).isdigit()]
        if valid_scores:
            avg = sum(valid_scores) / len(valid_scores)
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

    # 이름 입력
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

    # 질문 출력
    for i, question in enumerate(st.session_state.questions):
        st.subheader(f"질문 {i+1}")
        st.info(question)
        answer = st.text_area(
            "답변",
            key=f"answer_{i}",
            height=150
        )
        answers.append(answer)

    # 면접 시작 버튼 클릭 시 작동 로직
    if st.button("🚀 AI 면접 시작", use_container_width=True):
        if not name.strip():
            st.warning("이름을 입력해주세요.")
            st.stop()
            
        for answer in answers:
            if answer.strip() == "":
                st.warning("모든 질문에 답변해주세요.")
                st.stop()

        interview = ""
        for i in range(len(st.session_state.questions)):
            interview += f"\n질문 {i+1}\n\n{st.session_state.questions[i]}\n\n답변\n\n{answers[i]}\n\n----------------------------------------\n"

        with st.spinner("🤖 AI가 답변을 분석하는 중입니다..."):
            time.sleep(2)
            prompt = SYSTEM_PROMPT.replace("{interview}", interview)
            response = ask_gemini(prompt)

            response = response.replace("```json", "").replace("```", "").strip()

            try:
                result = json.loads(response)
            except Exception:
                st.error("JSON 파싱 실패")
                st.code(response)
                st.stop()

        # 구조적 안전 저장 함수 호출
        save_result(name, st.session_state.questions, answers, result)
        
        st.success("평가 완료! (기록이 안전하게 저장되었습니다.)")
        st.divider()

        # 결과 출력 화면
        st.header("🏆 AI 면접 결과")
        grade = result.get("grade", "C")

        if grade == "A":
            st.success("🏆 A등급 · 최종 합격")
        elif grade == "B":
            st.warning("🥈 B등급 · 예비 합격")
        else:
            st.error("📌 C등급 · 보완 필요")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("총점", f"{result.get('total', 0)}점")
        with col2:
            st.metric("등급", result.get("grade", "C"))

        st.subheader("📊 항목별 점수")

        # 안전한 데이터 형변환 및 progress 바 처리
        c_score = int(result.get("creativity", 0))
        p_score = int(result.get("problem_solving", 0))
        m_score = int(result.get("communication", 0))
        f_score = int(result.get("player_focus", 0))

        st.progress(max(0.0, min(1.0, c_score / 30)))
        st.write(f"💡 창의성 : {c_score} / 30")

        st.progress(max(0.0, min(1.0, p_score / 30)))
        st.write(f"🛠 문제 해결력 : {p_score} / 30")

        st.progress(max(0.0, min(1.0, m_score / 20)))
        st.write(f"🤝 협업 및 소통 : {m_score} / 20")

        st.progress(max(0.0, min(1.0, f_score / 20)))
        st.write(f"🎮 플레이어 중심 사고 : {f_score} / 20")

        st.divider()
        st.subheader("💪 강점")
        st.success(result.get("strength", ""))
        st.subheader("📝 보완점")
        st.warning(result.get("improvement", ""))
        st.subheader("📄 총평")
        st.info(result.get("summary", ""))

    st.divider()

    # 학생 기록 실시간 사이드바 버튼 매핑 뷰어
    if len(ranking) > 0 and 'show_record' in locals() and show_record:
        selected = None
        for student in ranking:
            if student.get("이름") == selected_student:
                selected = student
                break

        if selected:
            st.divider()
            with st.expander(f"📂 {selected_student} 면접 기록 조회", expanded=True):
                st.metric("총점", f"{selected.get('총점', 0)}점")
                st.metric("등급", selected.get("등급", "C"))
                st.divider()

                for i in range(1, 6):
                    st.subheader(f"질문 {i}")
                    st.info(selected.get(f"질문{i}", "정보 없음"))
                    st.write("**답변**")
                    st.success(selected.get(f"답변{i}", "정보 없음"))
                    
                    # 관리자 페이지처럼 개별 코멘트가 존재하는 포맷일 경우 처리
                    if selected.get(f"코멘트{i}"):
                        st.write("**🤖 AI 개별 코멘트**")
                        st.warning(selected.get(f"코멘트{i}"))

                st.divider()
                st.subheader("💪 강점")
                st.success(selected.get("강점", ""))
                st.subheader("📝 보완점")
                st.warning(selected.get("보완점", ""))
                st.subheader("📄 AI 총평")
                st.info(selected.get("총평", ""))

    if st.button("🔄 새로운 면접 시작"):
        st.session_state.questions = get_questions()
        for key in list(st.session_state.keys()):
            if key.startswith("answer_"):
                del st.session_state[key]
        st.rerun()
