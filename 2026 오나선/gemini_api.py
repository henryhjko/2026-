from google import genai

client = genai.Client(api_key="AQ.Ab8RN6JKDVXmSLQDG9spShpZ8JmbgkRShaEtBPYW_Pdbv0vuKg")

MODEL = "gemini-3.5-flash"

def ask_gemini(prompt):
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text