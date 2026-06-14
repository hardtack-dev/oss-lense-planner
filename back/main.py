# back/main.py (FastAPI 백엔드 엔트리)
# 추천 결과를 JSON으로 반환
# 엔드포인트: /okay, /catalog, /recommend-lens
from fastapi import FastAPI
from pydantic import BaseModel, Field

import recommend

app = FastAPI(title="렌즈 플래너 API", version="0.1.0")


# 추천 요청 바디 (FastAPI가 타입 검증)
class RecommendRequest(BaseModel):
    body_id: str | None = None     # 목록 카메라면 ID, 직접 선택이면 None
    subjects: list[str] = Field(default_factory=list)
    lens_type: str = "상관없음"
    low_light: int = 3  # 1~5
    budget: int = 99_999_999
    priority: str = "화질"  # 화질 / 휴대성 / 가성비
    portability: int = 3   # 1~5
    # 목록에 없는 카메라(직접 선택)용 - body_id가 None일 때 사용
    mount: str | None = None
    sensor: str | None = None
    crop: float = 1.0
    cam_title: str | None = None


# 백엔드 상태 체크용
@app.get("/okay")
def okay():
    return {"status": "ok"}


# Step1 입력 옵션(카메라/주제/예산범위/렌즈형태) 제공
@app.get("/catalog")
def get_catalog():
    return recommend.catalog()


# 입력 -> 필터,점수,정렬 -> 추천 렌즈 리스트
@app.post("/recommend-lens")
def recommend_lens(req: RecommendRequest):
    return recommend.recommend(
        body_id=req.body_id, # 카메라 바디 ID (없으면 None)
        subjects=req.subjects, # 촬영 주제 리스트
        lens_type=req.lens_type, # 렌즈 형태 (단렌즈/줌렌즈/상관없음)
        low_light=req.low_light, # 저조도 중요도 (1~5)
        budget=req.budget, # 예산 (원 단위)
        priority=req.priority, # 우선순위 (화질/휴대성/가성비)
        portability=req.portability, # 휴대성 중요도 (1~5)
        mount=req.mount, # 직접 선택 시 마운트
        sensor=req.sensor, # 직접 선택 시 센서 종류
        crop=req.crop, # 직접 선택 시 크롭 배율
        cam_title=req.cam_title, # 직접 선택 시 표시용 이름
    )
