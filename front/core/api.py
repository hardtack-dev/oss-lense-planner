# core/api.py (백엔드 통신 전담 모듈)
# GET/POST 요청 함수, 백엔드 연결 실패 시 공통 처리 함수, 그리고 백엔드 API별 호출 함수
import os

import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 2  # 초 단위


# GET 요청 (실패하면 예외)
def base_get(path):
    res = requests.get(f"{BACKEND_URL}{path}", timeout=TIMEOUT)
    res.raise_for_status()
    return res.json()


# POST 요청 (실패하면 예외)
def base_post(path, payload):
    res = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=TIMEOUT)
    res.raise_for_status()
    return res.json()


# 백엔드 연결 실패 시 공통 처리 (안내 후 정지)
def connection_error():
    st.error("백엔드에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()


# [공개] 카탈로그(카메라/주제/예산범위) 가져오기
def get_catalog():
    try:
        return base_get("/catalog")
    except Exception:
        print("[LOG]: 백엔드 연결 실패 -> /catalog")
        connection_error()


# [공개] 입력값으로 렌즈 추천 받기
def recommend_lens(payload):
    try:
        return base_post("/recommend-lens", payload)
    except Exception:
        print("[LOG]: 백엔드 연결 실패 -> /recommend-lens")
        connection_error()
