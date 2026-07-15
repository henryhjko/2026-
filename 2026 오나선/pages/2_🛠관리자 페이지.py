import csv
import os
import streamlit as st
from sample_data import make_sample

st.set_page_config(
    page_title="관리자 페이지",
    page_icon="🛠",
    layout="wide"
)
# -----------------------------------
# 관리자 비밀번호
# -----------------------------------

PASSWORD = "Henry1009"

if "admin_login" not in st.session_state:
    st.session_state.admin_login = False
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

        return list(reader)


ranking = load_results()

# -----------------------------------
# 제목
# -----------------------------------

st.title("🛠 관리자 페이지")
st.subheader("AI Interview Dashboard")
col1, col2 = st.columns(2)

with col1:

    if st.button("📄 샘플 데이터 생성"):

        make_sample()

        st.success("샘플 데이터가 생성되었습니다.")

        st.rerun()

with col2:

    if st.button("🗑 샘플 데이터 삭제"):

        import os

        if os.path.exists("interview_results.csv"):

            os.remove("interview_results.csv")

        st.success("삭제되었습니다.")

        st.rerun()

st.divider()
# -----------------------------------
# 로그인
# -----------------------------------

if not st.session_state.admin_login:

    password = st.text_input(
        "관리자 비밀번호",
        type="password"
    )

    if st.button("로그인"):

        if password == PASSWORD:

            st.session_state.admin_login = True
            st.rerun()

        else:

            st.error("비밀번호가 올바르지 않습니다.")

    st.stop()
if st.button("🚪 로그아웃"):

    st.session_state.admin_login = False
    st.rerun()
# -----------------------------------
# 데이터가 없는 경우
# -----------------------------------

if len(ranking) == 0:

    st.warning("아직 저장된 면접 결과가 없습니다.")
    st.stop()

# -----------------------------------
# 총점 기준 정렬
# -----------------------------------

ranking.sort(
    key=lambda x: int(x["총점"]),
    reverse=True
)

# -----------------------------------
# 통계
# -----------------------------------

avg = sum(
    int(x["총점"])
    for x in ranking
) / len(ranking)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "👥 응시 인원",
        len(ranking)
    )

with col2:

    st.metric(
        "📊 평균 점수",
        f"{avg:.1f}"
    )

with col3:

    st.metric(
        "🏆 최고 점수",
        ranking[0]["총점"]
    )

st.divider()

# -----------------------------------
# 실시간 랭킹
# -----------------------------------

st.header("🏆 실시간 랭킹")

for i, student in enumerate(ranking):

    if i == 0:
        medal = "🥇"

    elif i == 1:
        medal = "🥈"

    elif i == 2:
        medal = "🥉"

    else:
        medal = f"{i+1}."

    st.write(
        f"{medal} {student['이름']}   ({student['총점']}점)"
    )

st.divider()

# -----------------------------------
# 학생 기록 조회
# -----------------------------------

st.header("📂 학생 기록 조회")

names = []

for student in ranking:

    if student["이름"] not in names:

        names.append(student["이름"])

selected = st.selectbox(
    "학생 선택",
    names
)

for student in ranking:

    if student["이름"] == selected:

        with st.expander(
            "📄 면접 기록",
            expanded=True
        ):

            st.metric(
                "총점",
                f"{student['총점']}점"
            )

            st.metric(
                "등급",
                student["등급"]
            )

            st.divider()

            for i in range(1,6):

                st.subheader(f"질문 {i}")

                st.info(student[f"질문{i}"])

                st.write("답변")

                st.success(student[f"답변{i}"])

            st.divider()

            st.subheader("💪 강점")
            st.success(student["강점"])

            st.subheader("📝 보완점")
            st.warning(student["보완점"])

            st.subheader("📄 총평")
            st.info(student["총평"])

        break

st.divider()

# -----------------------------------
# CSV 다운로드
# -----------------------------------

with open(
    CSV_FILE,
    "rb"
) as file:

    st.download_button(
        "📥 CSV 다운로드",
        file,
        file_name="interview_results.csv",
        mime="text/csv",
        use_container_width=True
    )