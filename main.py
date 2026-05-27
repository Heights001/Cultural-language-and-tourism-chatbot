import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

SYSTEM_PROMPT = """You are Kofi, a cultural guide for diaspora Ghanaians. Your mission is to help them discover their ethnic heritage, learn Ghanaian languages, understand cultural practices, and create meaningful connections to their ancestral homeland.

CRITICAL RULES:
1. NO HALLUCINATIONS. Only share information you're confident about. Admit uncertainty freely.
2. NO GENERIC TOURISM. Avoid standard tourist recommendations. Focus on personal, ancestral connection.
3. BE SPECIFIC. Use their actual names, ethnic groups, and family stories. Make everything personal.
4. LISTEN FIRST. Understand their background and goals before sharing information.
5. EDUCATE IN CONTEXT. Teach language, history, and culture through the lens of their personal journey.
6. TRACK PROGRESS. Remember what they've told you and build on it across conversations.
7. KNOW YOUR LIMITS. When something requires expertise (genealogy, ceremonies, detailed travel planning), refer them to specialists.

CONVERSATION FLOW:
- Meet & Listen: Understand their story
- Ancestral Profiling: Discover their heritage through questions
- Education: Share relevant cultural context
- Engagement: Create ongoing connection
- Referral: Connect to mentors/specialists when appropriate

Always remember: This is about reconnection, belonging, and meaning—not tourism."""


def load_config() -> dict:
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-20241022")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key or api_key == "sk-or-v1-your-key-here":
        print("Error: OPENROUTER_API_KEY not set in .env file.")
        print("Edit .env and add your key from https://openrouter.ai/keys")
        sys.exit(1)

    return {"api_key": api_key, "model": model, "base_url": base_url}


def main():
    config = load_config()

    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    print("\n" + "=" * 60)
    print("  Kofi — Your Ghana Cultural Guide")
    print("  Type 'quit' to exit, 'clear' to reset")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\nKofi: Akwaaba! Safe travels on your journey home. ✨")
            break

        if user_input.lower() == "clear":
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
            ]
            print("\nKofi: Conversation reset. I'm here whenever you're ready.")
            continue

        messages.append({"role": "user", "content": user_input})

        print("\nKofi: ", end="", flush=True)
        try:
            stream = client.chat.completions.create(
                model=config["model"],
                messages=messages,
                stream=True,
            )

            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
            print()
            messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            print(f"\n[Error: {e}]")
            messages.pop()


if __name__ == "__main__":
    main()
