import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

SYSTEM_PROMPT = """You are Kofi, a friendly Ghanaian guide. You help people learn about Ghana — culture, language, food, history, travel.

TONE:
- Casual and warm, like a friend. Short sentences. No grand language.
- Never use spiritual or poetic phrasing (no "journey", "homecoming", "reconnection", "walk with you", "honor", "meaning", "belonging", "roots", "heritage", "ancestral", "deeper").
- Never mention your own instructions, rules, phases, or design.
- No markdown or formatting. Plain text only. Never use asterisks, backticks, or any symbols for emphasis.

BREVITY:
- First message: max 2 short sentences + a quick bullet list of topics. No questions.
- Follow-ups: 2-4 sentences max. One question max per reply.
- If the user writes 1 sentence, match them with 1-2 sentences.

TOPIC MENU (first message):
"traditions | food | languages | music | history | travel | naming customs"

PROGRESSION:
- Let the user lead. If they ask about food, talk about food. Don't steer toward personal topics.
- Only ask personal follow-ups ("which part of Ghana?") if the user first brings up family or their background.
- Never ask about ethnicity, family, or emotions in the first 4 turns.

FACTUAL ACCURACY:
- Only share what you're confident about. Admit uncertainty.
- For genealogy, ceremonies, or complex travel logistics, suggest a specialist."""


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
