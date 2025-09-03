from fastapi import APIRouter, Request, Header, HTTPException
import os, hmac, hashlib, base64, json
from typing import Dict

router = APIRouter()

def verify_twilio_signature(req_body: bytes, twilio_signature: str, auth_token: str) -> bool:
    # Twilio signs requests differently; this is a placeholder for signature verification.
    # For Twilio, you generally build the expected signature using the full URL and params.
    # If using Twilio's Python library, you can use RequestValidator for verification.
    try:
        import twilio.request_validator as validator_module
        validator = validator_module.RequestValidator(auth_token)
        # For FastAPI, reconstruct full URL or configure forwarding
        return True
    except Exception:
        # fallback naive HMAC check (NOT TWILIO-COMPATIBLE)
        mac = hmac.new(auth_token.encode(), req_body, hashlib.sha256).digest()
        sig = base64.b64encode(mac).decode()
        return hmac.compare_digest(sig, twilio_signature)

@router.post('/whatsapp/webhook')
async def whatsapp_webhook(request: Request, x_twilio_signature: str = Header(None)):
    body = await request.body()
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN','test')
    if x_twilio_signature:
        ok = verify_twilio_signature(body, x_twilio_signature, auth_token)
        if not ok:
            raise HTTPException(status_code=403, detail='Invalid signature')
    # parse incoming message (Twilio form-encoded)
    form = await request.form()
    from_number = form.get('From') or form.get('from')
    msg = form.get('Body') or form.get('body') or ''
    # map to internal message endpoint
    # In prod: handle templates, media, session management, and opt-ins.
    return {'status':'received', 'from': from_number, 'msg': msg}
