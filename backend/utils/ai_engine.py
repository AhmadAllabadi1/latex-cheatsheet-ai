from openai import OpenAI
import os

def generate_cheatsheet(content: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ OPENAI_API_KEY not found in environment variables.")
    
    client = OpenAI(api_key=api_key)

    prompt = """
    You are a concise technical summarizer. Your goal is to convert academic or technical content into a dense, LaTeX-ready cheat sheet.

    Follow these strict rules:

    1. Do NOT include section titles or headings.
    2. Do NOT paraphrase, skip, or reword — compress key ideas only.
    3. Do NOT output explanations or commentary.
    4. Use \\textbf{} to highlight key terms or concepts.
    5. Include formulas using math mode: \\( ... \\) or \\[ ... \\].
    6. Each item should be one line or less. Avoid full sentences when possible.
    7. Maintain all important mathematical or technical details. Do not simplify or generalize.
    8. Seperate each item with a new line.
    9. You have enough space for 1 page in \small text. Utilize as much as possible.
    10. Ensure you use the correct math symbols, do not use symbols such as μ directly, use \\mu instead.
    Only return valid LaTeX. Do not include markdown or code blocks. Your output will be compiled directly into a PDF cheat sheet.

    Now, summarize the following:
    """ + content


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )

    return response.choices[0].message.content.strip()
