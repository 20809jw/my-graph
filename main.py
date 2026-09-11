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
    
    # 날짜 열 안전하게 datetime형으로 변환 (YYYYMMDD 형식)
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str).str.replace('.0', '', regex=False), format='%Y%m%d', errors='coerce')
    
    # 수치형 데이터 정리
    num_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # 결측치 제거
    df = df.dropna(subset=['날짜', '영화명', '일관객'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 사이드바 (도감 목차 관리 - Anchor 링크 연결)
st.sidebar.header("📌 도감 목차")
st.sidebar.markdown("- [Section 1. 영화별 일별 관객수 변화](#1)")
st.sidebar.markdown("- [Section 2. 누적 일관객 TOP 5 영화 비교](#2-top-5)")
st.sidebar.markdown("- [Section 3. 일별 10위권 관객수 합계 추이](#3-10)")
st.sidebar.markdown("- [Section 4. 기간 내 관객수 TOP 10 영화](#4-top-10)")
st.sidebar.markdown("- [Section 5. 월×요일별 관객수 히트맵](#5)")

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
    
    # 수정 가능한 요약 문구
    default_text_1 = f"{selected_movie}의 개봉 후 일별 관객수 증감 흐름과 주요 흥행 피크(Peak) 시점을 한눈에 파악할 수 있습니다."
    st.text_area("💡 이 그래프로 알 수 있는 것 (수정 가능):", value=default_text_1, key="desc_1", height=100)


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

# 선 그래프 생성
fig2 = px.line(
    top5_df,
    x='날짜',
    y='일관객',
    color='영화명',
    title="기간 내 일관객 합계 상위 5개 영화의 날짜별 일관객 추이",
    labels={'날짜': '날짜', '일관객': '일별 관객수 (명)', '영화명': '영화 제목'},
    markers=False
)

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

st.plotly_chart(fig2, use_container_width=True)

top5_str = ", ".join(top5_movies)
default_text_2 = f"기간 내 가장 흥행한 상위 5개 영화({top5_str})의 흥행 시기 겹침 여부와 개봉 초기 화력 비교를 한눈에 볼 수 있으며, 범례 항목을 클릭해 특정 영화를 켜거나 끌 수 있습니다."
st.text_area("💡 이 그래프로 알 수 있는 것 (수정 가능):", value=default_text_2, key="desc_2", height=100)


# ==========================================
# Section 3. 일별 10위권 관객수 합계 영역 그래프
# ==========================================
st.markdown("---")
st.header("3. 일별 10위권 전체 관객수 합계 추이 (영역 그래프)")

# 날짜별 10위권 관객수 합계 집계
daily_total = df.groupby('날짜')['일관객'].sum().reset_index().sort_values('날짜')

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

# TOP 3일 주석(Annotation) 추가
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

st.plotly_chart(fig3, use_container_width=True)

top3_dates_fmt = [f"{r['날짜'].strftime('%Y년 %m월 %d일')}({int(r['일관객']):,}명)" for _, r in top3_days.iterrows()]
top3_text = ", ".join(top3_dates_fmt)

default_text_3 = f"극장가 전체의 성수기와 비수기 흐름을 한눈에 볼 수 있으며, 관객수가 가장 많았던 상위 3일({top3_text})을 파악할 수 있습니다."
st.text_area("💡 이 그래프로 알 수 있는 것 (수정 가능):", value=default_text_3, key="desc_3", height=100)


# ==========================================
# Section 4. 기간 내 관객수 TOP 10 영화 가로 막대그래프
# ==========================================
st.markdown("---")
st.header("4. 기간 내 일관객 합계 TOP 10 영화 (가로 막대그래프)")

# 영화별 일관객 합계 및 10위권 등재 일수 집계
top10_df = (
    df.groupby('영화명')
    .agg(
        총관객수=('일관객', 'sum'),
        차트인일수=('날짜', 'count')
    )
    .reset_index()
    .sort_values('총관객수', ascending=False)
    .head(10)
)

# Plotly 가로 막대 순서 조정 (아래에서 위로 그려지므로 ascending=True)
top10_df_plot = top10_df.sort_values('총관객수', ascending=True)

fig4 = px.bar(
    top10_df_plot,
    x='총관객수',
    y='영화명',
    orientation='h',
    title="기간 내 일관객 합계 TOP 10 영화 순위",
    labels={'총관객수': '총 일관객수 (명)', '영화명': '영화 제목'},
    text='총관객수'
)

fig4.update_traces(
    texttemplate='%{x:,}명',
    textposition='outside',
    cliponaxis=False,
    hovertemplate="<b>영화명:</b> %{y}<br><b>기간 내 총 관객수:</b> %{x:,}명<br><b>10위권 등재 일수:</b> %{customdata}일<extra></extra>",
    customdata=top10_df_plot['차트인일수'],
    marker_color='#4A90E2'
)

fig4.update_layout(
    xaxis_title="총 관객수 (명)",
    yaxis_title="영화 제목",
    template="plotly_white",
    height=550,
    xaxis=dict(showgrid=True)
)

st.plotly_chart(fig4, use_container_width=True)

top_movie_name = top10_df.iloc[0]['영화명']
top_movie_audience = int(top10_df.iloc[0]['총관객수'])
top_movie_days = int(top10_df.iloc[0]['차트인일수'])

default_text_4 = f"해당 기간 동안 가장 많은 관객을 모은 TOP 10 영화 순위를 확인할 수 있으며, 1위인 '{top_movie_name}'(총 {top_movie_audience:,}명, 10위권 {top_movie_days}일 유지)을 비롯한 각 영화의 10위권 유지 기간(차트인 일수)을 함께 비교할 수 있습니다."
st.text_area("💡 이 그래프로 알 수 있는 것 (수정 가능):", value=default_text_4, key="desc_4", height=100)


# ==========================================
# Section 5. 월×요일별 관객수 합계 히트맵
# ==========================================
st.markdown("---")
st.header("5. 월×요일별 관객수 합계 (히트맵)")

# 데이터 전처리: 월, 요일 파생변수 생성
heatmap_df = df.copy()
heatmap_df['월'] = heatmap_df['날짜'].dt.month.astype(str) + "월"

# 요일 한글 변환 매핑
weekday_map = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
heatmap_df['요일'] = heatmap_df['날짜'].dt.weekday.map(weekday_map)

# 요일 순서 지정을 위해 Categorical 타입 적용 (월요일 -> 일요일)
day_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
heatmap_df['요일'] = pd.Categorical(heatmap_df['요일'], categories=day_order, ordered=True)

# 월×요일 관객수 합계 피벗 테이블 작성
pivot_df = heatmap_df.pivot_table(
    index='월',
    columns='요일',
    values='일관객',
    aggfunc='sum',
    fill_value=0,
    observed=False
)

# 월 정렬 (1월 -> 12월)
month_order = [f"{m}월" for m in range(1, 13) if f"{m}월" in pivot_df.index]
pivot_df = pivot_df.reindex(month_order)

# 히트맵 생성
fig5 = px.imshow(
    pivot_df,
    labels=dict(x="요일", y="월", color="총 관객수 (명)"),
    x=day_order,
    y=pivot_df.index,
    color_continuous_scale="Blues",
    title="월 및 요일별 일관객 합계 분포",
    text_auto=',d'
)

fig5.update_traces(
    hovertemplate="<b>%{y} %{x}</b><br>총 관객수: %{z:,}명<extra></extra>"
)

fig5.update_layout(
    xaxis_title="요일",
    yaxis_title="월",
    template="plotly_white",
    height=600
)

st.plotly_chart(fig5, use_container_width=True)

default_text_5 = "월별/요일별 극장 관객수의 집중도를 한눈에 확인할 수 있습니다. 주말(토, 일) 및 특정 성수기 월에 관객수가 어떻게 몰리는지 패턴을 직관적으로 파악할 수 있습니다."
st.text_area("💡 이 그래프로 알 수 있는 것 (수정 가능):", value=default_text_5, key="desc_5", height=100)
