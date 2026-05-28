import json
import os
import uuid

from collections import defaultdict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

from roots_season import ROOTS_INTAKE_PROMPT

load_dotenv()

app = FastAPI(title="Kofi Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
)
MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-20241022")

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


sessions: dict[str, list[dict]] = defaultdict(list)


class MessagePayload(BaseModel):
    session_id: str
    message: str


@app.post("/chat")
async def chat(payload: MessagePayload):
    sid = payload.session_id

    if sid not in sessions or len(sessions[sid]) == 0:
        sessions[sid] = [{"role": "system", "content": SYSTEM_PROMPT}]

    msg = payload.message.strip()

    if msg.lower() == "/roots":
        sessions[sid] = [{"role": "system", "content": ROOTS_INTAKE_PROMPT}]
        sessions[sid].append({"role": "user", "content": "Start the Roots Season intake."})
    elif msg.lower() == "/clear":
        sessions[sid] = [{"role": "system", "content": SYSTEM_PROMPT}]
        return json.dumps({"text": "Conversation reset."})
    else:
        sessions[sid].append({"role": "user", "content": msg})

    async def stream():
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=sessions[sid],
                stream=True,
            )
            full = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full += content
                    yield f"data: {json.dumps({'token': content})}\n\n"
            sessions[sid].append({"role": "assistant", "content": full})
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    from fastapi.responses import StreamingResponse
    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/session")
async def new_session():
    sid = str(uuid.uuid4())
    return {"session_id": sid}


@app.get("/health")
async def health():
    return {"status": "ok"}
