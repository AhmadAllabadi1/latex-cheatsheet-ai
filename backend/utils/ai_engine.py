from openai import OpenAI
import os

def generate_cheatsheet(content: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ OPENAI_API_KEY not found in environment variables.")
    
    client = OpenAI(api_key=api_key)

    prompt = (
        "You are a LaTeX expert. Create a concise, one-page cheat sheet from the following notes.\n"
        "DO NOT include \\documentclass, \\begin{document}, or \\end{document}.\n"
        "DO NOT include Markdown-style code blocks like ```latex.\n"
        "Return ONLY the LaTeX body content with sections, subsections, itemize/enumerate/environments.\n"
        "Avoid explanations or wrapping.\n\n"
        "--- NOTES ---\n"
        f"{content}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )

    return response.choices[0].message.content.strip()
