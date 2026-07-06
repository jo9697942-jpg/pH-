import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# 1. 페이지 기본 설정 및 디자인 (화공 공정 대시보드 느낌)
st.set_page_config(page_title="Bio-Reactor pH Control Simulator", layout="wide")
st.title("🧪 바이오리액터 pH 피드백 제어 시스템 시뮬레이터")
st.subheader("화공생명공학 공정 제어(Process Control) 및 모니터링 시스템 구현")
st.markdown("---")

# 2. 제공된 CSV 데이터 로드 (데이터 세트 2 활용)
# 학생이 제공한 데이터 세트 2의 흐름을 반영한 하드코딩 데이터
data = {
    "Time": [0, 10, 20, 30, 40, 50, 55, 56, 57, 57.5, 58, 59, 60, 65, 70, 75, 80, 90, 100, 110, 115, 118, 120, 125, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 145, 150, 155, 160],
    "Raw_pH": [1.39, 1.38, 1.39, 1.39, 1.39, 1.40, 1.40, 1.45, 1.53, 1.57, 1.60, 1.62, 1.63, 1.62, 1.69, 1.71, 1.76, 1.83, 1.86, 1.90, 1.91, 2.02, 2.15, 2.15, 2.37, 2.75, 3.34, 4.12, 4.89, 5.69, 6.45, 7.15, 7.85, 8.63, 9.27, 9.70, 10.00, 10.21, 10.90, 11.45, 11.50, 10.80]
}
df = pd.DataFrame(data)

# 사이드바 제어 설정
st.sidebar.header("⚙️ 제어 시스템 설정 (Control Settings)")
target_min = st.sidebar.slider("최적 pH 하한선 (Target Min)", 5.0, 6.5, 6.0, 0.1)
target_max = st.sidebar.slider("최적 pH 상한선 (Target Max)", 7.5, 9.0, 8.0, 0.1)
control_enabled = st.sidebar.checkbox("자동 피드백 제어 시스템 가동 (Feedback Loop ON)", value=True)

# 시뮬레이션 실행 버튼
start_button = st.sidebar.button("시뮬레이션 시작 (Run)")

# 대시보드 레이아웃 구성
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📊 실시간 공정 상태")
    status_box = st.empty()
    ph_metric = st.empty()
    valve_metric = st.empty()

with col2:
    st.markdown("### 📈 바이오리액터 내 pH 트렌드")
    chart_holder = st.empty()

# 3. 실시간 제어 시뮬레이션 루프
if start_button:
    current_times = []
    current_phs = []
    controlled_phs = []
    
    for i in range(len(df)):
        t = df.iloc[i]["Time"]
        raw_ph = df.iloc[i]["Raw_pH"]
        
        # 피드백 제어 로직 (Feedback Control Loop)
        # pH가 상한선을 넘어가면 제어 시스템이 산성 중화제를 투입하여 pH를 강제로 최적 범위 내로 끌어내린다고 가정
        if control_enabled and raw_ph > target_max:
            # 중화제 투입으로 인한 pH 보정 모델링 (수학적 억제 가상 구현)
            excess = raw_ph - target_max
            controlled_ph = target_max + (excess * 0.15) # 85%의 제어 효율로 pH 억제
            valve_status = f"🔴 중화제(Acid) 밸브 개방! 투입률: {min(100, int(excess*50))}%"
            status_color = "error"
            status_text = "⚠️ [경고] pH 상한선 초과! 피드백 제어 스케일 가동 중."
        elif control_enabled and raw_ph < target_min and t > 0: 
            # 초기 산성 상태를 지나 공정 중 pH가 너무 떨어질 때의 제어 (예시)
            controlled_ph = target_min
            valve_status = "🔵 중화제(Base) 밸브 개방!"
            status_color = "warning"
            status_text = "⚠️ [경고] pH 하한선 미달! 염기성 물질 투입 중."
        else:
            controlled_ph = raw_ph
            valve_status = "🟢 정상 (밸브 닫힘)"
            status_color = "success"
            status_text = "✅ 시스템 안정 상태. 미생물 최적 대사 환경 유지 중."

        current_times.append(t)
        current_phs.append(raw_ph)
        controlled_phs.append(controlled_ph)

        # UI 업데이트
        if status_color == "success": st.success(status_text)
        elif status_color == "warning": st.warning(status_text)
        else: st.error(status_text)
        
        ph_metric.metric(label="현재 리액터 pH", value=f"{controlled_ph:.2f}", delta=f"{controlled_ph - 7.0:.2f} (from Neutral)")
        valve_metric.info(f"밸브 상태: {valve_status}")

        # 그래프 그리기
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(current_times, current_phs, 'r--', label="Raw Data (No Control)", alpha=0.5)
        ax.plot(current_times, controlled_phs, 'b-', linewidth=2, label="Controlled pH (Feedback Loop)")
        
        # 최적 범위 가이드라인
        ax.axhline(target_max, color='green', linestyle=':', label="Target pH Max")
        ax.axhline(target_min, color='green', linestyle=':', label="Target pH Min")
        
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("pH")
        ax.set_title(f"Bioreactor pH Dynamic Response (Time: {t}s)")
        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 14)       # Y축 눈금을 원본처럼 0~14로 고정
        ax.set_xlim(-5, 165)  
        
        chart_holder.pyplot(fig)
        plt.close()
        
        time.sleep(0.3) # 시뮬레이션 속도 조절
else:
    st.info("사이드바에서 설정을 확인한 후 '시뮬레이션 시작' 버튼을 눌러주세요.")
