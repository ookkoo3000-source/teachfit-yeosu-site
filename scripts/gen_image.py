import sys, os, json, base64, io, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def key():
    for line in open(os.path.join(ROOT, ".env.local"), encoding="utf-8"):
        if line.startswith("GEMINI_IMAGE_KEY="):
            return line.strip().split("=", 1)[1]

# 여수 톤: 밤바다(미드나잇 블루) + 네온 핑크 + 동백꽃 + 돌산대교 실루엣 (사이트 컬러와 동일)
PROMPT = """A clean, professional graphic design template for an educational advertisement, in the mood of Yeosu's romantic night sea. Square image with rounded corners on a slightly larger deep navy background with a subtle wave-line pattern. The interior is a soft, minimal illustration of a calm midnight-blue sea with gentle wave lines, tiny glowing city-light reflections in pale pink, a simple stylized cable-stayed bridge silhouette (Dolsan Bridge) glowing softly in the distance, and a few neon-pink camellia flowers (Odongdo camellia) as decorative accents in the corners. The top text in bold pale-pink brackets reads "[{school}]". Below it is the large, very bold white central title "1:1 화상과외". Below the main title is smaller white text "{sub}". At the bottom, a rounded rectangular button-like element in neon pink (#FF4F81) contains small dark-navy text "무료 체험". Palette: midnight blue (#0E2A4A, #071A2E), neon pink (#FF4F81), soft white. Clean even lighting, high contrast so all Korean text is rendered exactly and legibly, no other text."""

def generate(school, slug, sub="내신 관리 | 30분 무료체험", model="gemini-3.1-flash-image"):
    url = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}".format(model, key())
    body = {"contents": [{"parts": [{"text": PROMPT.format(school=school, sub=sub)}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "1:1"}}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    for part in d["candidates"][0]["content"]["parts"]:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline:
            raw = base64.b64decode(inline["data"])
            break
    else:
        raise RuntimeError("no image: " + json.dumps(d)[:300])
    from PIL import Image
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    print("original", im.size, len(raw))
    im.thumbnail((720, 720))
    os.makedirs(os.path.join(ROOT, "blog", "img"), exist_ok=True)
    out = os.path.join(ROOT, "blog", "img", slug + ".webp")
    im.save(out, "WEBP", quality=82)
    im.save(os.path.join(ROOT, "blog", "img", slug + ".jpg"), "JPEG", quality=88)
    print("saved", out, os.path.getsize(out))

if __name__ == "__main__":
    generate(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or []))
