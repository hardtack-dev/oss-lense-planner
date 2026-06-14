# core/assets.py (로컬 이미지 조회)
# 사진이 있으면 경로를 돌려주고, 없으면 None (호출부에서 아이콘/플레이스홀더로 폴백).
# 카메라: front/assets/cameras/{body_id}.jpg
# 렌즈:   front/assets/lenses/{lens_id}__{mount}.jpg
import os

import streamlit as st

# 에셋 폴더 경로 (이 파일 기준 ../assets)
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
EXTS = (".jpg", ".jpeg", ".png", ".webp")  # 이 순서로 먼저 찾은 파일을 사용


# assets/{category}/{name}.<확장자> 중 먼저 존재하는 파일 경로를 돌려주기 (없으면 None)
def find_asset(category, name):
    if not name:
        return None
    for ext in EXTS:
        file_path = os.path.join(ASSETS_DIR, category, name + ext)
        if os.path.exists(file_path):
            return file_path
    return None


# 이미지 바이너리 캐싱
# 매 rerun마다 디스크에서 다시 읽지 않도록 한 번 읽은 바이트를 캐싱
@st.cache_data(show_spinner=False)
def load_image(path):
    with open(path, "rb") as f:
        return f.read()
