# 렌즈 플래너 (Lens Planner)

카메라와 촬영 스타일을 입력하면, **환산 화각**을 계산해 알맞은 렌즈를 추천해 주는 웹 애플리케이션입니다.
(오픈소스소프트웨어 실습 기말 대체과제로 **Streamlit · FastAPI · Docker · AWS EC2** 로 구현하였습니다)

## 주요 기능
- 카메라(마운트·센서·crop) + 촬영 주제 + 예산·우선순위 입력
- 카메라 crop을 반영한 **환산 화각 적합도** 기반 렌즈 추천 (상위 3종)
- 추천 렌즈 화각 비교 / 초점거리 화각 시뮬레이터 (Plotly)

## 기술 스택
- **프론트엔드**: Streamlit
- **백엔드**: FastAPI (Pydantic, uvicorn)
- **시각화**: Plotly
- **배포**: Docker / docker-compose, AWS EC2


## 실행 방법
### Docker (권장)
```bash
docker compose up --build
# 브라우저에서 http://localhost:8501 접속
```

### 로컬 실행
```bash
# 백엔드
cd back
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# 프론트엔드 (다른 터미널)
cd front
pip install -r requirements.txt
streamlit run app.py
```

## API 엔드포인트
- `GET /okay` : 헬스 체크
- `GET /catalog` : 입력 옵션(카메라·주제·예산 범위·렌즈 형태)
- `POST /recommend-lens` : 입력값을 받아 추천 렌즈 반환

## 폴더 구조
```
.
├── docker-compose.yml
├── back/                 # FastAPI 백엔드
│   ├── main.py           # 엔드포인트
│   ├── recommend.py      # 추천 로직
│   └── data/             # 카메라·렌즈 데이터(JSON)
└── front/                # Streamlit 프론트엔드
    ├── app.py
    ├── pages/            # 랜딩 / 입력 / 결과
    ├── core/             # state·api·fov·assets
    └── assets/           # 카메라·렌즈 이미지
```

## 제출자
- 학번: 2023204006
- 이름: 하건우
