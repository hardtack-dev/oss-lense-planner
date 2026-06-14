# back/recommend.py (렌즈 추천 로직)
# 입력(사용자 선택) + 정적 데이터(bodies/lenses)를 받아 추천 결과 생성
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# data 폴더의 JSON 읽기
def load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


BODIES = load_json("bodies.json")["bodies"]
LENSES = load_json("lenses.json")["lenses"]

# 사용자에게 보여줄 촬영 주제. 입력 multiselect는 key/label 사용
SUBJECTS = [
    {"key": "인물",       "label": "👤 인물",        "tags": ["인물", "클로즈업"]},
    {"key": "풍경/여행",  "label": "🏞️ 풍경·여행",   "tags": ["풍경", "건축", "여행", "스냅"]},
    {"key": "일상/거리",  "label": "🚶 일상·거리",   "tags": ["일상", "거리", "스냅"]},
    {"key": "실내/음식",  "label": "🍽️ 실내·음식",   "tags": ["실내", "음식"]},
    {"key": "스포츠/동물", "label": "🐦 스포츠·동물", "tags": ["스포츠", "야생", "망원압축"]},
    {"key": "접사/제품",  "label": "🔬 접사·제품",   "tags": ["접사", "제품", "꽃", "디테일"]},
    {"key": "공연/무대",  "label": "🎤 공연·무대",   "tags": ["공연", "클로즈업"]},
]

LENS_TYPES = ["상관없음", "단렌즈", "줌렌즈"]

# 마운트 -> 이미지 파일명 코드. 렌즈 사진: front/assets/lenses/{lens_id}__{mount}.jpg
MOUNT_IMG = {
    "Sony E": "sony_e", "Canon RF": "canon_rf", "Nikon Z": "nikon_z",
    "Fujifilm X": "fuji_x", "Leica L": "leica_l", "Micro Four Thirds": "mft",
}

# 주제별 이상적인 환산 화각대(35mm 환산 mm)
# 렌즈의 focal x crop이 이 구간에 얼마나 드는지로 계산
SUBJECT_FOCAL = {
    "인물":        (50, 135),
    "풍경/여행":   (16, 40),
    "일상/거리":   (28, 50),
    "실내/음식":   (24, 50),
    "스포츠/동물": (100, 400),
    "접사/제품":   (60, 105),
    "공연/무대":   (85, 200),
}


# body_id로 카메라 한 대 찾기
def get_body(body_id):
    return next((b for b in BODIES if b["id"] == body_id), None)


# Step1 옵션 제공용 (카메라 / 주제 / 예산범위 / 렌즈형태)
def catalog():
    prices = [ # 모든 렌즈 스펙의 가격 리스트 담기 (예산범위 계산용)
        spec["price"]
        for lens in LENSES # 렌즈 8개 순회(화각별)
        for spec in lens["by_mount"].values() #by_mount안에 담긴 렌즈들의 가격 가져오기
    ]
    return { # 응답으로 제공
        "cameras": [
            {
                "id": b["id"], "title": b["title"], "brand": b["brand"],
                "mount": b["mount"], "sensor": b["sensor"], "crop": b["crop"],
                "sensor_w_mm": b["sensor_w_mm"], "sensor_h_mm": b["sensor_h_mm"],
            }
            for b in BODIES
        ],
        "subjects": SUBJECTS,
        "lens_types": LENS_TYPES,
        "budget_range": {"min": min(prices), "max": max(prices)},
    }


# 실제 초점거리 -> 환산 화각 문자열 ("75mm" 또는 "36-105mm")
def eff_focal_str(focal_min, focal_max, crop):
    lo = round(focal_min * crop)
    hi = round(focal_max * crop)
    return f"{lo}mm" if lo == hi else f"{lo}-{hi}mm"


# 개방 조리개가 밝을수록(작을수록) 큰 값. F3.5 이상은 0.
def brightness_score(max_aperture):
    return max(0.0, 3.5 - max_aperture)


# 가벼울수록 0~1 사이 큰 값
def lightness_score(weight):
    return max(0.0, (800 - weight) / 800)


# 렌즈 환산 화각 구간이 주제 이상구간에 얼마나 닿는지 0~1.
# 구간이 겹치면 1.0, 멀어질수록 선형으로 감소.
def focal_fit(eff_min, eff_max, lo, hi, decay=60.0):
    if eff_max < lo:
        gap = lo - eff_max
    elif eff_min > hi:
        gap = eff_min - hi
    else:
        gap = 0.0
    return max(0.0, 1.0 - gap / decay)


# 추천 이유 문장 만들기 (화각 적합도 + 크롭 보정 + 밝은조리개 + 경량)
def build_reason(lens, spec, body, fits, low_light, portability):
    parts = []
    eff = eff_focal_str(spec["focal_min"], spec["focal_max"], body["crop"])

    # 가장 잘 맞는 주제를 화각 적합도로 설명
    best_subj = max(fits, key=fits.get) if fits else None
    if best_subj and fits[best_subj] >= 0.5:
        parts.append(f"환산 {eff}가 {best_subj} 화각대에 잘 맞는 {lens['role']}")
    else:
        parts.append(f"두루 쓰기 좋은 {lens['role']} (환산 {eff})")

    # 크롭 보정 설명 (크롭 바디면 환산 화각이 더 넓어지는 점)
    if abs(body["crop"] - 1.0) > 0.01:
        nat = (f"{spec['focal_min']}mm" if spec["focal_min"] == spec["focal_max"]
               else f"{spec['focal_min']}-{spec['focal_max']}mm")
        parts.append(f"{body['sensor']}({body['crop']}×)에선 {nat}가 {eff}처럼 보여요")

    # 저조도 중요하면 밝은 조리개(f값) 강조, 휴대성 중요하면 가벼움 강조
    if low_light >= 4 and brightness_score(spec["max_aperture"]) > 0:
        parts.append(f"F{spec['max_aperture']} 밝은 조리개로 저조도·배경흐림에 유리")
    if portability >= 4 and lightness_score(spec["weight"]) > 0.5:
        parts.append(f"{spec['weight']}g으로 가벼워 휴대 부담이 적음")

    return ". ".join(parts) + "."

#   1) 필터: 마운트 호환 + 예산 + 렌즈형태
#   2) 점수(가중합): 화각 적합도 + 저조도 + 휴대성 + 우선순위
#   3) 총점 높은 순 정렬 -> 상위 N개
#   4) 실제 제품명 + 이유 문장으로 가공
def recommend(body_id, subjects, lens_type="상관없음",
              low_light=3, budget=99_999_999,
              priority="화질", portability=3, top_k=3,
              mount=None, sensor=None, crop=1.0, cam_title=None):
    print(f"[LOG]: 추천 계산 시작 (body={body_id}, subjects={subjects})")
    body = get_body(body_id)
    if body is None:
        # 목록에 없는 카메라(직접 선택): 마운트/센서/크롭으로 body 구성
        if not mount:
            return {"error": "마운트 정보가 없어 추천할 수 없습니다.", "results": []}
        body = {"title": cam_title or "내 카메라", "mount": mount,
                "sensor": sensor or "직접 입력", "crop": crop}

    mount = body["mount"]
    crop = body["crop"]

    scored = []
    for lens in LENSES:
        spec = lens["by_mount"].get(mount)
        if spec is None:  # 마운트 비호환
            continue
        if spec["price"] > budget: # 예산 초과
            continue
        if lens_type == "단렌즈" and lens["type"] not in ("단렌즈", "매크로"):
            continue
        if lens_type == "줌렌즈" and lens["type"] != "줌렌즈":
            continue

        # 환산 화각 구간(focal x crop) - 카메라(crop)가 점수에 들어가는 지점
        eff_min = spec["focal_min"] * crop
        eff_max = spec["focal_max"] * crop

        # 1) 화각 적합도: 고른 주제의 이상 화각대에 얼마나 맞는지 (연속값 0~1)
        fits = {s: focal_fit(eff_min, eff_max, *SUBJECT_FOCAL[s])
                for s in subjects if s in SUBJECT_FOCAL}
        # 고른 주제 중 가장 잘 맞는 값을 사용 (없으면 중립 0.5)
        fit = max(fits.values()) if fits else 0.5
        fit_score = fit * 3.0

        # 접사/제품은 화각만으론 부족하므로, 매크로 렌즈면 점수 크게 가산, 아니면 감산.
        # 밝은 조리개 점수에 묻히지 않도록 강하게 가/감산.
        if "접사/제품" in subjects:
            fit_score += 2.0 if lens["type"] == "매크로" else -1.5

        # 2) 저조도/배경흐림: 밝은 조리개 x 중요도
        bright = brightness_score(spec["max_aperture"])
        low_light_score = bright * (low_light / 5) * 1.2

        # 3) 휴대성: 가벼움 x 우선도
        light = lightness_score(spec["weight"])
        portability_score = light * (portability / 5) * 1.2

        # 4) 우선순위 (약한 가중 겸 동점 보정)
        if priority == "화질":
            pr = bright * 0.5 + (0.6 if lens["type"] in ("단렌즈", "매크로") else 0.0) # 화질 우선이면 밝기와 단렌즈 보정
        elif priority == "휴대성":
            pr = light * 1.2
        else:  # 가성비
            pr = max(0.0, (budget - spec["price"]) / budget) * 1.2 if budget else 0.0 # 예산이 있을 때만 가성비 점수 계산
        priority_score = pr

        total = fit_score + low_light_score + portability_score + priority_score # 총점 계산 (화각 적합도 + 저조도 + 휴대성 + 우선순위)

        # 정렬 전 점수 append
        scored.append({"lens": lens, "spec": spec, "fits": fits, "total": total})

    # 정렬: 총점 높은 순
    scored.sort(key=lambda x: x["total"], reverse=True)

    # 상위 top_k개를 실제 제품 정보 + 이유 문장으로 가공
    results = []
    for item in scored[:top_k]:
        lens, spec = item["lens"], item["spec"]
        results.append({
            "name": spec["product"], # 제품명
            "role": lens["role"], # 인물용/풍경용 등 렌즈의 주된 용도
            "type": lens["type"], # 단렌즈/줌렌즈/매크로
            "focal": (f"{spec['focal_min']}mm" if spec["focal_min"] == spec["focal_max"] # 실제 초점거리
                      else f"{spec['focal_min']}-{spec['focal_max']}mm"), 
            "eff_focal": eff_focal_str(spec["focal_min"], spec["focal_max"], crop), # 환산 화각
            "aperture": spec["max_aperture"], # 최대 개방 조리개 (밝기)
            "price": spec["price"], # 가격
            "weight": spec["weight"],# 무게
            "tags": lens["good_for"],# 렌즈의 추천 주제 태그 (인물, 풍경..)
            "reason": build_reason(lens, spec, body, item["fits"], low_light, portability), # 추천 이유 문장
            "score": round(item["total"], 2), # 총점 (화각 적합도 + 저조도 + 휴대성 + 우선순위)
            "img": f"{lens['id']}__{MOUNT_IMG.get(mount, mount)}", # 사진 파일명
        })

    return { # 응답으로 추천 결과 반환
        "body": {"title": body["title"], "mount": mount,
                 "sensor": body["sensor"], "crop": crop},
        "results": results,
        "total_candidates": len(scored),
    }
