import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# Title
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("일별 박스오피스 데이터를 바탕으로 시각화한 데이터 분석 도감입니다.")

# 데이터 불러오기 및 전처리 (캐싱)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)
    
    # 날짜 열을 datetime형으로 변환 (YYYYMMDD 형식)
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    
    # 수치형 데이터 정리
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
st.sidebar.markdown("- **Section 2.** 누적 일관객 TOP 5 영화 비교")
st.sidebar.markdown("- **Section 3.** 일별 10위권 관객수 합계 추이")

# ==========================================
# Section 1. 영화별 일별 관객수 변화
# ==========================================
st.markdown("---")
st.header("1. 영화별 일별 관객수 변화 (선 그래프)")

# 영화 목록 추출 (영화명 기준 sorting)
movie_list = sorted(df['영화명'].dropna().unique())

# 드롭다운 선택 box
selected_movie = st.selectbox(
    "📊 관객수 추이를 확인할 영화를 선택하세요:",
    options=movie_list,
    index=0
)

if selected_movie:
    # 필터링
    movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')
    
    # Plotly 선 그래프 생성
    fig1 = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"[{selected_movie}] 일별 관객수 변화 추이",
        labels={'날짜': '날짜', '일관객': '일별 관객수 (명)'},
        markers=True
    )
    
    # 마우스 오버(Hover) 툴팁 설정
    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객수:</b> %{y:,}명<extra></extra>"
    )
    
    # 레이아웃 스타일 적용
    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객수 (명)",
        hovermode="x unified",
        template="plotly_white",
        height=500
    )
    
    # Streamlit에 그래프 표시
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 요약 문구 자리
    st.info(f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 후 일별 관객수 증감 흐름과 주요 흥행 피크(Peak) 시점을 한눈에 파악할 수 있습니다.")


# ==========================================
# Section 2. 누적 일관객 TOP 5 영화 비교
# ==========================================
st.markdown("---")
st.header("2. 기간 내 일관객 합계 TOP 5 영화 비교")

# 기간 내 일관객 합계 상위 5개 영화 추출
top5_movies = (
    df.groupby('영화명')['일관객']
    .sum()
    .nlargest(5)
    .index.tolist()
)

# TOP 5 영화 데이터 필터링 및 날짜순 정렬
top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')

# 선 그래프 생성 (color='영화명'으로 영화별 색상 구분)
fig2 = px.line(
    top5_df,
    x='날짜',
    y='일관객',
    color='영화명',
    title="기간 내 일관객 합계 상위 5개 영화의 날짜별 일관객 추이",
    labels={'날짜': '날짜', '일관객': '일별 관객수 (명)', '영화명': '영화 제목'},
    markers=False
)

# 마우스 오버 툴팁 및 범례 커스텀
fig2.update_traces(
    hovertemplate="<b>영화명:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객수:</b> %{y:,}명<extra></extra>"
)

fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객수 (명)",
    hovermode="x unified",
    template="plotly_white",
    height=550,
    legend=dict(
        title="영화 제목 (클릭 시 토글)",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

# Streamlit에 그래프 표시
st.plotly_chart(fig2, use_container_width=True)

top5_str = ", ".join(top5_movies)
st.info(f"💡 **이 그래프로 알 수 있는 것:** 기간 내 가장 흥행한 상위 5개 영화({top5_str})의 흥행 시기 겹침 여부와 개봉 초기 화력 비교를 한눈에 볼 수 있으며, 범례 항목을 클릭해 특정 영화를 켜거나 끌 수 있습니다.")


# ==========================================
# Section 3. 일별 10위권 관객수 합계 영역 그래프
# ==========================================
st.markdown("---")
st.header("3. 일별 10위권 전체 관객수 합계 추이 (영역 그래프)")

# 날짜별 10위권 관객수 합계 집계
daily_total = df.groupby('날짜')['일관객'].sum().reset_index()
daily_total = daily_total.sort_values('날짜')

# 관객수 합계 상위 3일 추출
top3_days = daily_total.nlargest(3, '일관객').sort_values('날짜')

# 영역 그래프(Area Chart) 생성
fig3 = px.area(
    daily_total,
    x='날짜',
    y='일관객',
    title="일별 박스오피스 10위권 영화 전체 관객수 합계 변화",
    labels={'날짜': '날짜', '일관객': '10위권 관객수 합계 (명)'}
)

fig3.update_traces(
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>전체 관객수:</b> %{y:,}명<extra></extra>",
    line_color='#2b5c8f',
    fillcolor='rgba(43, 92, 143, 0.3)'
)

# TOP 3일 데이터 주석(Annotation) 추가
for index, row in top3_days.iterrows():
    date_str = row['날짜'].strftime('%Y-%m-%d')
    audience_str = f"{int(row['일관객']):,}명"
    
    fig3.add_annotation(
        x=row['날짜'],
        y=row['일관객'],
        text=f"<b>TOP 3</b><br>{date_str}<br>({audience_str})",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#d9534f",
        ax=0,
        ay=-50,
        bgcolor="#ffffff",
        bordercolor="#d9534f",
        borderwidth=1.5,
        borderpad=4,
        font=dict(size=11, color="#333333")
    )

fig3.update_layout(
    xaxis_title="날짜",
    yaxis_title="총 관객수 (명)",
    hovermode="x unified",
    template="plotly_white",
    height=550
)

# Streamlit에 그래프 표시
st.plotly_chart(fig3, use_container_width=True)

# TOP 3 날짜 문구 정리
top3_dates_fmt = [f"{r['날짜'].strftime('%Y년 %m월 %d일')}({int(r['일관객']):,}명)" for _, r in top3_days.iterrows()]
top3_text = ", ".join(top3_dates_fmt)

st.info(f"💡 **이 그래프로 알 수 있는 것:** 극장가 전체의 성수기와 비수기 흐름을 한눈에 볼 수 있으며, 관객수가 가장 많았던 상위 3일({top3_text})을 파악할 수 있습니다.")
