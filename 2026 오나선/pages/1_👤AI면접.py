# 코드 실행하기:     cd "C:\Users\Family\Desktop\2026 오나선"     작성 후
#                python -m streamlit run app.py    작성

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

    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return data

def save_result(name, questions, answers, result):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "이름", "총점", "등급", "창의성", "문제해결력", "협업", "플레이어중심", 
                "강점", "보완점", "총평", 
                "질문1", "답변1", "질문2", "답변2", "질문3", "답변3", "질문4", "답변4", "질문5", "답변5"
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
# 세션 상태(Session State) 초기화
# -----------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "questions" not in st.session_state:
    st.session_state.questions = get_questions()

# [수정] 기록 조회가 활성화되었는지 유지하기 위한 세션 추가
if "active_record_student" not in st.session_state:
    st.session_state.active_record_student = None

# -----------------------------------
# 사이드바 데이터 로드 및 랭킹 세팅
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

ranking = load_results()
student_names = []

for student in ranking:
    if student["이름"] not in student_names:
        student_names.append(student["이름"])

if len(ranking) > 0:
    # 총점 내림차순 정렬
    ranking.sort(key=lambda x: int(x["총점"]), reverse=True)
    
    st.sidebar.title("🏆 실시간 랭킹")
    top = ranking[:10]
    medals = ["🥇", "🥈", "🥉"]

    for i, student in enumerate(top):
        if i < 3:
            icon = medals[i]
        else:
            icon = f"{i+1}."
        st.sidebar.write(f"{icon} {student['이름']}  ({student['총점']}점)")

    # 평균 점수 출력
    avg = sum(int(x["총점"]) for x in ranking) / len(ranking)
    st.sidebar.divider()
    st.sidebar.metric("📊 평균 점수", f"{avg:.1f}점")
    st.sidebar.divider()

    # 학생 기록 조회 박스
    selected_student = st.sidebar.selectbox("📂 학생 기록 조회", student_names)
    
    # [수정] 기록 보기 버튼을 누르면 세션에 조회 대상 학생을 박아둡니다.
    if st.sidebar.button("📄 기록 보기", use_container_width=True):
        st.session_state.active_record_student = selected_student

# -----------------------------------
# 메인 홈 화면 구동
# -----------------------------------
if st.session_state.page == "home":
    st.title("🎮 AI가 심사하는 모의면접 체험하기")
    st.subheader("30402 고현준 30521 정우성 오나선")
    st.divider()

    # 이름 입력
    name = st.text_input("👤 이름을 입력하세요.", placeholder="예) 고현준")

    st.header("📋 AI 면접")
    st.info("""
    AI 면접에 오신 것을 환영합니다.
    게임 개발자의 핵심 역량인
    • 창의성 • 문제 해결력 • 협업 능력 • 플레이어 중심 사고
    를 AI가 종합적으로 평가합니다.
    """)
    st.write("다음 질문에 자유롭게 답변해주세요.")

    answers = []

    # 질문 출력 및 입력창 생성
    for i, question in enumerate(st.session_state.questions):
        st.subheader(f"질문 {i+1}")
        st.info(question)
        answer = st.text_area("답변", key=f"answer_{i}", height=150)
        answers.append(answer)

    # -----------------------------------
    # AI 면접 시작 제출 동작
    # -----------------------------------
    if st.button("🚀 AI 면접 시작", use_container_width=True):
        # 이름 검사
        if name.strip() == "":
            st.warning("이름을 입력해야 면접을 시작할 수 있습니다.")
            st.stop()
            
        # 빈 답변 확인
        for answer in answers:
            if answer.strip() == "":
                st.warning("모든 질문에 답변해주세요.")
                st.stop()

        # 면접 내용 결합
        interview = ""
        for i in range(len(st.session_state.questions)):
            interview += f"\n질문 {i+1}\n{st.session_state.questions[i]}\n답변\n{answers[i]}\n----------------------------------------\n"

        with st.spinner("🤖 AI가 답변을 분석하는 중입니다..."):
            prompt = SYSTEM_PROMPT.replace("{interview}", interview)
            response = ask_gemini(prompt)

            # JSON 파싱 가공
            response = response.replace("```json", "").replace("```", "").strip()

            try:
                result = json.loads(response)
            except Exception:
                st.error("JSON 파싱 실패")
                st.code(response)
                st.stop()

        # CSV 파일에 저장
        save_result(name, st.session_state.questions, answers, result)
        
        # 새로운 응답 갱신 후 화면 전환을 위한 rerun
        st.success("평가 완료! 리더보드가 업데이트되었습니다.")
        time.sleep(1)
        st.rerun()

    # -----------------------------------
    # [수정] 학생 기록 화면단 출력 파트
    # -----------------------------------
    # 세션에 보기 요청된 학생 정보가 남아 있다면 하단에 출력합니다.
    if len(ranking) > 0 and st.session_state.active_record_student is not None:
        target_student = st.session_state.active_record_student
        
        # 랭킹 데이터에서 매핑되는 학생의 '가장 최근 데이터' 가져오기
        selected = None
        for student in ranking:
            if student["이름"] == target_student:
                selected = student
                break # 이미 정렬 상태이므로 첫번째 매칭 데이터를 가져옴

        if selected:
            st.divider()
            with st.expander(f"📂 {target_student} 학생의 실제 면접 답변 및 평가 기록", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("총점", f"{selected['총점']}점")
                with col2:
                    st.metric("등급", selected["등급"])

                st.divider()

                # 1번부터 5번 질문과 실제 CSV에 기록된 답변 출력하기
                for i in range(1, 6):
                    st.markdown(f"### ❓ 질문 {i}")
                    st.info(selected.get(f"질문{i}", "등록된 질문 정보가 없습니다."))
                    st.markdown("**✏️ 학생의 실제 입력 답변**")
                    st.success(selected.get(f"답변{i}", "작성된 답변이 없습니다."))
                    st.write("")

                st.divider()
                st.subheader("📊 역량 스코어 요약")
                
                # 역량별 점수 시각화 (CSV 컬럼명 백업 매핑)
                # 만약 CSV 헤더가 영어 key값이 아니라 한글 컬럼명으로 들어왔을 경우를 대비한 .get 안전 가드 처리
                c_score = int(selected.get("창의성", 0))
                p_score = int(selected.get("문제해결력", 0))
                co_score = int(selected.get("협업", 0))
                pl_score = int(selected.get("플레이어중심", 0))
                
                st.progress(c_score / 30)
                st.write(f"💡 창의성 : {c_score} / 30")
                st.progress(p_score / 30)
                st.write(f"🛠️ 문제 해결력 : {p_score} / 30")
                st.progress(co_score / 20)
                st.write(f"🤝 협업 및 소통 : {co_score} / 20")
                st.progress(pl_score / 20)
                st.write(f"🎮 플레이어 중심 사고 : {pl_score} / 20")

                st.divider()
                st.subheader("💪 강점")
                st.info(selected.get("강점", "데이터 없음"))

                st.subheader("📝 보완점")
                st.warning(selected.get("보완점", "데이터 없음"))

                st.subheader("📄 AI 최종 심사평")
                st.success(selected.get("총평", "데이터 없음"))

    # -----------------------------------
    # 새로운 면접 시작 버튼 초기화
    # -----------------------------------
    st.divider()
    if st.button("🔄 새로운 면접 시작 (입력 폼 초기화)"):
        st.session_state.questions = get_questions()
        st.session_state.active_record_student = None # 기록 보기 창 닫기
        
        for key in list(st.session_state.keys()):
            if key.startswith("answer_"):
                del st.session_state[key]
        st.rerun()
