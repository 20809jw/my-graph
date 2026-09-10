import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# 타이틀 및 설명
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("일별 박스오피스 데이터를 바탕으로 시각화한 데이터 분석 도감입니다.")

# 데이터 불러오기 및 전처리 (캐싱)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)
    
    # 8자리 숫자 날짜(YYYYMMDD)를 datetime 객체로 변환
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    
    # 수치형 데이터 형변환
    num_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 사이드바 (도감 목차 관리)
st.sidebar.header("📌 도감 목차")
st.sidebar.markdown("- **Section 1.** 영화별 일별 관객수 변화")
st.sidebar.markdown("- *다음 섹션 추가 대기 중...*")

# ==========================================
# Section 1. 영화별 일별 관객수 변화
# ==========================================
st.markdown("---")
st.header("1. 영화별 일별 관객수 변화 (선 그래프)")

# 영화 목록 추출
movie_list = sorted(df['영화명'].dropna().unique())

# 드롭다운 선택 박스
selected_movie = st.selectbox(
    "📊 관객수 추이를 확인할 영화를 선택하세요:",
    options=movie_list,
    index=0
)

if selected_movie:
    # 해당 영화 데이터 필터링 및 날짜 오름차순 정렬
    movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')
    
    # Plotly 선 그래프 생성
    fig = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"[{selected_movie}] 일별 관객수 변화 추이",
        labels={'날짜': '날짜', '일관객': '일별 관객수 (명)'},
        markers=True
    )
    
    # 마우스 호버(Hover) 툴팁 설정 (날짜와 관객수가 한눈에 보이도록 커스텀)
    fig.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객수:</b> %{y:,}명<extra></extra>"
    )
    
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객수 (명)",
        hovermode="x unified",
        template="plotly_white",
        height=500
    )
    
    # 그래프 출력
    st.plotly_chart(fig, use_container_width=True)
    
    # 그래프 요약 설명 문구 자리
    st.info(f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 후 일별 관객수 증감 흐름과 주요 흥행 피크(Peak) 시점을 한눈에 파악할 수 있습니다.")

# ==========================================
# Section 2. (추후 그래프 추가 구역 예시)
# ==========================================
# st.markdown("---")
# st.header("2. 새로운 그래프 추가 구역")
