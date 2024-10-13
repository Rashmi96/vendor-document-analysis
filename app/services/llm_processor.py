import openai
from app.config import Config

openai.api_key = Config.OPENAI_API_KEY

def extract_fields_with_llm(text):
    prompt = f"Extract the relevant fields from the following text:\n\n{text}\n\nFields: Name, Email, Phone, Date."

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )

    return response.choices[0].text.strip()
