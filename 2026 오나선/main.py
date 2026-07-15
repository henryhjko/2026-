import json

from gemini_api import ask_gemini
from prompt import SYSTEM_PROMPT


print("=" * 55)
print("🎮 Pixel Forge Studio AI 면접 시스템")
print("=" * 55)

print()
print("면접 질문")
print("-" * 55)
print("우리 게임이 '재미없다'는 평가를 받고 있습니다.")
print("단 하나의 업데이트만 할 수 있다면 무엇을 추가하시겠습니까?")
print("그리고 왜 그렇게 생각하는지 설명해주세요.")
print()

print("=" * 55)
print("답변을 입력하세요.")
print("(입력이 끝나면 빈 줄에서 Enter를 누르세요.)")
print("=" * 55)

lines = []

while True:

    line = input()

    if line == "":
        break

    lines.append(line)

answer = "\n".join(lines)

prompt = SYSTEM_PROMPT.replace("{answer}", answer)

print("\n🤖 AI가 답변을 분석하는 중입니다...\n")

response = ask_gemini(prompt)

response = response.replace("```json", "")
response = response.replace("```", "")
response = response.strip()

try:

    result = json.loads(response)

except Exception:

    print("JSON 파싱 실패\n")
    print(response)
    exit()

print("=" * 55)
print("🎮 Pixel Forge Studio AI 면접 결과")
print("=" * 55)

print()

print(f"🏆 총점 : {result['total']}점")
print(f"🎖 등급 : {result['grade']}")

print()

print("📊 항목별 점수")
print("-" * 55)

print(f"💡 창의성              {result['creativity']} / 30")
print(f"🛠 문제 해결력         {result['problem_solving']} / 30")
print(f"🤝 협업 및 소통        {result['communication']} / 20")
print(f"🎮 플레이어 중심 사고   {result['player_focus']} / 20")

print()

print("💪 강점")
print(result["strength"])

print()

print("📝 보완점")
print(result["improvement"])

print()

print("📄 총평")
print(result["summary"])

print()
print("=" * 55)