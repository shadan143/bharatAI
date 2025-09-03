import os, json
from typing import List, Dict, Optional

# LLM wrapper that prefers OpenAI (if OPENAI_API_KEY set) and falls back to a simple template.
# In production you might use Azure, Anthropic, or a local LLM with proper batching, retries, and safety filters.

def build_system_prompt(lang: str = "hi"):
    if lang.startswith("hi") or lang == "hi":
        return (
            "You are BharatAI Assistant — a helpful, concise assistant that replies in the user's language. "
            "When provided with supporting documents, synthesize them into a short, accurate answer. "
            "If the documents don't answer the user's query, say so and provide a short next step."
        )
    return (
        "You are BharatAI Assistant — a helpful, concise assistant that replies in the user's language. "
        "When provided with supporting documents, synthesize them into a short, accurate answer. "
        "If the documents don't answer the user's query, say so and provide a short next step."
    )

def build_prompt(question: str, docs: List[Dict], lang: str = "hi"):
    # docs: list of {id, content, metadata}
    system = build_system_prompt(lang)
    # Join docs with separators
    doc_texts = "\n\n---\n\n".join([f"Source {d.get('id')}:\n{d.get('content')}" for d in docs])
    user_message = f"Question: {question}\n\nSupporting documents:\n{doc_texts}\n\nRespond in { 'Hindi' if lang.startswith('hi') else 'the same language as the question' }, be concise, and include citations like [Source <id>] when referencing docs."
    return system, user_message

def generate_answer(question: str, docs: List[Dict], lang: str = 'hi', max_tokens: int = 400) -> str:
    """Attempt to generate an answer using OpenAI if API key is configured.
    If OpenAI client is not available or API key not set, produce a safe fallback answer combining docs.
    """
    system, user_prompt = build_prompt(question, docs, lang)

    # Try OpenAI (both 'openai' package and the new 'OpenAI' class)
    try:
        import openai
        api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_APIKEY')
        if api_key:
            openai.api_key = api_key
            # Use chat completions
            try:
                resp = openai.ChatCompletion.create(
                    model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
                    messages=[{'role':'system','content':system},{'role':'user','content':user_prompt}],
                    temperature=0.2,
                    max_tokens=max_tokens,
                )
                # different OpenAI package versions return differently
                text = None
                if isinstance(resp, dict):
                    # old response shape
                    text = resp.get('choices',[{}])[0].get('message',{}).get('content')
                else:
                    # resp may be an object with .choices
                    try:
                        text = resp.choices[0].message.content
                    except Exception:
                        text = str(resp)
                if text:
                    return text.strip()
            except Exception as e:
                # fallback to trying new OpenAI client style
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    chat_resp = client.chat.create(
                        model=os.environ.get('OPENAI_MODEL','gpt-4o-mini'),
                        messages=[{'role':'system','content':system},{'role':'user','content':user_prompt}],
                        temperature=0.2,
                        max_tokens=max_tokens
                    )
                    # client.chat.create returns dict-like
                    if isinstance(chat_resp, dict):
                        return chat_resp.get('choices',[{}])[0].get('message',{}).get('content','').strip()
                    else:
                        # try attribute access
                        return getattr(chat_resp.choices[0].message,'content','').strip()
                except Exception as e2:
                    # proceed to local fallback
                    pass
    except Exception:
        # openai package not installed or import failed
        pass

    # Fallback synthesis (no external LLM). Concatenate top doc snippets and answer conservatively.
    if not docs:
        if lang.startswith('hi'):
            return "माफ़ कीजिये — मेरे पास इस प्रश्न का उत्तर देने के लिए संदर्भ सामग्री नहीं है। कृपया अधिक जानकारी दें।"
        return "Sorry — I don't have supporting documents to answer this. Please provide more info."

    # Build a concise synthesis from docs
    synthesis_lines = []
    for d in docs[:3]:
        content = d.get('content','').strip().replace('\n',' ')
        snippet = (content[:300] + '...') if len(content) > 300 else content
        synthesis_lines.append(f"[Source {d.get('id')}] {snippet}")
    header = "संदर्भ से सारांश:" if lang.startswith('hi') else "Summary from sources:"
    footer = "(यह डेमो उत्तर है — उत्पादन के लिए LLM एकीकरण जोड़ें)" if lang.startswith('hi') else "(Demo answer — add LLM integration for production)"
    return header + "\n" + "\n".join(synthesis_lines) + "\n\n" + footer
