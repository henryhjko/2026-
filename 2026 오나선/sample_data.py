import csv
import random
import os

CSV_FILE = "interview_results.csv"

names = [
    "김민수","이서준","박지훈","최현우","정예린",
    "한지민","윤도현","강민재","송지우","조서연",
    "신유진","백승호","김도윤","박서연","이준혁",
    "최은우","장하린","오지훈","문예진","유시현"
]

questions = [
    "게임 질문 1",
    "게임 질문 2",
    "게임 질문 3",
    "윤리 질문 1",
    "윤리 질문 2"
]

strengths = [
    "창의적인 아이디어가 돋보입니다.",
    "논리적인 설명이 뛰어납니다.",
    "협업을 중요하게 생각합니다.",
    "플레이어 중심 사고가 우수합니다.",
    "문제 해결 과정이 체계적입니다."
]

improvements = [
    "조금 더 구체적인 근거를 제시하면 좋겠습니다.",
    "답변을 더 논리적으로 구성하면 좋겠습니다.",
    "사례를 함께 제시하면 설득력이 높아집니다.",
    "협업 과정 설명이 부족합니다.",
    "플레이어 입장을 더 고려하면 좋겠습니다."
]

summaries = [
    "전반적으로 우수한 답변입니다.",
    "잠재력이 높은 지원자입니다.",
    "조금만 보완하면 매우 좋은 평가를 받을 수 있습니다.",
    "창의성과 문제 해결력이 인상적입니다."
]


def make_sample():

    if os.path.exists(CSV_FILE):
        return

    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "이름","총점","등급",

            "질문1","답변1",
            "질문2","답변2",
            "질문3","답변3",
            "질문4","답변4",
            "질문5","답변5",

            "강점","보완점","총평"
        ])

        for name in names:

            creativity = random.randint(18,30)
            solving = random.randint(18,30)
            communication = random.randint(12,20)
            player = random.randint(12,20)

            total = creativity + solving + communication + player

            if total >= 90:
                grade = "S"

            elif total >= 80:
                grade = "A"

            elif total >= 70:
                grade = "B"

            else:
                grade = "C"

            writer.writerow([
                name,
                total,
                grade,

                questions[0],
                "샘플 답변입니다.",

                questions[1],
                "샘플 답변입니다.",

                questions[2],
                "샘플 답변입니다.",

                questions[3],
                "샘플 답변입니다.",

                questions[4],
                "샘플 답변입니다.",

                random.choice(strengths),
                random.choice(improvements),
                random.choice(summaries)
            ])