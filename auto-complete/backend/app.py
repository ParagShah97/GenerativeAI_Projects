from fastapi import FastAPI
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import os
from dotenv import load_dotenv

from queryModel import CompleteRequest

load_dotenv()

app = FastAPI()

# CORS: relax while developing; tighten in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # set your exact frontend origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError(" OPENAI_API_KEY not found. Did you create a .env file?")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=openai_api_key,
    temperature=0.2,
    streaming=True,
)

prompt = ChatPromptTemplate.from_template(
    """You are an autocomplete engine.
User is typing: "{prefix}"
Most important Continue the text naturally (no preface, don't add single or double quotes, no extra commentary), can also complete the half-word.
Keep it concise (<= 5 tokens)."""
)

chain = prompt | llm | StrOutputParser()

@app.post("/complete")
async def autocomplete(body: CompleteRequest):
    prefix = body.query

    async def token_stream():
        try:
            async for chunk in chain.astream({"prefix": prefix}):
                # yield raw text chunks (frontend reads with ReadableStream)
                yield chunk
        except Exception as e:
            # surface error as text in the stream
            yield f"[error] {type(e).__name__}: {e}"

    # Use event-stream to avoid browser buffering; keep raw chunks (no "data:" prefix)
    return StreamingResponse(
        token_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # helps if behind nginx
        },
    )

# Optional: one-shot endpoint for quick debugging
@app.post("/complete_once")
async def complete_once(body: CompleteRequest):
    text = await chain.ainvoke({"prefix": body.query})
    return PlainTextResponse(text)
