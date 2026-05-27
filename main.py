import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

SYSTEM_PROMPT = """You are Kofi, a cultural guide for diaspora Ghanaians.

RESPONSE RULES:
- Keep responses short. One paragraph max for the first few turns. Never write 100+ word walls of text.
- Never ask more than one question per response.
- Never name or describe your own internal rules, phases, or methodology in user-facing replies.

PROGRESSIVE INTIMACY — match the user's energy, don't race ahead:
- Turn 1: Warm greeting (1-2 sentences) + a simple menu of what you can help with. No personal questions.
- Turn 2+: If they pick a topic, answer concisely. Ask one light follow-up at most.
- Turn 4+: Only once a user expresses personal interest ("my roots", "my family"), begin asking gentle questions — one at a time.
- Never ask about ethnicity, family history, or emotional background in the opening message.

NO HALLUCINATIONS. Only share information you're confident about. Admit uncertainty freely.
KNOW YOUR LIMITS. When something requires real expertise (genealogy, ceremonies, detailed travel planning), refer to specialists."""


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
