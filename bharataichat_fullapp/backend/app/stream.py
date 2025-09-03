import os, asyncio, json
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()

async def event_stream(generator):
    try:
        async for chunk in generator:
            # SSE format
            yield f"data: {json.dumps({'delta': chunk})}\n\n"
    except asyncio.CancelledError:
        return

@router.get('/stream')
async def stream_response(q: str, lang: str = 'hi'):
    """Streamed responses: attempts to stream from OpenAI if available, otherwise streams a simple synthesis."""
    # If OPENAI_API_KEY present, attempt streaming via OpenAI's streaming API.
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        # We'll spawn a background generator that yields token chunks.
        async def gen_openai():
            try:
                import openai
                openai.api_key = api_key
                # Note: openai.ChatCompletion.create(..., stream=True) yields chunks in the sync client.
                # For simplicity we call it in a thread to avoid blocking; production should use async client.
                from concurrent.futures import ThreadPoolExecutor
                def blocking_stream():
                    try:
                        resp = openai.ChatCompletion.create(
                            model=os.environ.get('OPENAI_MODEL','gpt-4o-mini'),
                            messages=[{'role':'system','content':'You are BharatAI Assistant (stream).'},
                                      {'role':'user','content': q}],
                            temperature=0.2,
                            stream=True
                        )
                        for chunk in resp:
                            # chunk may have choices with delta
                            parts = chunk.get('choices',[{}])
                            for c in parts:
                                delta = c.get('delta',{})
                                text = delta.get('content')
                                if text:
                                    yield text
                    except Exception as e:
                        yield f"[stream-error] {str(e)}"
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor(max_workers=1) as ex:
                    for piece in await loop.run_in_executor(ex, lambda: list(blocking_stream())):
                        yield piece
            except Exception as e:
                yield f"[stream-failed] {str(e)}"

        return StreamingResponse(event_stream(gen_openai()), media_type='text/event-stream')

    # Fallback simple streamed chunks (simulate streaming)
    async def gen_fallback():
        parts = [q[i:i+100] for i in range(0, len(q), 100)]
        for p in parts:
            await asyncio.sleep(0.2)
            yield p
        yield '\n--end--'
    return StreamingResponse(event_stream(gen_fallback()), media_type='text/event-stream')
