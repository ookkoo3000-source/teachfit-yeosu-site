import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_image
ROOT = gen_image.ROOT
# slug -> (표시 이름, 부제). 새 글을 발행하면 여기에 한 줄 추가하고 python scripts/gen_all_images.py 실행
POSTS = {
    "yeosu-hs-gimalgosa-daebi": ("여수고등학교", "기말고사 대비 | 30분 무료체험"),
    "yeosu-ms-naeshin-gwanri": ("여수중학교", "내신 관리 | 30분 무료체험"),
    "yeosuyeoja-hs-suneung-gukeo": ("여수여자고등학교", "수능 국어 | 30분 무료체험"),
    "yeodo-es-haksseub-seupgwan": ("여도초등학교", "학습 습관 | 30분 무료체험"),
    "yeocheon-ms-suhak-gwaoe": ("여천중학교", "수학 과외 | 30분 무료체험"),
    "hwayang-ms-yeongeo-naeshin": ("화양중학교", "영어 내신 | 30분 무료체험"),
    "yeosugongeob-hs-gimalgosa": ("여수공업고등학교", "기말고사 대비 | 30분 무료체험"),
    "jinseongyeoja-hs-gukeo-naeshin": ("진성여자고등학교", "국어 내신 | 30분 무료체험"),
    "yeosugubong-es-seonhaeng": ("여수구봉초등학교", "선행학습 | 30분 무료체험"),
    "yeosu-hwasang-gwaoe-biyong": ("여수 학부모님", "과외 비용 안내 | 30분 무료체험"),
}
for slug, (name, sub) in POSTS.items():
    out = os.path.join(ROOT, "blog", "img", slug + ".webp")
    if os.path.exists(out):
        continue
    for attempt in range(3):
        try:
            gen_image.generate(name, slug, sub)
            break
        except Exception as e:
            print("retry", slug, str(e)[:120]); time.sleep(8)
    time.sleep(2)
print("ALL DONE")
