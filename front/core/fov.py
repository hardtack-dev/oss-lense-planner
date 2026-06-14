# core/fov.py (화각 계산 + 부채꼴/센서 다이어그램)
# 실제 초점거리 f, 센서 한 변 d 일 때  AOV = 2 * atan(d / (2*f)) 
# 환산 초점거리 eff_focal = f * crop (crop=1이면 풀프레임 기준)
import math
import plotly.graph_objects as go


# 한 변(가로 또는 세로)에 대한 화각(도) 계산
def angle_of_view(focal_mm, sensor_dim_mm):
    return math.degrees(2 * math.atan(sensor_dim_mm / (2 * focal_mm)))


# 환산 화각으로 광각~초망원 분류
def classify(eff_focal):
    if eff_focal < 24:
        return "초광각"
    if eff_focal < 35:
        return "광각"
    if eff_focal < 70:
        return "표준"
    if eff_focal < 135:
        return "망원"
    return "초망원"


# 분류별 어울리는 피사체
SUITED = {
    "초광각": ["풍경", "건축", "인테리어"],
    "광각":   ["풍경", "단체", "실내 스냅"],
    "표준":   ["일상 스냅", "거리", "인물"],
    "망원":   ["인물", "클로즈업", "공연"],
    "초망원": ["스포츠", "야생", "달 촬영"],
}


# 특정 초점거리에 대한 화각 정보 묶음
def fov_point(focal_mm, crop, sensor_w, sensor_h):
    eff_focal = focal_mm * crop
    category = classify(eff_focal)
    return {
        "focal": round(focal_mm),
        "eff_focal": round(eff_focal),
        "h_aov": round(angle_of_view(focal_mm, sensor_w), 1),
        "v_aov": round(angle_of_view(focal_mm, sensor_h), 1),
        "category": category,
        "suited_for": SUITED[category],
    }


# 부채꼴 다이어그램 그리기 (plotly)
# 화각(n도)을 부채꼴로 변환 ,12시 방향 중심 좌우 대칭
def wedge_xy(aov_deg, radius=1.0, n=48):
    half = math.radians(aov_deg / 2)
    base = math.pi / 2
    thetas = [base - half + (2 * half) * i / (n - 1) for i in range(n)]
    xs = [0.0] + [radius * math.cos(t) for t in thetas] + [0.0]
    ys = [0.0] + [radius * math.sin(t) for t in thetas] + [0.0]
    return xs, ys


# 단일 화각 부채꼴
def wedge_figure(h_aov, label, height=340):
    xs, ys = wedge_xy(h_aov)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys, fill="toself", mode="lines",
        line=dict(color="#4CAF50"), fillcolor="rgba(76,175,80,0.25)",
        hoverinfo="skip", name=label,
    ))
    fig.add_annotation(x=0, y=-0.08, text="📷", showarrow=False, font=dict(size=22))
    fig.add_annotation(x=0, y=1.05, text=f"{label} · {h_aov:.1f}°",
                       showarrow=False, font=dict(size=14))
    style_fig(fig, height=height)
    return fig


PALETTE = ["#4CAF50", "#2196F3", "#FF9800", "#E91E63", "#9C27B0"]


# 여러 화각을 반지름 다르게 겹쳐 비교 (망원일수록 짧고 좁게)
def compare_figure(items):
    fig = go.Figure()
    # 넓은 화각(광각)을 먼저 그려 뒤로, 좁은 화각을 앞으로
    items_sorted = sorted(items, key=lambda d: d["h_aov"], reverse=True)
    for i, item in enumerate(items_sorted):
        color = PALETTE[i % len(PALETTE)]
        radius = 0.45 + 0.55 * (item["h_aov"] / max(x["h_aov"] for x in items))
        xs, ys = wedge_xy(item["h_aov"], radius=radius)
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill="toself", mode="lines",
            line=dict(color=color), opacity=0.45,
            name=f'{item["eff_focal"]}mm ({item["h_aov"]:.0f}°)',
        ))
    fig.add_annotation(x=0, y=-0.08, text="📷", showarrow=False, font=dict(size=22))
    style_fig(fig, legend=True)
    return fig


# 표준 센서 포맷(이름, 가로mm, 세로mm, 색) - 큰 것부터 현재 센서를 이 위에 강조.
SENSOR_FORMATS = [
    ("풀프레임", 35.9, 24.0, "#607D8B"),
    ("APS-C", 23.5, 15.6, "#FF9800"),
    ("마이크로포서드", 17.3, 13.0, "#9C27B0"),
]


# 센서 크기 그리기 함수
# 작을수록 크롭이 큰 거임 = 같은 렌즈라도 화각이 좁아진다고 함.
# compact=True 면 라벨/주석 없이 작은 썸네일(텍스트 옆 배치용)로 그릴수 있음!!
def sensor_figure(sensor_w, sensor_h, crop, compact=False):
    ff_w, ff_h = SENSOR_FORMATS[0][1], SENSOR_FORMATS[0][2]
    fig = go.Figure()
    # 기준 포맷 윤곽선(점선) + (컴팩트가 아니면) 우상단 라벨
    for name, w, h, color in SENSOR_FORMATS:
        fig.add_shape(type="rect", x0=-w / 2, y0=-h / 2, x1=w / 2, y1=h / 2,
                      line=dict(color=color, width=1.5, dash="dot"),
                      fillcolor="rgba(0,0,0,0)")
        if not compact:
            fig.add_annotation(x=w / 2, y=h / 2, text=f" {name}", xanchor="left",
                               yanchor="bottom", showarrow=False,
                               font=dict(size=10, color=color))
    # 내 센서 강조(사각형 채구기)
    fig.add_shape(type="rect", x0=-sensor_w / 2, y0=-sensor_h / 2,
                  x1=sensor_w / 2, y1=sensor_h / 2,
                  line=dict(color="#4CAF50", width=2.5),
                  fillcolor="rgba(76,175,80,0.35)")
    if not compact:
        fig.add_annotation(x=0, y=-ff_h / 2 - 1.8,
                           text=f"내 센서 ×{crop:g} · {sensor_w}×{sensor_h}mm",
                           showarrow=False, font=dict(size=11, color="#2E7D32"))

    # 컴팩트 여부에 따라 크기/여백 조정
    if compact:
        xr = [-ff_w / 2 - 1, ff_w / 2 + 1]
        yr = [-ff_h / 2 - 1, ff_h / 2 + 1]
        height, top = 150, 6
    else:
        xr = [-ff_w / 2 - 2, ff_w / 2 + 13]
        yr = [-ff_h / 2 - 4, ff_h / 2 + 3]
        height, top = 230, 20
    fig.update_layout(
        margin=dict(l=6, r=6, t=top, b=6), height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, range=xr, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False, range=yr),
    )
    return fig


# 부채꼴 차트 공통 레이아웃 (배경 투명, 정사각 비율)
def style_fig(fig, legend=False, height=340):
    fig.update_layout(
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=30, b=10),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, range=[-1.1, 1.1], scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False, range=[-0.2, 1.2]),
    )
