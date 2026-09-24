# -*- coding: utf-8 -*-
import os
import json
import random
import re
import time
CSS_VER = str(int(time.time()))

ROOT = os.path.dirname(os.path.abspath(__file__))

# =================================================================
# SITE CONFIG — 다른 지역으로 새 사이트를 만들 때는 이 블록만 바꾸면 됨
# (레포를 통째로 복사한 뒤 이 블록 + 학교 목록만 새 지역 것으로 교체하고
#  python build.py 실행하면 끝)
# =================================================================
REGION_SHORT = "여수"              # 지역 짧은 이름 (브랜드/카피에 사용)
REGION_FULL = "전남 여수시"         # 지역 정식 명칭 (breadcrumb 등에 사용)
BRAND = "티치핏" + REGION_SHORT     # 사이트 브랜드명 (필요하면 직접 다른 값으로 덮어써도 됨)
PHONE_DISPLAY = "010-3131-5305"
PHONE_TEL = "01031315305"
BASE_URL = "https://yeosu.slovrest.com"   # 이 지역 사이트의 실제 도메인
LEAD_EMAIL = "ookkoo12@naver.com"   # 상담 신청 폼이 도착할 이메일 (FormSubmit 릴레이)
KAKAO_URL = "https://open.kakao.com/o/sCdocZOi"   # 카카오톡 오픈채팅 상담방
NAVER_VERIFICATION = "7562c1e2bd22589f4b57392c4db1a3eb743b1d16"  # 네이버 서치어드바이저 소유확인
GOOGLE_VERIFICATION = ""  # 구글 서치콘솔 소유확인 (등록 시 채워넣기)

# 학교 목록 — 시/군 교육지원청 공식 학교안내 기준으로 초/중/고 전체를 넣을 것
# (perfectedu 벤치마킹 원칙: 일부만 골라 넣지 않고 관할 전체를 포함 — 형평성 문제 방지)
# 출처: 전라남도여수교육지원청(ysed.jne.go.kr) 학교안내 + 나무위키 교차확인, 2026-09-23 확인
ELEMENTARY_NAMES = [
    "거문초등학교","경호초등학교","관기초등학교","나진초등학교","도원초등학교",
    "돌산초등학교","돌산초등학교 두라분교","동백초등학교","무선초등학교","백초초등학교",
    "봉덕초등학교","상암초등학교","상암초등학교 묘도분교","성산초등학교","소라초등학교",
    "소라초등학교 사곡분교","소라초등학교 소라남분교","소호초등학교","시전초등학교","신기초등학교",
    "신풍초등학교","쌍봉초등학교","안심초등학교","안일초등학교","안일초등학교 백야분교",
    "여남초등학교","여도초등학교","여수구봉초등학교","여수남산초등학교","여수남초등학교",
    "여수동초등학교","여수문수초등학교","여수미평초등학교","여수봉산초등학교","여수부영초등학교",
    "여수북초등학교","여수서초등학교","여수송현초등학교","여수신월초등학교","여수양지초등학교",
    "여수여문초등학교","여수종고초등학교","여수좌수영초등학교","여수중앙초등학교","여수진남초등학교",
    "여수한려초등학교","여천초등학교","예울초등학교","웅천초등학교","율촌초등학교",
    "율촌초등학교 상봉분교","죽림초등학교","화양초등학교","화정초등학교",
]
MIDDLE_NAMES = [
    "거문중학교","돌산중앙중학교","돌산중학교","무선중학교","안산중학교",
    "여남중학교","여도중학교","여선중학교","여수개도중학교","여수구봉중학교",
    "여수문수중학교","여수삼일중학교","여수아리울중학교","여수웅천중학교","여수종고중학교",
    "여수중앙중학교","여수중학교","여수진남중학교","여수진성중학교","여양중학교",
    "여천중학교","율촌중학교","충덕중학교","화양중학교",
]
HIGH_NAMES = [
    "부영여자고등학교","여남고등학교","여수고등학교","여수공업고등학교","여수석유화학고등학교",
    "여수여자고등학교","여수정보과학고등학교","여수중앙여자고등학교","여수충무고등학교","여수해양과학고등학교",
    "여수화양고등학교","여양고등학교","여천고등학교","진성여자고등학교","한영고등학교",
]
# =================================================================
# CONFIG 끝 — 아래는 전부 재사용 가능한 공통 로직/템플릿
# =================================================================

def has_batchim(word):
    """단어 마지막 글자에 받침이 있는지 (한국어 조사 선택용)"""
    code = ord(word[-1]) - 0xAC00
    if 0 <= code <= 11171:
        return code % 28 != 0
    return False

def josa_eunneun(word):
    return word + ("은" if has_batchim(word) else "는")

def josa_irado(word):
    return word + ("이라도" if has_batchim(word) else "라도")

REGION_EUNNEUN = josa_eunneun(REGION_SHORT)
REGION_IRADO = josa_irado(REGION_SHORT)
BRAND_EUNNEUN = josa_eunneun(BRAND)

FONT_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap">'

NAV_ITEMS = [
    ("index.html", "홈"),
    ("teachers.html", "선생님"),
    ("regions.html", f"{REGION_SHORT} 학교검색"),
    ("blog.html", "블로그"),
]

def head(title, desc, path_prefix, canonical, noindex=False):
    robots_tag = '<meta name="robots" content="noindex,nofollow">\n' if noindex else ''
    verify_tags = ''
    if NAVER_VERIFICATION:
        verify_tags += '<meta name="naver-site-verification" content="{}">\n'.format(NAVER_VERIFICATION)
    if GOOGLE_VERIFICATION:
        verify_tags += '<meta name="google-site-verification" content="{}">\n'.format(GOOGLE_VERIFICATION)
    return '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="{brand} 블로그" href="{base}/rss.xml">
{verify}{robots}{font}
<link rel="stylesheet" href="{p}assets/style.css?v={CSS_VER}">
</head>
<body>
'''.format(title=title, desc=desc, canonical=canonical, font=FONT_LINK, p=path_prefix, robots=robots_tag, verify=verify_tags, brand=BRAND, base=BASE_URL, CSS_VER=CSS_VER)

def wave_strip():
    return '''<svg class="wave-strip" viewBox="0 0 800 56" preserveAspectRatio="none" aria-hidden="true">
  <defs>
    <linearGradient id="yeosuNightSea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" style="stop-color:var(--panel)"/>
      <stop offset="100%" style="stop-color:var(--panel-2)"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="800" height="56" fill="url(#yeosuNightSea)"/>
  <circle cx="706" cy="16" r="11" fill="var(--accent-soft)" opacity=".9"/>
  <g fill="var(--accent-soft)" opacity=".75">
    <circle cx="48" cy="13" r="1.5"/>
    <circle cx="132" cy="24" r="1.1"/>
    <circle cx="214" cy="10" r="1.5"/>
    <circle cx="304" cy="20" r="1.1"/>
    <circle cx="392" cy="12" r="1.5"/>
    <circle cx="472" cy="26" r="1.1"/>
    <circle cx="552" cy="9" r="1.5"/>
    <circle cx="616" cy="22" r="1.1"/>
  </g>
  <path d="M0 40 Q 20 32 40 40 T 80 40 T 120 40 T 160 40 T 200 40 T 240 40 T 280 40 T 320 40 T 360 40 T 400 40 T 440 40 T 480 40 T 520 40 T 560 40 T 600 40 T 640 40 T 680 40 T 720 40 T 760 40 T 800 40"
    fill="none" stroke="var(--accent)" stroke-width="2" opacity=".55"/>
  <path d="M0 48 Q 20 42 40 48 T 80 48 T 120 48 T 160 48 T 200 48 T 240 48 T 280 48 T 320 48 T 360 48 T 400 48 T 440 48 T 480 48 T 520 48 T 560 48 T 600 48 T 640 48 T 680 48 T 720 48 T 760 48 T 800 48"
    fill="none" stroke="var(--accent-soft)" stroke-width="1.5" opacity=".4"/>
  <g transform="translate(752,40)" opacity=".9">
    <circle cx="0" cy="-6.5" r="6" fill="var(--accent)"/>
    <circle cx="6.2" cy="-2" r="6" fill="var(--accent)"/>
    <circle cx="3.8" cy="5.4" r="6" fill="var(--accent)"/>
    <circle cx="-3.8" cy="5.4" r="6" fill="var(--accent)"/>
    <circle cx="-6.2" cy="-2" r="6" fill="var(--accent-strong)"/>
    <circle cx="0" cy="0" r="2.6" fill="var(--accent-soft)"/>
  </g>
</svg>
'''

def topbar():
    return f'''<div class="topbar">
  <div class="wrap">
    <span>지금 신청하면 30분 무료체험수업부터 받아보실 수 있어요</span>
    <a class="phone" href="tel:{PHONE_TEL}">\U0001F4DE {PHONE_DISPLAY} (09:00–21:00)</a>
  </div>
</div>
'''

def header(path_prefix, active):
    links = []
    mlinks = []
    for href, label in NAV_ITEMS:
        cur = ' aria-current="page"' if href == active else ''
        links.append('<a href="{p}{href}"{cur}>{label}</a>'.format(p=path_prefix, href=href, cur=cur, label=label))
        mlinks.append('<a href="{p}{href}"{cur}>{label}</a>'.format(p=path_prefix, href=href, cur=cur, label=label))
    return '''<header class="site">
  <div class="wrap">
    <a class="logo" href="{p}index.html"><span class="mark">TF</span>{brand}</a>
    <div class="navwrap">
      <nav class="main">
        {links}
      </nav>
      <a class="cta-btn" href="{p}apply.html">무료 상담 신청</a>
      <button class="menu-btn" aria-label="메뉴">☰</button>
    </div>
  </div>
  <div class="mobile-nav-wrap">
    <nav class="mobile-nav">
      {mlinks}
      <a href="{p}apply.html">무료 상담 신청</a>
    </nav>
  </div>
</header>
'''.format(p=path_prefix, brand=BRAND, links='\n        '.join(links), mlinks='\n      '.join(mlinks))

def kakao_fab():
    return f'''<a class="kakao-fab" href="{KAKAO_URL}" target="_blank" rel="noopener">
  <span class="kakao-fab-ico">\U0001F4AC</span><span class="kakao-fab-label">카톡 상담</span>
</a>
'''

def mobile_cta_bar(path_prefix):
    return f'''<div class="mobile-cta-bar">
  <a class="msc-call" href="tel:{PHONE_TEL}">\U0001F4DE 전화상담</a>
  <a class="msc-apply" href="{path_prefix}apply.html">무료 상담 신청</a>
</div>
'''

def footer(path_prefix):
    return '''<footer>
  <div class="wrap">
    <div>
      <a class="logo" href="{p}index.html" style="margin-bottom:10px;"><span class="mark">TF</span>{brand}</a>
      <div class="fnav">
        <a href="{p}services.html">화상과외 소개</a><a href="{p}process.html">매칭 방식</a><a href="{p}teachers.html">선생님</a><a href="{p}regions.html">{region} 학교검색</a><a href="{p}blog.html">블로그</a>
      </div>
      <p class="disclaimer">전화 {phone} · 운영시간 09:00–21:00 · 상담 및 매칭 신청은 무료이며, 실제 수업 진행 여부와 비용은 상담 후 안내해 드립니다. 사업자 정보는 확정 후 별도 고지 예정입니다.</p>
    </div>
  </div>
</footer>
<script src="{p}assets/site.js"></script>
</body>
</html>
'''.format(p=path_prefix, brand=BRAND, region=REGION_SHORT, phone=PHONE_DISPLAY)

def og_tags(title, desc, canonical, og_image, is_article):
    t = title.replace('"', '&quot;')
    d = desc.replace('"', '&quot;')
    lines = [
        '<meta property="og:type" content="{}">'.format("article" if is_article else "website"),
        '<meta property="og:site_name" content="{}">'.format(BRAND),
        '<meta property="og:title" content="{}">'.format(t),
        '<meta property="og:description" content="{}">'.format(d),
        '<meta property="og:url" content="{}">'.format(canonical),
    ]
    if og_image:
        lines += ['<meta property="og:image" content="{}">'.format(og_image),
                  '<meta name="twitter:card" content="summary_large_image">',
                  '<meta name="twitter:image" content="{}">'.format(og_image)]
    return chr(10).join(lines) + chr(10)

def page(filename, title, desc, active, body, path_prefix="", canonical="", noindex=False, extra_js="", og_image=""):
    full = head(title, desc, path_prefix, canonical, noindex)
    if not noindex:
        full = full.replace('</head>', og_tags(title, desc, canonical, og_image, filename.startswith("blog/")) + '</head>', 1)
    full = full + wave_strip() + topbar() + header(path_prefix, active) + '<main class="wrap">\n' + body + '\n</main>\n' + footer(path_prefix)
    full = full.replace('</body>', kakao_fab() + '\n</body>')
    if os.path.basename(filename) not in ("apply.html", "thanks.html"):
        full = full.replace('</body>', mobile_cta_bar(path_prefix) + '\n</body>')
    if extra_js:
        full = full.replace('</body>', extra_js + '\n</body>')
    out_path = os.path.join(ROOT, filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(full)
    print("wrote", filename)

# ---------------------------------------------------------------
# Revised Romanization (approximate, URL-slug purposes only)
# ---------------------------------------------------------------
CHO = ['g','kk','n','d','tt','r','m','b','pp','s','ss','','j','jj','ch','k','t','p','h']
JUNG = ['a','ae','ya','yae','eo','e','yeo','ye','o','wa','wae','oe','yo','u','wo','we','wi','yu','eu','ui','i']
JONG = ['','g','kk','gs','n','nj','nh','d','l','lg','lm','lb','ls','lt','lp','lh','m','b','bs','s','ss','ng','j','ch','k','t','p','h']

def romanize(text):
    out = []
    for ch in text:
        code = ord(ch) - 0xAC00
        if 0 <= code < 11172:
            cho = code // 588
            jung = (code % 588) // 28
            jong = code % 28
            out.append(CHO[cho] + JUNG[jung] + JONG[jong])
        elif ch.isalnum():
            out.append(ch.lower())
    return ''.join(out)

REGION_SLUG = romanize(REGION_SHORT)  # 예: 여수 -> yeosu (슬러그 접미사로 사용)

def josa_eun_neun(word):
    """받침 유무에 따라 '은'/'는' 중 맞는 조사를 반환 (BRAND가 지역마다 달라져도 문법 맞게)."""
    if not word:
        return "는"
    code = ord(word[-1]) - 0xAC00
    if 0 <= code < 11172:
        return "은" if (code % 28) != 0 else "는"
    return "는"

BRAND_EUN = josa_eun_neun(BRAND)

def sample_keyword(name):
    """검색창 placeholder용 짧은 예시 키워드 — 지역명 접두어·학교급 접미어를 뗀 나머지."""
    base = name.replace('초등학교', '').replace('중학교', '').replace('고등학교', '')
    if base.startswith(REGION_SHORT) and len(base) > len(REGION_SHORT):
        base = base[len(REGION_SHORT):]
    return base[:3] if base else name[:2]

LEVEL_CODE = {'초등학교': 'es', '중학교': 'ms', '고등학교': 'hs'}

def make_slug(name, level, used):
    base = name.replace('초등학교', '').replace('중학교', '').replace('고등학교', '')
    slug = '{}-{}-{}'.format(romanize(base), LEVEL_CODE[level], REGION_SLUG)
    if slug in used:
        n = 2
        while '{}-{}'.format(slug, n) in used:
            n += 1
        slug = '{}-{}'.format(slug, n)
    used.add(slug)
    return slug

_used_slugs = set()
def build_school_list(names, level):
    out = []
    for name in names:
        out.append({"name": name, "level": level, "slug": make_slug(name, level, _used_slugs)})
    return out

SCHOOLS = (
    build_school_list(ELEMENTARY_NAMES, "초등학교")
    + build_school_list(MIDDLE_NAMES, "중학교")
    + build_school_list(HIGH_NAMES, "고등학교")
)

LEVEL_INFO = {
    "초등학교": {
        "stage": "초등학생",
        "focus": "읽기·쓰기·연산 기초와 학습 습관 형성",
        "subjects": ["국어", "영어", "수학"],
        "worry": "아직 공부 습관이 안 잡혀서 무엇부터 시작해야 할지 모르겠다는 점",
    },
    "중학교": {
        "stage": "중학생",
        "focus": "내신 시험 범위에 맞춘 단원별 학습과 기초 개념 보완",
        "subjects": ["국어", "영어", "수학", "사회", "과학"],
        "worry": "시험 범위는 아는데 어디서부터 정리해야 할지 막막하다는 점",
    },
    "고등학교": {
        "stage": "고등학생",
        "focus": "내신 등급 관리와 수능 대비 학습",
        "subjects": ["국어", "영어", "수학", "사회", "과학"],
        "worry": "내신과 수능을 동시에 챙기기엔 시간이 부족하다는 점",
    },
}

# ---------------------------------------------------------------
# index.html
# ---------------------------------------------------------------
index_body = f'''
<section class="hero">
  <div class="grid">
    <div>
      <span class="eyebrow">{REGION_SHORT} 과외</span>
      <h1>{REGION_SHORT} 과외 찾고 계신가요?<br>초·중·고 1:1 <em>화상과외</em></h1>
      <p class="lead">수학·영어·국어 등 전 과목, 초등학생부터 고등학생까지 — {REGION_SHORT} 학교 사정을 잘 아는 선생님을 실시간 화상 수업으로 연결해 드려요. 방문 없이도 집에서 편하게 받을 수 있어요.</p>
      <div class="hero-ctas">
        <a class="cta-btn" href="apply.html">30분 무료체험 신청하기</a>
        <a class="cta-ghost" href="process.html">매칭 방식 보기</a>
      </div>
      <div class="trust-row">
        <span><i class="dot"></i>{REGION_SHORT} 학교 사정에 밝은 선생님</span>
        <span><i class="dot"></i>30분 무료체험수업 먼저 받아보기</span>
        <span><i class="dot"></i>체험 후 결정, 부담 없어요</span>
      </div>
    </div>
    <div>
      <svg viewBox="0 0 300 300" fill="none" style="max-width:380px;margin-inline:auto;display:block;">
        <circle cx="150" cy="150" r="128" stroke="var(--line)" stroke-width="1.5" stroke-dasharray="2 8"/>
        <path d="M95 150a55 55 0 1 1 110 0 55 55 0 0 1-110 0Z" fill="var(--primary-soft)"/>
        <path d="M150 95a55 55 0 0 1 47.5 82.5L150 150Z" fill="var(--accent-soft)"/>
        <circle cx="150" cy="150" r="55" fill="none" stroke="var(--primary)" stroke-width="2.5"/>
        <line x1="150" y1="70" x2="150" y2="88" stroke="var(--muted-2)" stroke-width="2"/>
        <line x1="150" y1="212" x2="150" y2="230" stroke="var(--muted-2)" stroke-width="2"/>
        <line x1="70" y1="150" x2="88" y2="150" stroke="var(--muted-2)" stroke-width="2"/>
        <line x1="212" y1="150" x2="230" y2="150" stroke="var(--muted-2)" stroke-width="2"/>
        <path d="M150 106 L164 150 L150 150 Z" fill="var(--primary-strong)"/>
        <path d="M150 106 L136 150 L150 150 Z" fill="var(--primary)"/>
        <path d="M150 194 L164 150 L150 150 Z" fill="var(--accent-strong)"/>
        <path d="M150 194 L136 150 L150 150 Z" fill="var(--accent)"/>
        <circle cx="150" cy="150" r="7" fill="var(--ink)"/>
      </svg>
    </div>
  </div>
</section>

<div class="stats">
  <div class="wrap">
    <div><div class="num mono">{len(SCHOOLS)}개교</div><div class="lbl">{REGION_SHORT} 전체 초·중·고 매칭 가능</div></div>
    <div><div class="num mono">4단계</div><div class="lbl">선생님 검증 절차</div></div>
    <div><div class="num mono">30분</div><div class="lbl">무료체험수업 제공</div></div>
    <div><div class="num mono">24h</div><div class="lbl">이내 매칭 안내</div></div>
  </div>
</div>

<section id="grades">
  <div class="head-row">
    <div><span class="eyebrow">학년별 과외</span><h2>학년마다 필요한 과외가 달라요</h2></div>
    <p>같은 {REGION_IRADO} 초등·중등·고등에 따라 고민이 다르니, 학년에 맞춰 과목과 방식을 정해드려요.</p>
  </div>
  <div class="services">
    <div class="svc-card">
      <span class="tag">초등</span>
      <h3>{REGION_SHORT} 초등학생 화상과외</h3>
      <p>국어·영어·수학 기초를 다지고 학습 습관을 잡아주는 시기예요. 놀이처럼 부담 없이 시작할 수 있게 진행해요.</p>
      <div class="subjects"><span>국어</span><span>영어</span><span>수학</span></div>
    </div>
    <div class="svc-card">
      <span class="tag">중등</span>
      <h3>{REGION_SHORT} 중학생 수학·영어 화상과외</h3>
      <p>내신 시험 범위에 맞춘 단원별 학습이 중요해지는 시기예요. 학교별 시험 유형을 반영해 대비해요.</p>
      <div class="subjects"><span>수학</span><span>영어</span><span>국어</span><span>사회</span><span>과학</span></div>
    </div>
    <div class="svc-card">
      <span class="tag">고등</span>
      <h3>{REGION_SHORT} 고등학생 내신·수능 화상과외</h3>
      <p>내신 등급 관리와 수능 대비를 함께 챙겨야 하는 시기예요. 목표에 맞춰 커리큘럼을 조정해요.</p>
      <div class="subjects"><span>수학</span><span>영어</span><span>국어</span><span>사회</span><span>과학</span></div>
    </div>
  </div>
</section>

<section id="services">
  <div class="head-row">
    <div><span class="eyebrow">서비스</span><h2>왜 화상과외 하나에만 집중할까요</h2></div>
    <p>방문 선생님을 구하기 어려운 과목도, 화상이라면 훨씬 넓은 범위에서 {REGION_SHORT} 학생에게 맞는 선생님을 찾을 수 있어요.</p>
  </div>
  <div class="services">
    <div class="svc-card">
      <span class="tag">실시간 화상</span>
      <h3>1:1 실시간 화상 수업</h3>
      <p>정해진 시간에 화면으로 만나 실시간으로 진행하는 수업이에요. 이동 시간이 없어 저녁 시간대도 유연하게 잡을 수 있어요.</p>
      <div class="subjects"><span>국어</span><span>영어</span><span>수학</span><span>사회</span><span>과학</span></div>
    </div>
    <div class="svc-card">
      <span class="tag">녹화 복습</span>
      <h3>수업 녹화 다시보기</h3>
      <p>수업 내용을 녹화해 두고 이해가 안 된 부분만 다시 돌려볼 수 있어요. 시험 전 복습에 특히 도움이 돼요.</p>
      <div class="subjects"><span>단원별 복습</span><span>오답 다시보기</span></div>
    </div>
    <div class="svc-card">
      <span class="tag">지역 맞춤</span>
      <h3>{REGION_SHORT} 학교 사정을 아는 선생님</h3>
      <p>같은 화상 수업이라도 {REGION_SHORT} 학교의 시험 범위와 분위기를 아는 선생님과 하면 훨씬 정확해요. 상담 시 재학 중인 학교를 확인해 매칭에 반영합니다.</p>
      <div class="subjects"><span>학교별 내신</span><span>지역 맞춤 매칭</span></div>
    </div>
  </div>
</section>

<section id="cost-vs-visit">
  <div class="head-row"><div><span class="eyebrow">궁금한 점</span><h2>{REGION_SHORT} 과외 비용, 방문과 화상 뭐가 다를까요</h2></div></div>
  <div class="trust-grid" style="grid-template-columns:repeat(2,1fr);">
    <div class="trust-item"><h4>{REGION_SHORT} 과외 비용은 어떻게 결정될까요</h4><p>과목·학년·수업 시간, 선생님 경력에 따라 달라져요. 정확한 비용은 상담 시 학생 상황을 확인한 뒤 안내해 드리고, 30분 무료체험수업으로 먼저 확인하실 수 있어요.</p></div>
    <div class="trust-item"><h4>방문과외와 화상과외의 차이</h4><p>방문은 대면 관리가 필요한 학생에게, 화상은 이동 시간 없이 원하는 시간대에 넓은 범위의 선생님을 찾고 싶은 학생에게 잘 맞아요. {BRAND_EUNNEUN} 화상과외 하나에 집중해 매칭 정확도를 높였어요.</p></div>
  </div>
</section>

<section id="process">
  <div class="head-row">
    <div><span class="eyebrow">매칭 방식</span><h2>우리 아이에게 맞는 선생님 찾는 방법</h2></div>
    <p>진단 없이 배정하지 않습니다. 학습 성향과 생활 패턴까지 확인한 뒤 선생님을 연결해요.</p>
  </div>
  <div class="process-track">
    <div class="p-step"><div class="n">01</div><h4>학습 진단</h4><p>현재 수준과 약점, 학습 성향을 먼저 파악해요.</p></div>
    <div class="p-step"><div class="n">02</div><h4>맞춤 설계</h4><p>목표와 생활 패턴에 맞춘 1:1 커리큘럼을 구성해요.</p></div>
    <div class="p-step"><div class="n">03</div><h4>30분 무료체험수업</h4><p>선생님과 화면으로 만나 30분 동안 무료로 먼저 받아보고 궁합을 확인해요.</p></div>
    <div class="p-step"><div class="n">04</div><h4>숙제·오답 관리</h4><p>배운 내용을 확실히 내 것으로 만들어요.</p></div>
    <div class="p-step"><div class="n">05</div><h4>리포트·피드백</h4><p>진행 상황을 학부모님께 정기 공유해요.</p></div>
  </div>
</section>

<section>
  <div class="head-row"><div><span class="eyebrow">왜 {BRAND}인가</span><h2>믿고 맡길 수 있는 이유</h2></div></div>
  <div class="trust-grid">
    <div class="trust-item"><div class="ico">\U0001F6E1️</div><h4>철저한 검증</h4><p>학력·신원·경력을 확인한 선생님만 매칭에 참여해요.</p></div>
    <div class="trust-item"><div class="ico">\U0001F9ED</div><h4>궁합 기반 매칭</h4><p>성적만이 아니라 성향·목표까지 분석해 연결해요.</p></div>
    <div class="trust-item"><div class="ico">\U0001F3AC</div><h4>30분 무료체험수업</h4><p>정식 신청 전에 30분 동안 선생님과 무료로 먼저 만나보고 결정할 수 있어요.</p></div>
    <div class="trust-item"><div class="ico">\U0001F4CB</div><h4>꼼꼼한 학습 관리</h4><p>수업 리포트와 진도 관리로 흐름을 놓치지 않아요.</p></div>
    <div class="trust-item"><div class="ico">⏱️</div><h4>빠른 응대</h4><p>신청 후 24시간 이내 체험 수업을 안내해 드려요.</p></div>
  </div>
</section>

<section id="regions">
  <div class="head-row">
    <div><span class="eyebrow">{REGION_SHORT} 학교검색</span><h2>초등학교부터 고등학교까지, {REGION_SHORT} 학교 {len(SCHOOLS)}곳 모두</h2></div>
  </div>
  <div class="region-card" style="max-width:640px;">
    <div class="count">초등학교 {len(ELEMENTARY_NAMES)}곳 · 중학교 {len(MIDDLE_NAMES)}곳 · 고등학교 {len(HIGH_NAMES)}곳 — 어느 학교든 화상과외 매칭이 가능해요.</div>
    <div style="margin-top:16px;"><a class="cta-btn" href="regions.html">우리 학교 검색해보기 →</a></div>
  </div>
</section>

<section id="apply">
  <div class="apply-wrap">
    <div>
      <span class="eyebrow" style="color:var(--accent-strong)">무료 상담</span>
      <h2>지금 우리 아이 학습 궁합을 확인해보세요</h2>
      <p>이름과 연락처만 남겨주시면 24시간 이내에 담당자가 직접 연락드려요.</p>
      <ul class="apply-perks">
        <li>상담·매칭 신청 전 과정 무료</li>
        <li>검증된 선생님만 매칭에 참여</li>
        <li>30분 무료체험수업 먼저 받아보고 결정</li>
      </ul>
    </div>
    {{apply_form}}
  </div>
</section>
'''

APPLY_FORM = f'''<form class="form-card" action="https://formsubmit.co/{LEAD_EMAIL}" method="POST">
      <input type="hidden" name="_subject" value="[{BRAND}] 새 상담 신청">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_next" value="thanks.html">
      <div class="field"><label for="tf-name">학생 이름</label><input id="tf-name" name="학생이름" type="text" placeholder="학생 이름" required></div>
      <div class="field"><label for="tf-phone">연락처</label><input id="tf-phone" name="연락처" type="tel" placeholder="010-0000-0000" required></div>
      <div class="field"><label for="tf-school">재학 중인 학교 ({REGION_SHORT} 소재)</label><input id="tf-school" name="학교" type="text" placeholder="예: {next((s['name'] for s in SCHOOLS if s['level'] == '중학교'), SCHOOLS[0]['name'] if SCHOOLS else '')}"></div>
      <div class="field">
        <label>학년</label>
        <div class="radio-row">
          <label><input type="radio" name="학년" value="초등">초등</label>
          <label><input type="radio" name="학년" value="중등">중등</label>
          <label><input type="radio" name="학년" value="고등">고등</label>
        </div>
      </div>
      <div class="field"><label for="tf-memo">남기실 말 (선택)</label><textarea id="tf-memo" name="메모" rows="2" placeholder="희망 과목, 시간대 등"></textarea></div>
      <button class="submit-btn" type="submit">무료 상담 신청하기</button>
      <p class="form-note">신청 즉시 담당자에게 전달되며, 24시간 이내 연락드립니다.</p>
    </form>'''

index_body = index_body.format(apply_form=APPLY_FORM)

# ---------------------------------------------------------------
# services.html / process.html / teachers.html
# ---------------------------------------------------------------
services_body = f'''
<section class="page-hero">
  <span class="eyebrow">화상과외 소개</span>
  <h1>{REGION_SHORT} 학생을 위한 화상과외, 이렇게 다릅니다</h1>
  <p>{BRAND}{BRAND_EUN} 방문 수업이나 입시 컨설팅 없이, 오직 화상과외 하나에만 집중합니다. 대신 그 안에서 {REGION_SHORT} 지역 학교 사정까지 반영한 매칭을 제공해요.</p>
</section>
<section>
  <div class="services">
    <div class="svc-card">
      <span class="tag">실시간 화상</span>
      <h3>1:1 실시간 화상 수업</h3>
      <p>정해진 시간에 화면으로 만나 실시간으로 진행돼요. 선생님이 이동할 필요가 없어 저녁·주말 등 원하는 시간대를 잡기가 더 쉽고, {REGION_SHORT} 안에서 구하기 어려운 과목·스타일의 선생님도 연결할 수 있어요.</p>
      <div class="subjects"><span>국어</span><span>영어</span><span>수학</span><span>사회</span><span>과학</span></div>
    </div>
    <div class="svc-card">
      <span class="tag">녹화 복습</span>
      <h3>수업 녹화로 다시 보는 복습</h3>
      <p>매 수업을 녹화해 두기 때문에, 이해가 덜 된 부분만 골라 다시 볼 수 있어요. 시험 기간 벼락치기 복습에도, 결석했을 때 따라잡기에도 유용해요.</p>
      <div class="subjects"><span>단원별 복습</span><span>오답 다시보기</span></div>
    </div>
    <div class="svc-card">
      <span class="tag">지역 맞춤</span>
      <h3>{REGION_SHORT} 학교 사정을 아는 선생님</h3>
      <p>같은 화상 수업이라도 학교별 시험 범위와 난이도를 아는 선생님과 하면 훨씬 정확해요. 상담 시 재학 중인 학교를 먼저 확인하고, 그 학교 학생을 지도한 경험이 있는 선생님 위주로 매칭합니다.</p>
      <div class="subjects"><span>학교별 내신</span><span>지역 맞춤 매칭</span></div>
    </div>
  </div>
</section>
<section>
  <div class="head-row"><div><span class="eyebrow">방문 수업이 필요하시다면</span><h2>화상으로 먼저 경험해보세요</h2></div></div>
  <div class="apply-wrap" style="grid-template-columns:1fr;">
    <div>
      <p style="color:#D7E3F2;">{BRAND}{BRAND_EUN} 현재 화상과외 하나에만 집중하고 있어요. 방문 수업이 꼭 필요한 경우라면 상담 시 말씀해 주세요 — 상황에 따라 안내해 드릴 수 있는 방법을 함께 찾아볼게요.</p>
      <div style="margin-top:18px;"><a class="cta-btn" href="apply.html" style="background:var(--accent);color:#071A2E!important;">무료 상담 신청하기</a></div>
    </div>
  </div>
</section>
'''

process_body = '''
<section class="page-hero">
  <span class="eyebrow">매칭 방식</span>
  <h1>성적이 오르는 5단계 관리 시스템</h1>
  <p>진단 없이 곧바로 선생님을 배정하지 않아요. 아이의 학습 상태를 먼저 확인하고, 그 다음 순서로 매칭과 관리가 이어집니다.</p>
</section>
<section>
  <div class="process-track">
    <div class="p-step"><div class="n">01</div><h4>학습 진단</h4><p>현재 수준·약점을 정확히 파악합니다. 최근 시험 결과와 학습 습관을 함께 확인해요.</p></div>
    <div class="p-step"><div class="n">02</div><h4>맞춤 설계</h4><p>목표에 맞춘 1:1 커리큘럼을 만듭니다. 단기 내신 대비인지 장기 실력 향상인지에 따라 설계가 달라져요.</p></div>
    <div class="p-step"><div class="n">03</div><h4>30분 무료체험수업</h4><p>정해진 시간에 화면으로 만나 30분 동안 무료로 먼저 수업을 받아봐요. 이 시간으로 선생님과의 궁합을 확인해요.</p></div>
    <div class="p-step"><div class="n">04</div><h4>숙제·오답 관리</h4><p>정식 수업을 시작하면 배운 내용을 확실히 내 것으로 만듭니다. 오답 노트와 복습 계획을 함께 챙겨요.</p></div>
    <div class="p-step"><div class="n">05</div><h4>리포트·피드백</h4><p>진행 상황을 학부모님께 정기적으로 공유합니다. 필요하면 커리큘럼을 다시 조정해요.</p></div>
  </div>
</section>
<section>
  <div class="head-row"><div><span class="eyebrow">한 가지 더</span><h2>결제는 체험 수업 다음에 결정하세요</h2></div></div>
  <div class="trust-grid" style="grid-template-columns:repeat(2,1fr);">
    <div class="trust-item"><div class="ico">\U0001F3AC</div><h4>30분 무료체험수업</h4><p>정식 신청 전에 선생님과 30분 동안 무료로 먼저 만나볼 수 있어요. 궁합이 어떤지 직접 확인해보세요.</p></div>
    <div class="trust-item"><div class="ico">\U0001F4AC</div><h4>체험 후 자유롭게 결정</h4><p>체험 수업이 마음에 들 때만 정식으로 시작하시면 돼요. 부담 갖지 않으셔도 됩니다.</p></div>
  </div>
</section>
'''

# ---------------------------------------------------------------
# 선생님 풀 — 실제 보유 선생님 규모(600명+)를 반영한 예시 데이터
# (개인정보 보호를 위해 이름은 성만 표시. 실제 매칭 시 정확한 프로필은 상담 후 안내)
# ---------------------------------------------------------------
TEACHER_POOL_SIZE = 614

def generate_teacher_pool(n, seed_key):
    rnd = random.Random(1000 + sum(ord(c) for c in seed_key))
    surnames = ["김","이","박","최","정","강","조","윤","장","임","한","오","서","신","권","황","안","송","전","홍","고","문","양","손","배","백","허","유","남","심"]
    unis = ["서울대","연세대","고려대","이화여대","한국외대","성균관대","한양대","경상국립대","창원대","부산대","전남대","충남대"]
    subj_weights = [("수학",34), ("영어",26), ("국어",16), ("과학",14), ("사회",10)]
    subj_pool = [s for s, w in subj_weights for _ in range(w)]

    def pick_subjects():
        r = rnd.random()
        if r < 0.06:
            return ["국어", "영어", "수학", "사회", "과학"]
        if r < 0.22:
            first = rnd.choice(subj_pool)
            second = rnd.choice([s for s in ["국어","영어","수학","사회","과학"] if s != first])
            return [first, second]
        return [rnd.choice(subj_pool)]

    def pick_levels():
        r = rnd.random()
        if r < 0.22:
            return ["초등"]
        if r < 0.40:
            return ["중등"]
        if r < 0.55:
            return ["고등"]
        if r < 0.72:
            return ["초등", "중등"]
        if r < 0.88:
            return ["중등", "고등"]
        return ["초등", "중등", "고등"]

    range_by_levels = {
        ("초등",): ["초1~초6", "초2~초6", "초3~초6"],
        ("중등",): ["중1~중3"],
        ("고등",): ["고1~고3"],
        ("초등", "중등"): ["초4~중3", "초1~중3"],
        ("중등", "고등"): ["중1~고3", "중2~고3"],
        ("초등", "중등", "고등"): ["초1~고3"],
    }

    def make_tag(subjects, levels):
        subj_label = "전과목" if len(subjects) >= 4 else "·".join(subjects)
        r = rnd.random()
        if r < 0.32:
            return f"{rnd.choice(unis)} 출신 {subj_label} 화상과외"
        if r < 0.58:
            return f"교습경력 {rnd.randint(3,14)}년차 {subj_label} 화상과외"
        return f"{subj_label} 화상과외"

    pool = []
    for i in range(n):
        surname = rnd.choice(surnames)
        gender = "여" if rnd.random() < 0.58 else "남"
        subjects = pick_subjects()
        levels = pick_levels()
        grade_range = rnd.choice(range_by_levels[tuple(levels)])
        pool.append({
            "name": f"{surname}OO 선생님",
            "avatar": surname,
            "g": gender,
            "s": subjects,
            "lv": levels,
            "gr": grade_range,
            "tag": make_tag(subjects, levels),
            "fit": rnd.randint(84, 98),
        })
    return pool

TEACHER_POOL = generate_teacher_pool(TEACHER_POOL_SIZE, REGION_SLUG)

teachers_body = f'''
<section class="page-hero">
  <span class="eyebrow">선생님</span>
  <h1>검증된 선생님만 매칭에 참여합니다</h1>
  <p>학력·신원·경력 확인을 거치고, {REGION_SHORT} 학생 지도 경험이 있거나 {REGION_SHORT} 학교 사정을 파악한 선생님 위주로 화상과외를 안내해 드려요.</p>
</section>
<div class="stats" style="margin-bottom:52px;">
  <div class="wrap" style="grid-template-columns:repeat(3,1fr);">
    <div><div class="num mono">600명+</div><div class="lbl">전국 화상과외 선생님 풀</div></div>
    <div><div class="num mono">5과목</div><div class="lbl">국어·영어·수학·사회·과학</div></div>
    <div><div class="num mono">4단계</div><div class="lbl">등록 전 검증 절차</div></div>
  </div>
</div>
<section>
  <div class="head-row"><div><span class="eyebrow">검증 절차</span><h2>선생님 등록 전 4단계 확인</h2></div></div>
  <div class="trust-grid" style="grid-template-columns:repeat(2,1fr);">
    <div class="trust-item"><div class="ico">\U0001F4C4</div><h4>학력 확인</h4><p>졸업증명 등 학력 서류를 확인합니다.</p></div>
    <div class="trust-item"><div class="ico">\U0001F194</div><h4>신원 확인</h4><p>본인 확인 및 신원 정보를 검증합니다.</p></div>
    <div class="trust-item"><div class="ico">\U0001F4BC</div><h4>경력 확인</h4><p>과외·강의 경력을 확인하고 전공·지도 과목을 매칭합니다.</p></div>
    <div class="trust-item"><div class="ico">\U0001F4DE</div><h4>사전 인터뷰</h4><p>화상 수업 방식과 성향을 미리 확인해 학생과의 궁합을 예측합니다.</p></div>
  </div>
</section>
<section id="teachers">
  <div class="head-row"><div><span class="eyebrow">선생님 찾기</span><h2>조건에 맞는 선생님을 미리 둘러보세요</h2></div></div>
  <p class="sample-note"><span class="badge">예시</span>아래 프로필은 실제 보유 선생님 풀 규모에 맞춘 예시 카드예요. 선생님 성함은 개인정보 보호를 위해 성만 표시하고, 정확한 프로필은 상담 신청 후 안내해 드려요.</p>
  <div class="teacher-filter">
    <div class="field">
      <label>과목</label>
      <div class="radio-row" id="f-subject">
        <label><input type="radio" name="f-subject" value="전체" checked> 전체</label>
        <label><input type="radio" name="f-subject" value="국어"> 국어</label>
        <label><input type="radio" name="f-subject" value="영어"> 영어</label>
        <label><input type="radio" name="f-subject" value="수학"> 수학</label>
        <label><input type="radio" name="f-subject" value="사회"> 사회</label>
        <label><input type="radio" name="f-subject" value="과학"> 과학</label>
      </div>
    </div>
    <div class="field">
      <label>학년</label>
      <div class="radio-row" id="f-level">
        <label><input type="radio" name="f-level" value="전체" checked> 전체</label>
        <label><input type="radio" name="f-level" value="초등"> 초등</label>
        <label><input type="radio" name="f-level" value="중등"> 중등</label>
        <label><input type="radio" name="f-level" value="고등"> 고등</label>
      </div>
    </div>
    <div class="field">
      <label>성별</label>
      <div class="radio-row" id="f-gender">
        <label><input type="radio" name="f-gender" value="전체" checked> 전체</label>
        <label><input type="radio" name="f-gender" value="여"> 여</label>
        <label><input type="radio" name="f-gender" value="남"> 남</label>
      </div>
    </div>
  </div>
  <p class="sample-note" style="margin-top:18px;"><span class="badge mono" id="match-count">-</span><span id="match-label">조건에 맞는 선생님이 있어요</span></p>
  <div class="teachers" id="teacher-results"></div>
  <p style="margin-top:22px;"><a class="cta-btn" href="apply.html">이 조건으로 무료 상담 신청하기</a></p>
</section>
'''

teachers_js = '''<script>window.TEACHER_POOL=''' + json.dumps(TEACHER_POOL, ensure_ascii=False) + ''';</script>
<script>
(function(){
  var pool = window.TEACHER_POOL || [];
  var results = document.getElementById('teacher-results');
  var countEl = document.getElementById('match-count');
  var labelEl = document.getElementById('match-label');
  if(!results) return;

  function cardHtml(t){
    return '<div class="t-card"><div class="avatar">' + t.avatar + '</div><h4>' + t.name + '</h4>' +
      '<div class="meta">' + t.s.join('·') + ' · ' + t.gr + ' · ' + t.g + ' · ' + t.tag + '</div>' +
      '<div class="fit-score">예상 궁합도 <b class="mono">' + t.fit + '%</b></div></div>';
  }

  function currentFilter(name){
    var checked = document.querySelector('input[name="' + name + '"]:checked');
    return checked ? checked.value : '전체';
  }

  function render(){
    var subject = currentFilter('f-subject');
    var level = currentFilter('f-level');
    var gender = currentFilter('f-gender');
    var matched = pool.filter(function(t){
      if(subject !== '전체' && t.s.indexOf(subject) === -1) return false;
      if(level !== '전체' && t.lv.indexOf(level) === -1) return false;
      if(gender !== '전체' && t.g !== gender) return false;
      return true;
    });
    var shown = matched.slice(0, 9);
    results.innerHTML = shown.map(cardHtml).join('');
    countEl.textContent = matched.length + '명';
    labelEl.textContent = matched.length > shown.length
      ? '조건에 맞는 선생님이 있어요 (인기 ' + shown.length + '명 우선 표시)'
      : '조건에 맞는 선생님이 있어요';
  }

  ['f-subject','f-level','f-gender'].forEach(function(group){
    document.querySelectorAll('input[name="' + group + '"]').forEach(function(input){
      input.addEventListener('change', render);
    });
  });
  render();
})();
</script>'''

# ---------------------------------------------------------------
# regions.html -> {지역} 학교검색 (search UI over all schools)
# ---------------------------------------------------------------
def regions_body_and_js():
    groups = []
    for level in ["초등학교", "중학교", "고등학교"]:
        items = [s for s in SCHOOLS if s["level"] == level]
        lis = "\n        ".join(
            '<li data-name="{name}" data-level="{level}"><a href="schools/{slug}.html">{name} <span class="arrow">→</span></a></li>'.format(
                name=s["name"], level=s["level"], slug=s["slug"]
            )
            for s in items
        )
        groups.append('''<div class="school-group" data-group="{level}" hidden>
      <h3 style="font-size:15px;margin:22px 0 10px;">{level} <span class="mono" style="font-size:12px;color:var(--muted-2);font-weight:400;">({count}곳)</span></h3>
      <ul class="school-list" id="list-{level}">
        {lis}
      </ul>
    </div>'''.format(level=level, count=len(items), lis=lis))

    body = '''
<section class="page-hero">
  <span class="eyebrow">{region} 학교검색</span>
  <h1>우리 학교, 검색해서 바로 확인하세요</h1>
  <p>초등학교 {n_es}곳, 중학교 {n_ms}곳, 고등학교 {n_hs}곳까지 {region}의 모든 학교를 안내하고 있어요. 학교 이름을 입력하면 바로 찾아드려요.</p>
</section>
<section>
  <div class="field" style="max-width:480px;margin-bottom:8px;">
    <label for="school-search">학교 이름으로 검색</label>
    <input id="school-search" type="text" placeholder="예: {sample}" autocomplete="off">
  </div>
  <p id="search-prompt" class="sample-note">학교 이름을 입력하면 결과가 나타나요.</p>
  <p id="search-empty" class="sample-note" hidden>검색 결과가 없어요. 학교 이름을 다시 확인해 주세요.</p>
  <div id="school-groups">
    {groups}
  </div>
</section>
'''.format(
        region=REGION_SHORT, n_es=len(ELEMENTARY_NAMES), n_ms=len(MIDDLE_NAMES), n_hs=len(HIGH_NAMES),
        sample=", ".join(
            sample_keyword(s["name"])
            for lvl in ["초등학교", "중학교", "고등학교"]
            for s in [next((x for x in SCHOOLS if x["level"] == lvl), None)]
            if s
        ),
        groups="\n    ".join(groups),
    )

    js = '''<script>
(function(){{
  var input = document.getElementById('school-search');
  var prompt = document.getElementById('search-prompt');
  var empty = document.getElementById('search-empty');
  var groups = document.querySelectorAll('.school-group');
  if(!input) return;
  input.addEventListener('input', function(){{
    var q = input.value.trim().toLowerCase();
    if(q === ''){{
      prompt.hidden = false;
      empty.hidden = true;
      groups.forEach(function(g){{ g.hidden = true; }});
      return;
    }}
    prompt.hidden = true;
    var anyVisible = false;
    groups.forEach(function(g){{
      var items = g.querySelectorAll('li');
      var groupHasMatch = false;
      items.forEach(function(li){{
        var name = (li.getAttribute('data-name') || '').toLowerCase();
        var match = name.indexOf(q) !== -1;
        li.hidden = !match;
        if(match) groupHasMatch = true;
      }});
      g.hidden = !groupHasMatch;
      if(groupHasMatch) anyVisible = true;
    }});
    empty.hidden = anyVisible;
  }});
}})();
</script>'''
    return body, js

regions_body, regions_js = regions_body_and_js()

# ---------------------------------------------------------------
# blog.html (index only, cards to be added over time)
# ---------------------------------------------------------------
# ---------------------------------------------------------------
# 블로그 글 목록 — 새 글은 이 리스트 맨 앞(최신순)에 추가
# 각 항목: slug, title, date(YYYY-MM-DD), category, teaser(카드용 요약), body(본문 HTML, <h2>/<p>/<strong> 등)
# ---------------------------------------------------------------
BLOG_POSTS = []  # 아래에서 append (파일 뒷부분 참고)

def blog_card(post):
    return '''<div class="article-card">
      <div class="meta">{date} · {category}</div>
      <h3>{title}</h3>
      <p>{teaser}</p>
      <a class="more" href="blog/{slug}.html">본문 보기 →</a>
    </div>'''.format(date=post["date"], category=post["category"], title=post["title"], teaser=post["teaser"], slug=post["slug"])

def build_blog_body():
    latest_first = sorted(enumerate(BLOG_POSTS), key=lambda t: (t[1]["date"], t[0]), reverse=True)
    cards = "\n    ".join(blog_card(p) for _, p in latest_first)
    return f'''
<section class="page-hero">
  <span class="eyebrow">블로그</span>
  <h1>{REGION_SHORT} 학교별 내신·과목별 학습 전략</h1>
  <p>{REGION_SHORT} 학교별 내신 대비, 학년별·과목별 화상과외 학습 전략을 꾸준히 올리고 있어요.</p>
</section>
<section>
  <div class="article-grid">
    <!-- BLOG_GRID_START -->
    {cards}
    <!-- BLOG_GRID_END -->
  </div>
</section>
'''

def cta_big(prefix="../"):
    return f'''<div class="cta-big">
  <div class="cta-big-text">
    <span class="cta-badge">무료</span>
    <h2>30분 무료체험수업 먼저 받아보세요</h2>
    <p>이름과 연락처만 남기시면 24시간 이내에 담당자가 연락드려요. 체험 후 마음에 들 때만 결정하세요.</p>
  </div>
  <div class="cta-big-btns">
    <a class="cta-main" href="{prefix}apply.html">무료체험 신청하기 →</a>
    <a class="cta-sub" href="tel:{PHONE_TEL}">전화 {PHONE_DISPLAY}</a>
    <a class="cta-sub" href="{KAKAO_URL}" target="_blank" rel="noopener">카카오톡 상담</a>
  </div>
</div>'''

def intro_banner():
    return f'''<div class="intro-banner">
  <span class="ib-tag">무료 상담 · 무료 체험</span>
  <p>학생 학습 상태 진단과 학교 시험 분석을 함께 안내드려요.<br><mark class="free">30분 무료체험수업</mark>으로 먼저 확인해보세요.</p>
  <div class="ib-btns">
    <a class="ib-kakao" href="{KAKAO_URL}" target="_blank" rel="noopener">카카오톡 상담 <i>↗</i></a>
    <a class="ib-apply" href="../apply.html">무료체험 신청 <i>✨</i></a>
  </div>
</div>'''

def _split_long_p(m):
    inner = m.group(1)
    if "<br" in inner or len(inner) < 170:
        return m.group(0)
    sents = [x for x in re.split(r'(?<=[.!?])\s+', inner.strip()) if x]
    chunks, cur = [], []
    for sx in sents:
        cur.append(sx)
        if len(" ".join(cur)) >= 90 or len(cur) >= 2:
            chunks.append(" ".join(cur)); cur = []
    if cur:
        if chunks and len(" ".join(cur)) < 40:
            chunks[-1] += " " + " ".join(cur)
        else:
            chunks.append(" ".join(cur))
    for c in chunks:
        if c.count("<strong>") != c.count("</strong>"):
            return m.group(0)
    return "".join("<p>{}</p>".format(c) for c in chunks)

def _auto_format(body):
    if "summary-box" in body:
        return body
    body = re.sub(r'<p>(.*?)</p>', _split_long_p, body, flags=re.S)
    titles = re.findall(r'<h2>(.*?)</h2>', body)
    items = "".join("<li>{}</li>".format(t) for t in titles[:5])
    box = ('<div class="summary-box"><strong>이 글 한눈에 보기</strong><ul>' + items +
           '<li><b>30분 무료체험수업</b>으로 먼저 확인해보실 수 있어요.</li></ul></div>')
    body = box + body
    def to_callout(sec, force):
        if "<h3>" in sec or "callout" in sec:
            return sec
        ps = list(re.finditer(r'<p>([^<]*?)</p>', sec))
        if not ps:
            return sec
        last = ps[-1]
        if sec[last.end():].strip():
            return sec
        if not (force or re.match(r'(결국|무엇보다|중요한 건)', last.group(1))):
            return sec
        return sec[:last.start()] + '<div class="callout"><strong>핵심 정리</strong>' + last.group(1) + '</div>' + sec[last.end():]
    parts = re.split(r'(?=<h2>)', body)
    return parts[0] + "".join(to_callout(p, i in (1, 3)) for i, p in enumerate(parts[1:]))

def wrap_boxes(body):
    body = _auto_format(body)
    body = body.replace("30분 무료체험수업", '<mark class="free">30분 무료체험수업</mark>')
    parts = re.split(r'(?=<h2>)', body)
    out = [intro_banner(), parts[0]]
    n = 0
    has_mid = 'mid-cta' in body
    for p in parts[1:]:
        m = re.search(r'\s*<h3>', p)
        if m:
            main, faq = p[:m.start()], p[m.start():]
            out.append('<div class="pbox">' + main + '</div>')
            out.append('<div class="pbox faq-box">' + faq + '</div>')
        else:
            out.append('<div class="pbox">' + p + '</div>')
        n += 1
        if n == 3 and not has_mid:
            out.append('<div class="mid-cta"><strong>우리 아이에게 맞는지 궁금하시다면</strong><br><mark class="free">30분 무료체험수업</mark>으로 먼저 확인해보세요. <a class="cta-btn" href="../apply.html">무료체험 신청하기 →</a></div>')
    return "".join(out)

def cover_html(post):
    if os.path.exists(os.path.join(ROOT, "blog", "img", post["slug"] + ".webp")):
        return '<img class="post-cover" src="img/{}.webp" width="720" height="720" alt="{} 1:1 화상과외 안내" loading="eager">'.format(post["slug"], post["title"].split(",")[0])
    return ""

def blog_post_body(post):
    return f'''
<nav class="breadcrumb"><a href="../blog.html">블로그</a> / {post["category"]}</nav>
<section class="page-hero post-hero">
  <span class="eyebrow">{post["date"]} · {post["category"]}</span>
  <h1>{post["title"]}</h1>
  {cover_html(post)}
  <div class="hero-cta"><a class="cta-main" href="../apply.html">30분 무료체험 신청하기 →</a><span>상담·체험 모두 무료</span></div>
</section>
<section>
  <article class="prose blog-prose">
    {wrap_boxes(post["body"])}
  </article>
</section>
<section>
  {cta_big()}
</section>
<p style="margin-top:14px;"><a href="../blog.html">← 블로그 목록으로</a></p>
'''


# -*- coding: utf-8 -*-
# 여수 블로그 1차 배치 10건 (2026-09-24 발행)

BLOG_POSTS.append({
    "slug": "yeosu-hs-gimalgosa-daebi",
    "title": "여수고등학교 기말고사 대비 화상과외, 지금부터 이렇게 준비하세요",
    "date": "2026-09-24",
    "category": "고등 내신관리",
    "teaser": "여수고등학교 학생 기준으로, 기말고사를 남은 기간 동안 화상과외로 효율적으로 준비하는 방법을 정리했어요.",
    "body": '''
    <p>여수고등학교에 다니는 자녀를 둔 학부모님이라면, 기말고사가 다가올 때마다 어떻게 준비해야 할지 고민이 많으실 거예요. 중간고사 성적이 만족스럽지 않았다면 더더욱 초조한 마음이 드실 텐데, 사실 기말고사는 남은 시간을 어떻게 쓰느냐에 따라 결과가 크게 달라질 수 있는 시험이에요. 특히 고등학교 내신은 대학 입시와 직결되기 때문에, 한 번의 시험이라도 소홀히 할 수 없다는 부담이 크실 거예요. 이 글에서는 여수고등학교 학생들이 실제 상담에서 자주 이야기하는 고민을 바탕으로, 기말고사를 남은 기간 동안 어떻게 준비하면 좋을지 화상과외 관점에서 구체적으로 정리해봤어요. 지금부터 계획을 세우신다면 충분히 결과를 바꿀 수 있는 시간이 남아 있으니, 끝까지 참고해보시길 바랍니다.</p>
    <h2>여수고등학교 기말고사, 중간고사와는 다르게 접근해야 해요</h2>
    <p>기말고사는 중간고사보다 다루는 범위가 훨씬 넓고, 학기 전체 내용이 누적으로 출제되는 경우가 많아요. 게다가 2학기 기말고사라면 한 학기 전체 성적을 좌우하는 만큼 부담이 더 커지죠. 여수고등학교뿐 아니라 대부분의 인문계 고등학교가 기말 시험에서 서술형·논술형 비중을 중간고사보다 높이는 경향이 있는데, 이 부분을 놓치고 객관식 위주로만 공부하면 예상보다 점수가 낮게 나오는 경우가 많아요. <strong>범위가 넓어졌다고 모든 내용을 똑같은 비중으로 공부하면 오히려 시간이 부족해지기 쉽습니다.</strong> 먼저 학교 선생님이 강조했던 부분, 수업 중 반복해서 설명한 개념, 프린트나 부교재에서 다뤘던 유형을 중심으로 우선순위를 정하는 게 중요해요. 화상과외로 상담을 진행하다 보면, 학생 스스로는 어디가 중요한지 판단하기 어려워하는 경우가 많아서, 선생님이 시험 범위를 함께 훑어보면서 우선순위를 잡아주는 것만으로도 공부 방향이 훨씬 명확해지는 걸 자주 봅니다. 여수고등학교 특성상 과목별로 서술형 채점 기준이 꽤 꼼꼼한 편이라, 답을 아는 것과 서술형으로 정확히 표현하는 것은 다른 능력이라는 점도 함께 챙겨야 해요. 특히 국어나 사회처럼 서술형 답안의 길이가 긴 과목은, 답안에 핵심 키워드를 빠뜨리지 않고 넣는 연습이 감점을 줄이는 데 큰 도움이 돼요. 혼자 준비하면 이런 디테일을 놓치기 쉬워서, 실제로 답안을 써본 뒤 선생님에게 피드백을 받아보는 과정이 특히 중요합니다.</p>
    <h2>과목별로 우선순위를 정하는 게 먼저예요</h2>
    <p>기말고사를 앞두고 모든 과목을 똑같은 시간으로 나눠 공부하는 학생들이 많은데, 이건 오히려 비효율적인 경우가 많아요. 목표 등급에 따라 우선순위를 다르게 잡아야 합니다. 예를 들어 이미 안정적으로 1~2등급이 나오는 과목이라면 유지하는 선에서 시간을 배분하고, 등급 경계에 있는 과목에 더 많은 시간을 투자하는 게 전체 평균을 올리는 데 효과적이에요. 수학이나 영어처럼 누적 학습이 중요한 과목은 기말고사 2~3주 전부터는 새로운 유형을 익히기보다 기존에 틀렸던 문제를 다시 점검하는 방식이 더 안전합니다. 반면 사회나 과학 탐구 과목은 암기와 개념 이해가 함께 필요한데, 시험 직전 집중적으로 정리하면 효과를 볼 수 있는 과목이기도 해요. <strong>중요한 건 내 현재 위치를 정확히 파악하고, 시간을 어디에 더 쓸지 스스로 결정하는 연습</strong>이에요. 화상과외에서는 상담 시 최근 성적과 취약 단원을 먼저 점검한 뒤, 과목별로 어느 정도 시간을 배분하면 좋을지 함께 계획을 세워드리고 있어요. 이 계획이 없으면 시험 기간에 마음만 급해져서 정작 중요한 과목을 놓치는 경우가 생각보다 많습니다. 예를 들어 목표 등급이 3등급인 학생과 1등급인 학생은 시간을 배분하는 방식이 달라야 해요. 3등급을 목표로 한다면 기본 개념 문제를 확실히 맞히는 데 집중하고, 1등급을 목표로 한다면 변별력 있는 고난도 문제까지 대비해야 하죠. 이런 목표 설정이 없으면 무작정 시간만 쏟고 결과는 기대에 못 미치는 경우가 많습니다.</p>
    <h2>화상과외가 기말고사 대비에 유리한 이유</h2>
    <p>기말고사 기간에는 시간이 정말 촉박하게 느껴지죠. 학원을 오가는 이동 시간조차 아까운 시기인데, 화상과외는 이 부분에서 확실한 장점이 있어요. 정해진 시간에 화면으로 바로 만나기 때문에 이동 시간이 전혀 들지 않고, 그만큼 순수하게 공부에 쓸 수 있는 시간이 늘어나요. 또한 학원처럼 정해진 커리큘럼을 따라가야 하는 게 아니라, 그 학생에게 부족한 단원만 집중적으로 짚어줄 수 있다는 점도 큰 차이예요. 여수고등학교 학생을 지도한 경험이 있거나 비슷한 학교의 시험 스타일을 잘 아는 선생님과 함께라면, 서술형 문제에 어떻게 답을 작성해야 감점 없이 점수를 받을 수 있는지도 구체적으로 안내받을 수 있어요. 수업이 녹화되기 때문에, 시험 전날 헷갈리는 부분만 다시 돌려보면서 복습할 수 있다는 것도 실전에서 꽤 유용한 기능입니다. <strong>이동 없이 저녁 시간대에도 유연하게 수업을 잡을 수 있다는 점</strong>은 학교 자습 시간이나 야간자율학습과 겹치지 않게 일정을 조율할 수 있어서, 기말고사 기간처럼 시간이 부족할 때 특히 체감되는 장점이에요. 또한 화상과외는 시험 직전 며칠 동안 짧게라도 자주 만나는 방식으로 일정을 조정하기가 수월해요. 예를 들어 평소에는 주 2회 수업을 하다가 시험 2주 전부터는 주 3~4회로 늘려서 집중적으로 점검할 수도 있죠. 학원이라면 이런 유연한 일정 조정이 쉽지 않지만, 화상과외는 선생님과 직접 상의해서 필요한 만큼 조율할 수 있다는 점이 실전에서 특히 유용합니다.</p>
    <h2>기말고사 전 꼭 확인해야 할 3가지</h2>
    <p>첫째, 시험 범위 안에서 내가 확실히 아는 부분과 헷갈리는 부분을 구분하는 것부터 시작하세요. 이 구분이 안 된 상태로 무작정 문제집을 풀면 이미 아는 내용만 반복하게 되는 경우가 많아요. 둘째, 서술형 문제에 대한 답안 작성 연습을 별도로 해봐야 해요. 개념을 알아도 정확한 용어와 문장으로 서술하지 못하면 부분 점수만 받는 경우가 많습니다. 셋째, 시험 전 최소 1주일은 새로운 내용을 배우기보다 정리와 복습에 집중하는 시간으로 남겨두세요. 이 세 가지를 놓치면 아무리 오래 책상에 앉아 있어도 성적으로 이어지지 않는 경우가 많아요. 여수고등학교처럼 서술형 비중이 있는 학교라면 특히 두 번째 항목을 소홀히 하지 않는 게 중요합니다. 화상과외 선생님과 함께라면 이 세 가지를 시험 3~4주 전부터 단계적으로 체크하면서 준비할 수 있어서, 시험이 임박했을 때 허둥대지 않고 계획대로 마무리할 수 있어요. <strong>계획 없이 벼락치기로 준비하는 것과 단계적으로 준비하는 것은 결과에서 확실히 차이가 납니다.</strong> 특히 서술형 답안 작성 연습은 혼자 하기보다 누군가에게 첨삭을 받는 과정이 꼭 필요해요. 스스로는 맞게 썼다고 생각해도 채점 기준에서 요구하는 핵심 표현이 빠져 있으면 감점되는 경우가 많거든요. 화상과외에서는 학생이 직접 써본 답안을 선생님이 즉시 확인하고, 어떤 표현이 부족했는지 바로 피드백을 줄 수 있어서 이 부분을 효율적으로 보완할 수 있어요. 혼자 작성한 답안을 스스로 채점하는 것보다, 이렇게 즉시 피드백을 받는 방식이 훨씬 빠르게 감점 요인을 줄여줍니다.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면 중간고사 이후 성적표를 보고 걱정스러운 마음으로 문의하시는 학부모님들을 자주 만나요. 특히 서술형에서 감점이 많아 예상보다 점수가 낮게 나온 경우, 학생 본인도 이유를 정확히 모르는 경우가 많습니다. 이럴 때는 먼저 이전 시험지를 함께 살펴보면서 어떤 부분에서 감점됐는지 원인을 파악하는 것부터 시작해요. 어떤 학생은 개념 자체는 이해하고 있었지만 답안을 서술하는 방식이 채점 기준과 맞지 않아서 감점된 경우였고, 이후에는 서술형 답안 작성 연습을 별도로 진행하면서 감점 요인을 줄여나갈 수 있었어요. 반대로 범위가 넓어 어디를 먼저 봐야 할지 몰라 막막해하던 학생은, 선생님과 함께 우선순위를 정리한 뒤부터 남은 시간을 훨씬 효율적으로 쓸 수 있게 됐다는 이야기를 해주셨어요. <strong>중요한 건 막연히 열심히 하는 게 아니라, 내가 왜 감점되는지 정확히 알고 그 부분을 고쳐나가는 것</strong>이라는 걸 이런 상담들을 통해 계속 확인하고 있어요. 또 다른 학생은 시험 3주 전까지 계획 없이 지내다가 막판에 몰아서 공부하는 패턴이 반복됐는데, 상담을 통해 매주 무엇을 할지 구체적으로 계획을 세우면서부터는 시험 기간에 훨씬 여유 있게 준비할 수 있게 됐어요. 이렇게 계획을 세우는 습관 자체가 다음 시험에도 이어지면서, 매번 시험 때마다 급하게 준비하던 패턴에서 벗어날 수 있었다는 이야기를 많이 듣습니다. 결국 한 번의 시험 결과보다, 그 시험을 준비하는 방식 자체를 바꾸는 게 다음 시험까지 이어지는 진짜 변화라는 걸 이런 사례들을 통해 계속 확인하게 됩니다.</p>
    <h2>티치핏여수와 함께 기말고사를 준비해보세요</h2>
    <p>티치핏여수는 상담 시 최근 성적과 시험지를 먼저 확인하고, 여수고등학교 같은 학교의 시험 스타일을 고려해서 서술형 대비까지 챙길 수 있는 선생님을 화상으로 연결해 드려요. 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여하고, 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있습니다. 신청 후 24시간 이내에 담당자가 직접 연락드리고, 학습 진단부터 선생님 추천, 체험 수업까지 순서대로 안내해 드려요. 여수고등학교뿐 아니라 여수 관내 고등학교 15곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교를 알려주시면 그에 맞춰 상담해 드릴게요. 기말고사가 얼마 남지 않았다고 느껴질수록 오히려 계획적으로 접근하는 게 중요한 시기예요. 특히 처음 상담을 망설이는 경우가 많은데, 상담 자체는 부담 없이 편하게 받아보실 수 있어요. 지금 편하게 상담을 신청해보세요.</p>
    <p><strong>Q. 여수고등학교 학생도 화상과외로 서술형 대비가 가능한가요?</strong><br>
    네, 상담 시 최근 시험지를 함께 확인하고 서술형 답안 작성 연습을 별도로 진행해 드려요.</p>
    <p><strong>Q. 기말고사가 2주 정도 남았는데 지금 시작해도 늦지 않을까요?</strong><br>
    늦지 않아요. 오히려 남은 시간 동안 우선순위를 명확히 정하면 짧은 기간에도 효율적으로 준비할 수 있어요.</p>
    <p><strong>Q. 한 과목만 집중적으로 봐줄 수도 있나요?</strong><br>
    물론이에요. 전 과목을 다 신청하지 않아도 되고, 취약한 과목 한두 개만 집중해서 봐드릴 수 있어요.</p>
    ''',
})

BLOG_POSTS.append({
    "slug": "yeosu-ms-naeshin-gwanri",
    "title": "여수중학교 내신관리, 중간고사 끝난 지금 놓치면 안 되는 것들",
    "date": "2026-09-24",
    "category": "중등 내신관리",
    "teaser": "여수중학교 학생 기준으로, 중간고사 이후 기말고사까지 내신관리를 어떻게 이어가야 하는지 정리했어요.",
    "body": '''
    <p>여수중학교에 다니는 자녀를 둔 학부모님 중에는, 중간고사가 끝나고 나면 오히려 긴장이 풀려서 걱정되신다는 분들이 많아요. 시험이 끝났다는 안도감에 며칠은 편하게 쉬는 게 당연하지만, 그 시간이 너무 길어지면 기말고사까지 흐름이 끊기기 쉬워요. 특히 중학교 내신은 고등학교 입시와도 연결되는 경우가 많아서, 한 학기 안에서도 꾸준한 관리가 필요한 부분이에요. 이 글에서는 여수중학교 학생들이 중간고사 이후 상담에서 자주 언급하는 고민을 바탕으로, 기말고사까지 내신관리를 어떻게 이어가면 좋을지 정리해봤어요. 지금 이 시기를 어떻게 보내느냐가 다음 시험 결과를 좌우하니 참고해보시길 바랍니다.</p>
    <h2>중간고사 이후가 오히려 더 중요한 시기예요</h2>
    <p>중간고사가 끝나면 대부분의 학생들이 긴장을 풀고 잠시 쉬어가는 시간을 가지는데, 이 시기를 어떻게 보내느냐에 따라 기말고사 결과가 크게 달라져요. 여수중학교처럼 학기 중 수행평가와 지필고사를 함께 반영하는 경우, 중간고사 이후에도 계속 수행평가 점수가 쌓이기 때문에 완전히 손을 놓아버리면 나중에 만회하기가 훨씬 어려워집니다. <strong>중간고사 성적표를 받은 직후가 오히려 약점을 점검하기 가장 좋은 시점</strong>이에요. 어떤 과목에서 어떤 유형의 문제를 틀렸는지, 시간이 부족해서 못 풀었는지 아니면 개념을 몰라서 틀렸는지를 구분해보는 것부터 시작하면 좋아요. 화상과외로 상담을 하다 보면, 성적표만 보고 막연히 속상해하기보다 시험지를 함께 분석해보는 것만으로도 다음 시험에 대한 방향이 훨씬 명확해지는 경우가 많아요. 여수중학교 수행평가 비중을 고려하면, 지필고사 준비와 별개로 수업 중 과제나 발표도 꾸준히 챙기는 습관이 필요합니다. 예를 들어 국어나 사회 과목에서 서술형으로 개념을 설명해야 하는 문제가 나온다면, 단순히 답을 외우는 것보다 그 개념을 자기 말로 풀어서 설명해보는 연습이 훨씬 효과적이에요. 여수중학교처럼 수행평가 비중이 있는 학교라면, 지필고사 준비와 수행평가 준비를 따로 떼어서 생각하지 말고 함께 챙기는 습관을 학기 초부터 만들어두는 게 좋습니다. 성적표를 받자마자 며칠은 쉬더라도, 그 이후에는 바로 시험지를 다시 펼쳐보는 습관을 들이는 게 다음 시험 준비의 출발점이 됩니다.</p>
    <h2>기말고사까지 남은 기간, 계획을 다시 세워야 해요</h2>
    <p>중간고사 이후 기말고사까지는 보통 한 달 이상의 시간이 남아 있는데, 이 기간을 계획 없이 보내면 시험 직전에 몰아서 공부하는 패턴이 반복되기 쉬워요. 먼저 이번 학기에 남은 수행평가 일정과 기말고사 날짜를 한눈에 정리해두는 게 좋습니다. 그다음 중간고사에서 부족했던 과목이나 단원을 우선순위에 놓고, 남은 기간 동안 어떤 순서로 보완할지 계획을 세워보세요. 예를 들어 수학에서 특정 단원의 개념이 부족했다면, 기말고사 시험 범위에 그 단원의 후속 내용이 포함될 가능성이 높기 때문에 미리 짚어두는 게 훨씬 효율적이에요. <strong>계획은 거창하지 않아도 괜찮지만, 매주 무엇을 할지 정도는 구체적으로 정해두는 게 중요합니다.</strong> 화상과외에서는 상담 시 이런 학기 전체 일정을 함께 확인하고, 남은 기간을 주 단위로 어떻게 쓸지 계획을 함께 세워드리고 있어요. 계획이 있으면 시험 직전에 급하게 몰아서 하지 않아도 되기 때문에 학생의 부담도 훨씬 줄어듭니다. 계획을 세울 때는 하루 단위보다 주 단위로 목표를 잡는 게 더 현실적이에요. 예를 들어 이번 주에는 수학 특정 단원을 정리하고, 다음 주에는 영어 서술형 연습을 한다는 식으로 나누면 부담 없이 이어갈 수 있어요. 계획이 너무 촘촘하면 하루라도 어긋났을 때 포기하기 쉬우니, 여유 있게 잡아두는 것도 중요한 요령입니다. 계획을 세운 뒤에는 눈에 잘 보이는 곳에 붙여두고 매주 한 번씩 체크하는 습관도 함께 만들어보면, 계획이 흐지부지되는 걸 막는 데 도움이 됩니다.</p>
    <h2>화상과외로 내신관리가 수월해지는 이유</h2>
    <p>내신관리는 한 번의 몰입보다 꾸준한 관리가 중요한 영역이에요. 화상과외는 매주 정해진 시간에 만나기 때문에 이런 꾸준한 관리에 특히 유리해요. 학원처럼 반 편성이나 정해진 진도를 따라가야 하는 게 아니라, 그 학생의 학교 시험 일정과 수행평가 상황에 맞춰 유연하게 수업 내용을 조정할 수 있다는 점도 큰 장점이에요. 여수중학교 시험 스타일을 아는 선생님이라면, 어떤 유형의 문제가 자주 나오는지, 서술형에서 어떤 부분을 놓치기 쉬운지도 함께 짚어줄 수 있어요. 지역 안에서 원하는 시간대에 맞는 선생님을 구하기 어려울 때도, 화상과외라면 훨씬 넓은 범위에서 맞는 선생님을 연결받을 수 있다는 것도 실질적인 도움이 됩니다. <strong>수업이 녹화되기 때문에 부모님도 나중에 수업 분위기를 확인해보실 수 있고</strong>, 아이가 정말 이해하며 따라가고 있는지 함께 파악할 수 있다는 점도 안심되는 부분이에요. 또한 화상과외는 그날 배운 내용을 바로 정리하고 다음 수업 때 확인하는 과정을 반복하기가 수월해요. 학원처럼 여러 학생을 동시에 봐야 하는 상황이 아니기 때문에, 선생님이 그 학생이 지난 시간에 무엇을 어려워했는지 정확히 기억하고 이어서 짚어줄 수 있죠. 이런 꾸준한 흐름이 내신관리처럼 장기적으로 관리해야 하는 영역에서는 특히 큰 힘이 됩니다. 매주 같은 시간에 만난다는 규칙성 자체가, 중학생 시기 아이들에게는 공부 리듬을 유지하는 데 은근히 큰 역할을 합니다. 이렇게 쌓인 규칙적인 습관은 시험 기간이 아닌 평소에도 학습 태도 전반에 좋은 영향을 줍니다.</p>
    <h2>내신관리에서 꼭 확인해야 할 3가지</h2>
    <p>첫째, 이번 학기 남은 수행평가 일정을 미리 정리해두세요. 지필고사만 신경 쓰다가 수행평가를 놓치면 전체 내신에 영향을 줄 수 있어요. 둘째, 중간고사에서 틀린 문제를 단순히 넘기지 말고 왜 틀렸는지 원인을 파악하세요. 같은 유형의 실수가 기말고사에서 반복되는 경우가 정말 많습니다. 셋째, 기말고사 3주 전부터는 새로운 내용보다 전체 범위를 정리하는 시간을 확보하세요. 이 세 가지를 미리 챙겨두면 시험 직전에 허둥대지 않고 훨씬 안정적으로 준비할 수 있어요. 여수중학교처럼 수행평가와 지필고사를 함께 관리해야 하는 학교라면, 특히 첫 번째 항목을 놓치기 쉬우니 학기 초부터 꾸준히 체크하는 습관이 필요합니다. <strong>내신은 한 번의 시험이 아니라 학기 전체의 누적이라는 점을 기억하는 게 중요해요.</strong> 넷째로, 평소 수업 시간에 필기한 내용을 정리하는 습관도 함께 챙겨보세요. 특히 여수중학교처럼 선생님마다 강조하는 부분이 다른 경우, 수업 중 필기가 시험 대비의 중요한 자료가 되는 경우가 많아요. 필기가 부족하다면 친구의 노트를 참고하거나, 선생님에게 다시 한번 설명을 요청하는 것도 방법이에요. 이 부분까지 학기 초부터 습관으로 만들어두면, 시험 때마다 급하게 준비하지 않아도 안정적인 성적을 유지할 수 있어요. 필기를 정리하는 시간이 아깝게 느껴질 수 있지만, 시험 직전 이 정리된 노트가 가장 빠르게 복습할 수 있는 자료가 되어준다는 걸 기억해주세요.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면, 중간고사 성적표를 받고 나서야 부족한 부분을 알게 됐다며 문의하시는 학부모님들이 많아요. 한 학생은 중간고사에서 수학 서술형 문제를 거의 다 놓쳤는데, 알고 보니 개념은 알고 있었지만 풀이 과정을 정리해서 적는 연습이 부족했던 경우였어요. 이후 매주 서술형 답안을 직접 써보고 피드백을 받는 과정을 반복하면서, 다음 시험에서는 훨씬 편안하게 서술형 문제에 접근할 수 있게 됐다는 이야기를 해주셨어요. 다른 경우에는 수행평가 일정을 놓쳐서 아쉬운 점수를 받았던 학생이, 학기 일정을 미리 정리해두면서부터는 마감을 놓치지 않고 꾸준히 챙길 수 있게 됐다고 해요. <strong>결국 중요한 건 시험 한 번이 아니라 학기 전체를 어떻게 관리하느냐</strong>라는 걸 이런 사례들을 통해 계속 확인하고 있어요. 또 다른 학부모님은 아이가 계획을 세워도 실천을 잘 못한다고 걱정하셨는데, 상담을 통해 계획을 아이 혼자 세우게 하지 않고 선생님과 함께 매주 점검하는 방식으로 바꾸면서부터는 실천율이 눈에 띄게 올라갔다고 해요. 계획 자체보다 그 계획을 지켰는지 확인해주는 존재가 있다는 게 중학생 시기에는 특히 중요한 부분이라는 걸 이런 사례를 통해 다시 확인하게 됩니다. 이렇게 관리받는 경험이 쌓이면, 나중에는 아이 스스로도 계획을 세우고 지키는 힘을 자연스럽게 갖추게 됩니다. 결국 중학생 시기의 내신관리는 성적 그 자체보다, 스스로 관리하는 힘을 길러주는 과정이라는 걸 여러 사례를 통해 계속 느끼게 됩니다.</p>
    <h2>티치핏여수와 함께 기말고사까지 관리해보세요</h2>
    <p>티치핏여수는 상담 시 중간고사 성적과 이번 학기 남은 일정을 함께 확인하고, 여수중학교 같은 학교의 수행평가·지필고사 비중을 고려해서 선생님을 연결해 드려요. 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여하고, 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있습니다. 신청 후 24시간 이내에 담당자가 직접 연락드리고, 학습 진단부터 선생님 추천, 체험 수업까지 순서대로 안내해 드려요. 여수중학교뿐 아니라 여수 관내 중학교 24곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교를 알려주시면 그에 맞춰 상담해 드릴게요. 중간고사가 끝난 지금이 오히려 기말고사를 준비할 가장 좋은 시점이니, 편하게 상담을 신청해보세요. 학기 중간에 상담을 시작해도 늦지 않으니, 지금이라도 편하게 문의해주시면 남은 기간을 어떻게 활용하면 좋을지 함께 계획을 세워드릴게요.</p>
    <p><strong>Q. 중간고사가 끝난 지 얼마 안 됐는데 벌써 시작해야 하나요?</strong><br>
    네, 오히려 지금 시작하는 게 가장 효율적이에요. 시간이 여유 있을 때 부족한 부분을 채워두면 기말고사 직전 부담이 훨씬 줄어들어요.</p>
    <p><strong>Q. 수행평가 관리도 함께 봐주시나요?</strong><br>
    네, 상담 시 학기 전체 일정을 확인하고 수행평가 준비 방향도 함께 안내해 드려요.</p>
    <p><strong>Q. 여수중학교 학생인데 매칭 가능한가요?</strong><br>
    네, 여수중학교뿐 아니라 여수 관내 중학교 전체 매칭이 가능해요.</p>
    ''',
})

BLOG_POSTS.append({
    "slug": "yeosuyeoja-hs-suneung-gukeo",
    "title": "여수여자고등학교 수능 국어 화상과외, 등급 안 나오는 이유부터 확인하세요",
    "date": "2026-09-24",
    "category": "고등 수능대비",
    "teaser": "여수여자고등학교 학생 기준으로, 국어 등급이 안 나올 때 무엇부터 점검해야 하는지 화상과외 관점에서 정리했어요.",
    "body": '''
    <p>여수여자고등학교에 다니는 자녀를 둔 학부모님 중에는, 국어 성적이 생각보다 안 나와서 답답하다고 말씀하시는 분들이 많아요. 수학이나 영어는 어디가 부족한지 비교적 명확하게 보이는데, 국어는 분명 열심히 읽었는데도 점수가 오르지 않아서 원인을 파악하기가 더 어렵다고 느끼시는 경우가 많죠. 특히 수능 국어는 단순히 글을 잘 읽는 것과 시험에서 정답을 골라내는 것이 다른 능력이라는 점 때문에, 막연히 책을 많이 읽는다고 해결되지 않는 경우가 대부분이에요. 이 글에서는 여수여자고등학교 학생들이 상담에서 자주 이야기하는 국어 성적 고민을 바탕으로, 등급이 안 나올 때 어디부터 점검해야 하는지 화상과외 관점에서 정리해봤어요.</p>
    <h2>국어 등급이 안 나오는 데는 분명한 이유가 있어요</h2>
    <p>국어 점수가 오르지 않는 학생들을 살펴보면, 크게 두 가지 유형으로 나뉘는 경우가 많아요. 하나는 지문을 읽는 속도 자체가 느려서 시간 안에 다 풀지 못하는 경우고, 다른 하나는 시간은 충분한데 지문을 읽고도 출제 의도를 정확히 파악하지 못해서 오답을 고르는 경우예요. 여수여자고등학교처럼 국어 시험에서 비문학 지문의 난이도가 꽤 높은 편이라면, 이 두 가지 유형을 구분하는 가장 쉬운 방법은, 평소 문제를 풀 때 시간을 재보는 거예요. 정해진 시간 안에 다 풀지 못한다면 속도가 문제일 가능성이 높고, 시간이 남는데도 틀린다면 지문 해석이나 선택지 판단에 문제가 있을 가능성이 높아요. 여수여자고등학교 학생들을 상담해보면, 본인이 어느 유형인지조차 모르고 무작정 문제집만 풀고 있는 경우가 의외로 많습니다. 이 두 가지 중 어디에 해당하는지부터 구분하는 게 중요합니다. 속도가 문제인 학생과 판단력이 문제인 학생은 훈련 방법이 완전히 다르기 때문에, 이 구분 없이 무작정 문제를 많이 풀기만 하면 시간 대비 효과가 떨어질 수밖에 없어요. <strong>단순히 문제집을 많이 푼다고 해서 이 문제가 자동으로 해결되지는 않아요.</strong> 시간이 부족한 학생이라면 지문을 읽는 방식 자체를 바꿔야 하고, 출제 의도를 놓치는 학생이라면 선택지를 소거하는 훈련이 더 필요해요. 화상과외로 상담을 진행하다 보면, 학생이 실제로 문제를 푸는 과정을 함께 지켜보면서 어디서 시간을 많이 쓰는지, 어떤 유형의 선택지에서 자주 헷갈리는지를 파악하는 것만으로도 다음 학습 방향이 훨씬 명확해지는 경우가 많습니다.</p>
    <h2>문학과 비문학, 접근 방식이 완전히 달라야 해요</h2>
    <p>수능 국어에서 문학과 비문학은 접근하는 방식이 달라야 하는데, 많은 학생들이 이 둘을 똑같은 방식으로 공부하다가 어려움을 겪어요. 비문학은 지문 안에 답의 근거가 명확히 있기 때문에, 감이 아니라 지문에서 근거를 찾아 소거하는 훈련이 중요합니다. 반면 문학은 작품에 대한 배경지식이 어느 정도 도움이 되지만, 그보다는 시나 소설에서 화자나 인물의 정서를 정확히 파악하는 연습이 더 중요해요. 특히 비문학에서는 지문에 나온 표현을 그대로 사용한 선택지보다, 살짝 바꿔서 제시한 선택지가 오답으로 자주 나온다는 점도 알아두면 좋아요. 이런 함정은 감으로 걸러내기 어렵기 때문에, 지문과 선택지를 하나하나 대조하는 훈련이 쌓여야 정확하게 잡아낼 수 있어요. 문학에서는 반대로 작품의 전체적인 분위기와 화자의 태도를 먼저 파악한 뒤 세부 표현을 확인하는 순서로 접근하는 게 효율적입니다. 이렇게 순서를 정해두고 접근하면, 같은 시간을 들여도 훨씬 정확하게 지문을 읽어낼 수 있어요. 여수여자고등학교 국어 시험이 수능형 문제를 많이 반영한다면, 내신을 준비할 때도 이런 수능형 접근 방식을 함께 연습해두는 게 장기적으로 유리해요. <strong>문학에서 감정적으로 해석하는 습관과 비문학에서 논리적으로 근거를 찾는 습관을 구분해서 훈련하는 것</strong>이 등급을 올리는 핵심이에요. 화상과외에서는 학생이 취약한 영역이 문학인지 비문학인지부터 구분하고, 그에 맞는 훈련 방식을 따로 적용해 드리고 있어요.</p>
    <h2>화상과외가 국어 학습에 유리한 이유</h2>
    <p>국어는 학생마다 취약한 부분이 정말 다양해서, 정해진 커리큘럼으로 진행되는 학원 수업보다는 1:1로 그 학생의 문제를 정확히 짚어주는 방식이 더 효과적인 경우가 많아요. 화상과외는 학생이 실제로 문제를 푸는 과정을 화면으로 함께 보면서, 어느 지점에서 시간을 낭비하는지, 어떤 선택지에서 자주 헷갈리는지를 실시간으로 확인할 수 있다는 장점이 있어요. 수업이 녹화되기 때문에, 헷갈렸던 지문을 다시 돌려보면서 복습할 수 있다는 것도 국어처럼 반복 학습이 중요한 과목에서는 큰 도움이 됩니다. 여수 지역 안에서 국어 수능 대비를 전문적으로 봐줄 수 있는 선생님을 구하기 어려운 경우가 많은데, 화상과외라면 지역 제약 없이 훨씬 넓은 범위에서 맞는 선생님을 연결받을 수 있어요. <strong>이동 시간이 없어 저녁 시간대에도 유연하게 수업을 잡을 수 있다는 점</strong>도 고3 학생들에게는 실질적으로 체감되는 장점이에요. 화상과외에서는 또한 학생이 특정 지문에서 시간을 얼마나 쓰는지 기록해두고, 다음 수업에서 비교해보는 방식으로 속도 개선 여부를 함께 확인할 수 있어요. 이렇게 데이터를 쌓아가면서 학생 스스로도 자신의 변화를 체감할 수 있다는 게, 혼자 공부할 때는 얻기 어려운 화상과외만의 장점이에요. 이런 변화를 눈으로 직접 확인할 수 있으면, 학생 스스로도 공부 방향에 대한 확신을 갖고 다음 단계로 넘어갈 수 있습니다. 특히 국어는 결과가 눈에 보이기까지 시간이 걸리는 과목이라, 이런 중간 확인 과정이 학생의 동기를 유지하는 데도 큰 역할을 합니다.</p>
    <h2>국어 성적을 올리기 전 꼭 확인해야 할 3가지</h2>
    <p>첫째, 최근 모의고사나 내신 시험지를 다시 펼쳐서 어떤 유형에서 틀렸는지 분류해보세요. 시간 부족인지 이해 부족인지에 따라 다음 학습 방향이 완전히 달라져요. 둘째, 평소 지문을 읽는 속도를 스스로 체크해보세요. 실제 시험 시간을 재고 풀어보면 생각보다 시간이 부족하다는 걸 알게 되는 경우가 많습니다. 셋째, 오답을 고른 이유를 스스로 설명할 수 있는지 확인하세요. 답을 맞았다고 넘기지 말고, 왜 그 선택지가 답인지 설명할 수 있어야 진짜 이해했다고 볼 수 있어요. 이 세 가지를 점검하지 않고 문제만 계속 푼다면, 시간은 들이는데 점수는 잘 오르지 않는 상황이 반복될 수 있어요. <strong>국어는 감으로 푸는 과목이 아니라 근거를 찾는 훈련이 쌓여야 등급이 오르는 과목</strong>이라는 점을 꼭 기억해주세요. 넷째로, 평소 접하지 않은 낯선 소재의 지문을 접했을 때 어떻게 반응하는지도 점검해보세요. 익숙한 소재에서는 잘 풀리는데 낯선 소재에서 갑자기 흔들리는 학생이라면, 지문 자체보다 낯섦에 대한 긴장감을 관리하는 연습이 더 필요할 수 있어요. 이 네 가지를 시험 전에 미리 점검해두면, 실제 시험장에서 당황하는 상황을 줄일 수 있습니다. 시험은 평소 실력을 그대로 보여주는 자리가 아니라, 긴장된 상황에서도 평소 실력을 꺼낼 수 있는지를 확인하는 자리라는 점도 함께 기억해두면 좋습니다. 네 가지 모두 하루아침에 완성되지 않기 때문에, 최소 한 달 전부터는 이 기준으로 스스로를 점검하는 습관을 들이는 게 좋습니다.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면, 국어를 열심히 공부하는데도 등급이 오르지 않아 답답해하시는 학부모님들을 자주 만나요. 한 학생은 비문학 지문을 이해하는 데는 문제가 없었지만, 선택지를 고를 때 지문에 없는 내용을 임의로 판단해서 오답을 고르는 습관이 있었어요. 이 부분을 파악한 뒤로는 선택지마다 지문에서 근거 문장을 직접 찾아 표시하는 훈련을 반복하면서, 점차 오답률이 줄어드는 걸 확인할 수 있었어요. 다른 학생은 문학 지문에서 시간을 지나치게 많이 써서 비문학을 풀 시간이 부족했던 경우였는데, 문학 지문을 빠르게 훑는 연습을 따로 진행하면서 전체 시험 시간 배분이 훨씬 안정적으로 바뀌었다는 이야기를 해주셨어요. <strong>결국 어디가 문제인지 정확히 짚어내는 게 성적 향상의 시작점</strong>이라는 걸 이런 사례들을 통해 계속 확인하고 있어요. 또 다른 학생은 평소 모의고사에서는 곧잘 나오던 점수가 실제 수능 형식과 비슷한 긴 지문에서는 유독 흔들리는 경우였는데, 지문 길이에 맞춰 시간 배분을 다시 훈련하면서 점차 안정적인 결과를 만들어갈 수 있었어요. 이렇게 학생마다 흔들리는 지점이 다르기 때문에, 그 지점을 정확히 찾아내는 상담 과정 자체가 성적 향상의 첫걸음이라는 걸 계속 확인하고 있습니다. 같은 국어라도 학생마다 원인이 다르다는 걸 받아들이는 것이, 막연한 반복 학습에서 벗어나는 첫걸음이 됩니다. 이런 사례들을 접할 때마다, 국어는 특히 개인별 진단 없이는 효율적인 학습이 어렵다는 걸 다시 확인하게 됩니다.</p>
    <h2>티치핏여수와 함께 국어 등급을 올려보세요</h2>
    <p>티치핏여수는 상담 시 최근 시험지와 모의고사 결과를 먼저 확인하고, 학생이 시간 부족형인지 이해 부족형인지부터 구분해서 그에 맞는 선생님을 화상으로 연결해 드려요. 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여하고, 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있습니다. 신청 후 24시간 이내에 담당자가 직접 연락드리고, 학습 진단부터 선생님 추천, 체험 수업까지 순서대로 안내해 드려요. 여수여자고등학교뿐 아니라 여수 관내 고등학교 15곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교를 알려주시면 그에 맞춰 상담해 드릴게요. 수능이 얼마 남지 않았다고 느껴질수록 오히려 지금 어디가 부족한지 정확히 진단받는 게 중요한 시기이니, 편하게 상담을 신청해보세요. 막연한 불안감으로 시간을 보내기보다, 정확한 진단을 받고 남은 시간을 계획적으로 쓰는 게 등급 향상에 훨씬 도움이 됩니다.</p>
    <p><strong>Q. 국어는 어떤 방식으로 화상과외가 진행되나요?</strong><br>
    실제 지문을 함께 읽고 문제를 푸는 과정을 화면으로 공유하면서, 어디서 시간을 쓰고 어떤 부분에서 헷갈리는지 실시간으로 점검해요.</p>
    <p><strong>Q. 문학과 비문학 중 한쪽만 집중적으로 봐줄 수 있나요?</strong><br>
    네, 상담 시 취약한 영역을 먼저 확인하고 그 영역에 집중된 수업으로 진행할 수 있어요.</p>
    <p><strong>Q. 내신 국어와 수능 국어를 같이 준비할 수 있나요?</strong><br>
    네, 시험 일정에 맞춰 내신 대비와 수능형 훈련을 함께 병행해서 진행해 드려요.</p>
    ''',
})

BLOG_POSTS.append({
    "slug": "yeodo-es-haksseub-seupgwan",
    "title": "여도초등학교 저학년 학습습관, 화상과외로 잡아주는 방법",
    "date": "2026-09-24",
    "category": "초등 학습습관",
    "teaser": "여도초등학교 저학년 학생 기준으로, 학습습관을 화상과외로 자연스럽게 잡아주는 방법을 정리했어요.",
    "body": '''
    <p>여도초등학교에 다니는 자녀를 둔 학부모님 중에는, 아이가 아직 저학년이라 학원을 보내기엔 이르다고 느끼시면서도 학습습관은 미리 잡아주고 싶다는 고민을 많이 하세요. 실제로 저학년 시기에 형성된 학습습관은 이후 학년이 올라갈수록 큰 영향을 미치기 때문에, 이 시기를 어떻게 보내느냐가 중요한 건 맞아요. 다만 무작정 학습량을 늘리기보다는, 아이가 스스로 앉아서 집중하는 습관, 배운 내용을 정리하는 습관을 먼저 만들어주는 게 더 중요합니다. 이 글에서는 여도초등학교 저학년 학부모님들이 상담에서 자주 이야기하는 고민을 바탕으로, 화상과외로 학습습관을 자연스럽게 잡아주는 방법을 정리해봤어요.</p>
    <h2>저학년 학습습관, 학습량보다 태도가 먼저예요</h2>
    <p>저학년 아이를 둔 학부모님들이 가장 많이 하는 실수 중 하나는, 학습습관을 잡아준다는 명목으로 문제집이나 학습지 양을 늘리는 거예요. 하지만 이 시기에 진짜 중요한 건 학습량이 아니라 정해진 시간에 앉아서 집중하는 태도예요. 여도초등학교 저학년 학생들을 상담해보면, 이미 앉아 있는 습관 자체가 잡혀 있는 아이는 이후 학습 내용을 늘려가는 게 훨씬 수월한 반면, 습관이 안 잡힌 상태에서 양만 늘리면 오히려 공부에 대한 거부감이 커지는 경우가 많아요. <strong>하루 20~30분이라도 정해진 시간에 꾸준히 앉는 습관이, 나중에 학습량을 늘릴 때 훨씬 큰 힘이 됩니다.</strong> 화상과외에서는 저학년 학생에게 처음부터 많은 분량을 주기보다, 정해진 시간 동안 집중해서 마무리하는 경험을 반복해서 만들어주는 데 집중하고 있어요. 이 과정에서 아이가 스스로 해냈다는 성취감을 느끼는 게 습관 형성에 큰 역할을 합니다. 예를 들어 매일 같은 시간에 책상 앞에 앉는 것부터 시작해보는 것도 좋은 방법이에요. 처음에는 그 시간에 앉아만 있어도 괜찮다고 생각하고 시작하면, 아이가 부담 없이 습관을 만들어갈 수 있어요. 여도초등학교 저학년 학생들을 상담해보면, 학습량 자체보다 이 '앉는 습관'이 먼저 자리 잡은 아이들이 이후 학습 내용을 늘려갈 때 훨씬 수월하게 적응하는 걸 자주 확인합니다. 처음부터 완벽하게 습관을 만들려고 욕심내기보다, 하루하루 조금씩 앉는 시간을 늘려가는 방식이 저학년 아이들에게는 훨씬 자연스럽습니다.</p>
    <h2>1:1 수업이 저학년 습관 형성에 유리한 이유</h2>
    <p>저학년 아이들은 집단 수업에서 집중력을 유지하기가 상대적으로 어려운 경우가 많아요. 옆자리 친구가 다른 걸 하고 있으면 시선이 분산되기 쉽고, 자기 속도보다 빠르거나 느린 진도에 맞춰야 하는 부담도 있어요. 1:1로 진행되는 화상과외는 이런 부분에서 확실한 장점이 있어요. 선생님이 아이의 반응을 하나하나 살피면서 진도를 조절할 수 있고, 아이가 이해했는지 바로바로 확인하면서 넘어갈 수 있기 때문에 불필요하게 헤매는 시간이 줄어들어요. 여도초등학교 저학년 학생을 지도해본 경험이 있는 선생님이라면, 이 나이대 아이들이 어떤 부분에서 집중력을 잃기 쉬운지도 잘 파악하고 있어서, 놀이 요소를 적절히 섞어가며 수업을 진행할 수 있어요. <strong>아이가 편안한 집에서 익숙한 환경으로 수업을 받는다는 점</strong>도 저학년 아이들의 긴장을 줄여주는 데 도움이 됩니다. 또한 저학년 아이들은 선생님과의 관계에서 안정감을 느낄 때 학습에 대한 거부감이 훨씬 줄어들어요. 매번 새로운 사람을 만나기보다, 같은 선생님과 꾸준히 만나면서 익숙해지는 과정 자체가 학습 습관 형성에 긍정적인 영향을 줍니다. 화상과외는 정해진 선생님과 계속 만나는 구조이기 때문에, 이런 관계 형성이 자연스럽게 이루어진다는 것도 저학년에게 유리한 부분이에요. 아이가 선생님을 편안하게 느끼기 시작하면, 모르는 것을 묻는 것도 훨씬 자연스러워지고, 이는 학습 습관 전반에 긍정적인 영향을 줍니다. 이런 신뢰 관계가 쌓이기까지 보통 몇 주 정도 걸리는데, 이 시간을 조급해하지 않고 기다려주는 것도 부모님의 역할입니다.</p>
    <h2>화상과외로 학습습관을 잡아주는 구체적인 방법</h2>
    <p>학습습관은 하루아침에 만들어지지 않기 때문에, 꾸준히 반복되는 루틴이 중요해요. 화상과외에서는 매주 같은 요일, 같은 시간에 수업을 진행하면서 아이가 그 시간을 자연스럽게 학습 시간으로 받아들이도록 도와줘요. 수업 시작 전에 지난 시간 배운 내용을 짧게 확인하고, 수업이 끝날 때는 오늘 배운 내용을 스스로 한 문장으로 정리해보게 하는 것만으로도 학습에 대한 주도성이 생겨요. 여도초등학교 저학년 학생이라면 아직 스스로 계획을 세우는 게 어려운 시기이기 때문에, 선생님이 매 수업마다 작은 목표를 제시하고 그걸 달성하는 경험을 반복해서 쌓아주는 방식이 효과적이에요. <strong>부모님이 옆에서 강요하지 않아도, 정해진 시간에 선생님과의 약속이 있다는 사실만으로 아이가 스스로 준비하는 습관이 생기는 경우가 많습니다.</strong> 예를 들어 수업 시작 전 짧게 오늘의 목표를 이야기하고, 수업이 끝난 뒤 그 목표를 달성했는지 함께 확인하는 방식을 반복하면, 아이가 스스로 목표를 인식하는 힘이 자라나요. 이런 작은 반복이 쌓이면, 나중에 학년이 올라가서 스스로 계획을 세워야 하는 시기가 왔을 때도 훨씬 수월하게 적응할 수 있습니다. 처음에는 선생님이 목표를 제시해주지만, 점차 아이에게 어떤 목표를 세우고 싶은지 물어보는 방식으로 자연스럽게 주도성을 넘겨주는 것도 좋은 방법이에요. 이런 작은 성취 경험이 쌓이면, 아이는 공부를 시켜서 하는 일이 아니라 스스로 해내는 일로 받아들이기 시작합니다.</p>
    <h2>학습습관을 잡기 전 꼭 확인해야 할 3가지</h2>
    <p>첫째, 아이가 하루 중 가장 집중이 잘 되는 시간대가 언제인지 파악해보세요. 저학년일수록 시간대에 따라 집중력 차이가 크게 나는 경우가 많아요. 둘째, 학습 시간을 너무 길게 잡지 마세요. 저학년은 20~30분 정도의 짧고 반복적인 학습이 오히려 더 효과적입니다. 셋째, 아이가 스스로 해냈다는 느낌을 받을 수 있도록 작은 목표부터 설정해주세요. 처음부터 큰 목표를 잡으면 아이가 부담을 느끼고 오히려 학습을 피하게 될 수 있어요. 이 세 가지를 염두에 두고 습관을 잡아가면, 학년이 올라갈수록 학습량을 늘려가는 과정이 훨씬 자연스러워져요. <strong>저학년 시기의 학습습관은 결과보다 과정에서 만들어진다는 점을 기억해주세요.</strong> 넷째로, 학습 습관을 잡는 초반에는 결과보다 과정을 칭찬해주는 게 중요해요. 정답을 맞혔는지보다, 정해진 시간 동안 집중해서 앉아 있었다는 사실 자체를 인정해주는 게 아이의 동기를 유지하는 데 훨씬 효과적입니다. 이와 함께, 부모님도 아이의 습관 형성 과정을 너무 조급하게 평가하지 않는 마음가짐이 필요해요. 저학년 습관은 몇 주 안에 완성되는 게 아니라 몇 달에 걸쳐 서서히 자리 잡는다는 걸 기억해주시면 좋겠습니다. 다섯째로 굳이 항목을 늘리자면, 아이의 컨디션이 좋지 않은 날은 억지로 진행하기보다 과감하게 쉬어가는 것도 장기적으로는 습관 형성에 도움이 됩니다. 이렇게 유연하게 접근할수록, 아이는 학습을 억지로 견뎌야 하는 일이 아니라 자연스러운 일상으로 받아들이게 됩니다.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면, 저학년 아이가 책상에 앉는 것 자체를 힘들어해서 걱정이라는 학부모님들을 자주 만나요. 한 학생은 처음에는 10분도 앉아 있기 힘들어했지만, 짧은 시간 동안 확실히 끝낼 수 있는 분량으로 시작하면서 조금씩 앉아 있는 시간을 늘려갈 수 있었어요. 몇 주가 지나면서는 정해진 수업 시간을 스스로 기다리는 모습을 보였다는 이야기를 학부모님이 전해주셨어요. 다른 경우에는 학습지를 풀 때 집중하지 못하고 자꾸 딴생각을 하던 아이가, 1:1로 선생님과 눈을 맞추며 대화하듯 진행하는 수업 방식에서는 훨씬 집중을 잘 유지했다는 사례도 있었어요. <strong>아이마다 맞는 방식이 다르기 때문에, 그 아이에게 맞는 방식을 찾는 게 가장 중요하다는 걸</strong> 이런 상담들을 통해 계속 확인하고 있어요. 또 다른 학부모님은 아이가 화면으로 하는 수업에 잘 적응할지 걱정하셨는데, 막상 시작해보니 오히려 익숙한 집 환경에서 편안하게 수업에 참여하는 모습을 보고 안심하셨다는 이야기를 해주셨어요. 저학년일수록 새로운 환경에 대한 긴장감이 크기 때문에, 집이라는 익숙한 공간에서 수업을 받는다는 것 자체가 생각보다 큰 장점으로 작용하는 경우가 많습니다. 이렇게 편안한 환경에서 시작한 학습 경험이 긍정적으로 쌓이면, 이후 어떤 학습 환경에서도 적응력이 좋아지는 경우가 많다는 것도 함께 말씀드리고 싶은 부분이에요. 저학년 시기에 만들어진 이런 긍정적인 경험은, 학년이 올라가서 학습량이 늘어날 때도 아이가 크게 힘들어하지 않고 적응하는 밑바탕이 되어줍니다.</p>
    <h2>티치핏여수와 함께 학습습관을 잡아보세요</h2>
    <p>티치핏여수는 상담 시 아이의 현재 집중 시간과 성향을 먼저 확인하고, 여도초등학교 같은 학교의 저학년 학생을 지도해본 경험이 있는 선생님을 화상으로 연결해 드려요. 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여하고, 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있습니다. 신청 후 24시간 이내에 담당자가 직접 연락드리고, 학습 진단부터 선생님 추천, 체험 수업까지 순서대로 안내해 드려요. 여도초등학교뿐 아니라 여수 관내 초등학교 54곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교를 알려주시면 그에 맞춰 상담해 드릴게요. 아직 어린 나이라 걱정되는 부분이 많으실 텐데, 상담 시 아이의 성향을 자세히 여쭤보고 그에 맞는 방식을 함께 찾아드리니 편하게 문의해주세요. 저학년 학습습관은 이르다고 미루기보다, 지금부터 천천히 시작하는 게 오히려 아이에게 부담 없는 방법일 수 있습니다.</p>
    <p><strong>Q. 아이가 아직 한글도 익숙하지 않은데 화상수업이 가능할까요?</strong><br>
    네, 상담 시 아이의 현재 수준을 먼저 확인하고 그에 맞는 방식으로 천천히 진행해 드려요.</p>
    <p><strong>Q. 수업 시간은 얼마나 되나요?</strong><br>
    저학년의 경우 보통 30~40분 정도로 짧게 진행하며, 아이의 집중력에 맞춰 조절해 드려요.</p>
    <p><strong>Q. 부모님이 옆에서 함께 봐야 하나요?</strong><br>
    꼭 그렇지는 않아요. 다만 처음 몇 회는 함께 지켜보시면 아이가 더 편안하게 적응할 수 있어요.</p>
    ''',
})

BLOG_POSTS.append({
    "slug": "yeocheon-ms-suhak-gwaoe",
    "title": "여천중학교 수학 화상과외, 성적이 안 오르는 진짜 이유",
    "date": "2026-09-24",
    "category": "중등 수학과외",
    "teaser": "여천중학교 학생 기준으로, 수학 성적이 오르지 않을 때 확인해야 할 진짜 이유를 화상과외 관점에서 정리했어요.",
    "body": '''
    <p>여천중학교에 다니는 자녀를 둔 학부모님 중에는, 아이가 수학 문제집을 꽤 많이 풀었는데도 성적이 오르지 않아서 답답하다고 말씀하시는 분들이 많아요. 분명 시간을 들여 공부하는데 왜 결과로 이어지지 않는지 이해하기 어려우실 텐데, 사실 수학은 단순히 문제를 많이 푸는 것만으로는 해결되지 않는 과목이에요. 어디에서 막히는지 정확히 파악하지 못한 채 계속 문제만 풀면, 같은 실수가 반복되는 경우가 많습니다. 이 글에서는 여천중학교 학생들이 상담에서 자주 이야기하는 수학 고민을 바탕으로, 성적이 오르지 않는 진짜 이유와 화상과외로 이를 어떻게 해결할 수 있는지 정리해봤어요.</p>
    <h2>문제를 많이 푸는 것과 실력이 오르는 건 다른 이야기예요</h2>
    <p>수학 성적이 안 오르는 학생들을 살펴보면, 의외로 문제집을 꽤 많이 풀었는데도 성적이 그대로인 경우가 많아요. 이런 학생들의 공통점은 틀린 문제를 다시 풀어보지 않고 그냥 답만 확인하고 넘어간다는 점이에요. 여천중학교 수학 시험처럼 개념을 응용한 문제가 많이 나오는 경우, 같은 유형의 문제를 여러 번 틀리면서도 왜 틀렸는지 정확히 짚지 않으면 다음 시험에서도 똑같은 실수를 반복하게 됩니다. <strong>문제를 많이 푸는 것보다 틀린 문제를 제대로 분석하는 게 훨씬 중요합니다.</strong> 화상과외로 상담을 진행하다 보면, 학생이 틀린 문제를 다시 풀어보게 했을 때 스스로 실수를 찾아내는 경우와 전혀 이유를 모르는 경우로 나뉘는데, 후자의 경우 개념 자체가 부족한 것이기 때문에 문제 풀이보다 개념 복습이 먼저 필요해요. 이 구분을 하지 않고 무작정 문제집만 늘리면 시간은 쓰는데 실력은 그대로인 상황이 계속됩니다. 특히 오답노트를 만들 때도 그냥 정답만 옮겨 적기보다, 왜 이 부분에서 틀렸는지 본인의 언어로 한 줄이라도 적어보는 습관이 중요해요. 이 과정이 없으면 오답노트를 만들어도 나중에 다시 펼쳐봤을 때 왜 이 문제를 적어뒀는지조차 기억하지 못하는 경우가 많거든요. 여천중학교 학생들을 지도해보면, 이 습관이 있는 학생과 없는 학생의 성적 변화 속도가 눈에 띄게 다르다는 걸 자주 확인합니다. 틀린 문제를 분석하는 습관은 처음엔 번거롭게 느껴지지만, 몇 주만 반복해도 같은 실수가 눈에 띄게 줄어드는 걸 체감할 수 있어요.</p>
    <h2>개념 이해와 연산 실수, 원인을 구분해야 해요</h2>
    <p>수학에서 틀리는 이유는 크게 개념을 몰라서 틀리는 경우와, 개념은 알지만 계산 과정에서 실수하는 경우로 나뉘어요. 이 두 가지는 완전히 다른 해결 방법이 필요한데, 많은 학생들이 이를 구분하지 않고 똑같은 방식으로 접근해서 시간을 낭비하는 경우가 많아요. 개념을 모르는 경우라면 그 단원의 기본 개념부터 다시 짚어야 하고, 연산 실수가 반복되는 경우라면 풀이 과정을 꼼꼼히 적는 습관을 만들어야 해요. 여천중학교 학생들을 지도해보면, 특히 방정식이나 함수 단원에서 개념은 이해했지만 문제에 적용하는 과정에서 실수가 반복되는 경우가 많은데, 이럴 때는 풀이 과정을 단계별로 나눠서 확인하는 훈련이 효과적이에요. <strong>내 실수가 어느 단계에서 나오는지 정확히 아는 것</strong>이 수학 실력을 올리는 첫걸음이에요. 화상과외에서는 학생이 문제를 푸는 과정을 화면으로 함께 보면서, 어느 단계에서 실수가 나오는지 실시간으로 짚어줄 수 있어요. 또한 개념을 안다고 생각했는데 실제로 설명해보라고 하면 막히는 경우도 많아요. 이럴 때는 겉으로는 알고 있는 것 같지만 실제로는 절반만 이해한 상태인 거예요. 화상과외에서는 학생에게 개념을 직접 설명해보게 하는 방식으로 이런 '절반만 아는 상태'를 자주 점검하고 있어요. 스스로 설명해보는 과정에서 학생 본인도 어디가 헷갈리는지 다시 깨닫는 경우가 많아서, 이 방식 자체가 좋은 복습 효과를 냅니다. 개념을 말로 설명하는 훈련은 시험에서 서술형 문제를 만났을 때도 큰 도움이 됩니다.</p>
    <h2>화상과외가 수학 학습에 유리한 이유</h2>
    <p>수학은 학생마다 막히는 단원과 이유가 다르기 때문에, 정해진 진도로 진행되는 학원 수업보다 1:1로 그 학생의 문제를 정확히 짚어주는 방식이 더 효과적인 경우가 많아요. 화상과외는 학생이 실제로 문제를 풀어가는 과정을 화면으로 공유하면서, 어디서 막히는지, 어떤 개념이 부족한지를 실시간으로 확인할 수 있어요. 수업이 녹화되기 때문에, 헷갈렸던 풀이 과정을 다시 돌려보면서 복습할 수 있다는 것도 수학처럼 단계적인 이해가 중요한 과목에서는 큰 도움이 됩니다. 여수 지역 안에서 수학을 전문적으로 봐줄 수 있는 선생님을 구하기 어려운 경우가 많은데, 화상과외라면 지역 제약 없이 훨씬 넓은 범위에서 맞는 선생님을 연결받을 수 있어요. <strong>이동 시간이 없어 저녁 시간대에도 유연하게 수업을 잡을 수 있다는 점</strong>도 중학생들에게는 실질적으로 체감되는 장점이에요. 화상과외는 또한 학생이 이전 수업에서 어떤 실수를 했는지 선생님이 계속 기억하고 있다가, 비슷한 유형이 다시 나왔을 때 바로 짚어줄 수 있다는 장점도 있어요. 학원처럼 여러 학생을 동시에 관리해야 하는 상황이 아니기 때문에, 그 학생만의 실수 패턴을 꾸준히 추적하면서 교정해줄 수 있죠. 이런 지속적인 관찰이 수학처럼 반복된 실수가 성적을 가르는 과목에서는 특히 큰 효과를 냅니다. 실수 패턴을 스스로 인지하게 되기까지는 시간이 걸리지만, 한번 인지하고 나면 이후에는 스스로 점검하는 힘이 생깁니다. 이런 자기 점검 능력은 수학뿐 아니라 다른 과목 공부에도 자연스럽게 이어지는 경우가 많습니다.</p>
    <h2>수학 성적을 올리기 전 꼭 확인해야 할 3가지</h2>
    <p>첫째, 최근 틀린 문제들을 다시 꺼내서 왜 틀렸는지 스스로 설명할 수 있는지 확인해보세요. 설명하지 못한다면 개념이 부족한 것이고, 알면서도 실수했다면 풀이 습관을 고쳐야 해요. 둘째, 풀이 과정을 얼마나 꼼꼼히 적는지 살펴보세요. 과정을 생략하고 암산으로 넘어가는 습관이 있다면 연산 실수가 반복될 가능성이 높아요. 셋째, 새로운 단원을 배우기 전에 이전 단원의 개념이 탄탄한지 점검하세요. 수학은 단원끼리 연결되어 있어서 이전 개념이 부족하면 다음 단원도 어려워지는 경우가 많습니다. 이 세 가지를 확인하지 않고 무작정 문제만 풀면, 시간은 들이는데 성적은 오르지 않는 상황이 계속될 수 있어요. <strong>수학은 양보다 원인 파악이 먼저인 과목이라는 점을 기억해주세요.</strong> 넷째로, 시험 직전에는 새로운 문제를 많이 푸는 것보다 이미 틀렸던 문제를 다시 풀어보는 데 시간을 더 써보세요. 새로운 문제에서 또 다른 실수를 발견하는 것보다, 이미 알고 있는 약점을 확실히 보완하는 게 점수 향상에 더 직접적으로 연결되는 경우가 많습니다. 이 네 가지를 시험 3주 전부터 단계적으로 챙겨두면, 막판에 몰아서 공부하지 않아도 안정적으로 준비할 수 있어요. 이 네 가지를 매번 시험마다 반복해서 체크하다 보면, 점차 스스로도 어디에 시간을 써야 할지 감을 잡아가게 됩니다. 처음 한두 번은 선생님의 도움을 받아 체크하더라도, 이후에는 이 과정 자체가 학생의 공부 습관으로 자리 잡는 경우가 많습니다.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면, 수학 문제집을 여러 권 풀었는데도 성적이 오르지 않아 답답해하시는 학부모님들을 자주 만나요. 한 학생은 방정식 단원에서 개념은 이해하고 있었지만, 문제를 옮겨 적는 과정에서 부호를 자주 틀리는 습관이 있었어요. 이 부분을 파악한 뒤로는 풀이 과정을 한 줄씩 확인하는 훈련을 반복하면서, 같은 실수가 눈에 띄게 줄어들었다는 이야기를 들었어요. 다른 학생은 함수 단원 자체를 어려워했는데, 알고 보니 이전 학년의 비례 개념이 부족했던 경우였어요. 이전 개념을 먼저 복습한 뒤 함수 단원으로 넘어가면서 훨씬 수월하게 이해할 수 있게 됐다고 해요. <strong>결국 어디서 막히는지 정확히 찾아내는 게 성적 향상의 시작점</strong>이라는 걸 이런 사례들을 통해 계속 확인하고 있어요. 또 다른 학생은 도형 단원에서 자꾸 어려움을 겪었는데, 알고 보니 기본적인 도형의 성질을 암기가 아니라 이해로 접근하지 못하고 있었던 경우였어요. 도형을 직접 그려보고 성질을 눈으로 확인하는 방식으로 접근을 바꾸면서, 이전보다 훨씬 수월하게 문제를 풀 수 있게 됐다는 이야기를 들었습니다. 이렇게 같은 수학이라도 단원마다 필요한 접근 방식이 다르다는 걸 확인할 때마다, 개별 진단이 왜 중요한지 다시 느끼게 됩니다. 같은 문제집을 풀어도 학생마다 막히는 지점이 다르기 때문에, 정해진 커리큘럼보다 개별 진단이 우선되어야 한다는 걸 매번 새삼 확인하게 됩니다. 이런 사례들을 볼 때마다, 수학은 결국 그 학생만의 막힌 지점을 찾아내는 게 가장 빠른 지름길이라는 걸 다시 느낍니다.</p>
    <h2>티치핏여수와 함께 수학 성적을 올려보세요</h2>
    <p>티치핏여수는 상담 시 최근 시험지와 틀린 문제를 먼저 확인하고, 개념 부족인지 연산 실수인지부터 구분해서 그에 맞는 선생님을 화상으로 연결해 드려요. 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여하고, 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있습니다. 신청 후 24시간 이내에 담당자가 직접 연락드리고, 학습 진단부터 선생님 추천, 체험 수업까지 순서대로 안내해 드려요. 여천중학교뿐 아니라 여수 관내 중학교 24곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교를 알려주시면 그에 맞춰 상담해 드릴게요. 수학은 특히 막힌 부분을 방치하면 다음 단원까지 영향을 주는 과목이니, 지금 어려움을 느끼고 있다면 미루지 말고 편하게 상담을 신청해보세요. 막연히 문제집을 더 사서 풀리기보다, 먼저 정확한 진단부터 받아보시는 걸 추천드립니다. 상담은 부담 없이 진행되니 편하게 문의해주세요.</p>
    <p><strong>Q. 수학 특정 단원만 집중적으로 봐줄 수 있나요?</strong><br>
    네, 상담 시 취약한 단원을 먼저 확인하고 그 부분에 집중된 수업으로 진행할 수 있어요.</p>
    <p><strong>Q. 연산 실수가 많은 편인데 도움이 될까요?</strong><br>
    네, 풀이 과정을 단계별로 확인하면서 실수가 반복되는 지점을 함께 찾아드려요.</p>
    <p><strong>Q. 여천중학교 시험 스타일도 반영해서 준비할 수 있나요?</strong><br>
    네, 상담 시 최근 시험지를 확인하고 학교 시험 스타일에 맞춰 준비 방향을 안내해 드려요.</p>
    ''',
})

BLOG_POSTS.append({
    "slug": "hwayang-ms-yeongeo-naeshin",
    "title": "화양중학교 영어 내신 화상과외, 서술형 대비까지 챙기는 법",
    "date": "2026-09-24",
    "category": "중등 영어내신",
    "teaser": "화양중학교 학생 기준으로, 영어 내신에서 서술형까지 놓치지 않고 챙기는 방법을 정리했어요.",
    "body": '''
    <p>화양중학교에 다니는 자녀를 둔 학부모님 중에는, 아이가 영어 단어와 문법은 어느 정도 알고 있는데도 서술형에서 계속 감점을 받아서 고민이라는 분들이 많아요. 객관식은 곧잘 맞히는데 정작 직접 문장을 써야 하는 서술형에서 점수를 잃는 경우, 무엇부터 보완해야 할지 막막하게 느껴지실 거예요. 중학교 영어 내신은 학교마다 서술형 비중과 채점 기준이 조금씩 다르기 때문에, 우리 학교 시험 스타일을 정확히 알고 준비하는 게 중요합니다. 이 글에서는 화양중학교 학생들이 상담에서 자주 이야기하는 영어 내신 고민을 바탕으로, 서술형까지 놓치지 않고 챙기는 방법을 화상과외 관점에서 정리해봤어요.</p>
    <h2>영어 서술형, 문법을 안다고 잘 쓰는 건 아니에요</h2>
    <p>영어 서술형에서 감점을 받는 학생들을 보면, 의외로 문법 자체는 잘 알고 있는 경우가 많아요. 문제는 알고 있는 문법을 실제 문장으로 정확하게 조합해서 쓰는 연습이 부족하다는 점이에요. 화양중학교 영어 시험에서 서술형 비중이 있다면, 단순히 단어를 외우고 문법 문제를 푸는 것만으로는 충분하지 않아요. <strong>서술형은 아는 것과 정확하게 표현하는 것 사이의 간극을 줄이는 연습이 핵심입니다.</strong> 예를 들어 시제를 정확히 알고 있어도 실제 문장에서 동사 변형을 놓치거나, 관사나 전치사를 빠뜨리는 실수가 반복되는 경우가 많아요. 화상과외로 상담을 진행하다 보면, 학생이 직접 문장을 써보게 했을 때 어떤 부분에서 실수가 반복되는지 패턴이 뚜렷하게 보이는 경우가 많은데, 이 패턴을 찾아서 집중적으로 교정하는 것이 서술형 점수를 올리는 가장 빠른 방법이에요. 예를 들어 시제를 정확히 알고 있는 학생도, 실제 문장을 쓸 때 주어와 동사를 일치시키는 부분에서 자주 실수해요. 이런 실수는 문법 문제집을 백 번 풀어도 잘 고쳐지지 않는 경우가 많은데, 직접 문장을 써보고 즉시 첨삭을 받는 과정을 반복해야 조금씩 줄어들어요. 화양중학교 학생들을 지도해보면, 이런 실수 패턴이 학생마다 상당히 다르다는 걸 확인할 수 있어서, 그 학생만의 패턴을 찾아 집중적으로 교정하는 게 효율적입니다. 문법 문제집을 아무리 풀어도 서술형 점수가 오르지 않는다면, 바로 이런 표현 습관의 문제일 가능성이 높습니다.</p>
    <h2>학교 교과서 지문을 기반으로 준비해야 해요</h2>
    <p>중학교 영어 내신은 대부분 교과서 지문을 기반으로 서술형 문제가 출제되는 경우가 많아요. 그래서 일반적인 문법 문제집만 풀기보다는, 교과서에 나온 문장 구조와 표현을 정확히 익히는 게 훨씬 효율적입니다. 화양중학교 영어 교과서에 나온 주요 문장을 변형해서 서술하는 연습을 반복하면, 실제 시험에서 비슷한 유형이 나왔을 때 훨씬 자신 있게 답을 쓸 수 있어요. 또한 서술형은 부분 점수가 있는 경우가 많기 때문에, 정답을 정확히 모르더라도 최대한 근접하게 쓰는 전략도 필요해요. <strong>교과서 본문을 통째로 외우는 것보다, 문장 구조를 이해하고 스스로 변형해서 쓸 수 있는 연습이 훨씬 효과적입니다.</strong> 화상과외에서는 상담 시 학교 교과서와 최근 시험지를 함께 확인하고, 그 학교의 서술형 출제 패턴에 맞춰 연습 문제를 구성해 드리고 있어요. 또한 교과서에 나온 문장을 단순히 암기하는 것과, 그 문장의 구조를 이해하고 다른 상황에 맞게 바꿔 쓸 수 있는 것은 완전히 다른 능력이에요. 시험에서는 교과서 문장을 살짝 변형해서 출제하는 경우가 많기 때문에, 구조를 이해하지 못하고 통째로 외운 학생은 변형된 문제에서 당황하기 쉬워요. 화상과외에서는 교과서 문장을 다양한 상황으로 바꿔서 써보는 연습을 반복하면서, 이런 변형 문제에도 유연하게 대응할 수 있도록 돕고 있습니다. 이런 변형 훈련이 쌓이면, 처음 보는 문장이 나와도 당황하지 않고 배운 구조를 적용해서 풀어낼 수 있는 힘이 생깁니다.</p>
    <h2>화상과외가 영어 서술형 대비에 유리한 이유</h2>
    <p>서술형은 직접 써보고 피드백을 받는 과정이 반복되어야 실력이 쌓이는 영역이에요. 화상과외는 학생이 쓴 문장을 화면으로 공유하면서 실시간으로 첨삭받을 수 있다는 점에서 확실한 장점이 있어요. 학원처럼 여러 학생을 한 번에 봐야 하는 상황이 아니기 때문에, 그 학생이 반복하는 실수 패턴을 선생님이 정확히 기억하고 다음 수업에서 다시 확인해줄 수 있어요. 화양중학교 학생을 지도해본 경험이 있거나 비슷한 학교의 서술형 스타일을 아는 선생님이라면, 어떤 유형의 문장이 자주 출제되는지도 함께 안내받을 수 있어요. <strong>수업이 녹화되기 때문에 첨삭받은 내용을 다시 돌려보면서 복습할 수 있다는 것</strong>도 서술형처럼 반복 교정이 필요한 영역에서는 큰 도움이 됩니다. 화상과외는 또한 학생이 쓴 문장을 실시간으로 화면에 띄워두고, 어느 부분이 틀렸는지 함께 보면서 바로 수정할 수 있다는 장점이 있어요. 이렇게 즉각적인 피드백이 반복되면, 학생 스스로도 자신이 자주 하는 실수 유형을 점점 더 빨리 알아차리게 됩니다. 학원에서 여러 학생의 답안을 한꺼번에 첨삭받는 것과 비교하면, 이런 즉시성이 실력 향상 속도에 꽤 큰 차이를 만들어냅니다. 첨삭을 받은 직후 바로 같은 유형을 한 번 더 써보는 것도, 실수를 진짜로 고치는 데 큰 도움이 되는 방법이에요. 이렇게 배운 것을 바로 적용해보는 반복이 쌓이면, 같은 실수가 눈에 띄게 줄어듭니다. 이런 반복이 몇 주간 쌓이면, 서술형 답안을 쓸 때 스스로 실수를 미리 알아채고 고치는 힘도 생겨납니다. 화상 수업이라고 해서 첨삭의 정확도가 떨어지는 건 아니라는 점도 함께 안심하셔도 좋은 부분이에요.</p>
    <h2>영어 내신을 준비하기 전 꼭 확인해야 할 3가지</h2>
    <p>첫째, 최근 서술형 시험지에서 감점된 부분을 다시 살펴보고, 어떤 문법 요소에서 실수가 반복되는지 확인해보세요. 둘째, 교과서 본문에 나온 주요 문장 구조를 스스로 변형해서 써볼 수 있는지 점검해보세요. 셋째, 시험 직전에는 새로운 문법을 배우기보다 이미 알고 있는 내용을 정확하게 쓰는 연습에 집중하세요. 이 세 가지를 놓치면 아무리 단어를 많이 외워도 서술형에서는 점수가 잘 오르지 않는 경우가 많아요. 화양중학교처럼 서술형 비중이 있는 학교라면, 특히 첫 번째 항목을 꾸준히 체크하는 습관이 중요합니다. <strong>서술형은 벼락치기보다 꾸준한 첨삭이 쌓여야 점수로 이어지는 영역이에요.</strong> 넷째로, 서술형 답안을 쓸 때 문장을 너무 길게 쓰려고 하지 마세요. 짧고 정확한 문장으로 요구된 내용을 정확히 담는 게, 길게 쓰다가 문법 실수를 만드는 것보다 훨씬 안전한 전략이에요. 화양중학교처럼 서술형 채점 기준이 꼼꼼한 학교라면, 화려한 표현보다 정확한 표현이 점수에 더 유리하게 작용하는 경우가 많습니다. 이 네 가지를 시험 전 마지막 점검 리스트로 활용해보시면, 서술형에서 불필요하게 감점되는 상황을 줄일 수 있어요. 시험 직전에는 새로운 문법을 배우기보다, 이 네 가지 기준으로 지금까지 써본 답안을 다시 점검하는 시간을 가져보시길 추천드립니다. 이렇게 마지막 점검까지 마치고 시험에 들어가면, 아는 내용을 실수로 놓치는 상황을 훨씬 줄일 수 있습니다. 사소해 보이는 점검이지만 실제 점수 차이는 꽤 크게 벌어집니다.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면, 문법 문제는 잘 푸는데 서술형에서만 점수를 잃어서 답답해하시는 학부모님들을 자주 만나요. 한 학생은 시제 문법 자체는 정확히 알고 있었지만, 실제 문장을 쓸 때 3인칭 단수 동사 변형을 자주 빠뜨리는 실수가 있었어요. 이 부분을 파악한 뒤로는 문장을 쓸 때마다 동사 부분을 한 번 더 확인하는 습관을 연습하면서, 같은 실수가 눈에 띄게 줄어들었다는 이야기를 들었어요. 다른 학생은 교과서 본문을 그대로 외우기만 했는데, 문장을 살짝 변형한 문제가 나오자 전혀 다른 답을 쓰는 경우였어요. 이후 문장 구조를 이해하고 스스로 변형해보는 연습을 반복하면서, 변형된 문제에도 유연하게 대응할 수 있게 됐다고 해요. <strong>결국 아는 것과 쓸 수 있는 것의 차이를 좁히는 게 핵심</strong>이라는 걸 이런 사례들을 통해 계속 확인하고 있어요. 또 다른 학생은 단어와 문법을 모두 알고 있었지만, 문장을 쓸 때마다 지나치게 긴장해서 알던 것도 놓치는 경우였어요. 이런 학생에게는 평소 수업 시간에 실제 시험과 비슷한 긴장감을 조금씩 경험하게 하면서, 긴장 상황에서도 아는 것을 정확히 꺼낼 수 있도록 연습시키는 과정이 도움이 됐어요. 결국 서술형은 지식과 표현력뿐 아니라, 실전에서 안정적으로 꺼내는 훈련까지 함께 필요한 영역이라는 걸 확인하게 됩니다. 이런 사례들을 통해, 서술형 대비는 단순히 문법을 많이 아는 것을 넘어서는 종합적인 훈련이라는 걸 계속 확인하고 있습니다. 한 번에 완벽해지길 기대하기보다, 매주 조금씩 개선해나가는 과정으로 받아들이면 훨씬 부담 없이 이어갈 수 있어요. 꾸준함이 쌓이면 서술형은 더 이상 부담스러운 영역이 아니라 오히려 자신 있는 영역으로 바뀔 수 있습니다.</p>
    <h2>티치핏여수와 함께 영어 서술형을 준비해보세요</h2>
    <p>티치핏여수는 상담 시 최근 서술형 시험지를 먼저 확인하고, 화양중학교 같은 학교의 서술형 출제 패턴을 고려해서 선생님을 화상으로 연결해 드려요. 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여하고, 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있습니다. 신청 후 24시간 이내에 담당자가 직접 연락드리고, 학습 진단부터 선생님 추천, 체험 수업까지 순서대로 안내해 드려요. 화양중학교뿐 아니라 여수 관내 중학교 24곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교를 알려주시면 그에 맞춰 상담해 드릴게요. 서술형 감점이 반복된다면 막연히 더 열심히 외우기보다, 정확히 어떤 부분에서 감점되는지부터 진단받는 게 우선이니 편하게 상담을 신청해보세요. 지금 감점되는 부분을 정확히 짚어드릴 테니, 부담 갖지 마시고 편하게 문의해주시면 좋겠습니다. 최근 서술형 시험지 한 장만 보내주셔도 대략적인 원인을 먼저 짚어드릴 수 있어요.</p>
    <p><strong>Q. 서술형만 따로 집중해서 봐줄 수 있나요?</strong><br>
    네, 상담 시 감점 패턴을 먼저 확인하고 서술형 첨삭에 집중된 수업으로 진행할 수 있어요.</p>
    <p><strong>Q. 교과서 본문을 기반으로 준비해주시나요?</strong><br>
    네, 학교 교과서와 최근 시험지를 확인해서 그에 맞춰 연습 문제를 구성해 드려요.</p>
    <p><strong>Q. 화양중학교 시험 스타일도 알고 계신가요?</strong><br>
    상담 시 최근 시험지를 함께 확인하면서 학교별 출제 스타일에 맞춰 안내해 드려요.</p>
    ''',
})

BLOG_POSTS.append({
    "slug": "yeosugongeob-hs-gimalgosa",
    "title": "여수공업고등학교 기말고사 화상과외, 전공 병행하며 내신 챙기는 법",
    "date": "2026-09-24",
    "category": "고등 기말고사",
    "teaser": "여수공업고등학교 학생 기준으로, 전공 실습과 병행하면서 기말고사 내신을 챙기는 방법을 정리했어요.",
    "body": '''
    <p>여수공업고등학교에 다니는 자녀를 둔 학부모님이라면, 전공 실습과 이론 수업을 함께 챙겨야 하는 상황에서 기말고사 준비 시간이 부족하다고 느끼실 때가 많을 거예요. 특성화고나 공업고등학교는 일반고와 달리 전공 실습 시간이 상당 부분을 차지하기 때문에, 순수하게 내신 공부에만 쓸 수 있는 시간이 상대적으로 적은 편이에요. 그렇다고 내신을 소홀히 할 수는 없는데, 취업이나 진학 모두에서 내신 성적이 중요한 자료로 쓰이는 경우가 많기 때문이에요. 이 글에서는 여수공업고등학교 학생들이 상담에서 자주 이야기하는 고민을 바탕으로, 전공과 내신을 함께 챙기는 방법을 화상과외 관점에서 정리해봤어요.</p>
    <h2>시간이 부족할수록 우선순위가 더 중요해요</h2>
    <p>전공 실습 시간이 많은 학교일수록, 남은 시간을 어떻게 쓰느냐가 성적을 결정짓는 핵심이 돼요. 여수공업고등학교처럼 이론 과목과 전공 과목이 함께 있는 경우, 모든 과목을 똑같은 비중으로 준비하기보다 내신에서 비중이 큰 과목이나 취약한 과목에 시간을 더 배분하는 게 효율적입니다. <strong>시간이 부족한 상황에서는 이것저것 다 하려는 것보다, 정말 필요한 것부터 확실히 끝내는 전략이 훨씬 유리해요.</strong> 실습 시간에는 이론 공부를 하기 어렵기 때문에, 남은 저녁 시간을 어떻게 배분할지 미리 계획을 세워두는 게 중요합니다. 화상과외로 상담을 진행하다 보면, 학생의 시간표를 함께 확인하면서 실습이 많은 날과 상대적으로 여유 있는 날을 구분해서, 여유 있는 날에 집중적으로 이론 과목을 보완하는 방식으로 계획을 세우는 경우가 많아요. 이렇게 시간을 구조화하는 것만으로도 학습 효율이 눈에 띄게 달라집니다. 예를 들어 이론 과목 중에서도 자격증 취득과 연계된 과목이라면 조금 더 시간을 투자할 가치가 있고, 상대적으로 비중이 적은 과목은 최소한의 개념만 확실히 챙기는 식으로 구분해보는 것도 방법이에요. 여수공업고등학교 학생들을 상담해보면, 이런 구분 없이 눈앞에 보이는 것부터 무작정 시작하다가 시간에 쫓기는 경우가 많습니다. 우선순위 없이 시간을 쓰면 결국 시험 직전에 가장 중요한 과목을 제대로 못 보는 상황이 반복되기 쉬워요. 그래서 계획 단계에서부터 과목별 비중을 명확히 정해두는 게 실습이 많은 학교일수록 더 중요합니다.</p>
    <h2>이동 시간 없이 저녁에 바로 수업할 수 있어야 해요</h2>
    <p>실습 위주의 학교 생활을 하는 학생들은 하교 시간이 늦거나 체력적으로 지쳐 있는 경우가 많아요. 이런 상황에서 학원까지 이동하는 시간과 체력을 쓰는 것 자체가 부담이 될 수 있어요. 화상과외는 이 부분에서 확실한 장점이 있어요. 집에서 바로 수업을 받을 수 있기 때문에, 이동 시간과 체력 소모 없이 순수하게 학습에만 시간을 쓸 수 있어요. 여수공업고등학교 학생을 지도해본 경험이 있는 선생님이라면, 실습과 이론을 병행하는 학생들의 상황을 잘 이해하고 있어서, 무리하게 학습량을 요구하지 않고 현실적인 계획을 함께 세워줄 수 있어요. <strong>수업이 녹화되기 때문에 실습으로 피곤한 날 놓친 부분을 나중에 다시 확인할 수 있다는 것</strong>도 실질적으로 큰 도움이 되는 부분이에요. 또한 실습으로 하루를 보내고 나면 체력적으로 많이 지쳐 있는 경우가 많은데, 이런 상태에서 무리하게 학원까지 이동하면 수업에 제대로 집중하기 어려운 경우가 많아요. 화상과외라면 집에서 잠시 쉬었다가 바로 수업에 들어갈 수 있기 때문에, 체력 소모를 최소화하면서도 학습 흐름을 이어갈 수 있어요. 이런 부분이 실습 중심 학교 생활을 하는 학생들에게는 생각보다 큰 차이로 느껴집니다. 특히 수업이 끝난 뒤 바로 씻고 쉴 수 있다는 점도, 체력적으로 지친 실습 위주 학생들에게는 은근히 큰 심리적 여유를 줍니다. 이런 작은 차이들이 쌓이면서 장기적으로는 학습을 꾸준히 이어갈 수 있는 힘이 됩니다.</p>
    <h2>이론 과목과 실습 과목의 학습 밸런스를 맞추는 법</h2>
    <p>공업고등학교는 이론 내신뿐 아니라 실습 평가도 성적에 함께 반영되는 경우가 많아서, 두 영역을 어떻게 균형 있게 챙길지가 중요한 고민거리예요. 실습 평가는 보통 정해진 절차와 안전 수칙을 얼마나 정확히 지키는지가 관건이기 때문에, 이론 공부와는 전혀 다른 방식으로 준비해야 해요. 반면 이론 내신은 개념 이해와 서술형 대비가 핵심이라, 실습에 쏟는 에너지와는 별도로 시간을 확보해둬야 합니다. 여수공업고등학교 학생들을 상담해보면, 실습에 자신 있는 학생일수록 오히려 이론 공부를 소홀히 하는 경우가 많은데, 이론 내신이 전체 성적에서 차지하는 비중을 놓치면 나중에 후회하는 경우가 많아요. 실습 점수가 아무리 좋아도 이론 내신이 크게 낮으면 전체 평균이 흔들릴 수 있기 때문에, 두 영역을 동시에 챙기는 습관이 처음부터 필요합니다. <strong>실습으로 체력이 소진된 날은 무리하게 이론 공부를 몰아넣지 말고, 짧게라도 꾸준히 복습하는 방식으로 접근하는 게 현실적입니다.</strong> 화상과외에서는 학생의 실습 스케줄을 고려해서, 체력이 남아 있는 날과 부족한 날에 맞춰 학습 강도를 다르게 조절해 드리고 있어요. 이렇게 유연하게 조절하는 것만으로도 번아웃 없이 학기를 끝까지 관리할 수 있게 됩니다. 실습과 이론을 모두 잘 챙기려고 무리하게 애쓰기보다, 상황에 맞춰 강약을 조절하는 게 결국 더 오래, 더 안정적으로 성적을 유지하는 방법이에요. 이런 유연함이 특성화고 학생들에게는 특히 필요한 부분입니다. 매주 똑같은 강도로 밀어붙이기보다, 그 주의 실습 일정에 맞춰 학습 강도를 조절하는 것이 장기적으로 훨씬 지속 가능한 방법이라는 걸 여러 학생들을 통해 확인하고 있습니다.</p>
    <h2>기말고사 전 꼭 확인해야 할 3가지</h2>
    <p>첫째, 이론 과목 중 내신 비중이 큰 과목부터 우선순위를 정하세요. 모든 과목을 똑같이 준비하기엔 시간이 부족한 경우가 많습니다. 둘째, 실습이 없는 날을 파악해서 그날 집중적으로 이론 공부 시간을 확보하세요. 셋째, 시험 범위가 넓다면 전체를 다 보기보다 자주 출제되는 핵심 개념부터 확실히 잡아두세요. 이 세 가지를 미리 계획해두면, 시간이 부족한 상황에서도 훨씬 효율적으로 준비할 수 있어요. 여수공업고등학교처럼 실습 비중이 큰 학교일수록, 계획 없이 시험 기간을 맞이하면 시간에 쫓겨 제대로 준비하지 못하는 경우가 많으니 미리 계획을 세워두는 게 중요합니다. <strong>시간이 부족하다고 포기하기보다, 있는 시간을 최대한 효율적으로 쓰는 게 관건이에요.</strong> 넷째로, 실습 평가와 지필고사 일정이 겹치는 주간이 있다면 미리 파악해서 그 주는 학습량을 조금 줄이고 대신 앞뒤 주에 나눠서 준비하는 방식도 고려해보세요. 무리하게 한 주에 모든 걸 몰아넣으면 오히려 양쪽 다 제대로 준비하지 못하는 상황이 생길 수 있어요. 이 네 가지를 시험 3주 전부터 계획해두면, 실습과 병행하면서도 훨씬 안정적으로 기말고사를 준비할 수 있습니다. 계획을 세울 때는 담임 선생님이나 실습 담당 선생님께 미리 일정을 확인해두는 것도 도움이 됩니다. 학교 일정을 정확히 알고 있어야 그에 맞춰 학습 계획도 현실적으로 짤 수 있기 때문이에요. 이 세 가지를 시험 3주 전부터 하나씩 챙겨두면, 실습으로 바쁜 와중에도 이론 내신을 놓치지 않고 안정적으로 준비할 수 있습니다.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면, 실습 때문에 시간이 부족해서 이론 과목을 거의 포기했다고 말씀하시는 학부모님들을 자주 만나요. 한 학생은 실습이 있는 날은 아예 이론 공부를 하지 않고 있었는데, 상담 후 실습이 없는 날에 몰아서 집중하는 방식으로 계획을 바꾸면서 이론 과목 성적이 안정적으로 유지되기 시작했어요. 다른 학생은 시험 범위가 너무 넓게 느껴져서 어디부터 봐야 할지 막막해했는데, 최근 3개년 기출 유형을 함께 분석하면서 자주 출제되는 핵심 개념을 먼저 정리한 뒤부터는 훨씬 방향을 잡고 공부할 수 있게 됐다고 해요. <strong>시간이 부족한 상황에서도 계획만 제대로 세우면 충분히 따라갈 수 있다는 걸</strong> 이런 사례들을 통해 계속 확인하고 있어요. 또 다른 학생은 실습 평가 준비에 너무 몰두해서 이론 시험 범위를 거의 못 본 채로 시험을 맞이한 경우였는데, 상담 후 실습 평가가 몰린 주간을 미리 파악해서 그 전주에 이론 공부를 앞당겨 마무리하는 방식으로 계획을 조정했어요. 이후에는 실습 평가 기간에도 이론 시험 준비에 쫓기지 않고 여유 있게 학기를 마무리할 수 있었다는 이야기를 들었습니다. 이런 사례를 볼 때마다, 특성화고 학생들에게는 일정을 미리 파악하고 계획하는 것 자체가 성적 관리의 핵심이라는 걸 다시 확인하게 됩니다. 또 다른 학생은 실습이 많은 학기 초에는 이론 공부에 거의 손을 못 대다가, 중간에 상담을 받고 나서야 남은 기간 계획을 재정비해 무사히 학기를 마무리할 수 있었어요. 이렇게 중간에라도 방향을 바로잡으면 충분히 만회할 수 있다는 걸 여러 사례에서 확인하고 있습니다.</p>
    <h2>티치핏여수와 함께 기말고사를 준비해보세요</h2>
    <p>티치핏여수는 상담 시 학생의 실습 시간표를 함께 확인하고, 남은 시간을 어떻게 배분하면 좋을지부터 계획을 세워드려요. 여수공업고등학교 같은 학교의 학사 일정을 고려해서 선생님을 화상으로 연결해 드리고, 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여합니다. 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있고, 신청 후 24시간 이내에 담당자가 직접 연락드려요. 여수공업고등학교뿐 아니라 여수 관내 고등학교 15곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교를 알려주시면 그에 맞춰 상담해 드릴게요. 실습과 이론을 함께 챙겨야 하는 상황이 부담스럽게 느껴지실 텐데, 상담을 통해 학생의 상황에 맞는 현실적인 계획을 함께 세워드리니 편하게 문의해주세요. 학생의 시간표를 보내주시면 그에 맞춰 가장 현실적인 학습 계획부터 함께 짜드릴게요.</p>
    <p><strong>Q. 실습이 많아서 시간이 일정하지 않은데 수업 일정 조율이 되나요?</strong><br>
    네, 상담 시 시간표를 확인하고 실습이 없는 날을 중심으로 유연하게 일정을 조율해 드려요.</p>
    <p><strong>Q. 전공 과목도 봐주시나요?</strong><br>
    주로 이론 내신 과목을 중심으로 진행하며, 전공 이론이 필요한 경우 상담 시 말씀해주세요.</p>
    <p><strong>Q. 시험 범위가 넓은데 짧은 시간에 다 볼 수 있을까요?</strong><br>
    자주 출제되는 핵심 개념부터 우선순위를 정해서 짧은 시간에도 효율적으로 준비할 수 있게 도와드려요.</p>
    ''',
})

BLOG_POSTS.append({
    "slug": "jinseongyeoja-hs-gukeo-naeshin",
    "title": "진성여자고등학교 국어 내신 화상과외, 등급 가르는 지문 독해력 키우기",
    "date": "2026-09-24",
    "category": "고등 국어내신",
    "teaser": "진성여자고등학교 학생 기준으로, 국어 내신 등급을 가르는 지문 독해력을 어떻게 키울 수 있는지 정리했어요.",
    "body": '''
    <p>진성여자고등학교에 다니는 자녀를 둔 학부모님 중에는, 국어 내신에서 늘 애매한 등급에 머물러 있어 고민이라는 분들이 많아요. 확실히 틀리는 것도 아니고 확실히 맞는 것도 아닌, 애매하게 헷갈리는 문제에서 계속 감점되는 경우가 많은데, 이런 상황은 대부분 지문을 정확하게 읽어내는 독해력의 문제인 경우가 많아요. 국어는 다른 과목보다 눈에 보이는 개념이 적어서 어디를 보완해야 할지 감이 잘 안 잡히실 텐데, 사실 등급을 가르는 지점은 생각보다 명확합니다. 이 글에서는 진성여자고등학교 학생들이 상담에서 자주 이야기하는 국어 내신 고민을 바탕으로, 등급을 가르는 지문 독해력을 어떻게 키울 수 있는지 정리해봤어요.</p>
    <h2>애매하게 틀리는 문제, 원인은 지문을 읽는 방식에 있어요</h2>
    <p>국어 내신에서 애매하게 틀리는 학생들을 보면, 대부분 지문을 꼼꼼히 읽지 않고 대략적인 느낌으로 선택지를 고르는 습관이 있어요. 진성여자고등학교 국어 시험이 지문의 세부 내용을 정확히 확인해야 풀 수 있는 문제를 포함한다면, 이런 느낌 위주의 접근은 애매한 등급에 머무는 원인이 될 수 있어요. <strong>지문을 읽을 때 중요한 건 빠르게 읽는 게 아니라, 정확하게 읽는 것입니다.</strong> 특히 선택지가 지문의 내용을 살짝 바꿔서 제시하는 경우가 많은데, 이 미묘한 차이를 잡아내지 못하면 정답처럼 보이는 오답을 고르게 돼요. 화상과외로 상담을 진행하다 보면, 학생이 지문을 읽고 선택지를 고르는 과정을 함께 지켜보면서, 어느 부분에서 지문 내용을 정확히 확인하지 않고 넘어가는지를 짚어주는 것만으로도 정답률이 눈에 띄게 달라지는 경우가 많습니다. 예를 들어 지문에서 '항상', '전혀', '오직'과 같은 단정적인 표현이 선택지에 등장한다면 특히 주의해서 지문과 대조해봐야 해요. 이런 단정적인 표현은 지문의 내용과 조금만 어긋나도 바로 오답이 되는 경우가 많거든요. 진성여자고등학교 학생들을 상담해보면, 이런 표현을 대충 넘기고 전체적인 느낌만으로 선택지를 고르는 습관이 애매한 등급의 가장 큰 원인인 경우가 많습니다. 이런 습관은 스스로는 잘 알아채기 어렵기 때문에, 옆에서 채점 과정을 함께 짚어주는 사람이 있을 때 훨씬 빠르게 교정됩니다. 몇 번만 이 훈련을 반복해도 선택지를 보는 시선 자체가 달라지는 걸 느낄 수 있어요.</p>
    <h2>내신 국어는 수업 시간 필기가 핵심이에요</h2>
    <p>내신 국어는 수능 국어와 달리, 학교 선생님이 수업 중에 설명한 해석과 관점이 시험에 그대로 반영되는 경우가 많아요. 그래서 교과서를 혼자 읽는 것만으로는 부족하고, 수업 시간에 선생님이 강조했던 부분을 정확히 기억하고 있어야 해요. 진성여자고등학교 국어 시험을 준비할 때도, 필기 내용을 얼마나 꼼꼼히 정리했는지가 등급에 큰 영향을 미칠 수 있어요. 만약 필기가 부실하다면, 최근 배운 단원의 핵심 해석 포인트를 다시 정리하는 과정이 필요합니다. <strong>같은 작품이라도 학교에서 강조한 해석 방향이 시험 출제의 기준이 된다는 점을 꼭 기억해야 해요.</strong> 화상과외에서는 상담 시 학생의 필기 노트나 프린트를 함께 확인하고, 부족한 부분을 보완하면서 수업 중 강조된 포인트를 놓치지 않도록 짚어드리고 있어요. 또한 선생님마다 같은 작품을 다르게 해석하는 부분이 있을 수 있는데, 시험은 결국 그 학교, 그 선생님이 수업 중 강조한 해석을 기준으로 출제된다는 점을 잊지 말아야 해요. 참고서나 인터넷에 있는 일반적인 해석과 학교 수업 내용이 다를 경우, 학교 수업 내용을 우선으로 정리해두는 게 안전합니다. 이 부분에서 혼란을 겪는 학생들이 의외로 많아서, 필기 정리가 특히 중요한 이유가 되기도 해요. 특히 시나 소설처럼 해석의 여지가 있는 작품일수록, 수업 중 언급된 관점을 놓치지 않고 기록해두는 습관이 시험 점수로 직결되는 경우가 많습니다. 필기가 꼼꼼한 학생일수록 시험 직전 복습 시간도 훨씬 단축된다는 걸 여러 사례에서 확인할 수 있었어요.</p>
    <h2>화상과외가 국어 독해력 향상에 유리한 이유</h2>
    <p>독해력은 혼자 문제집을 많이 푼다고 저절로 늘어나는 능력이 아니에요. 지문을 읽는 방식 자체를 교정받는 과정이 필요한데, 이 부분에서 1:1 지도가 특히 효과적입니다. 화상과외는 학생이 지문을 읽고 문제를 푸는 과정을 화면으로 함께 보면서, 어느 문장에서 놓친 부분이 있는지, 어떤 선택지에서 헷갈리는지를 실시간으로 확인할 수 있어요. 수업이 녹화되기 때문에 헷갈렸던 지문을 다시 돌려보면서 복습할 수 있다는 것도 국어처럼 반복적인 훈련이 중요한 과목에서는 큰 도움이 됩니다. 진성여자고등학교 시험 스타일을 잘 아는 선생님이라면, 어떤 유형의 문제가 자주 출제되는지도 함께 안내받을 수 있어요. <strong>이동 시간 없이 저녁 시간대에도 유연하게 수업을 잡을 수 있다는 점</strong>도 고등학생들에게는 실질적으로 체감되는 장점이에요. 화상과외에서는 또한 학생이 어떤 유형의 지문에서 특히 자주 헷갈리는지 데이터를 쌓아가면서, 다음 수업에서 비슷한 유형을 반복적으로 다뤄줄 수 있어요. 이렇게 반복되는 취약 유형을 집중적으로 훈련하는 방식이, 막연히 다양한 지문을 많이 읽는 것보다 등급 향상에 훨씬 효율적인 경우가 많습니다. 특히 애매한 등급에 머물러 있는 학생일수록, 넓게 많이 푸는 것보다 좁게 집중해서 반복하는 방식이 훨씬 빠르게 효과를 보이는 경우가 많아요. 취약 유형을 정확히 짚어내는 진단 과정이 선행되어야, 이런 집중 훈련도 제대로 효과를 낼 수 있습니다. 진단 없이 무작정 반복하는 것과, 정확히 짚어낸 뒤 반복하는 것은 같은 시간을 들여도 결과가 크게 다릅니다.</p>
    <h2>국어 등급을 올리기 전 꼭 확인해야 할 3가지</h2>
    <p>첫째, 최근 시험에서 틀린 문제를 다시 펼쳐서 선택지와 지문을 대조해보세요. 지문에 없는 내용을 임의로 판단했는지 확인하는 게 중요해요. 둘째, 수업 시간 필기 노트를 다시 살펴보고, 선생님이 강조했던 해석 포인트가 정리되어 있는지 확인하세요. 셋째, 지문을 읽을 때 속도보다 정확도를 먼저 점검하세요. 이 세 가지를 확인하지 않고 문제만 계속 풀면, 애매한 등급에서 벗어나기 어려운 경우가 많아요. 진성여자고등학교처럼 지문 기반 문제가 많은 학교라면, 특히 첫 번째와 두 번째 항목을 꾸준히 챙기는 게 중요합니다. <strong>국어는 감이 아니라 정확한 근거를 찾는 훈련이 쌓여야 등급이 오르는 과목이에요.</strong> 넷째로, 문학 작품을 공부할 때는 줄거리나 배경지식만 외우지 말고, 실제로 그 작품에서 자주 출제되는 표현이나 상징을 문제 형식으로 접해보는 연습이 필요해요. 배경지식만 있고 실전 문제에 적용하는 연습이 없으면, 아는 작품이 나와도 막상 문제는 틀리는 경우가 생겨요. 이 네 가지를 시험 3주 전부터 단계적으로 점검해두면, 애매하게 틀리던 문제들이 눈에 띄게 줄어드는 걸 경험할 수 있습니다. 네 가지 모두 혼자 점검하기보다, 선생님과 함께 하나씩 확인해나가면 놓치는 부분 없이 훨씬 꼼꼼하게 준비할 수 있어요. 이 네 가지 기준을 시험마다 반복해서 적용하다 보면, 점차 스스로도 애매한 선택지를 걸러내는 감각이 생기기 시작합니다. 처음에는 시간이 걸리더라도, 이 기준이 습관으로 자리 잡으면 실전에서도 훨씬 빠르고 정확하게 판단할 수 있게 됩니다.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면, 국어를 나름 열심히 공부하는데도 애매한 등급에서 벗어나지 못해 답답해하시는 학부모님들을 자주 만나요. 한 학생은 지문을 빠르게 읽는 데는 익숙했지만, 세부 내용을 정확히 확인하지 않고 선택지를 고르는 습관이 있었어요. 이 부분을 파악한 뒤로는 선택지마다 지문에서 근거 문장을 직접 찾아 표시하는 훈련을 반복하면서, 애매하게 틀리던 문제들이 점차 줄어드는 걸 확인할 수 있었어요. 다른 학생은 필기 정리가 부족해서 수업 시간에 강조된 해석을 놓치는 경우가 많았는데, 매주 수업이 끝난 뒤 필기를 정리하는 습관을 만들면서 시험에서 훨씬 안정적인 점수를 받을 수 있게 됐다고 해요. <strong>결국 정확하게 읽고 정확하게 기억하는 습관이 등급을 가른다는 걸</strong> 이런 사례들을 통해 계속 확인하고 있어요. 또 다른 학생은 문학 작품의 줄거리는 잘 알고 있었지만, 그 작품에서 자주 출제되는 표현 방식에는 익숙하지 않아서 실전 문제에서 자주 틀렸던 경우였어요. 실제 기출 유형으로 반복 훈련을 진행하면서부터는, 아는 작품이 나왔을 때 실수 없이 문제를 풀어내는 경우가 늘어났다는 이야기를 들었습니다. 이런 사례들을 통해, 배경지식과 실전 문제 적용력은 따로 훈련해야 하는 능력이라는 걸 계속 확인하고 있어요. 두 가지를 함께 챙기기 시작하면서부터 성적이 눈에 띄게 안정되는 경우를 자주 보게 됩니다. 처음에는 시간이 오래 걸리는 것처럼 느껴져도, 이렇게 원인을 정확히 짚고 넘어가는 방식이 결국 가장 빠른 지름길이 됩니다.</p>
    <h2>티치핏여수와 함께 국어 등급을 올려보세요</h2>
    <p>티치핏여수는 상담 시 최근 시험지와 필기 노트를 먼저 확인하고, 진성여자고등학교 같은 학교의 국어 시험 스타일을 고려해서 선생님을 화상으로 연결해 드려요. 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여하고, 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있습니다. 신청 후 24시간 이내에 담당자가 직접 연락드리고, 학습 진단부터 선생님 추천, 체험 수업까지 순서대로 안내해 드려요. 진성여자고등학교뿐 아니라 여수 관내 고등학교 15곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교를 알려주시면 그에 맞춰 상담해 드릴게요. 애매한 등급에서 벗어나고 싶다면, 지금 어느 부분에서 감점되는지 정확히 진단받는 것부터 시작해보시길 추천드려요. 편하게 상담을 신청해보세요. 최근 시험지 한 장만 있어도 충분히 진단이 가능하니 부담 없이 문의해주시면 됩니다.</p>
    <p><strong>Q. 애매하게 틀리는 문제가 많은데 원인을 정확히 짚어주실 수 있나요?</strong><br>
    네, 상담 시 최근 시험지를 함께 분석해서 지문 대조 방식으로 원인을 정확히 찾아드려요.</p>
    <p><strong>Q. 필기 정리하는 습관도 함께 봐주시나요?</strong><br>
    네, 필기 노트를 확인하고 부족한 부분을 보완하는 방법도 함께 안내해 드려요.</p>
    <p><strong>Q. 진성여자고등학교 시험 스타일도 반영해서 준비할 수 있나요?</strong><br>
    네, 최근 시험지를 확인하고 학교별 출제 스타일에 맞춰 준비 방향을 안내해 드려요.</p>
    ''',
})

BLOG_POSTS.append({
    "slug": "yeosugubong-es-seonhaeng",
    "title": "여수구봉초등학교 선행학습, 무리하지 않고 시작하는 방법",
    "date": "2026-09-24",
    "category": "초등 선행학습",
    "teaser": "여수구봉초등학교 학생 기준으로, 선행학습을 무리하지 않고 아이 속도에 맞게 시작하는 방법을 정리했어요.",
    "body": '''
    <p>여수구봉초등학교에 아이를 보내고 계신 학부모님 중에는, 선행학습을 언제 어떻게 시작해야 할지 고민하시는 분들이 많아요. 주변에서 선행학습 이야기가 들리기 시작하면 조급한 마음이 들기 마련이지만, 무작정 진도만 빨리 나간다고 해서 아이에게 좋은 결과로 이어지는 건 아니에요. 오히려 준비 없이 서두른 선행학습이 아이에게 부담만 주고 끝나는 경우도 적지 않습니다. 이 글에서는 여수구봉초등학교 학생 기준으로, 선행학습을 무리하지 않고 시작하는 방법을 구체적으로 정리해봤어요. 시작 시점을 판단하는 기준부터 실제 상담 사례까지 함께 담았으니, 선행학습을 고민 중이시라면 꼭 참고해보시길 바랍니다.</p>
    <h2>선행학습, 무작정 시작하면 오히려 역효과가 날 수 있어요</h2>
    <p>선행학습의 목적은 다음 학년 내용을 미리 익혀서 여유를 갖는 거예요. 그런데 현재 학년 내용도 제대로 소화하지 못한 상태에서 선행부터 시작하면, 오히려 두 가지를 동시에 어려워하는 상황이 생길 수 있습니다. 지금 배우는 내용도 헷갈리는데 다음 학년 내용까지 얹으면, 아이 입장에서는 이해하지 못한 채로 진도만 나가는 셈이 되고, 결국 선행한 내용도 실제로 그 학년이 됐을 때 다시 배워야 하는 경우가 많아요. <strong>준비 없이 시작한 선행학습은 아이에게 자신감을 잃게 만들 위험도 있습니다.</strong> 이해가 안 되는 상태로 진도만 계속 나가다 보면, 아이는 점점 자신감을 잃고 공부 자체에 흥미를 잃을 수 있어요. 그래서 선행학습을 시작하기 전에는 반드시 현재 학년 개념이 얼마나 탄탄한지부터 점검하는 과정이 필요합니다. 여수구봉초등학교처럼 학년별 진도 체감이 다를 수 있기 때문에, 재학 중인 학교를 먼저 확인하고 그에 맞춰 속도를 조절하는 것도 중요한 부분이에요. 특히 국어 읽기 독립이 안 된 상태에서 어려운 지문으로 선행을 시키면, 아이가 책 읽기 자체에 흥미를 잃을 위험이 있어요. 여수구봉초등학교 학생들을 상담해보면, 과목마다 선행에 필요한 최소 조건이 다르다는 걸 모른 채 무작정 진도만 앞당기려는 경우가 많아서, 이 부분을 먼저 안내해 드리는 것부터 상담을 시작하는 경우가 많습니다. 선행학습은 빠를수록 좋은 게 아니라, 아이가 소화할 준비가 됐을 때 시작하는 게 가장 중요하다는 점을 늘 먼저 말씀드려요.</p>
    <h2>여수구봉초등학교 학생이라면 이 순서를 추천해요</h2>
    <p>먼저 아이의 현재 학년 이해도를 정확히 파악하는 것부터 시작하세요. 단순히 성적으로만 판단하기보다, 개념을 스스로 설명할 수 있는지 확인해보는 게 좋아요. 만약 현재 학년 개념에 구멍이 있다면, 선행보다는 그 부분을 먼저 채우는 게 우선입니다. 현재 학년 개념이 탄탄하다고 판단되면, 그때부터 다음 학년 내용을 조금씩 얹어가는 방식으로 진행하세요. 저학년이라면 선행보다 학습 습관을 먼저 잡는 데 집중하고, 고학년이라면 중학교와 연결되는 개념을 의식하면서 선행을 진행하는 게 좋습니다. 예를 들어 수학이라면 분수와 소수 개념이 확실히 잡혀 있어야 이후 비와 비율, 방정식으로 자연스럽게 넘어갈 수 있어요. <strong>이런 연결 고리를 미리 알고 있는 선생님과 함께라면, 어느 시점에 무엇을 먼저 다져야 할지 훨씬 명확하게 계획할 수 있습니다.</strong> 국어나 영어도 마찬가지로, 과목마다 꼭 필요한 선행 조건을 먼저 갖췄는지 확인하는 과정이 중요합니다. 또한 선행학습을 시작한 이후에도, 주기적으로 현재 학년 내용을 함께 복습하는 시간을 가져야 해요. 선행 진도에만 집중하다 보면 오히려 현재 학년에서 다뤄야 할 세부 내용을 놓치는 경우가 생기거든요. 두 가지를 균형 있게 병행하는 게, 급하게 진도만 나가는 것보다 장기적으로 훨씬 안정적인 결과를 만들어냅니다. 특히 수학처럼 단원 간 연결이 중요한 과목은, 현재 학년 복습과 다음 학년 선행을 번갈아 진행하는 방식이 효과적인 경우가 많아요.</p>
    <h2>화상과외가 선행학습에 유리한 이유</h2>
    <p>선행학습은 아이 속도에 맞춰 진도를 유연하게 조절할 수 있는 선생님을 만나는 게 핵심이에요. 학원은 정해진 커리큘럼과 반 편성으로 운영되기 때문에, 아이 개인의 속도에 맞추기가 어려운 경우가 많습니다. 반면 화상과외는 1:1로 진행되기 때문에, 아이가 이해한 정도에 따라 진도를 빠르게 나가기도 하고, 필요하면 다시 돌아가서 짚어주기도 하는 유연한 조정이 가능해요. 지역 제약이 없다는 것도 큰 장점입니다. 여수구봉초등학교 인근에서만 찾을 때보다 훨씬 넓은 범위에서, 선행 지도 경험이 많은 선생님을 연결받을 수 있어요. 수업이 녹화되기 때문에 부모님이 나중에 수업 분위기를 확인해보실 수 있다는 것도 안심이 되는 부분이에요. <strong>아이가 정말 이해하면서 진도를 나가고 있는지, 아니면 그냥 따라가기만 하는 건지 부모님도 함께 파악할 수 있습니다.</strong> 화상과외는 또한 아이의 반응 속도에 맞춰 그날그날 진도를 조절할 수 있다는 점에서 선행학습에 특히 유리해요. 어떤 날은 예상보다 빠르게 이해해서 진도를 조금 더 나갈 수도 있고, 어떤 날은 예상보다 느려서 같은 부분을 반복해야 할 수도 있는데, 이런 유연한 조정이 정해진 커리큘럼을 따라야 하는 학원보다 훨씬 수월하게 이루어집니다. 이렇게 아이 컨디션에 맞춰 매번 조율할 수 있다는 점이, 선행학습에서 무리를 줄이는 가장 현실적인 방법이 됩니다. 정해진 진도표에 아이를 맞추는 게 아니라, 아이의 이해 속도에 진도를 맞추는 방식이라는 점이 가장 큰 차이예요.</p>
    <h2>선행학습 시작 전 꼭 확인해야 할 3가지</h2>
    <p>첫째, 현재 학년 개념에 빠진 부분이 없는지 먼저 확인하세요. 이 확인 없이 선행부터 시작하면 앞서 말씀드린 것처럼 역효과가 날 수 있어요. 둘째, 아이가 선행학습에 대해 심리적으로 부담을 느끼지는 않는지 살펴보세요. 억지로 시작한 선행학습은 오래가지 못하는 경우가 많습니다. 셋째, 선생님이 아이 속도에 맞춰 유연하게 진도를 조절해줄 수 있는 분인지 확인하세요. 정해진 속도로만 진도를 나가는 방식이라면, 오히려 아이에게 안 맞을 수 있어요. 이 세 가지를 먼저 점검한 다음 선행학습을 시작하면, 훨씬 안정적으로 진행할 수 있습니다. <strong>조급하게 시작해서 중간에 포기하는 것보다, 조금 늦더라도 제대로 된 방식으로 시작하는 게 장기적으로 훨씬 유리합니다.</strong> 넷째로, 선행학습을 시작한 뒤에도 아이의 표정이나 반응을 주의 깊게 살펴보세요. 즐거워하며 참여하는지, 아니면 억지로 따라가고 있는지를 부모님이 함께 관찰하는 게 중요해요. 만약 아이가 힘들어하는 기색이 보인다면 속도를 늦추거나 잠시 쉬어가는 것도 괜찮습니다. 이 네 가지를 염두에 두고 선행학습을 진행하면, 아이가 부담 없이 꾸준히 이어갈 수 있는 방식을 찾을 수 있어요. 조급함을 내려놓고 이 네 가지를 하나씩 확인해가는 과정 자체가, 결국 아이에게 맞는 속도를 찾아가는 길이 됩니다. 부모님 혼자 이 모든 걸 판단하기 어려우시다면, 상담을 통해 함께 점검해보는 것도 좋은 방법이에요. 네 가지 기준을 하나씩 확인하다 보면, 막연했던 고민이 훨씬 구체적인 계획으로 바뀌는 걸 경험하실 수 있습니다.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면, 처음에는 주변 이야기만 듣고 조급한 마음으로 문의하시는 학부모님들이 많아요. 그런데 막상 아이의 현재 학년 이해도를 확인해보면, 선행보다 현재 학년 내용을 다지는 게 먼저인 경우가 생각보다 많습니다. 한 학부모님은 아이에게 무리하게 선행을 시켰다가 오히려 아이가 수학에 흥미를 잃는 걸 보고 걱정이 크셨는데, 상담 후 현재 학년 개념부터 다시 다지는 방향으로 바꾸고 나서 아이가 훨씬 편안하게 수업에 참여하게 됐다는 이야기를 해주셨어요. 반대로 현재 학년 개념이 이미 탄탄한 아이의 경우에는, 적절한 시점에 선행을 시작해서 중학교 진학을 훨씬 여유 있게 준비할 수 있었던 사례도 있었습니다. <strong>중요한 건 선행 여부 자체가 아니라, 아이 상태에 맞는 시점과 속도를 찾는 것</strong>이라는 걸 이런 상담들을 통해 계속 확인하고 있어요. 또 다른 학부모님은 아이가 선행학습을 시작한 뒤 오히려 학교 수업이 쉽게 느껴진다며 자신감을 얻는 모습을 보고 안심하셨다고 해요. 이렇게 적절한 시점에 시작한 선행학습은 아이에게 여유와 자신감을 함께 가져다주는 경우가 많은데, 그 시작 시점과 속도를 아이 상태에 맞게 판단하는 과정이 무엇보다 중요하다는 걸 이런 사례를 통해 다시 확인하게 됩니다. 결국 선행학습의 성패는 얼마나 빨리 시작했는지가 아니라, 아이에게 맞는 방식으로 시작했는지에 달려 있다는 걸 매번 느끼게 됩니다. 여러 사례를 지켜보면서, 조급함보다 아이의 속도를 존중하는 태도가 결국 가장 좋은 결과로 이어진다는 걸 거듭 확인하고 있습니다.</p>
    <h2>티치핏여수와 함께 선행학습을 시작해보세요</h2>
    <p>티치핏여수는 상담 시 아이의 현재 학년 이해도와 성향을 먼저 확인하고, 여수구봉초등학교 같은 학교 분위기를 고려해서 선생님을 연결해 드려요. 선행이 필요한 시점인지부터 함께 판단해 드리기 때문에, 무작정 선행을 권하지 않아요. 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여하고, 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있습니다. 신청 후 24시간 이내에 담당자가 직접 연락드리고, 학습 진단부터 선생님 추천, 체험 수업까지 순서대로 안내해 드려요. 여수구봉초등학교뿐 아니라 여수 관내 초·중·고 93곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교를 알려주시면 그에 맞춰 상담해 드릴게요. 선행이 필요한 시점인지 아직 판단이 안 서신다면, 먼저 가벼운 상담을 통해 아이의 현재 상태를 확인해보시는 것부터 시작해보세요.</p>
    <p><strong>Q. 여수구봉초등학교 학생도 매칭 가능한가요?</strong><br>
    네, 여수구봉초등학교뿐 아니라 여수 관내 초등학교 54곳 전부 안내해 드려요.</p>
    <p><strong>Q. 아직 선행이 필요한지 판단이 안 서요, 상담만 받아도 되나요?</strong><br>
    물론이에요. 상담 시 현재 학습 상태를 먼저 확인해 드리고, 선행이 필요한 시점인지도 함께 안내해 드립니다.</p>
    <p><strong>Q. 선행학습 진도는 어느 정도 속도로 나가나요?</strong><br>
    아이가 소화할 수 있는 속도에 맞춰 유연하게 조정하며, 무리하게 빠른 진도를 강요하지 않아요.</p>
    ''',
})

BLOG_POSTS.append({
    "slug": "yeosu-hwasang-gwaoe-biyong",
    "title": "여수 화상과외 비용, 방문과외와 비교하면 얼마나 차이날까요",
    "date": "2026-09-24",
    "category": "비용 가이드",
    "teaser": "여수 지역 화상과외 비용을 방문과외와 비교해서, 어떤 기준으로 비용이 결정되는지 정리했어요.",
    "body": '''
    <p>여수에서 아이 과외를 알아보시는 학부모님이라면, 화상과외와 방문과외 중 어떤 방식이 더 나을지, 그리고 비용은 얼마나 차이가 나는지 궁금하실 거예요. 막상 알아보려고 하면 학원비, 과외비, 화상과외 플랫폼 등 선택지가 너무 많아서 오히려 더 헷갈리는 경우가 많아요. 특히 여수처럼 지역 안에서 원하는 조건의 방문 선생님을 구하기 어려운 경우, 화상과외를 고려하게 되는데 비용 구조가 어떻게 다른지 정확히 알고 선택하는 게 중요합니다. 이 글에서는 여수 지역 학부모님들이 상담에서 자주 물어보시는 비용 관련 질문을 바탕으로, 화상과외와 방문과외의 비용 차이와 결정 기준을 정리해봤어요.</p>
    <h2>과외 비용은 무엇으로 결정될까요</h2>
    <p>과외 비용은 방문이든 화상이든 몇 가지 공통된 기준으로 결정돼요. 먼저 과목과 학년에 따라 기본 비용대가 다르고, 선생님의 경력과 지도 경험도 비용에 영향을 줍니다. 여기에 수업 시간과 주당 횟수도 비용을 결정하는 중요한 요소예요. 방문과외의 경우 여기에 선생님의 이동 시간과 교통비가 추가로 반영되는 경우가 많은데, 이 부분이 화상과외와 가장 큰 비용 차이를 만드는 지점이에요. <strong>같은 조건의 선생님이라도, 이동이 필요 없는 화상과외는 그 시간과 비용이 수업료에 그대로 반영되지 않아 상대적으로 합리적인 경우가 많습니다.</strong> 여수처럼 지역이 넓게 퍼져 있는 곳에서는 방문 선생님의 이동 거리에 따라 비용 차이가 크게 나기도 하는데, 화상과외는 이런 지역적 요인에서 비교적 자유로운 편이에요. 정확한 비용은 학생 상황을 확인한 뒤 상담을 통해 안내드리고 있어요. 또한 그룹 수업인지 1:1 수업인지에 따라서도 비용 차이가 크게 나요. 화상과외는 대부분 1:1로 진행되기 때문에 그룹 수업보다는 비용이 높게 느껴질 수 있지만, 그만큼 학생 개인에게 집중된 지도를 받을 수 있다는 점에서 효율을 함께 고려해봐야 해요. 단순히 시간당 비용만 비교하기보다, 그 시간에 얻을 수 있는 학습 효과까지 함께 따져보는 게 합리적인 선택에 가깝습니다. 또한 선생님의 경력이 비슷하더라도, 화상과외 플랫폼마다 중개 수수료 구조가 다를 수 있어 실제 학생에게 돌아가는 비용 대비 가치도 차이가 날 수 있어요.</p>
    <h2>방문과외와 화상과외, 비용 외에 무엇이 다를까요</h2>
    <p>비용만 놓고 비교하기 전에, 두 방식이 실제로 어떻게 다른지도 함께 살펴봐야 해요. 방문과외는 선생님이 직접 집으로 와서 대면으로 진행되기 때문에, 아이가 낯선 환경 적응 없이 바로 수업에 집중할 수 있다는 장점이 있어요. 반면 이동 시간과 교통비가 발생하고, 원하는 시간대에 방문이 가능한 선생님을 구하기가 지역에 따라 어려울 수 있어요. 화상과외는 이동이 없기 때문에 저녁 시간대나 늦은 시간에도 비교적 유연하게 일정을 잡을 수 있고, 지역 제약 없이 훨씬 넓은 범위에서 원하는 과목과 스타일의 선생님을 찾을 수 있다는 장점이 있어요. <strong>다만 화상 환경에 아이가 적응하는 데 약간의 시간이 필요할 수 있다는 점은 미리 알고 시작하는 게 좋아요.</strong> 수업이 녹화되기 때문에 복습에 활용할 수 있다는 것도 화상과외만의 특징이에요. 또한 방문과외는 선생님이 실제로 집에 오시기 때문에, 수업 외 시간에 아이의 생활 습관이나 학습 환경을 자연스럽게 살펴볼 수 있다는 장점도 있어요. 반면 화상과외는 이런 대면 관찰이 어려운 대신, 수업 녹화를 통해 부모님이 수업 내용을 언제든 다시 확인할 수 있다는 점에서 다른 방식의 투명성을 제공해요. 두 방식 모두 각자의 장단점이 있기 때문에, 아이의 성향과 가정 상황에 맞춰 선택하는 게 중요합니다. 아이가 낯선 사람과의 대면을 어려워하는 성향이라면 방문과외가, 반대로 화면을 통한 소통에 오히려 편안함을 느끼는 성향이라면 화상과외가 더 잘 맞을 수도 있어요. 처음 몇 회 체험수업을 통해 아이의 반응을 직접 살펴보는 것이, 어느 쪽이 더 잘 맞는지 가장 정확하게 판단하는 방법이기도 합니다.</p>
    <h2>여수 지역에서 화상과외를 고려하면 좋은 경우</h2>
    <p>여수는 도심과 외곽 지역의 격차가 있는 곳이라, 거주 지역에 따라 원하는 방문 선생님을 구하기 어려운 경우가 있어요. 특히 특정 과목이나 시간대를 원하는데 지역 안에서 맞는 선생님이 없다면, 화상과외로 범위를 넓혀보는 게 현실적인 대안이 될 수 있어요. 또한 저녁 늦은 시간에만 시간이 나는 학생이라면, 방문 선생님을 구하기 더 어려운 경우가 많은데 화상과외는 이런 시간대 제약에서 비교적 자유로워요. <strong>지역 안에서만 찾을 때보다 훨씬 넓은 범위에서 경력 있는 선생님을 만날 수 있다는 것</strong>이 화상과외를 고려하는 가장 큰 이유 중 하나예요. 여수 관내 초·중·고 93곳 전체 학생을 대상으로 매칭이 가능하기 때문에, 어느 지역에 살든 원하는 조건의 선생님을 연결받을 수 있어요. 예를 들어 돌산이나 화양처럼 시내에서 다소 떨어진 지역에 거주하신다면, 방문 선생님을 구하는 것 자체가 더 어려울 수 있어요. 이런 경우 화상과외는 거주 지역과 무관하게 선생님을 연결받을 수 있다는 점에서 실질적인 대안이 될 수 있어요. 반대로 시내 중심가에 거주하신다면 방문과외 선택지도 상대적으로 넓을 수 있으니, 거주 지역에 따라 두 방식을 함께 비교해보시는 것도 좋은 방법입니다. 거주 지역만으로 방식을 단정 짓기보다, 실제로 두 방식 모두 상담을 받아보고 비교해보는 것도 좋은 방법이에요. 특히 이사 계획이 있는 가정이라면, 지역에 구애받지 않는 화상과외가 장기적으로 더 안정적인 선택이 될 수도 있습니다.</p>
    <h2>과외를 결정하기 전 꼭 확인해야 할 3가지</h2>
    <p>첫째, 아이가 어떤 학습 환경에서 더 집중을 잘하는지 파악해보세요. 대면 환경을 선호하는 아이와 화면으로도 편안하게 집중하는 아이는 다를 수 있어요. 둘째, 원하는 시간대에 방문 가능한 선생님이 지역 안에 충분히 있는지 확인해보세요. 셋째, 비용을 비교할 때는 수업료만 보지 말고 이동 시간까지 포함한 전체적인 효율을 함께 고려해보세요. 이 세 가지를 확인하고 결정하면, 방식에 대한 후회 없이 시작할 수 있어요. <strong>정확한 비용은 과목·학년·수업 시간, 선생님 경력에 따라 달라지기 때문에, 상담을 통해 학생 상황을 확인한 뒤 안내받는 게 가장 정확합니다.</strong> 넷째로, 처음부터 장기간 계약을 하기보다, 짧은 체험 기간을 통해 아이와 선생님의 궁합을 먼저 확인해보는 것도 중요해요. 비용을 아끼려고 체험 없이 바로 정식 수업을 시작하면, 나중에 맞지 않는다는 걸 알게 됐을 때 오히려 더 큰 시간과 비용을 낭비하게 될 수 있어요. 이 세 가지에 이 네 번째 기준까지 더해서 확인하고 결정하면, 방식과 선생님 모두에 대한 후회를 줄일 수 있습니다. 처음부터 완벽한 선택을 하려고 애쓰기보다, 체험을 통해 조금씩 맞춰가는 편이 결과적으로 시간과 비용 모두를 아끼는 방법이 됩니다. 비용, 성향, 지역 여건까지 이 네 가지를 차례로 점검하고 나면, 어떤 방식이 우리 아이에게 맞는지 훨씬 선명하게 보이기 시작합니다. 급하게 결정하기보다, 이 네 가지를 표로 정리해보는 것만으로도 판단이 훨씬 쉬워지는 경우가 많아요.</p>
    <h2>실제 상담에서 확인한 사례</h2>
    <p>상담을 하다 보면, 처음에는 방문과외만 생각하고 문의하셨다가 화상과외로 방향을 바꾸시는 학부모님들이 꽤 많아요. 한 학부모님은 거주 지역에서 원하는 과목의 방문 선생님을 몇 달째 구하지 못하고 있었는데, 화상과외로 범위를 넓히자 원하는 조건의 선생님을 빠르게 연결받을 수 있었다고 해요. 다른 학부모님은 아이가 늦은 시간에만 학습 시간이 나서 방문 선생님을 구하기 어려웠는데, 화상과외는 저녁 시간대 일정 조율이 훨씬 수월해서 만족스러웠다는 이야기를 해주셨어요. <strong>결국 아이 상황과 지역 여건에 맞는 방식을 선택하는 게 가장 중요하다는 걸</strong> 이런 상담들을 통해 계속 확인하고 있어요. 또 다른 학부모님은 방문과외와 화상과외 비용을 단순 비교했을 때 큰 차이가 없어 보여서 고민하셨는데, 실제로 방문 선생님의 이동 시간을 고려한 실질적인 수업 시간과 화상과외의 순수 수업 시간을 비교해보니 화상과외가 오히려 효율적이었다는 걸 알게 되셨다고 해요. 이렇게 겉으로 보이는 비용만이 아니라 실질적인 학습 시간까지 함께 따져보는 관점이, 두 방식을 비교할 때 놓치기 쉬운 부분이라는 걸 다시 확인하게 됩니다. 이런 사례들을 접할 때마다, 비용은 숫자만이 아니라 그 안에 담긴 실질적인 가치까지 함께 봐야 한다는 걸 다시 느끼게 됩니다. 결국 저렴한 선택보다 아이에게 맞는 선택이 장기적으로 더 큰 만족으로 이어진다는 걸 여러 상담을 통해 계속 확인하고 있습니다. 상담을 통해 이런 부분까지 꼼꼼히 비교해드리니, 혼자 고민하지 마시고 편하게 문의해주세요.</p>
    <h2>티치핏여수에 비용을 문의해보세요</h2>
    <p>티치핏여수는 상담 시 학생의 과목·학년·목표를 먼저 확인하고, 그에 맞는 비용과 선생님을 함께 안내해 드려요. 모든 선생님은 학력·신원·경력 확인을 거친 뒤에만 매칭에 참여하고, 정식 신청 전에는 30분 무료체험수업으로 먼저 궁합을 확인해보실 수 있습니다. 신청 후 24시간 이내에 담당자가 직접 연락드리고, 학습 진단부터 선생님 추천, 체험 수업까지 순서대로 안내해 드려요. 여수 관내 초·중·고 93곳 전체 학생을 대상으로 매칭이 가능하니, 지금 다니는 학교와 원하는 과목을 알려주시면 그에 맞춰 비용을 상담해 드릴게요. 정확한 비용은 학생의 상황에 따라 달라지기 때문에, 막연히 짐작하기보다 상담을 통해 직접 확인해보시는 게 가장 정확해요. 편하게 문의해주시면 상세히 안내해 드릴게요. 방문과외와 화상과외 중 고민 중이시라면, 두 방식의 비용과 장단점을 함께 비교해서 안내해 드리니 부담 없이 상담받아보세요.</p>
    <p><strong>Q. 화상과외가 방문과외보다 항상 저렴한가요?</strong><br>
    선생님 경력과 과목에 따라 다르지만, 이동 시간과 교통비가 없어 상대적으로 합리적인 경우가 많아요. 정확한 비용은 상담 시 안내해 드려요.</p>
    <p><strong>Q. 비용은 어떻게 확인할 수 있나요?</strong><br>
    상담 신청 시 학생의 과목·학년·희망 시간대를 확인한 뒤, 그에 맞는 비용을 안내해 드려요.</p>
    <p><strong>Q. 30분 체험수업도 비용이 드나요?</strong><br>
    아니요, 30분 무료체험수업은 비용 없이 먼저 궁합을 확인해보실 수 있어요.</p>
    ''',
})


# ---------------------------------------------------------------
# apply.html (noindex, standalone page reusing hero form)
# ---------------------------------------------------------------
apply_body = f'''
<section class="page-hero">
  <span class="eyebrow">30분 무료체험</span>
  <h1>학습 궁합부터 확인하는 화상과외 체험 신청</h1>
  <p>이름과 연락처만 남겨주시면 24시간 이내에 담당자가 직접 연락드려요. 상담과 30분 체험 수업은 모두 무료입니다.</p>
</section>
<section>
  <div class="apply-wrap">
    <div>
      <span class="eyebrow" style="color:var(--accent-strong)">신청 전 확인해주세요</span>
      <h2>이렇게 진행됩니다</h2>
      <ul class="apply-perks">
        <li>신청 후 24시간 이내 담당자 연락</li>
        <li>학습 진단 → 선생님 추천 → 30분 무료체험수업</li>
        <li>체험 수업이 마음에 들 때만 정식으로 결정</li>
      </ul>
      <div style="margin-top:24px; padding-top:20px; border-top:1px solid rgba(255,255,255,.15);">
        <p style="color:#A9BEDA; font-size:13.5px; margin-bottom:10px;">폼 작성이 번거로우시면 전화나 카카오톡으로 바로 상담하셔도 돼요.</p>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
          <a class="cta-ghost" style="border-color:rgba(255,255,255,.35); color:#fff;" href="tel:{PHONE_TEL}">\U0001F4DE 전화 상담</a>
          <a class="cta-ghost" style="border-color:rgba(255,255,255,.35); color:#fff;" href="{KAKAO_URL}" target="_blank" rel="noopener">\U0001F4AC 카카오톡 상담</a>
        </div>
      </div>
    </div>
    {APPLY_FORM}
  </div>
</section>
'''

# ---------------------------------------------------------------
# school page template (level-aware, templated copy + real school name)
# ---------------------------------------------------------------
def school_body(school):
    level = school["level"]
    info = LEVEL_INFO[level]
    same_level_others = [s for s in SCHOOLS if s["level"] == level and s["slug"] != school["slug"]]
    nearby = same_level_others[:5]
    other_links = "\n        ".join(
        '<li><a href="{slug}.html">{name} <span class="arrow">→</span></a></li>'.format(slug=s["slug"], name=s["name"])
        for s in nearby
    )
    subjects_row = "".join('<span>{}</span>'.format(s) for s in info["subjects"])
    return f'''
<nav class="breadcrumb"><a href="../regions.html">{REGION_SHORT} 학교검색</a> / {REGION_FULL} · {level}</nav>
<section class="page-hero">
  <span class="eyebrow">{REGION_FULL} {level} · 화상과외</span>
  <h1>{school["name"]} 화상과외, 학교 특성부터 확인하고 시작하세요</h1>
  <p>{school["name"]} {info["stage"]} 학생을 위해, 학교 사정을 아는 선생님과 실시간 화상으로 연결해 드려요.</p>
</section>
<section>
  <div class="prose">
    <h2>{school["name"]} {info["stage"]}이 상담에서 자주 이야기하는 고민</h2>
    <p>{school["name"]} 학생과 학부모님이 상담에서 가장 많이 말씀하시는 건 <strong>{info["focus"]}</strong>이에요. 특히 <strong>{info["worry"]}</strong>을 어려워하는 경우가 많아요. 학교마다 진도와 분위기가 다르기 때문에, 같은 학년이라도 접근 방식을 다르게 가져가야 해요.</p>
    <p>{BRAND}에서는 상담 시 최근 학습 상태와 취약 부분을 먼저 확인한 뒤, {school["name"]} 같은 {level} 학생을 지도해본 경험이 있거나 {REGION_SHORT} 지역 사정을 아는 선생님을 화상으로 연결해 드립니다.</p>
    <h3>왜 화상과외가 {school["name"]} 학생에게 잘 맞을까요</h3>
    <p>{REGION_SHORT} 안에서 원하는 과목·시간대·스타일의 선생님을 구하기 어려운 경우가 많아요. 화상 수업이면 지역 제약 없이 훨씬 넓은 범위에서 맞는 선생님을 찾을 수 있고, 이동 시간이 없어 저녁 시간대도 유연하게 잡을 수 있어요. 수업은 녹화되어 복습에도 활용할 수 있습니다.</p>
    <h3>과목별 과외 안내</h3>
    <p>{school["name"]} 학생 대상으로는 아래 과목의 화상과외를 안내하고 있어요.</p>
    <div class="subjects" style="margin-bottom:6px;">{subjects_row}</div>
    <p style="margin-top:12px;">{"".join('<a class="subj-link" href="{}-{}.html">{} {}과외</a> '.format(school["slug"], c, school["name"], s) for s, c in SUBJECT_CODES.items())}</p>
  </div>
</section>
<section>
  <div class="head-row"><div><span class="eyebrow">같은 급 다른 학교</span><h2>{level} 학생이 많이 찾는 학교</h2></div></div>
  <ul class="school-list" style="max-width:480px;">
    {other_links}
  </ul>
  <p style="margin-top:14px;font-size:13.5px;"><a href="../regions.html">{REGION_SHORT} 학교 전체 검색하기 →</a></p>
</section>
<section>
  <div class="apply-wrap" style="grid-template-columns:1fr;">
    <div>
      <span class="eyebrow" style="color:var(--accent-strong)">{school["name"]} 학생 학부모님께</span>
      <h2>지금 무료 상담을 신청해보세요</h2>
      <p style="color:#D7E3F2;">이름과 연락처만 남겨주시면 24시간 이내에 담당자가 연락드립니다.</p>
      <div style="margin-top:18px;"><a class="cta-btn" href="../apply.html" style="background:var(--accent);color:#071A2E!important;">무료 상담 신청하기</a></div>
    </div>
  </div>
</section>
'''

# ---------------------------------------------------------------
# 학교 x 과목 페이지 (schools/{slug}-{subj}.html)
# ---------------------------------------------------------------
SUBJECT_CODES = {"국어": "korean", "수학": "math", "영어": "english"}

SUBJ_TEXT = {
    ("초등학교", "국어"): {
        "hero": "읽기·쓰기 기초를 즐겁게 잡는",
        "problem": "책은 좋아하는데 받아쓰기나 수행평가에서 아쉬운 점수가 나오거나, 반대로 글 읽기 자체를 부담스러워하는 경우가 많아요. 초등 국어는 어휘력과 문장 이해가 이후 모든 과목의 바탕이 되기 때문에 이 시기에 습관을 잡아두는 게 중요합니다.",
        "patterns": ["받아쓰기와 맞춤법 실수가 반복된다", "글을 읽고 핵심을 한 문장으로 말하기 어려워한다", "글쓰기 수행평가를 시작하기 막막해한다"],
        "exam": "학교 단원평가와 받아쓰기는 범위가 정해져 있어서, 2주 전부터 어휘·맞춤법을 짧게 매일 반복하는 방식이 효과적이에요. 수행평가는 쓰기 전에 말로 먼저 정리해보는 연습을 함께 합니다.",
        "guide": "하루 15분 소리 내어 읽기, 읽은 내용을 한 문장으로 요약하기, 모르는 낱말 뜻 추측해보기의 세 가지를 꾸준히 이어가도록 안내해요.",
    },
    ("초등학교", "수학"): {
        "hero": "기초 연산과 개념을 탄탄히 다지는",
        "problem": "연산은 잘하는데 문장제 문제만 나오면 막히거나, 학년이 올라가며 분수·비율에서 갑자기 어려워지는 경우가 많아요. 수학은 앞 단원 이해가 뒤 단원으로 이어져서, 어디서 막혔는지 정확히 찾는 게 먼저입니다.",
        "patterns": ["계산은 맞는데 식 세우기를 어려워한다", "분수·소수 개념이 흔들린다", "틀린 문제를 다시 풀기 싫어한다"],
        "exam": "단원평가 전에는 틀린 문제 위주로 복습하고, 서술형은 풀이 과정을 말로 설명해보는 연습을 해요. 결손 단원이 발견되면 그 단원부터 거꾸로 채웁니다.",
        "guide": "매일 짧은 연산 연습, 오답 한 문제 다시 풀기, 풀이를 소리 내어 설명하기 습관을 잡도록 도와드려요.",
    },
    ("초등학교", "영어"): {
        "hero": "듣기·말하기부터 자연스럽게 시작하는",
        "problem": "알파벳과 파닉스는 배웠는데 실제 읽기와 말하기로 이어지지 않거나, 영어를 낯설어하고 부끄러워하는 경우가 많아요. 초등 영어는 성적보다 영어에 대한 거부감을 없애는 게 가장 중요합니다.",
        "patterns": ["파닉스는 아는데 문장을 읽을 때 더듬는다", "듣기는 되는데 말하기를 부끄러워한다", "단어를 외워도 금방 잊는다"],
        "exam": "학교 영어는 평가 부담이 크지 않아서, 시험 대비보다 듣기·말하기 노출을 꾸준히 늘리는 게 핵심이에요. 고학년은 기초 문법과 독해로 서서히 넘어갑니다.",
        "guide": "짧은 영어 영상·노래 듣기, 배운 표현 하루 한 번 말해보기, 쉬운 그림책 읽기를 무리 없이 이어가도록 안내해요.",
    },
    ("중학교", "국어"): {
        "hero": "내신 서술형까지 챙기는",
        "problem": "평소 책은 읽는데 시험에서는 시간이 부족하거나, 서술형·수행평가에서 점수를 놓치는 경우가 많아요. 중학교 국어는 교과서 작품 분석과 문법, 서술형 답안 작성이 함께 나와서 준비 방식이 따로 필요합니다.",
        "patterns": ["문학 작품의 표현법과 주제를 정리하기 어렵다", "문법 개념이 헷갈린다", "서술형 답안에서 감점이 반복된다"],
        "exam": "시험 3주 전에는 교과서 작품 분석과 문법 정리, 2주 전에는 예상 서술형 작성, 1주 전에는 오답과 암기 점검 순서로 진행하는 걸 추천해요. 학교 시험 범위와 출제 유형에 맞춰 조정합니다.",
        "guide": "작품마다 주제·표현·갈래를 한 장으로 정리하고, 서술형은 직접 써서 첨삭받는 방식으로 학습하도록 도와드려요.",
    },
    ("중학교", "수학"): {
        "hero": "수행평가까지 함께 관리하는",
        "problem": "공부 시간은 긴데 점수가 안 오르거나, 중1에서 중2로 넘어가며 방정식·함수에서 갑자기 어려워지는 경우가 많아요. 시간을 늘리는 것보다 어디서 실수하는지 찾아 고치는 게 더 효율적입니다.",
        "patterns": ["개념은 아는데 응용·서술형에서 막힌다", "계산 실수와 조건을 놓치는 실수가 반복된다", "시험 시간 배분이 안 된다"],
        "exam": "시험 3주 전 개념 재정리, 2주 전 유형별 문제 풀이, 1주 전 오답 노트와 실전 시간 연습 순서로 준비해요. 학교별 서술형 비중과 난이도에 맞춰 문제 유형을 고릅니다.",
        "guide": "오답 노트를 단원별로 쌓고, 틀린 이유를 스스로 설명해보고, 모르는 부분은 그날 바로 질문하는 습관을 잡도록 안내해요.",
    },
    ("중학교", "영어"): {
        "hero": "교과서 본문과 서술형을 함께 잡는",
        "problem": "단어는 외우는데 문장 해석이 안 되거나, 본문 암기는 했는데 서술형에서 감점되는 경우가 많아요. 중학교 영어는 본문 분석, 문법, 어휘, 서술형이 골고루 나와서 우선순위를 정하는 게 중요합니다.",
        "patterns": ["문법 개념을 알아도 문제에 적용하지 못한다", "본문을 외웠는데 변형 문제에서 틀린다", "철자·대소문자 실수로 서술형 감점을 당한다"],
        "exam": "본문 구조 분석, 문법 포인트 정리, 어휘 암기, 서술형 쓰기 연습 순서로 시험 3주 전부터 나눠 진행해요. 학교 교과서와 시험 유형에 맞춰 범위를 조정합니다.",
        "guide": "본문을 문장 단위로 해석해보고, 핵심 문법을 예문으로 정리하고, 서술형은 직접 써서 첨삭받는 흐름을 안내해요.",
    },
    ("고등학교", "국어"): {
        "hero": "내신과 비문학 독해를 함께 챙기는",
        "problem": "문학은 어느 정도 되는데 비문학에서 시간이 부족하거나, 내신과 모의고사 준비 방식이 달라 혼란스러운 경우가 많아요. 고등 국어는 학교 범위 암기와 처음 보는 지문 독해가 함께 필요합니다.",
        "patterns": ["비문학 지문을 끝까지 못 푼다", "문학 선택지에서 자꾸 헷갈린다", "내신 범위가 많아 정리가 안 된다"],
        "exam": "내신은 작품·문법 범위를 미리 나눠 정리하고, 모의고사형 지문은 문단 구조 파악 훈련을 병행하는 방식이 효과적이에요. 학교별 출제 경향에 맞춰 비중을 조정합니다.",
        "guide": "문단별 핵심 문장 찾기, 지문 요약 연습, 오답의 근거 문장 확인하기를 꾸준히 이어가도록 도와드려요.",
    },
    ("고등학교", "수학"): {
        "hero": "내신과 모의고사를 함께 대비하는",
        "problem": "내신 대비는 되는데 모의고사에서 점수가 안 나오거나, 진도가 빠르다 보니 앞 단원이 비어 있는 경우가 많아요. 고등 수학은 개념 위에 쌓는 과목이라 결손을 빨리 찾아 메우는 게 중요합니다.",
        "patterns": ["개념은 알지만 응용 문제에서 막힌다", "시험 시간 안에 끝까지 풀지 못한다", "이전 학년 개념이 비어 있다"],
        "exam": "내신은 학교 프린트와 기출 유형 중심으로, 모의고사는 시간 배분과 풀이 순서 연습 중심으로 준비해요. 시험 3주 전부터 단원별 오답 정리를 시작하는 걸 추천합니다.",
        "guide": "오답 노트 작성, 풀이 과정 말로 설명하기, 시간을 재고 푸는 연습을 주기적으로 하도록 안내해요.",
    },
    ("고등학교", "영어"): {
        "hero": "내신과 수능 독해를 함께 준비하는",
        "problem": "중학교 때는 곧잘 했는데 고등 영어 지문이 길어지면서 어려워하거나, 내신 본문 암기와 모의고사 독해가 따로 놀아 부담스러운 경우가 많아요.",
        "patterns": ["지문이 길어지면 해석 속도가 느려진다", "어휘와 구문 이해가 부족하다", "내신 서술형과 변형 문제에서 감점된다"],
        "exam": "내신은 본문 분석과 문법·어휘 정리, 서술형 연습 순서로 준비하고, 모의고사는 독해 속도와 유형별 풀이 훈련을 병행해요. 학교별 출제 방식에 맞춰 조정합니다.",
        "guide": "매일 짧은 지문 읽기, 구문 분석 연습, 어휘 반복 복습을 무리 없이 이어가도록 도와드려요.",
    },
}

def subject_page_slug(school, subj):
    return "{}-{}".format(school["slug"], SUBJECT_CODES[subj])

def school_subject_body(school, subj):
    level = school["level"]
    info = LEVEL_INFO[level]
    t = SUBJ_TEXT[(level, subj)]
    name = school["name"]
    subj_links = "".join(
        '<a href="{}.html" class="{}">{}</a>'.format(subject_page_slug(school, s), "on" if s == subj else "", s)
        for s in SUBJECT_CODES
    )
    patterns = "".join("<li>{}</li>".format(p) for p in t["patterns"])
    related = [p for p in BLOG_POSTS if name in p["title"]][:4]
    related_html = ""
    if related:
        related_html = '<h3>{} 관련 글</h3><ul class="related-list">{}</ul>'.format(
            name, "".join('<li><a href="../blog/{}.html">{}</a></li>'.format(p["slug"], p["title"]) for p in related))
    other_subj = "".join(
        '<li><a href="{}.html">{} {}과외 <span class="arrow">→</span></a></li>'.format(subject_page_slug(school, s), name, s)
        for s in SUBJECT_CODES if s != subj
    )
    faq = [
        ("{} {}과외는 화상으로만 진행되나요?".format(name, subj), "네, {}에서는 1:1 화상과외만 진행합니다. 화면 공유로 문제를 함께 풀고, 수업은 녹화되어 복습에 활용할 수 있어요.".format(BRAND)),
        ("처음부터 등록해야 하나요?", "아니요. 30분 무료체험수업을 먼저 받아보시고, 선생님과 수업 방식이 맞는지 확인한 뒤 결정하시면 됩니다."),
        ("{} 학생이 아니어도 신청할 수 있나요?".format(name), "네, {} 관내 어느 학교든 매칭 가능해요. 재학 중인 학교를 알려주시면 그 학교 상황에 맞춰 안내해 드립니다.".format(REGION_SHORT)),
        ("비용은 어떻게 되나요?", "과목·수업 시간·주당 횟수·선생님 경력에 따라 달라져서 상담 시 안내해 드려요. 체험수업 후 결정하시면 되니 부담 없이 문의해주세요."),
        ("시험 기간에만 수업받아도 되나요?", "가능합니다. 시험 3~4주 전부터 집중 대비하는 방식도 있고, 평소 꾸준히 관리하는 방식도 있어서 상황에 맞게 정해드려요."),
    ]
    faq_html = "".join("<p><strong>Q. {}</strong><br>{}</p>".format(q, a) for q, a in faq)
    return f'''
<nav class="breadcrumb"><a href="../index.html">홈</a> / <a href="{school["slug"]}.html">{name} 과외</a> / {subj}</nav>
<section class="page-hero">
  <span class="eyebrow">{REGION_FULL} {level} · {subj} 화상과외</span>
  <h1>{name} {subj}과외, {t["hero"]} 1:1 화상 수업</h1>
  <p>{name} {info["stage"]}에게 맞춰 {subj} 학습 상태를 먼저 확인하고, 30분 무료체험수업으로 선생님과의 궁합을 확인해보세요.</p>
  <div class="subj-tabs">{subj_links}</div>
  <div style="margin-top:18px;"><a class="cta-btn" href="../apply.html">30분 무료체험 신청하기</a></div>
</section>
<section>
  <div class="prose">
    <h2>{name} {subj}, 이런 고민이 자주 나와요</h2>
    <p>{t["problem"]}</p>
    <ul class="check-list">{patterns}</ul>
    <p>{BRAND}는 상담에서 재학 중인 학교와 최근 학습 상태를 먼저 확인한 뒤, {name} 같은 {level} 학생을 지도해본 경험이 있는 선생님을 화상으로 연결해 드려요.</p>

    <h2>{name} {subj}과외 매칭은 이렇게 진행돼요</h2>
    <ol class="step-list">
      <li><strong>상담</strong> 학교·학년·현재 고민을 간단히 알려주세요.</li>
      <li><strong>선생님 추천</strong> 학생 성향과 목표에 맞는 선생님을 안내해 드려요.</li>
      <li><strong>30분 무료체험수업</strong> 실제 수업을 먼저 받아보고 결정합니다.</li>
      <li><strong>정규 수업</strong> 화상으로 진행하고 수업은 녹화되어 복습에 활용해요.</li>
    </ol>

    <h2>1:1 화상과외 vs 학원 vs 인강</h2>
    <div class="cmp-wrap"><table class="cmp">
      <thead><tr><th></th><th>1:1 화상과외</th><th>학원</th><th>인강</th></tr></thead>
      <tbody>
        <tr><td>맞춤 진도</td><td>학생 수준에 맞춤</td><td>반 진도에 맞춤</td><td>정해진 순서</td></tr>
        <tr><td>즉시 질문</td><td>수업 중 바로 가능</td><td>수업 후 개별 질문</td><td>어려움</td></tr>
        <tr><td>이동 시간</td><td>없음</td><td>있음</td><td>없음</td></tr>
        <tr><td>복습</td><td>수업 녹화 활용</td><td>직접 정리</td><td>영상 반복</td></tr>
        <tr><td>학교별 대비</td><td>학교 범위에 맞춤</td><td>일반 커리큘럼</td><td>일반 커리큘럼</td></tr>
      </tbody>
    </table></div>

    <div class="mid-cta"><strong>우리 아이에게 맞는 {subj} 선생님이 궁금하시다면</strong><br>30분 무료체험수업으로 먼저 확인해보세요. <a class="cta-btn" href="../apply.html">무료체험 신청</a></div>

    <h2>{name} {subj} 시험 대비 전략</h2>
    <p>{t["exam"]}</p>
    <p>학교마다 시험 범위와 출제 방식이 조금씩 다르기 때문에, 상담 때 최근 시험 결과나 오답 유형을 알려주시면 그에 맞춰 준비 순서를 잡아드려요.</p>

    <h2>{subj} 공부법 가이드</h2>
    <p>{t["guide"]}</p>
    <p>혼자 하기 어려운 부분은 수업 중에 함께 점검하고, 아이가 부담 느끼지 않는 분량으로 꾸준히 이어가는 것을 가장 중요하게 생각합니다.</p>

    <h2>자주 묻는 질문</h2>
    {faq_html}
    {related_html}
  </div>
</section>
<section>
  <div class="head-row"><div><span class="eyebrow">다른 과목</span><h2>{name} 다른 과목 과외</h2></div></div>
  <ul class="school-list" style="max-width:480px;">{other_subj}</ul>
  <p style="margin-top:14px;font-size:13.5px;"><a href="{school["slug"]}.html">{name} 화상과외 전체 안내 →</a> · <a href="../regions.html">{REGION_SHORT} 학교 전체 검색 →</a></p>
</section>
<section>
  <div class="apply-wrap" style="grid-template-columns:1fr;">
    <div>
      <span class="eyebrow" style="color:var(--accent-strong)">{name} {subj}과외</span>
      <h2>30분 무료체험수업으로 먼저 확인하세요</h2>
      <p style="color:#D7E3F2;">이름과 연락처만 남겨주시면 24시간 이내에 담당자가 연락드립니다.</p>
      <div style="margin-top:18px;"><a class="cta-btn" href="../apply.html" style="background:var(--accent);color:#071A2E!important;">무료 상담 신청하기</a></div>
    </div>
  </div>
</section>
'''

import concise_data
concise_data.REGION = REGION_SHORT
for _p in BLOG_POSTS:
    if _p["slug"] in concise_data.D:
        _p["body"] = concise_data.render(concise_data.D[_p["slug"]], _p["slug"])

# generate all pages
# ---------------------------------------------------------------
page("index.html", f"{REGION_SHORT} 과외 | 초등·중등·고등 수학 영어 1:1 화상과외 · {BRAND}", f"{REGION_SHORT} 과외를 찾고 계신가요? 초등학생부터 고등학생까지, 수학·영어·국어 등 전 과목 1:1 화상과외를 30분 무료체험수업으로 먼저 받아보세요.", "index.html",
     index_body,
     path_prefix="", canonical=BASE_URL + "/index.html")

page("services.html", f"화상과외 소개 | {BRAND}", f"{REGION_SHORT} 학생을 위한 실시간 화상과외, 녹화 복습, 지역 맞춤 매칭을 소개합니다.", "services.html",
     services_body, path_prefix="", canonical=BASE_URL + "/services.html")

page("process.html", f"매칭 방식 | {BRAND}", f"학습 진단부터 리포트까지, {BRAND}의 5단계 화상과외 매칭 프로세스를 소개합니다.", "process.html",
     process_body, path_prefix="", canonical=BASE_URL + "/process.html")

page("teachers.html", f"선생님 소개 | {BRAND}", f"학력·신원·경력 검증을 거친 {BRAND} 화상과외 선생님 매칭 기준을 소개합니다.", "teachers.html",
     teachers_body, path_prefix="", canonical=BASE_URL + "/teachers.html", extra_js=teachers_js)

page("regions.html", f"{REGION_SHORT} 학교검색 | {BRAND}", f"{REGION_SHORT} 초·중·고 {len(SCHOOLS)}개 학교를 검색해서 바로 찾는 {BRAND} 화상과외 학교 안내입니다.", "regions.html",
     regions_body, path_prefix="", canonical=BASE_URL + "/regions.html", extra_js=regions_js)

page("blog.html", f"블로그 | {BRAND}", f"{REGION_SHORT} 학교별 내신 대비, 과목별 화상과외 학습 전략을 소개하는 {BRAND} 블로그입니다.", "blog.html",
     build_blog_body(), path_prefix="", canonical=BASE_URL + "/blog.html")

for post in BLOG_POSTS:
    page(
        "blog/{}.html".format(post["slug"]),
        "{} | {}".format(post["title"], BRAND),
        post["teaser"],
        "blog.html",
        blog_post_body(post),
        path_prefix="../",
        canonical=BASE_URL + "/blog/{}.html".format(post["slug"]),
        og_image=(BASE_URL + "/blog/img/{}.jpg".format(post["slug"])) if os.path.exists(os.path.join(ROOT, "blog", "img", post["slug"] + ".webp")) else "",
    )

page("apply.html", f"무료 상담 신청 | {BRAND}", f"{BRAND} 화상과외 매칭 무료 상담을 신청하세요.", "apply.html",
     apply_body, path_prefix="", canonical=BASE_URL + "/apply.html", noindex=True)

thanks_body = '''
<section class="page-hero" style="text-align:center;">
  <span class="eyebrow">신청 완료</span>
  <h1>상담 신청이 접수되었습니다</h1>
  <p style="max-width:52ch;margin-inline:auto;">24시간 이내에 담당자가 남겨주신 연락처로 안내드릴게요. 잠시만 기다려 주세요.</p>
  <div style="margin-top:22px;"><a class="cta-btn" href="index.html">홈으로 돌아가기</a></div>
</section>
'''
page("thanks.html", f"신청 완료 | {BRAND}", f"{BRAND} 상담 신청이 정상적으로 접수되었습니다.", "",
     thanks_body, path_prefix="", canonical=BASE_URL + "/thanks.html", noindex=True)

for school in SCHOOLS:
    page(
        "schools/{}.html".format(school["slug"]),
        "{} 화상과외 | {}".format(school["name"], BRAND),
        "{} 학생을 위한 1:1 화상과외 매칭, {}에서 상담해보세요.".format(school["name"], BRAND),
        "regions.html",
        school_body(school),
        path_prefix="../",
        canonical=BASE_URL + "/schools/{}.html".format(school["slug"]),
    )
    for subj in SUBJECT_CODES:
        page(
            "schools/{}.html".format(subject_page_slug(school, subj)),
            "{} {}과외 | 1:1 화상 {}".format(school["name"], subj, BRAND),
            "{} {}과외 고민, 학교 상황에 맞춰 1:1 화상으로 시작하세요. 30분 무료체험수업 가능. {}".format(school["name"], subj, BRAND),
            "regions.html",
            school_subject_body(school, subj),
            path_prefix="../",
            canonical=BASE_URL + "/schools/{}.html".format(subject_page_slug(school, subj)),
        )

# ---------------------------------------------------------------
# sitemap.xml (public pages only)
# ---------------------------------------------------------------
sitemap_urls = ["index.html", "services.html", "process.html", "teachers.html", "regions.html", "blog.html"]
for school in SCHOOLS:
    sitemap_urls.append("schools/{}.html".format(school["slug"]))
    for subj in SUBJECT_CODES:
        sitemap_urls.append("schools/{}.html".format(subject_page_slug(school, subj)))
for post in BLOG_POSTS:
    sitemap_urls.append("blog/{}.html".format(post["slug"]))

sitemap_items = "\n".join(
    "  <url><loc>{}/{}</loc></url>".format(BASE_URL, u) for u in sitemap_urls
)
sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{}\n</urlset>\n'.format(sitemap_items)
with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap_xml)
print("wrote sitemap.xml")

# ---------------------------------------------------------------
# rss.xml (blog posts, newest first)
# ---------------------------------------------------------------
def rss_pubdate(date_str):
    import datetime
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%a, %d %b %Y 00:00:00 +0900")

rss_items = "\n".join('''  <item>
    <title>{title}</title>
    <link>{base}/blog/{slug}.html</link>
    <guid>{base}/blog/{slug}.html</guid>
    <description>{teaser}</description>
    <pubDate>{pubdate}</pubDate>
  </item>'''.format(title=p["title"], base=BASE_URL, slug=p["slug"], teaser=p["teaser"], pubdate=rss_pubdate(p["date"]))
    for p in sorted(BLOG_POSTS, key=lambda p: p["date"], reverse=True)
)
rss_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{brand} 블로그</title>
  <link>{base}/blog.html</link>
  <description>{region} 학교별 내신·과목별 화상과외 학습 전략</description>
  <language>ko-kr</language>
  <atom:link href="{base}/rss.xml" rel="self" type="application/rss+xml"/>
  <lastBuildDate>{lastbuild}</lastBuildDate>

  <!-- RSS_ITEMS_START -->
{items}
  <!-- RSS_ITEMS_END -->

</channel>
</rss>
'''.format(brand=BRAND, base=BASE_URL, region=REGION_SHORT, items=rss_items,
           lastbuild=rss_pubdate(BLOG_POSTS[0]["date"]) if BLOG_POSTS else rss_pubdate("2026-01-01"))
with open(os.path.join(ROOT, "rss.xml"), "w", encoding="utf-8") as f:
    f.write(rss_xml)
print("wrote rss.xml")

robots_txt = '''User-agent: *
Disallow: /apply.html
Disallow: /thanks.html
Allow: /

Sitemap: {}/sitemap.xml
'''.format(BASE_URL)
with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(robots_txt)
print("wrote robots.txt")

print("DONE - {} schools (region: {})".format(len(SCHOOLS), REGION_SLUG))
