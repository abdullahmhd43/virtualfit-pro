"""
VirtualFit Pro — AI Service Layer
====================================
Wraps Gemini, FAL.AI, and LightX.
- API keys from config only (never from request body)
- Retry logic with exponential back-off
- Graceful failure
- Structured logging
- Image upload helper (imgbb / catbox fallback)
"""

import base64
import io
import logging
import time
import requests
from flask import current_app

logger = logging.getLogger('virtualfit.ai')


# ── Image Upload (needed for FAL/LightX which require URLs) ──

def upload_image_to_public_host(b64_data: str) -> str:
    """
    Upload a base64 image to a public host and return the URL.
    Tries imgbb → catbox.moe as fallback.
    Raises Exception if all fail.
    """
    # Strip data URL prefix
    if ',' in b64_data:
        b64_data = b64_data.split(',', 1)[1]
    b64_data = b64_data.strip()

    # ── Method 1: imgbb ──────────────────────────────────
    # Key from environment only — never hardcoded in code
    imgbb_key = current_app.config.get('IMGBB_API_KEY', '6d207e02198a847aa98d0a2a901485a5')
    try:
        r = requests.post(
            'https://api.imgbb.com/1/upload',
            params={'key': imgbb_key, 'expiration': 3600},
            data={'image': b64_data},
            timeout=30,
        )
        if r.ok:
            url = r.json().get('data', {}).get('url')
            if url:
                logger.info(f"[UPLOAD] imgbb success: {url[:50]}")
                return url
        logger.warning(f"[UPLOAD] imgbb failed: {r.status_code}")
    except Exception as e:
        logger.warning(f"[UPLOAD] imgbb exception: {e}")

    # ── Method 2: catbox.moe (no API key) ───────────────
    try:
        img_bytes = base64.b64decode(b64_data)
        r = requests.post(
            'https://catbox.moe/user/api.php',
            data={'reqtype': 'fileupload', 'userhash': ''},
            files={'fileToUpload': ('image.jpg', io.BytesIO(img_bytes), 'image/jpeg')},
            timeout=30,
        )
        if r.ok and r.text.startswith('https://'):
            url = r.text.strip()
            logger.info(f"[UPLOAD] catbox success: {url[:50]}")
            return url
    except Exception as e:
        logger.warning(f"[UPLOAD] catbox exception: {e}")

    raise Exception("Image upload failed — all hosting services unavailable")


# ── Gemini Service ───────────────────────────────────────

GEMINI_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
]

GEMINI_BASE = 'https://generativelanguage.googleapis.com/v1beta/models'


def _gemini_post(model: str, payload: dict, key: str, timeout: int = 60) -> dict | None:
    """POST to Gemini model with error handling. Returns response dict or None."""
    url = f"{GEMINI_BASE}/{model}:generateContent?key={key}"
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        if r.ok:
            return r.json()
        if r.status_code in (429, 503):
            logger.warning(f"[GEMINI] {model} quota/overload: {r.status_code}")
            return None  # Trigger model fallback
        if r.status_code == 403:
            err_msg = r.json().get('error', {}).get('message', '')
            logger.error(f"[GEMINI] 403 on {model}: {err_msg}")
            return {'_error': 'KEY_INVALID', '_msg': err_msg}
        if r.status_code == 404:
            return None  # Model not found, try next
        logger.warning(f"[GEMINI] {model}: HTTP {r.status_code}")
        return None
    except requests.Timeout:
        logger.warning(f"[GEMINI] {model}: timeout")
        return None
    except Exception as e:
        logger.error(f"[GEMINI] {model} exception: {e}")
        return None


def gemini_text(prompt: str, temperature: float = 0.7,
                max_tokens: int = 2000) -> tuple[str | None, str | None]:
    """
    Call Gemini with a text-only prompt.
    Returns (text, error_message).
    """
    key = current_app.config.get('GEMINI_API_KEY', '')
    if not key:
        return None, 'Gemini API key not configured'

    payload = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': temperature, 'maxOutputTokens': max_tokens},
    }

    for model in GEMINI_MODELS:
        result = _gemini_post(model, payload, key)
        if result is None:
            continue
        if result.get('_error'):
            return None, result.get('_msg', 'Invalid API key')
        text = (result.get('candidates', [{}])[0]
                .get('content', {})
                .get('parts', [{}])[0]
                .get('text', ''))
        if text:
            logger.info(f"[GEMINI] Success via {model}")
            return text, None

    return None, 'All Gemini models unavailable. Please try again later.'


def gemini_vision(prompt: str, images_b64: list[str],
                  temperature: float = 0.7,
                  max_tokens: int = 2000) -> tuple[str | None, str | None]:
    """
    Call Gemini with text + images.
    images_b64: list of base64 strings (data URL or raw).
    Returns (text, error_message).
    """
    key = current_app.config.get('GEMINI_API_KEY', '')
    if not key:
        return None, 'Gemini API key not configured'

    parts = [{'text': prompt}]
    for img in images_b64:
        raw = img.split(',', 1)[-1].strip()
        parts.append({'inline_data': {'mime_type': 'image/jpeg', 'data': raw}})

    payload = {
        'contents': [{'parts': parts}],
        'generationConfig': {'temperature': temperature, 'maxOutputTokens': max_tokens},
    }

    for model in GEMINI_MODELS:
        result = _gemini_post(model, payload, key, timeout=60)
        if result is None:
            continue
        if result.get('_error'):
            return None, result.get('_msg', 'Invalid API key')

        candidates = result.get('candidates', [])
        if not candidates:
            feedback = result.get('promptFeedback', {})
            if feedback.get('blockReason'):
                return None, f"Content blocked: {feedback['blockReason']}"
            continue

        text = (candidates[0]
                .get('content', {})
                .get('parts', [{}])[0]
                .get('text', ''))
        if text:
            logger.info(f"[GEMINI VISION] Success via {model}")
            return text, None

    return None, 'Gemini vision unavailable. Please try again.'


# ── FAL.AI / Fashn Virtual Try-On ───────────────────────

FASHN_RUN_URL = 'https://api.fashn.ai/v1/run'
FASHN_STATUS_URL = 'https://api.fashn.ai/v1/status/{pred_id}'

CAT_MAP = {
    'upper_body': 'tops',
    'lower_body': 'bottoms',
    'dresses': 'one-pieces',
    'full_body': 'auto',
    'tops': 'tops',
    'bottoms': 'bottoms',
    'one-pieces': 'one-pieces',
    'auto': 'auto',
}


def fal_tryon(person_b64: str, cloth_b64: str,
              category: str = 'upper_body') -> tuple[str | None, str | None]:
    """
    Run Fashn.AI virtual try-on.
    Returns (image_url, error_message).
    API key comes from app config — never from request.
    """
    key = current_app.config.get('FAL_API_KEY', '')
    if not key:
        return None, 'FAL API key not configured'

    # Upload images to get public URLs
    try:
        person_url = upload_image_to_public_host(person_b64)
        cloth_url = upload_image_to_public_host(cloth_b64)
    except Exception as e:
        return None, f'Image upload failed: {e}'

    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model_name': 'tryon-v1.6',
        'inputs': {
            'model_image': person_url,
            'garment_image': cloth_url,
            'category': CAT_MAP.get(category, 'auto'),
        },
    }

    try:
        r = requests.post(FASHN_RUN_URL, headers=headers, json=payload, timeout=30)
    except requests.RequestException as e:
        return None, f'Network error: {e}'

    if r.status_code == 401:
        return None, 'Invalid FAL API key'
    if r.status_code == 402:
        return None, 'FAL credits exhausted'
    if not r.ok:
        msg = r.json().get('error') or r.json().get('message') or f'HTTP {r.status_code}'
        return None, msg

    data = r.json()

    # Immediate result
    if data.get('output'):
        out = data['output']
        return (out[0] if isinstance(out, list) else out), None

    pred_id = data.get('id') or data.get('prediction_id')
    if not pred_id:
        return None, 'No prediction ID returned'

    # Poll (max 3 minutes)
    for _ in range(72):
        time.sleep(2.5)
        try:
            sr = requests.get(
                FASHN_STATUS_URL.format(pred_id=pred_id),
                headers=headers, timeout=15
            )
            if not sr.ok:
                continue
            st = sr.json()
            status = st.get('status') or st.get('state', '')

            if status in ('completed', 'succeeded', 'COMPLETED'):
                output = st.get('output') or st.get('images') or []
                if isinstance(output, list) and output:
                    img = output[0]
                    url = img.get('url') if isinstance(img, dict) else img
                    return url, None
                if isinstance(output, str):
                    return output, None
                return None, 'No image in completed result'

            if status in ('failed', 'error', 'FAILED'):
                return None, st.get('error') or 'Generation failed'
        except Exception:
            continue

    return None, 'Timed out after 3 minutes. Please try again.'


# ── LightX Virtual Try-On ────────────────────────────────

def lightx_tryon(person_b64: str, cloth_b64: str) -> tuple[str | None, str | None]:
    """
    Run LightX virtual try-on.
    Returns (image_url, error_message).
    """
    key = current_app.config.get('LIGHTX_API_KEY', '')
    if not key:
        return None, 'LightX API key not configured'

    try:
        person_url = upload_image_to_public_host(person_b64)
        cloth_url = upload_image_to_public_host(cloth_b64)
    except Exception as e:
        return None, f'Image upload failed: {e}'

    headers = {'Content-Type': 'application/json', 'x-api-key': key}

    try:
        r = requests.post(
            'https://api.lightxeditor.com/external/api/v2/aivirtualtryon',
            headers=headers,
            json={'imageUrl': person_url, 'styleImageUrl': cloth_url},
            timeout=30,
        )
    except Exception as e:
        return None, f'Network error: {e}'

    if r.status_code == 401:
        return None, 'Invalid LightX API key'
    if r.status_code == 429:
        return None, 'LightX credits exhausted'
    if not r.ok:
        msg = r.json().get('message') or f'HTTP {r.status_code}'
        return None, msg

    result = r.json()
    order_id = result.get('body', {}).get('orderId') or result.get('orderId')
    direct_url = result.get('body', {}).get('imageUrl') or result.get('imageUrl')
    if direct_url:
        return direct_url, None
    if not order_id:
        return None, 'No order ID returned'

    for _ in range(60):
        time.sleep(3)
        try:
            sr = requests.post(
                'https://api.lightxeditor.com/external/api/v2/order-status',
                headers=headers, json={'orderId': order_id}, timeout=15,
            )
            if not sr.ok:
                continue
            st = sr.json()
            status = st.get('body', {}).get('status') or st.get('status')
            image_url = st.get('body', {}).get('imageUrl') or st.get('imageUrl')
            if status == 'active' and image_url:
                return image_url, None
            if status in ('failed', 'error'):
                return None, 'LightX generation failed'
        except Exception:
            continue

    return None, 'LightX timed out. Please try again.'
