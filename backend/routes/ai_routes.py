"""
VirtualFit Pro — AI Routes Blueprint
========================================
POST /api/tryon/fal
POST /api/tryon/lightx
POST /api/analyze/gemini
POST /api/detect/gender
POST /api/chat
POST /api/size
POST /api/outfit
POST /api/multiview
"""

import logging
import time
import requests
from flask import Blueprint, request, current_app

from backend.auth.jwt_manager import optional_auth
from backend.validators.input_validators import validate_base64_image, is_valid_category, is_valid_gender
from backend.services.ai_service import (
    fal_tryon, lightx_tryon, gemini_vision, gemini_text,
    upload_image_to_public_host
)
from backend.middleware.security import log_security_event
from backend.utils.errors import error, success

ai_bp = Blueprint('ai', __name__, url_prefix='/api')
logger = logging.getLogger('virtualfit.ai')


def _get_images(data: dict) -> tuple[str, str, str | None]:
    """Extract and validate person + cloth images from request."""
    person_b64 = data.get('person_image', '')
    cloth_b64 = data.get('cloth_image', '')

    ok1, msg1 = validate_base64_image(person_b64)
    ok2, msg2 = validate_base64_image(cloth_b64)

    if not ok1:
        return '', '', f'Person image: {msg1}'
    if not ok2:
        return '', '', f'Clothing image: {msg2}'

    return person_b64, cloth_b64, None


# ── FAL.AI Try-On ────────────────────────────────────────

@ai_bp.route('/tryon/fal', methods=['POST'])
@optional_auth
def tryon_fal():
    data = request.get_json(silent=True) or {}

    # SECURITY: Never accept api_key from request body
    # Keys come from server config only
    if 'api_key' in data:
        log_security_event('API_KEY_IN_REQUEST', {'endpoint': '/tryon/fal'})

    person_b64, cloth_b64, img_error = _get_images(data)
    if img_error:
        return error(img_error, 400, 'IMAGE_ERROR')

    category = data.get('category', 'upper_body')
    if not is_valid_category(category):
        return error('Invalid category', 400, 'VALIDATION_ERROR')

    if not current_app.config.get('FAL_API_KEY'):
        return error('FAL AI is not configured on this server', 503, 'SERVICE_UNAVAILABLE')

    image_url, err = fal_tryon(person_b64, cloth_b64, category)
    if err:
        logger.warning(f"[TRYON/FAL] Error: {err}")
        return error(err, 502, 'AI_ERROR')

    logger.info("[TRYON/FAL] Success")
    return success({'image_url': image_url}, 'Try-on complete')


# ── LightX Try-On ────────────────────────────────────────

@ai_bp.route('/tryon/lightx', methods=['POST'])
@optional_auth
def tryon_lightx():
    data = request.get_json(silent=True) or {}

    if 'api_key' in data:
        log_security_event('API_KEY_IN_REQUEST', {'endpoint': '/tryon/lightx'})

    person_b64, cloth_b64, img_error = _get_images(data)
    if img_error:
        return error(img_error, 400, 'IMAGE_ERROR')

    if not current_app.config.get('LIGHTX_API_KEY'):
        return error('LightX is not configured on this server', 503, 'SERVICE_UNAVAILABLE')

    image_url, err = lightx_tryon(person_b64, cloth_b64)
    if err:
        return error(err, 502, 'AI_ERROR')

    return success({'image_url': image_url}, 'Try-on complete')


# ── Gemini Style Analysis ─────────────────────────────────

@ai_bp.route('/analyze/gemini', methods=['POST'])
@optional_auth
def analyze_gemini():
    data = request.get_json(silent=True) or {}
    person_b64, cloth_b64, img_error = _get_images(data)
    if img_error:
        return error(img_error, 400, 'IMAGE_ERROR')

    style = data.get('style', 'casual')
    if style not in ('casual', 'formal', 'sporty', 'evening', 'business', 'streetwear'):
        style = 'casual'

    prompt = f"""You are an expert fashion stylist AI. I am showing you TWO images:
- Image 1: A person (the customer)
- Image 2: A clothing item they want to try on

Analyze how this clothing item would look on this person for {style} style.

Reply in this EXACT format:

SCORE: [X]/10

FIT ANALYSIS:
[2-3 sentences about how this clothing fits their body type]

COLOR & TONE:
[1-2 sentences about color compatibility with their skin tone]

WHAT WORKS:
• [Specific positive point 1]
• [Specific positive point 2]

STYLING TIP:
• [One actionable improvement]

COMPLETE THE LOOK:
[Suggest shoes and one accessory]

VERDICT:
[One confident final sentence]

Be warm, specific, and encouraging like a personal stylist friend."""

    text, err = gemini_vision(prompt, [person_b64, cloth_b64])
    if err:
        return error(err, 502, 'AI_ERROR')

    return success({'analysis': text}, 'Analysis complete')


# ── Gender Detection ──────────────────────────────────────

@ai_bp.route('/detect/gender', methods=['POST'])
@optional_auth
def detect_gender():
    data = request.get_json(silent=True) or {}
    image_b64 = data.get('image', '')
    ok, msg = validate_base64_image(image_b64)
    if not ok:
        return error(msg, 400, 'IMAGE_ERROR')

    prompt = (
        "This is a person photo. "
        "What is their gender and age group? "
        "Choose EXACTLY ONE from: men, women, boys, girls, mid-age. "
        "men=adult male 18-34. women=adult female 18-34. "
        "boys=male under 18. girls=female under 18. mid-age=35 or older. "
        "Reply with just the one word."
    )
    text, err = gemini_vision(
        prompt, [image_b64], temperature=0.0, max_tokens=15
    )
    if err or not text:
        return error('Gender detection unavailable — please select manually', 503, 'AI_UNAVAILABLE')

    gender = _parse_gender(text.strip().lower())
    if not gender:
        return error('Could not determine gender — please select manually', 422, 'PARSE_ERROR')

    return success({'gender': gender})


def _parse_gender(raw: str) -> str | None:
    if any(w in raw for w in ['mid', 'middle', 'older', 'mature', 'senior', '35', '40', '45']):
        return 'mid-age'
    if any(w in raw for w in ['girl', 'young female', 'teen girl']):
        return 'girls'
    if any(w in raw for w in ['women', 'woman', 'female', 'lady']):
        return 'women'
    if any(w in raw for w in ['boy', 'young male', 'teen boy']):
        return 'boys'
    if any(w in raw for w in ['men', 'man', 'male', 'guy']):
        return 'men'
    direct = {'men':'men','man':'men','male':'men','women':'women','woman':'women',
               'female':'women','boys':'boys','boy':'boys','girls':'girls',
               'girl':'girls','mid-age':'mid-age'}
    first_word = raw.strip().split()[0] if raw.strip() else ''
    return direct.get(first_word)


# ── AI Chatbot ────────────────────────────────────────────

@ai_bp.route('/chat', methods=['POST'])
@optional_auth
def ai_chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get('message', '')).strip()[:500]  # Limit input
    if not message:
        return error('Message required', 400, 'VALIDATION_ERROR')

    prompt = (
        "You are VirtualFit Pro's AI fashion assistant. Help with:\n"
        "- Clothing sizes (ask height/weight if needed)\n"
        "- Styling tips and outfit ideas\n"
        "- Color coordination\n"
        "- Occasion dressing\n"
        "- Product recommendations\n"
        "Keep responses friendly, under 120 words. Use emojis occasionally.\n\n"
        f"Customer: {message}\n\nAssistant:"
    )

    text, err = gemini_text(prompt, temperature=0.8, max_tokens=250)
    if err:
        return error(err, 502, 'AI_ERROR')

    return success({'reply': text})


# ── Size Recommender ──────────────────────────────────────

@ai_bp.route('/size', methods=['POST'])
@optional_auth
def ai_size():
    data = request.get_json(silent=True) or {}
    h = str(data.get('height', '')).strip()[:10]
    w = str(data.get('weight', '')).strip()[:10]
    chest = str(data.get('chest', '')).strip()[:10]
    waist = str(data.get('waist', '')).strip()[:10]
    gender = data.get('gender', 'men')
    clothing_type = str(data.get('type', 'shirt')).strip()[:50]

    if not is_valid_gender(gender):
        gender = 'men'

    prompt = (
        f"Fashion sizing expert. Customer: {gender}, "
        f"Height:{h}cm, Weight:{w}kg"
        + (f', Chest:{chest}cm' if chest else '')
        + (f', Waist:{waist}cm' if waist else '')
        + f', Clothing:{clothing_type}\n\n'
        "Reply EXACTLY:\n"
        "RECOMMENDED SIZE: [size]\n"
        "FITS WELL: [one sentence why]\n"
        "AVOID: [sizes to avoid]\n"
        "TIP: [one fitting tip]"
    )

    text, err = gemini_text(prompt, temperature=0.2, max_tokens=200)
    if err:
        return error(err, 502, 'AI_ERROR')

    return success({'result': text})


# ── Outfit Combiner ───────────────────────────────────────

@ai_bp.route('/outfit', methods=['POST'])
@optional_auth
def ai_outfit():
    data = request.get_json(silent=True) or {}
    img1 = data.get('img1', '')
    img2 = data.get('img2', '')
    occasion = str(data.get('occasion', 'casual')).strip()[:50]

    ok1, _ = validate_base64_image(img1)
    ok2, _ = validate_base64_image(img2)
    if not ok1 or not ok2:
        return error('Both clothing images required', 400, 'IMAGE_ERROR')

    prompt = (
        f"Fashion stylist: analyze these 2 clothing items for {occasion}.\n"
        "Reply:\n"
        "MATCH SCORE: [X]/10\n"
        "VERDICT: [GREAT/GOOD/AVERAGE/POOR] MATCH\n"
        "WHY: [2 sentences]\n"
        "TIP: [1 tip]\n"
        "COMPLETE WITH: [shoes + accessory]"
    )

    text, err = gemini_vision(prompt, [img1, img2], temperature=0.7, max_tokens=300)
    if err:
        return error(err, 502, 'AI_ERROR')

    return success({'result': text})


# ── Multi-view 360° ───────────────────────────────────────

@ai_bp.route('/multiview', methods=['POST'])
@optional_auth
def multiview():
    data = request.get_json(silent=True) or {}
    person_b64 = data.get('person_image', '')
    cloth_b64 = data.get('cloth_image', '')
    gender = data.get('gender', 'men')
    category = data.get('category', 'upper_body')

    ok1, msg1 = validate_base64_image(person_b64)
    ok2, msg2 = validate_base64_image(cloth_b64)
    if not ok1 or not ok2:
        return error('Both images required', 400, 'IMAGE_ERROR')

    if not is_valid_gender(gender):
        gender = 'men'

    # Front view via FAL.AI
    front_url = None
    if current_app.config.get('FAL_API_KEY'):
        front_url, _ = fal_tryon(person_b64, cloth_b64, category)

    # Get outfit description from Gemini
    outfit_desc = 'stylish modern outfit'
    desc_text, _ = gemini_vision(
        'Describe clothing in 8 words: color, style, type only.',
        [cloth_b64], temperature=0.0, max_tokens=20
    )
    if desc_text:
        outfit_desc = desc_text.strip()

    gender_desc = {
        'men': 'handsome young South Asian male model, athletic build',
        'women': 'beautiful young South Asian female model, slim build',
        'boys': 'South Asian teenage boy',
        'girls': 'South Asian teenage girl',
        'mid-age': 'South Asian adult 40s confident',
    }.get(gender, 'South Asian model')

    seed = int(time.time())

    def purl(prompt_text, s):
        quoted = requests.utils.quote(prompt_text)
        return (f"https://image.pollinations.ai/prompt/{quoted}"
                f"?width=512&height=768&seed={s}&model=flux&nologo=true")

    views = {
        'front': front_url,
        'angle': purl(f'professional fashion photo, {gender_desc}, wearing {outfit_desc}, 45 degree angle, full body, white studio background, photorealistic 4K', seed + 1),
        'side': purl(f'professional fashion photo, {gender_desc}, wearing {outfit_desc}, side profile 90 degrees, full body, white studio background, photorealistic 4K', seed + 2),
        'back': purl(f'professional fashion photo, {gender_desc}, wearing {outfit_desc}, back view showing rear, full body, white studio background, photorealistic 4K', seed + 3),
        'side2': purl(f'professional fashion photo, {gender_desc}, wearing {outfit_desc}, 270 degree side view, full body, white studio background, photorealistic 4K', seed + 4),
        'outfit_desc': outfit_desc,
    }

    return success({'views': views})
