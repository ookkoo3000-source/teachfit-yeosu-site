# -*- coding: utf-8 -*-
"""
Gemini로 블로그 글 초안을 생성하는 스크립트.
사용법: python scripts/gen_blog.py "<학교명>" "<급(초등학교/중학교/고등학교)>" "<키워드/앵글>"
결과: JSON을 stdout으로 출력 (title/teaser/intro/sections[6]/faq[3])
API 키는 .env.local (gitignored)에서 읽음.
"""
import sys, os, json, re, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_key():
    env_path = os.path.join(ROOT, ".env.local")
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("GEMINI_API_KEY not found in .env.local")

API_KEY = load_key()
MODEL = "gemini-3.6-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

SYSTEM_PROMPT = """당신은 전문 블로거이자 콘텐츠 마케팅 전문가입니다. "티치핏여수"(여수 지역 초중고 대상 1:1 화상과외 매칭 서비스, 30분 무료체험수업이 핵심 강점, 방문수업·입시컨설팅은 취급 안 함)의 블로그 글을 씁니다.

[작성 규칙 - 반드시 지킬 것]
- 한국어로 작성, 학부모 대상 존댓말("~해요", "~드려요")
- 제목에 주어진 키워드를 반드시 포함
- 서론(intro)은 300자 이상
- 본문 소제목(sections)은 정확히 6개, 각 섹션의 본문 텍스트는 (HTML 태그 제외하고) 700자 이상이어야 함 - 이게 가장 중요한 규칙입니다. 짧으면 안 됩니다. 각 섹션은 <p> 태그 2~3개로 문단을 나누세요.
- FAQ는 정확히 3개
- 전체 2000자 이상
- 주어진 학교명을 자연스럽게 본문에 여러 번 언급하되, 그 학교에 대한 구체적인 수치(학생 수, 순위, 합격률 등)는 지어내지 말 것 - 일반적으로 알려진 사실(공립/사립, 지역적 위치 느낌 정도)만 안전하게 언급
- 특정 학생의 이름, 점수, 합격 실적 등은 절대 지어내지 말 것 - 검증 불가능한 사실은 만들지 않기
- "티치핏여수" 서비스를 자연스럽게 1~2회 언급하고, 마지막에 "30분 무료체험수업" 신청을 자연스럽게 권유
- 화상과외 전문 서비스라는 것을 감안해서 화상과외의 장점(이동시간 없음, 넓은 선생님 풀, 녹화 복습 등)을 자연스럽게 녹여낼 것
- 비용은 구체적 금액을 지어내지 말고 "상담 시 안내, 체험 후 결정" 방향으로
- 키워드 스터핑처럼 어색하게 반복하지 말고 자연스럽게

[출력 형식]
아래 JSON 스키마로만 출력하세요. 다른 설명 텍스트 없이 JSON만 출력합니다.
{
  "title": "제목 (키워드 포함)",
  "teaser": "카드용 1문장 요약 (60자 내외)",
  "intro": "<p>...</p><p>...</p>",
  "sections": [
    {"heading": "소제목1", "html": "<p>...</p><p>...</p>"},
    {"heading": "소제목2", "html": "<p>...</p><p>...</p>"},
    {"heading": "소제목3", "html": "<p>...</p><p>...</p>"},
    {"heading": "소제목4", "html": "<p>...</p><p>...</p>"},
    {"heading": "소제목5", "html": "<p>...</p><p>...</p>"},
    {"heading": "소제목6", "html": "<p>...</p><p>...</p>"}
  ],
  "faq": [
    {"q": "질문1", "a": "답변1"},
    {"q": "질문2", "a": "답변2"},
    {"q": "질문3", "a": "답변3"}
  ]
}
"""

def strip_tags(html):
    return re.sub(r"<[^>]+>", "", html).strip()

def call_gemini(prompt_text, temperature=0.9):
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 8192},
    }
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    last_err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text
        except Exception as e:
            last_err = e
            time.sleep(min(2 ** attempt, 30))
    raise last_err

def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)

def validate(post):
    problems = []
    intro_len = len(strip_tags(post["intro"]))
    if intro_len < 300:
        problems.append(("intro", intro_len))
    if len(post["sections"]) != 6:
        problems.append(("section_count", len(post["sections"])))
    for i, sec in enumerate(post["sections"]):
        l = len(strip_tags(sec["html"]))
        if l < 700:
            problems.append((f"section_{i}", l))
    if len(post.get("faq", [])) != 3:
        problems.append(("faq_count", len(post.get("faq", []))))
    return problems

def expand_section(school, level, keyword, heading, current_html, current_len):
    need = 750 - current_len
    prompt = f"""다음은 "{school}"({level}) "{keyword}" 관련 블로그 글의 한 섹션입니다. 소제목: "{heading}"

현재 내용:
{current_html}

이 섹션이 너무 짧습니다(현재 {current_len}자, HTML 태그 제외 기준). 같은 주제와 톤을 유지하면서 최소 {need}자 이상 늘려서, 전체 (태그 제외) 750자 이상이 되도록 다시 작성해주세요. 문단(<p>)은 2~3개로 나누고, 학교명({school})을 자연스럽게 한 번 더 언급해도 좋습니다. 구체적 수치나 실적은 지어내지 마세요.

출력은 <p>...</p> 형식의 HTML만 출력하세요. 다른 설명은 붙이지 마세요."""
    text = call_gemini(prompt, temperature=0.8)
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(html)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text

def generate(school, level, keyword, region="여수", brand="티치핏여수"):
    prompt = f"""학교명: {school} ({level})
지역: {region}
타깃 키워드: {keyword}
이 학교와 키워드를 결합해서 위 규칙에 맞는 블로그 글 1편을 JSON으로 작성해주세요."""
    raw = call_gemini(prompt)
    post = extract_json(raw)

    # 부족한 섹션 자동 보강 (최대 2회 재시도)
    for _ in range(2):
        problems = validate(post)
        section_problems = [p for p in problems if p[0].startswith("section_")]
        if not section_problems:
            break
        for pname, plen in section_problems:
            idx = int(pname.split("_")[1])
            sec = post["sections"][idx]
            new_html = expand_section(school, level, keyword, sec["heading"], sec["html"], plen)
            post["sections"][idx]["html"] = new_html

    problems = validate(post)
    return post, problems

if __name__ == "__main__":
    school, level, keyword = sys.argv[1], sys.argv[2], sys.argv[3]
    post, problems = generate(school, level, keyword)
    result = {"post": post, "problems": problems}
    print(json.dumps(result, ensure_ascii=False))
