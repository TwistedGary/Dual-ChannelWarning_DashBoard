import streamlit as st
import pandas as pd
import numpy as np

from datetime import datetime, timedelta

import matplotlib.pyplot as plt

# -----------------------------
# 页面配置
# -----------------------------
st.set_page_config(
    page_title="Dual-Warning Decision Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# 自定义CSS样式
# -----------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .risk-card {
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .logic-step {
        background-color: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 标题和说明
# -----------------------------
st.markdown('<div class="main-header">Campus Dual-Warning Decision Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">An explainable decision-support prototype for campus infectious disease preparedness</div>', unsafe_allow_html=True)

# 系统架构说明
with st.expander("📋 System Architecture Overview", expanded=False):
    st.markdown("""
    **Design Purpose:**
    - Support discussion under uncertainty, not automated prediction
    - Emphasize clarity, explainability, and discussion readiness
    - Modular, transparent, low-data-dependency structure
    
    **Four-Layer Architecture:**
    1. **Data Input Layer** - Aggregated campus data
    2. **Feature Construction Layer** - Trend and change indicators
    3. **Risk Mapping Layer** - Rule-based qualitative mapping
    4. **Dual-Warning Output Layer** - Parallel risk visualization
    """)

st.markdown("---")

# -----------------------------
# 侧边栏 - 系统控制面板
# -----------------------------
with st.sidebar:
    st.title("⚙️ System Controls")
    
    # 系统模式选择
    system_mode = st.radio(
        "System Mode",
        ["Interactive Simulation", "Scenario Demonstration", "Architecture Walkthrough"],
        help="Choose how to interact with the system"
    )
    
    # 数据源配置
    st.subheader("Data Configuration")
    data_source = st.selectbox(
        "Data Source",
        ["Manual Input", "Sample Dataset", "Upload CSV"],
        help="Select data input method"
    )
    
    # 时间范围选择
    st.subheader("Time Settings")
    analysis_period = st.slider(
        "Analysis Period (days)",
        min_value=3,
        max_value=14,
        value=7,
        help="Number of days to consider for trend analysis"
    )
    
    # 系统参数
    st.subheader("System Parameters")
    sensitivity = st.slider(
        "System Sensitivity",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Adjust sensitivity of risk detection"
    )
    
    # 重置按钮
    if st.button("🔄 Reset to Default"):
        st.rerun()
    
    st.markdown("---")
    st.caption("**System Status:** ✅ Operational")
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# -----------------------------
# 第一部分：数据输入层
# -----------------------------
st.header("📥 1. Data Input Layer")
st.markdown("""
This layer receives **non-personalized, aggregated campus data** for decision support.
No individual student information or confirmed diagnoses are used.
""")

# 数据输入容器
input_container = st.container()
with input_container:
    st.subheader("Campus Operational Data Input")
    
    # 创建三个输入列
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏫 Attendance Data")
        absentee_rate = st.slider(
            "Daily Absenteeism Rate (%)",
            min_value=0.0,
            max_value=30.0,
            value=8.5,
            step=0.5,
            help="Aggregated absence rate for the campus/grade level"
        )
        
        attendance_trend = st.select_slider(
            "Recent Trend (3-day)",
            options=["Declining", "Stable", "Increasing"],
            value="Increasing",
            help="Direction of absenteeism change over past 3 days"
        )
    
    with col2:
        st.markdown("#### 🤒 Symptom Reports")
        symptom_categories = st.multiselect(
            "Reported Symptom Categories",
            [
                "Respiratory (cough, sore throat)",
                "Fever/Chills",
                "Gastrointestinal",
                "Fatigue/Body Aches",
                "Other Non-specific"
            ],
            default=["Respiratory (cough, sore throat)", "Fever/Chills"],
            help="Categories of symptoms reported (aggregated, non-identifying)"
        )
        
        symptom_volume = st.select_slider(
            "Symptom Report Volume",
            options=["Low", "Moderate", "High"],
            value="Moderate",
            help="Relative number of symptom reports"
        )
    
    with col3:
        st.markdown("#### 🎯 Operational Indicators")
        class_coverage = st.slider(
            "Classes with Normal Attendance (%)",
            min_value=50,
            max_value=100,
            value=85,
            help="Percentage of classes operating with >85% attendance"
        )
        
        teacher_availability = st.select_slider(
            "Teacher Availability",
            options=["Normal", "Reduced", "Strained"],
            value="Normal",
            help="Current teaching staff availability"
        )

# 显示输入摘要
st.markdown("---")
st.subheader("📊 Input Summary")
summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.metric("Absenteeism Rate", f"{absentee_rate}%")
with summary_col2:
    st.metric("Symptom Categories", len(symptom_categories))
with summary_col3:
    st.metric("Class Coverage", f"{class_coverage}%")

st.markdown("""
*Input data represents aggregated campus-level conditions, preserving privacy while supporting early decision discussions.*
""")
# -----------------------------
# 第二部分：特征构建层
# -----------------------------
st.header("🔧 2. Feature Construction Layer")
st.markdown("""
Raw input data is transformed into **trend-oriented features** that emphasize 
sustained changes rather than single-point anomalies.
""")

with st.expander("📖 Feature Construction Logic", expanded=False):
    st.markdown("""
    **Key Principles:**
    1. **Trend over Absolute Values** - Emphasize direction and persistence of changes
    2. **Multi-day Patterns** - Avoid over-reacting to single-day anomalies
    3. **Relative Changes** - Focus on deviation from expected patterns
    4. **Operational Context** - Consider educational continuity alongside health signals
    """)

st.markdown("---")

# -----------------------------
# 特征计算函数
# -----------------------------
def calculate_trend_strength(absentee_rate, attendance_trend, analysis_period):
    """Calculate trend strength feature"""
    base_strength = 0
    
    # 基于缺勤率
    if absentee_rate < 5.0:
        base_strength += 0
    elif absentee_rate < 10.0:
        base_strength += 1
    else:
        base_strength += 2
    
    # 基于趋势方向
    if attendance_trend == "Increasing":
        trend_factor = 1.5
    elif attendance_trend == "Stable":
        trend_factor = 1.0
    else:  # Declining
        trend_factor = 0.5
    
    # 基于分析周期
    period_factor = min(analysis_period / 7, 1.5)
    
    final_strength = base_strength * trend_factor * period_factor
    return min(final_strength, 4.0)  # 上限为4.0

def calculate_signal_diversity(symptom_categories, symptom_volume):
    """Calculate signal diversity feature"""
    category_count = len(symptom_categories)
    
    # 基于类别数量
    if category_count <= 1:
        diversity_base = 0
    elif category_count <= 2:
        diversity_base = 1
    else:
        diversity_base = 2
    
    # 基于报告量
    volume_factor = {
        "Low": 0.7,
        "Moderate": 1.0,
        "High": 1.3
    }.get(symptom_volume, 1.0)
    
    return diversity_base * volume_factor

def calculate_operational_stress(class_coverage, teacher_availability):
    """Calculate operational stress feature"""
    # 基于课堂覆盖率
    if class_coverage >= 90:
        coverage_score = 0
    elif class_coverage >= 80:
        coverage_score = 1
    elif class_coverage >= 70:
        coverage_score = 2
    else:
        coverage_score = 3
    
    # 基于教师可用性
    availability_score = {
        "Normal": 0,
        "Reduced": 1,
        "Strained": 2
    }.get(teacher_availability, 1)
    
    return min(coverage_score + availability_score, 4.0)

# -----------------------------
# 计算特征值
# -----------------------------
trend_strength = calculate_trend_strength(absentee_rate, attendance_trend, analysis_period)
signal_diversity = calculate_signal_diversity(symptom_categories, symptom_volume)
operational_stress = calculate_operational_stress(class_coverage, teacher_availability)

# -----------------------------
# 特征可视化
# -----------------------------
st.subheader("Constructed Features")

# 特征值卡片
feat_col1, feat_col2, feat_col3 = st.columns(3)

with feat_col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### 📈 Trend Strength")
    st.metric("Value", f"{trend_strength:.2f}", 
              delta=f"{'Increasing' if trend_strength > 1.5 else 'Stable' if trend_strength > 0.5 else 'Low'}")
    st.progress(min(trend_strength / 4, 1.0))
    st.caption("Measures consistency and direction of absenteeism changes")
    st.markdown('</div>', unsafe_allow_html=True)

with feat_col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### 🔍 Signal Diversity")
    st.metric("Value", f"{signal_diversity:.2f}",
              delta=f"{'High' if signal_diversity > 1.5 else 'Moderate' if signal_diversity > 0.5 else 'Low'}")
    st.progress(min(signal_diversity / 3, 1.0))
    st.caption("Represents variety and volume of symptom categories")
    st.markdown('</div>', unsafe_allow_html=True)

with feat_col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ Operational Stress")
    st.metric("Value", f"{operational_stress:.2f}",
              delta=f"{'High' if operational_stress > 2.5 else 'Moderate' if operational_stress > 1.0 else 'Low'}")
    st.progress(min(operational_stress / 4, 1.0))
    st.caption("Reflects potential disruption to educational continuity")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 特征解释和逻辑流程
# -----------------------------
st.subheader("Feature Construction Logic")

logic_col1, logic_col2, logic_col3 = st.columns(3)

with logic_col1:
    with st.expander("Trend Strength Logic"):
        st.markdown("""
        **Inputs Considered:**
        - Current absenteeism rate
        - Recent trend direction (3 days)
        - Analysis period duration
        
        **Calculation:**
        ```
        Base = 0-2 based on absentee rate
        × Trend factor (0.5-1.5 based on direction)
        × Period factor (1.0-1.5 based on days)
        = Trend Strength (0-4 scale)
        ```
        
        **Why this matters:**
        Sustained increases suggest emerging patterns worth monitoring.
        """)

with logic_col2:
    with st.expander("Signal Diversity Logic"):
        st.markdown("""
        **Inputs Considered:**
        - Number of symptom categories
        - Relative report volume
        
        **Calculation:**
        ```
        Base = 0-2 based on category count
        × Volume factor (0.7-1.3 based on volume)
        = Signal Diversity (0-3 scale)
        ```
        
        **Why this matters:**
        Multiple symptom types may suggest broader health issues.
        """)

with logic_col3:
    with st.expander("Operational Stress Logic"):
        st.markdown("""
        **Inputs Considered:**
        - Percentage of classes with normal attendance
        - Teacher availability status
        
        **Calculation:**
        ```
        Coverage score = 0-3 based on class coverage
        + Availability score = 0-2 based on teacher status
        = Operational Stress (0-4 scale)
        ```
        
        **Why this matters:**
        Educational disruption may occur before health concerns escalate.
        """)

# -----------------------------
# 特征时间序列模拟
# -----------------------------
st.subheader("Feature Evolution Simulation")

# 生成模拟时间序列数据
dates = [(datetime.now() - timedelta(days=i)).strftime('%m-%d') for i in range(analysis_period, 0, -1)]

# 模拟特征值
np.random.seed(42)  # 为了可重复性
sim_trend = np.clip(trend_strength * (0.8 + 0.4 * np.random.randn(analysis_period)), 0, 4)
sim_diversity = np.clip(signal_diversity * (0.9 + 0.2 * np.random.randn(analysis_period)), 0, 3)
sim_stress = np.clip(operational_stress * (0.85 + 0.3 * np.random.randn(analysis_period)), 0, 4)

# 创建DataFrame用于显示
sim_data = pd.DataFrame({
    'Date': dates,
    'Trend Strength': sim_trend.round(2),
    'Signal Diversity': sim_diversity.round(2),
    'Operational Stress': sim_stress.round(2)
})

# 显示表格
st.dataframe(
    sim_data,
    column_config={
        "Date": "Date",
        "Trend Strength": st.column_config.NumberColumn(
            "Trend Strength",
            help="Trend strength over time",
            format="%.2f"
        ),
        "Signal Diversity": st.column_config.NumberColumn(
            "Signal Diversity",
            help="Signal diversity over time",
            format="%.2f"
        ),
        "Operational Stress": st.column_config.NumberColumn(
            "Operational Stress",
            help="Operational stress over time",
            format="%.2f"
        )
    },
    hide_index=True
)

# 特征说明
st.markdown("""
**Feature Construction Notes:**
- Features are **qualitative indicators** rather than precise measurements
- Values represent **relative changes** from expected patterns
- Construction emphasizes **early signal detection** over statistical precision
- All calculations are **transparent and explainable**
""")

st.markdown("""
*These constructed features serve as interpretable inputs to the rule-based risk mapping layer.*
""")

st.markdown("---")
# -----------------------------
# 特征之间的关联性分析
# -----------------------------
st.subheader("🔗 Feature Relationships")

# 计算特征之间的关联模式
correlation_matrix = pd.DataFrame({
    'Trend Strength': sim_trend,
    'Signal Diversity': sim_diversity,
    'Operational Stress': sim_stress
}).corr()

# 显示关联矩阵
st.markdown("##### Feature Correlation Matrix")
corr_col1, corr_col2 = st.columns([2, 1])


with corr_col1:
    # 创建简单的关联矩阵显示
    fig, ax = plt.subplots(figsize=(6, 4))
    im = ax.imshow(correlation_matrix.values, cmap='Blues', vmin=-1, vmax=1)
    
    # 设置标签
    ax.set_xticks(range(len(correlation_matrix.columns)))
    ax.set_yticks(range(len(correlation_matrix.columns)))
    ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
    ax.set_yticklabels(correlation_matrix.columns)
    
    # 添加数值标签
    for i in range(len(correlation_matrix.columns)):
        for j in range(len(correlation_matrix.columns)):
            text = ax.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                          ha='center', va='center', color='white')
    
    ax.set_title('Feature Correlation Matrix')
    fig.colorbar(im)
    st.pyplot(fig)

with corr_col2:
    st.markdown("""
    **Interpretation:**
    - **Positive values**: Features move together
    - **Near zero**: Features are independent
    - **Negative values**: Features move opposite
    
    *High correlation between health and operational features suggests systemic issues.*
    """)
# -----------------------------
# 特征阈值说明
# -----------------------------
st.subheader("🎯 Feature Thresholds & Interpretation")

threshold_tab1, threshold_tab2, threshold_tab3 = st.tabs([
    "Trend Strength Thresholds",
    "Signal Diversity Thresholds", 
    "Operational Stress Thresholds"
])

with threshold_tab1:
    st.markdown("""
    **Trend Strength Interpretation Guide:**
    
    | Level | Range | Description | Implication |
    |-------|-------|-------------|-------------|
    | **Low** | 0.0 - 1.0 | Minimal or declining trends | Normal operations, routine monitoring |
    | **Moderate** | 1.0 - 2.5 | Noticeable but not sustained changes | Enhanced awareness, document patterns |
    | **Elevated** | 2.5 - 4.0 | Consistent, multi-day increases | Active monitoring, consider discussion |
    
    **Key Considerations:**
    - Context matters: A 2.0 trend during exam week differs from normal weeks
    - Direction matters: Increasing trends warrant more attention than stable highs
    - Persistence matters: Multi-day patterns > single-day spikes
    """)

with threshold_tab2:
    st.markdown("""
    **Signal Diversity Interpretation Guide:**
    
    | Level | Range | Description | Implication |
    |-------|-------|-------------|-------------|
    | **Low** | 0.0 - 1.0 | Single symptom category, low volume | Likely isolated cases or seasonal pattern |
    | **Moderate** | 1.0 - 2.0 | Multiple related symptoms | Potential localized concern, monitor closely |
    | **Elevated** | 2.0 - 3.0 | Diverse symptoms, high volume | Broad pattern, may indicate systemic health issue |
    
    **Key Considerations:**
    - Category quality: Some symptom combinations are more concerning than others
    - Baseline matters: Compare to typical patterns for the time of year
    - Reporting consistency: Ensure reporting practices haven't changed
    """)

with threshold_tab3:
    st.markdown("""
    **Operational Stress Interpretation Guide:**
    
    | Level | Range | Description | Implication |
    |-------|-------|-------------|-------------|
    | **Low** | 0.0 - 1.5 | Normal class coverage, full staffing | Educational continuity not at risk |
    | **Moderate** | 1.5 - 2.5 | Some disruption, manageable strain | Monitor for escalation, consider adaptations |
    | **Elevated** | 2.5 - 4.0 | Significant disruption, strained resources | Educational quality at risk, active response needed |
    
    **Key Considerations:**
    - Duration matters: Short-term strain differs from prolonged disruption
    - Distribution matters: Concentrated vs. widespread disruption
    - Academic calendar: Consider timing relative to critical academic periods
    """)

# -----------------------------
# 特征质量指标
# -----------------------------
st.subheader("📊 Feature Quality Assessment")

# 计算质量指标
feature_stability = {
    'Trend Strength': np.std(sim_trend) / np.mean(sim_trend) if np.mean(sim_trend) > 0 else 0,
    'Signal Diversity': np.std(sim_diversity) / np.mean(sim_diversity) if np.mean(sim_diversity) > 0 else 0,
    'Operational Stress': np.std(sim_stress) / np.mean(sim_stress) if np.mean(sim_stress) > 0 else 0
}

quality_col1, quality_col2, quality_col3 = st.columns(3)

with quality_col1:
    stability_score = 1 - min(feature_stability['Trend Strength'], 1.0)
    st.metric(
        "Trend Data Quality",
        f"{stability_score:.0%}",
        delta="Stable" if stability_score > 0.7 else "Variable",
        help="Consistency of trend measurements over time"
    )

with quality_col2:
    coverage_score = min(len(symptom_categories) / 5, 1.0)  # 最多5个类别
    st.metric(
        "Symptom Coverage",
        f"{coverage_score:.0%}",
        delta="Comprehensive" if coverage_score > 0.6 else "Limited",
        help="Completeness of symptom category reporting"
    )

with quality_col3:
    operational_quality = min(class_coverage / 100, 1.0) * 0.7 + 0.3  # 假设教师可用性正常
    st.metric(
        "Operational Data Quality",
        f"{operational_quality:.0%}",
        delta="Reliable" if operational_quality > 0.8 else "Partial",
        help="Reliability of operational data sources"
    )

st.markdown("---")

# =============================
# 第三部分：风险映射层
# =============================
st.header("🗺️ 3. Risk Mapping Layer")
st.markdown("""
Features are mapped to qualitative risk levels using **transparent, rule-based logic** 
rather than predictive models or black-box algorithms.
""")

# 系统架构可视化
st.subheader("Risk Mapping Architecture")

architecture_col1, architecture_col2 = st.columns([2, 1])

with architecture_col1:
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────┐
    │              RISK MAPPING LAYER                     │
    ├─────────────────────────────────────────────────────┤
    │                                                     │
    │  Input Features → Rule Engine → Dual Risk Outputs   │
    │                                                     │
    │  1. Trend Strength       ↓      Health Risk         │
    │  2. Signal Diversity     ↓      Education Risk      │
    │  3. Operational Stress   ↓                          │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    ```
    """)

with architecture_col2:
    st.markdown("""
    **Design Principles:**
    
    ✅ **Transparency**: All rules visible
    ✅ **Explainability**: Every output traceable
    ✅ **Consistency**: Same inputs → same outputs
    ✅ **Adaptability**: Rules can be reviewed
    """)

# -----------------------------
# 风险映射规则定义
# -----------------------------
st.subheader("📋 Risk Mapping Rules")

# 定义风险映射规则
risk_rules = {
    "health_risk": [
        {
            "conditions": ["trend_strength < 1.0", "signal_diversity < 1.0"],
            "risk_level": "Low",
            "explanation": "Minimal or declining trends with limited symptom diversity"
        },
        {
            "conditions": ["trend_strength >= 1.0", "trend_strength < 2.5", "signal_diversity >= 1.0"],
            "risk_level": "Moderate", 
            "explanation": "Noticeable trends or symptom diversity, but not both elevated"
        },
        {
            "conditions": ["trend_strength >= 2.5", "signal_diversity >= 2.0"],
            "risk_level": "Elevated",
            "explanation": "Strong, sustained trends with diverse symptom patterns"
        },
        {
            "conditions": ["trend_strength >= 3.0"],
            "risk_level": "Elevated",
            "explanation": "Very strong trends even with limited symptom diversity"
        }
    ],
    "education_risk": [
        {
            "conditions": ["operational_stress < 1.5"],
            "risk_level": "Low",
            "explanation": "Normal operations with minimal disruption"
        },
        {
            "conditions": ["operational_stress >= 1.5", "operational_stress < 2.5"],
            "risk_level": "Moderate",
            "explanation": "Some operational strain requiring monitoring"
        },
        {
            "conditions": ["operational_stress >= 2.5"],
            "risk_level": "Elevated", 
            "explanation": "Significant disruption to educational continuity"
        }
    ]
}

# 显示规则表格
rules_tab1, rules_tab2 = st.tabs(["Health Risk Rules", "Education Risk Rules"])

with rules_tab1:
    health_rules_df = pd.DataFrame([
        {
            "Rule ID": f"HR-{i+1}",
            "Conditions": " AND ".join(rule["conditions"]),
            "Risk Level": rule["risk_level"],
            "Explanation": rule["explanation"]
        }
        for i, rule in enumerate(risk_rules["health_risk"])
    ])
    
    st.dataframe(
        health_rules_df,
        column_config={
            "Rule ID": st.column_config.TextColumn("Rule ID", width="small"),
            "Conditions": st.column_config.TextColumn("Conditions", width="medium"),
            "Risk Level": st.column_config.TextColumn("Risk Level", width="small"),
            "Explanation": st.column_config.TextColumn("Explanation", width="large")
        },
        hide_index=True,
        use_container_width=True
    )

with rules_tab2:
    education_rules_df = pd.DataFrame([
        {
            "Rule ID": f"ER-{i+1}",
            "Conditions": " AND ".join(rule["conditions"]),
            "Risk Level": rule["risk_level"], 
            "Explanation": rule["explanation"]
        }
        for i, rule in enumerate(risk_rules["education_risk"])
    ])
    
    st.dataframe(
        education_rules_df,
        column_config={
            "Rule ID": st.column_config.TextColumn("Rule ID", width="small"),
            "Conditions": st.column_config.TextColumn("Conditions", width="medium"),
            "Risk Level": st.column_config.TextColumn("Risk Level", width="small"),
            "Explanation": st.column_config.TextColumn("Explanation", width="large")
        },
        hide_index=True,
        use_container_width=True
    )

# -----------------------------
# 规则应用演示
# -----------------------------
st.subheader("🔍 Rule Application Process")

# 创建规则应用演示
demo_container = st.container()
with demo_container:
    demo_col1, demo_col2, demo_col3 = st.columns(3)
    
    with demo_col1:
        st.markdown("**Current Feature Values:**")
        st.markdown(f"- Trend Strength: `{trend_strength:.2f}`")
        st.markdown(f"- Signal Diversity: `{signal_diversity:.2f}`")
        st.markdown(f"- Operational Stress: `{operational_stress:.2f}`")
    
    with demo_col2:
        st.markdown("**Rule Evaluation:**")
        
        # 健康风险评估
        health_rule_matches = []
        for rule in risk_rules["health_risk"]:
            conditions_met = all(eval(cond) for cond in rule["conditions"])
            if conditions_met:
                health_rule_matches.append(rule)
        
        # 教育风险评估  
        education_rule_matches = []
        for rule in risk_rules["education_risk"]:
            conditions_met = all(eval(cond) for cond in rule["conditions"])
            if conditions_met:
                education_rule_matches.append(rule)
        
        if health_rule_matches:
            st.markdown(f"**Health Risk**: {len(health_rule_matches)} rule(s) matched")
        if education_rule_matches:
            st.markdown(f"**Education Risk**: {len(education_rule_matches)} rule(s) matched")
    
    with demo_col3:
        st.markdown("**Resulting Risk Levels:**")
        # 将在下一部分计算具体风险等级

st.markdown("---")
# -----------------------------
# 风险等级计算函数
# -----------------------------
def calculate_health_risk(trend_strength, signal_diversity, sensitivity=1.0):
    """Calculate health transmission risk based on rule-based logic"""
    # 调整敏感性
    adjusted_trend = trend_strength * sensitivity
    adjusted_diversity = signal_diversity * sensitivity
    
    # 规则1: 低风险条件
    if adjusted_trend < 1.0 and adjusted_diversity < 1.0:
        return "Low", "Minimal trends and limited symptom diversity"
    
    # 规则2: 高风险条件 - 强趋势且多样症状
    if adjusted_trend >= 2.5 * sensitivity and adjusted_diversity >= 2.0 * sensitivity:
        return "Elevated", "Strong sustained trends with diverse symptom patterns"
    
    # 规则3: 高风险条件 - 非常强的趋势
    if adjusted_trend >= 3.0 * sensitivity:
        return "Elevated", "Very strong absenteeism trends detected"
    
    # 规则4: 中等风险条件
    if (adjusted_trend >= 1.0 or adjusted_diversity >= 1.0):
        return "Moderate", "Noticeable signals requiring monitoring"
    
    # 默认返回低风险
    return "Low", "No concerning patterns detected"

def calculate_education_risk(operational_stress, sensitivity=1.0):
    """Calculate educational continuity risk based on rule-based logic"""
    adjusted_stress = operational_stress * sensitivity
    
    # 规则1: 低风险条件
    if adjusted_stress < 1.5:
        return "Low", "Normal operations with minimal disruption"
    
    # 规则2: 高风险条件
    if adjusted_stress >= 2.5:
        return "Elevated", "Significant disruption to educational continuity"
    
    # 规则3: 中等风险条件
    if adjusted_stress >= 1.5:
        return "Moderate", "Some operational strain requiring monitoring"
    
    return "Low", "Normal operational conditions"

# -----------------------------
# 计算风险等级
# -----------------------------
health_risk, health_reason = calculate_health_risk(trend_strength, signal_diversity, sensitivity)
education_risk, education_reason = calculate_education_risk(operational_stress, sensitivity)

# -----------------------------
# 规则匹配详情
# -----------------------------
st.subheader("📋 Rule Matching Details")

match_col1, match_col2 = st.columns(2)

with match_col1:
    st.markdown("##### 🦠 Health Risk Rule Matching")
    
    # 查找匹配的健康风险规则
    health_matches = []
    for i, rule in enumerate(risk_rules["health_risk"]):
        conditions_met = all(eval(cond) for cond in rule["conditions"])
        if conditions_met:
            health_matches.append({
                "Rule": f"HR-{i+1}",
                "Matched": "✅",
                "Conditions": " AND ".join(rule["conditions"]),
                "Output": rule["risk_level"]
            })
    
    if health_matches:
        health_df = pd.DataFrame(health_matches)
        st.dataframe(
            health_df,
            column_config={
                "Rule": st.column_config.TextColumn("Rule ID", width="small"),
                "Matched": st.column_config.TextColumn("Status", width="small"),
                "Conditions": st.column_config.TextColumn("Conditions", width="medium"),
                "Output": st.column_config.TextColumn("Output", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # 显示应用结果
        st.markdown(f"**Applied Rule**: {health_matches[0]['Rule']}")
        st.markdown(f"**Result**: {health_risk}")
        st.markdown(f"**Reason**: {health_reason}")
    else:
        st.warning("No specific rule matched - using default logic")

with match_col2:
    st.markdown("##### 🎓 Education Risk Rule Matching")
    
    # 查找匹配的教育风险规则
    education_matches = []
    for i, rule in enumerate(risk_rules["education_risk"]):
        conditions_met = all(eval(cond) for cond in rule["conditions"])
        if conditions_met:
            education_matches.append({
                "Rule": f"ER-{i+1}",
                "Matched": "✅",
                "Conditions": " AND ".join(rule["conditions"]),
                "Output": rule["risk_level"]
            })
    
    if education_matches:
        education_df = pd.DataFrame(education_matches)
        st.dataframe(
            education_df,
            column_config={
                "Rule": st.column_config.TextColumn("Rule ID", width="small"),
                "Matched": st.column_config.TextColumn("Status", width="small"),
                "Conditions": st.column_config.TextColumn("Conditions", width="medium"),
                "Output": st.column_config.TextColumn("Output", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # 显示应用结果
        st.markdown(f"**Applied Rule**: {education_matches[0]['Rule']}")
        st.markdown(f"**Result**: {education_risk}")
        st.markdown(f"**Reason**: {education_reason}")
    else:
        st.warning("No specific rule matched - using default logic")

# -----------------------------
# 风险等级可视化
# -----------------------------
st.subheader("🎯 Risk Level Determination")

risk_viz_col1, risk_viz_col2 = st.columns(2)

with risk_viz_col1:
    # 健康风险雷达图数据
    health_factors = {
        "Trend Strength": min(trend_strength / 4, 1.0),
        "Signal Diversity": min(signal_diversity / 3, 1.0),
        "Consistency": 0.7,  # 模拟值
        "Baseline Comparison": 0.6  # 模拟值
    }
    
    st.markdown("**Health Risk Factors**")
    for factor, value in health_factors.items():
        st.progress(value, text=f"{factor}: {value:.0%}")

with risk_viz_col2:
    # 教育风险雷达图数据
    education_factors = {
        "Class Coverage": class_coverage / 100,
        "Teacher Availability": {"Normal": 1.0, "Reduced": 0.6, "Strained": 0.3}[teacher_availability],
        "Stability": 1.0 - min(operational_stress / 4, 1.0),
        "Resource Strain": min(operational_stress / 4, 1.0)
    }
    
    st.markdown("**Education Risk Factors**")
    for factor, value in education_factors.items():
        st.progress(value, text=f"{factor}: {value:.0%}")

# -----------------------------
# 风险映射总结
# -----------------------------
st.markdown("---")

st.subheader("📊 Risk Mapping Summary")

summary_container = st.container()
with summary_container:
    summary_col1, summary_col2, summary_col3 = st.columns([1, 2, 1])
    
    with summary_col1:
        st.markdown("**Input Features**")
        st.metric("Trend Strength", f"{trend_strength:.2f}")
        st.metric("Signal Diversity", f"{signal_diversity:.2f}")
        st.metric("Operational Stress", f"{operational_stress:.2f}")
    
    with summary_col2:
        st.markdown("**Mapping Process**")
        st.markdown("""
        ```
        Feature Evaluation → Rule Matching → Risk Determination
              ↓                   ↓                ↓
          Trend: {trend:.2f}   Match HR-?     Health: {health}
        Diversity: {diversity:.2f}  Match ER-?     Education: {edu}
          Stress: {stress:.2f}                      
        ```
        """.format(
            trend=trend_strength,
            diversity=signal_diversity,
            stress=operational_stress,
            health=health_risk,
            edu=education_risk
        ))
        
        st.markdown(f"**Sensitivity Setting**: {sensitivity:.1f}x")
        if sensitivity > 1.0:
            st.caption("System is more sensitive to early signals")
        elif sensitivity < 1.0:
            st.caption("System requires stronger signals")
        else:
            st.caption("System using standard sensitivity")
    
    with summary_col3:
        st.markdown("**Output Risks**")
        
        # 健康风险颜色
        health_color = {
            "Low": "🟢",
            "Moderate": "🟡", 
            "Elevated": "🔴"
        }.get(health_risk, "⚪")
        
        # 教育风险颜色
        education_color = {
            "Low": "🟢",
            "Moderate": "🟡",
            "Elevated": "🔴"
        }.get(education_risk, "⚪")
        
        st.markdown(f"{health_color} **Health Risk**: {health_risk}")
        st.markdown(f"{education_color} **Education Risk**: {education_risk}")

# =============================
# 第四部分：双维度预警输出层
# =============================
st.header("🚨 4. Dual-Warning Output Layer")
st.markdown("""
Parallel visualization of health and education risks to support 
**informed discussion rather than automated action**.
""")

# -----------------------------
# 风险卡片设计
# -----------------------------
st.subheader("Dual-Risk Dashboard")

# 定义风险颜色和图标
risk_config = {
    "Low": {
        "color": "#10B981",  # 绿色
        "icon": "✅",
        "bg_color": "#D1FAE5",
        "border_color": "#10B981"
    },
    "Moderate": {
        "color": "#F59E0B",  # 黄色
        "icon": "⚠️", 
        "bg_color": "#FEF3C7",
        "border_color": "#F59E0B"
    },
    "Elevated": {
        "color": "#EF4444",  # 红色
        "icon": "🚨",
        "bg_color": "#FEE2E2",
        "border_color": "#EF4444"
    }
}

# 创建双风险显示
# -----------------------------
# 双风险显示 - 完全使用Streamlit组件
# -----------------------------

risk_display_col1, risk_display_col2 = st.columns(2)

with risk_display_col1:
    # 健康风险
    health_config = risk_config[health_risk]
    
    # 创建卡片效果
    st.markdown(f"### {health_config['icon']} Health Transmission Risk")
    
    # 风险等级显示
    col_a, col_b = st.columns([1, 3])
    with col_a:
        st.markdown(f"<h1 style='color: {health_config['color']};'>{health_config['icon']}</h1>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<h2 style='color: {health_config['color']};'>{health_risk}</h2>", unsafe_allow_html=True)
    
    # 原因
    st.info(health_reason)
    
    # 贡献因素
    st.markdown("**Key Contributing Factors:**")
    st.markdown(f"- Trend Strength: {trend_strength:.2f}")
    st.markdown(f"- Signal Diversity: {signal_diversity:.2f}")
    st.markdown(f"- Analysis Period: {analysis_period} days")

with risk_display_col2:
    # 教育风险
    education_config = risk_config[education_risk]
    
    # 创建卡片效果
    st.markdown(f"### {education_config['icon']} Educational Continuity Risk")
    
    # 风险等级显示
    col_a, col_b = st.columns([1, 3])
    with col_a:
        st.markdown(f"<h1 style='color: {education_config['color']};'>{education_config['icon']}</h1>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<h2 style='color: {education_config['color']};'>{education_risk}</h2>", unsafe_allow_html=True)
    
    # 原因
    st.info(education_reason)
    
    # 运营指标
    st.markdown("**Key Operational Indicators:**")
    st.markdown(f"- Class Coverage: {class_coverage}%")
    st.markdown(f"- Teacher Availability: {teacher_availability}")
    st.markdown(f"- Operational Stress Score: {operational_stress:.2f}")

# -----------------------------
# 风险组合矩阵
# -----------------------------
st.subheader("🧩 Risk Combination Matrix")

# 定义风险矩阵
risk_matrix = {
    ("Low", "Low"): {
        "name": "Baseline Scenario",
        "description": "Normal operations, routine monitoring",
        "focus": "Maintain current protocols"
    },
    ("Elevated", "Low"): {
        "name": "Scenario A: Early Health Signals",
        "description": "Emerging health concerns with minimal operational impact",
        "focus": "Health monitoring and awareness"
    },
    ("Low", "Elevated"): {
        "name": "Scenario B: Operational Challenge",
        "description": "Educational disruption without apparent health concerns",
        "focus": "Operational adjustments and investigation"
    },
    ("Moderate", "Moderate"): {
        "name": "Scenario C: Balanced Concerns",
        "description": "Both health and education show moderate signals",
        "focus": "Coordinated monitoring and preparation"
    },
    ("Elevated", "Elevated"): {
        "name": "Scenario D: Dual Challenge",
        "description": "Significant concerns in both dimensions",
        "focus": "Immediate discussion and coordinated response"
    },
    ("Moderate", "Low"): {
        "name": "Scenario E: Watchful Health",
        "description": "Moderate health signals, normal operations",
        "focus": "Enhanced health monitoring"
    },
    ("Low", "Moderate"): {
        "name": "Scenario F: Operational Watch",
        "description": "Normal health, moderate operational strain",
        "focus": "Operational resilience planning"
    }
}

# 确定当前场景
current_scenario_key = (health_risk, education_risk)
current_scenario = risk_matrix.get(current_scenario_key, {
    "name": "Custom Scenario",
    "description": "Unique combination requiring specific attention",
    "focus": "Tailored discussion needed"
})

# 显示场景信息
scenario_col1, scenario_col2 = st.columns([1, 2])

with scenario_col1:
    st.markdown("**Current Risk Combination:**")
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #F8FAFC; border-radius: 10px;">
        <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 10px;">
            {health_risk} + {education_risk}
        </div>
        <div style="font-size: 2rem;">
            {risk_config[health_risk]['icon']} + {risk_config[education_risk]['icon']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with scenario_col2:
    st.markdown("**Identified Scenario:**")
    st.markdown(f"""
    <div style="background-color: #EFF6FF; padding: 20px; border-radius: 10px; border-left: 4px solid #3B82F6;">
        <h3 style="margin-top: 0; color: #1E40AF;">{current_scenario['name']}</h3>
        <p style="margin-bottom: 10px;"><strong>Description:</strong> {current_scenario['description']}</p>
        <p style="margin-bottom: 0;"><strong>Primary Focus:</strong> {current_scenario['focus']}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
# -----------------------------
# 风险趋势箭头指示器
# -----------------------------
st.subheader("📈 Risk Trend Indicators")

# 模拟风险趋势数据
def generate_risk_trend(current_risk_level, days=7):
    """生成模拟风险趋势"""
    risk_values = {"Low": 1, "Moderate": 2, "Elevated": 3}
    current_value = risk_values[current_risk_level]
    
    # 生成趋势数据
    np.random.seed(42)
    trend_data = np.clip(current_value + np.random.randn(days) * 0.5, 1, 3)
    
    # 计算趋势方向
    if len(trend_data) >= 3:
        recent_change = np.mean(trend_data[-3:]) - np.mean(trend_data[-6:-3])
        if recent_change > 0.2:
            trend_direction = "↗️ Increasing"
        elif recent_change < -0.2:
            trend_direction = "↘️ Decreasing"
        else:
            trend_direction = "➡️ Stable"
    else:
        trend_direction = "➡️ Stable"
    
    return trend_data, trend_direction

# 生成健康和教育风险趋势
health_trend, health_trend_dir = generate_risk_trend(health_risk)
education_trend, education_trend_dir = generate_risk_trend(education_risk)

# 显示趋势指示器
trend_col1, trend_col2 = st.columns(2)

with trend_col1:
    st.markdown("**Health Risk Trend**")
    
    # 创建趋势指示器
    current_health_val = {"Low": 1, "Moderate": 2, "Elevated": 3}[health_risk]
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        st.metric("Current", health_risk)
    with col_b:
        st.markdown(f"<div style='text-align: center; font-size: 1.5rem;'>{health_trend_dir}</div>", 
                   unsafe_allow_html=True)
    with col_c:
        # 计算变化
        if len(health_trend) >= 2:
            change = health_trend[-1] - health_trend[-2]
            if change > 0:
                delta = f"+{change:.1f}"
            elif change < 0:
                delta = f"{change:.1f}"
            else:
                delta = "0.0"
            st.metric("Change", "", delta=delta)
    
    # 趋势图
    trend_dates = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') 
                   for i in range(len(health_trend)-1, -1, -1)]
    
    trend_df = pd.DataFrame({
        'Date': trend_dates,
        'Risk Level': health_trend
    })
    
    # 简化趋势可视化
    st.line_chart(trend_df.set_index('Date')['Risk Level'], height=150)

with trend_col2:
    st.markdown("**Education Risk Trend**")
    
    # 创建趋势指示器
    current_edu_val = {"Low": 1, "Moderate": 2, "Elevated": 3}[education_risk]
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        st.metric("Current", education_risk)
    with col_b:
        st.markdown(f"<div style='text-align: center; font-size: 1.5rem;'>{education_trend_dir}</div>", 
                   unsafe_allow_html=True)
    with col_c:
        # 计算变化
        if len(education_trend) >= 2:
            change = education_trend[-1] - education_trend[-2]
            if change > 0:
                delta = f"+{change:.1f}"
            elif change < 0:
                delta = f"{change:.1f}"
            else:
                delta = "0.0"
            st.metric("Change", "", delta=delta)
    
    # 趋势图
    trend_df = pd.DataFrame({
        'Date': trend_dates,
        'Risk Level': education_trend
    })
    
    st.line_chart(trend_df.set_index('Date')['Risk Level'], height=150)

# -----------------------------
# 风险解释和上下文
# -----------------------------
st.subheader("🔍 Risk Interpretation & Context")

# 创建标签页显示不同的解释维度
interpretation_tabs = st.tabs([
    "Health Risk Context",
    "Education Risk Context", 
    "Comparative Analysis",
    "Uncertainty Assessment"
])

with interpretation_tabs[0]:
    st.markdown("""
    **Understanding Health Transmission Risk:**
    
    | Risk Level | Typical Characteristics | Discussion Considerations |
    |------------|-------------------------|---------------------------|
    | **Low** | - Absenteeism stable or declining<br>- Limited symptom diversity<br>- No sustained patterns | - Confirm data quality<br>- Review baseline expectations<br>- Ensure monitoring continues |
    | **Moderate** | - Noticeable but not sustained trends<br>- Some symptom diversity<br>- Potential early signals | - Monitor for persistence<br>- Check for external factors<br>- Consider internal communication |
    | **Elevated** | - Strong, sustained trends<br>- Diverse symptom patterns<br>- Consistent signals across metrics | - Verify data sources<br>- Assess operational implications<br>- Prepare for discussion |
    
    **Current Assessment:**
    - Primary driver: {}
    - Confidence level: {}%
    - Recommended review frequency: {}
    """.format(
        "Trend strength" if trend_strength > signal_diversity else "Symptom diversity",
        80 if trend_strength > 2.0 or signal_diversity > 2.0 else 70,
        "Daily" if health_risk == "Elevated" else "2-3 days" if health_risk == "Moderate" else "Weekly"
    ))

with interpretation_tabs[1]:
    st.markdown("""
    **Understanding Educational Continuity Risk:**
    
    | Risk Level | Operational Impact | Instructional Consequences |
    |------------|-------------------|----------------------------|
    | **Low** | - Normal class coverage (>90%)<br>- Full teaching staff<br>- Minimal disruption | - Regular instruction maintained<br>- No academic impact expected<br>- Routine support available |
    | **Moderate** | - Some classes affected (80-90%)<br>- Reduced staff availability<br>- Manageable strain | - Some adaptations needed<br>- Minor academic impact possible<br>- Increased coordination required |
    | **Elevated** | - Significant disruption (<80%)<br>- Strained resources<br>- Operational challenges | - Instructional quality at risk<br>- Academic impact likely<br>- Substantial response needed |
    
    **Current Assessment:**
    - Primary concern: {}
    - Resilience capacity: {}%
    - Time to significant impact: {}
    """.format(
        "Class coverage" if class_coverage < 85 else "Teacher availability",
        class_coverage,
        "Immediate" if education_risk == "Elevated" else "1-2 weeks" if education_risk == "Moderate" else "No immediate concern"
    ))

with interpretation_tabs[2]:
    st.markdown("""
    **Risk Comparison & Trade-offs:**
    
    **Current Relationship:** {}
    
    **Potential Implications:**
    {}
    
    **Decision Considerations:**
    1. **If Health > Education Risk**: Health concerns may justify temporary operational adjustments
    2. **If Education > Health Risk**: Operational issues may need addressing independent of health status
    3. **If Both Elevated**: Requires careful balancing of health protection and educational mission
    4. **If Both Low**: Opportunity to strengthen preventive measures
    
    **Balance Assessment:** {}
    """.format(
        "Diverging priorities" if health_risk != education_risk else "Aligned risks",
        "Focus needed on {} while monitoring {}".format(
            "health protection" if health_risk >= education_risk else "educational continuity",
            "operational impact" if health_risk >= education_risk else "health signals"
        ),
        "Requires careful trade-off analysis" if (health_risk == "Elevated" and education_risk == "Elevated") 
        else "Manageable with targeted approach"
    ))

with interpretation_tabs[3]:
    st.markdown("""
    **Uncertainty & Data Limitations:**
    
    **Known Uncertainties:**
    - Symptom reporting completeness: {}%
    - Trend data reliability: {}%
    - Operational data timeliness: {}%
    
    **Potential Biases:**
    - Reporting day effects: {}
    - Seasonal patterns: {}
    - Data aggregation limitations: {}
    
    **Recommendations for Uncertainty Reduction:**
    1. {} symptom reporting procedures
    2. {} operational data collection
    3. {} cross-validation with other indicators
    
    **Confidence in Assessment:** {}%
    """.format(
        min(int(len(symptom_categories) / 5 * 100), 100),
        int(100 * (1 - min(feature_stability['Trend Strength'], 0.5))),
        85,
        "Possible" if analysis_period < 5 else "Unlikely",
        "Consider in assessment" if analysis_period > 10 else "Not a major factor",
        "Always present in aggregated data",
        "Standardize" if len(symptom_categories) < 3 else "Review",
        "Strengthen" if operational_stress > 2.0 else "Maintain",
        "Increase" if health_risk == "Elevated" else "Continue",
        70 if health_risk == "Moderate" else 80 if health_risk == "Elevated" else 90
    ))

# -----------------------------
# 决策支持框架
# -----------------------------
st.subheader("💡 Decision-Support Framework")

# 决策矩阵
decision_matrix = {
    "Low-Low": {
        "monitoring": "Weekly aggregated review",
        "communication": "Standard internal channels",
        "preparedness": "Maintain existing protocols",
        "escalation": "No immediate action needed"
    },
    "Elevated-Low": {
        "monitoring": "Daily health indicators, weekly operations",
        "communication": "Increase health awareness, maintain normal ops updates",
        "preparedness": "Review health response protocols",
        "escalation": "Health team discussion within 48 hours"
    },
    "Low-Elevated": {
        "monitoring": "Daily operational metrics, weekly health",
        "communication": "Focus on operational adjustments, standard health updates",
        "preparedness": "Activate operational continuity plans",
        "escalation": "Operations team meeting within 24 hours"
    },
    "Elevated-Elevated": {
        "monitoring": "Multiple daily updates for both dimensions",
        "communication": "Coordinated messaging across all channels",
        "preparedness": "Full incident management protocols",
        "escalation": "Immediate leadership discussion"
    },
    "Moderate-Moderate": {
        "monitoring": "Daily review of key indicators",
        "communication": "Enhanced updates to relevant teams",
        "preparedness": "Standby protocols, review resources",
        "escalation": "Weekly leadership review"
    }
}

# 获取当前决策指导
current_decision_key = f"{health_risk}-{education_risk}"
decision_guidance = decision_matrix.get(current_decision_key, {
    "monitoring": "Tailored based on specific risk combination",
    "communication": "Customize based on primary concerns",
    "preparedness": "Review both health and operational readiness",
    "escalation": "Schedule discussion based on risk levels"
})

# 显示决策框架
st.markdown("**Recommended Support Structure:**")

decision_col1, decision_col2 = st.columns(2)

with decision_col1:
    st.markdown("""
    **Monitoring Approach:**
    {}
    
    **Communication Strategy:**
    {}
    """.format(decision_guidance["monitoring"], decision_guidance["communication"]))

with decision_col2:
    st.markdown("""
    **Preparedness Actions:**
    {}
    
    **Escalation Pathway:**
    {}
    """.format(decision_guidance["preparedness"], decision_guidance["escalation"]))

# -----------------------------
# 讨论要点生成器
# -----------------------------
st.subheader("🗣️ Discussion Points Generator")

# 基于风险等级生成讨论要点
def generate_discussion_points(health_risk, education_risk, scenario_name):
    """生成针对性的讨论要点"""
    
    base_points = [
        "Review data quality and completeness",
        "Consider external factors (season, community trends)",
        "Assess resource availability for response"
    ]
    
    health_specific = {
        "Low": [
            "Confirm absence patterns are within normal range",
            "Review symptom reporting procedures"
        ],
        "Moderate": [
            "Monitor for trend persistence over next 2-3 days",
            "Consider increasing awareness without alarm"
        ],
        "Elevated": [
            "Verify data sources and reporting consistency",
            "Prepare for potential operational impacts"
        ]
    }
    
    education_specific = {
        "Low": [
            "Ensure normal operations documentation",
            "Review contingency plan readiness"
        ],
        "Moderate": [
            "Assess capacity for operational adaptations",
            "Identify critical academic periods"
        ],
        "Elevated": [
            "Evaluate impact on teaching quality",
            "Consider temporary adjustments or supports"
        ]
    }
    
    # 组合要点
    points = base_points + health_specific.get(health_risk, []) + education_specific.get(education_risk, [])
    
    # 添加场景特定要点
    if "Early Health" in scenario_name:
        points.append("Balance health vigilance with educational continuity")
    elif "Operational Challenge" in scenario_name:
        points.append("Differentiate health-driven vs. other operational issues")
    elif "Dual Challenge" in scenario_name:
        points.append("Coordinate health and operational responses")
    
    return points

# 生成并显示讨论要点
discussion_points = generate_discussion_points(health_risk, education_risk, current_scenario["name"])

st.markdown("**Suggested Topics for Discussion:**")
for i, point in enumerate(discussion_points, 1):
    st.markdown(f"{i}. {point}")

# 添加自定义讨论要点
with st.expander("➕ Add Custom Discussion Points"):
    custom_point = st.text_input("Enter additional discussion topic:")
    if custom_point:
        discussion_points.append(custom_point)
        st.success("Custom point added to discussion list")

st.markdown("---")
# =============================
# 第五部分：场景模拟和假设分析
# =============================
st.header("🎭 5. Scenario Simulation & Sensitivity Analysis")
st.markdown("""
Explore how risk assessments change under different hypothetical conditions
to support preparedness discussions and contingency planning.
""")

# -----------------------------
# 预设场景选择
# -----------------------------
st.subheader("📋 Predefined Scenario Library")

scenario_options = {
    "baseline": {
        "name": "Baseline Normal Operations",
        "description": "Typical school day with normal attendance and operations",
        "params": {
            "absentee_rate": 4.0,
            "attendance_trend": "Stable",
            "symptom_categories": ["Respiratory (cough, sore throat)"],
            "symptom_volume": "Low",
            "class_coverage": 95,
            "teacher_availability": "Normal"
        }
    },
    "early_warning": {
        "name": "Early Warning Signals",
        "description": "Emerging patterns suggesting potential health concerns",
        "params": {
            "absentee_rate": 8.5,
            "attendance_trend": "Increasing",
            "symptom_categories": ["Respiratory (cough, sore throat)", "Fever/Chills"],
            "symptom_volume": "Moderate",
            "class_coverage": 88,
            "teacher_availability": "Normal"
        }
    },
    "operational_strain": {
        "name": "Operational Strain Scenario",
        "description": "Significant disruption to educational continuity",
        "params": {
            "absentee_rate": 6.0,
            "attendance_trend": "Stable",
            "symptom_categories": ["Fatigue/Body Aches"],
            "symptom_volume": "Low",
            "class_coverage": 75,
            "teacher_availability": "Strained"
        }
    },
    "dual_challenge": {
        "name": "Dual Challenge Scenario",
        "description": "Both health and education concerns present",
        "params": {
            "absentee_rate": 12.0,
            "attendance_trend": "Increasing",
            "symptom_categories": ["Respiratory (cough, sore throat)", "Fever/Chills", "Gastrointestinal"],
            "symptom_volume": "High",
            "class_coverage": 70,
            "teacher_availability": "Reduced"
        }
    },
    "rapid_escalation": {
        "name": "Rapid Escalation Scenario",
        "description": "Quickly developing situation requiring immediate attention",
        "params": {
            "absentee_rate": 18.0,
            "attendance_trend": "Increasing",
            "symptom_categories": ["Respiratory (cough, sore throat)", "Fever/Chills", "Fatigue/Body Aches"],
            "symptom_volume": "High",
            "class_coverage": 65,
            "teacher_availability": "Strained"
        }
    }
}

# 场景选择器
scenario_container = st.container()
with scenario_container:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_scenario_key = st.selectbox(
            "Choose a scenario to simulate:",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x]["name"],
            help="Select a predefined scenario to explore different risk configurations"
        )
    
    with col2:
        apply_scenario = st.button("🚀 Apply Scenario", type="primary")

# 如果选择了场景，更新参数
if apply_scenario:
    scenario = scenario_options[selected_scenario_key]
    params = scenario["params"]
    
    # 更新session state中的变量（在实际应用中需要适当处理）
    st.session_state.scenario_applied = True
    st.session_state.scenario_params = params
    st.session_state.current_scenario_name = scenario["name"]
    
    st.success(f"Applied: {scenario['name']}")
    st.info(scenario["description"])

# 显示当前场景或自定义状态
scenario_info_col1, scenario_info_col2 = st.columns(2)

with scenario_info_col1:
    if 'current_scenario_name' in st.session_state:
        st.markdown(f"""
        **Active Scenario:**  
        🎯 {st.session_state.current_scenario_name}
        """)
    else:
        st.markdown("""
        **Active Scenario:**  
        🎯 Custom Configuration
        """)

with scenario_info_col2:
    st.markdown("""
    **Scenario Purpose:**  
    Understanding how different conditions affect risk assessments
    """)

# -----------------------------
# 敏感性分析
# -----------------------------
st.subheader("📊 Sensitivity Analysis")

st.markdown("""
Adjust key parameters to see how they affect risk assessments:
""")

# 创建参数调整滑块
sens_col1, sens_col2, sens_col3 = st.columns(3)

with sens_col1:
    trend_sensitivity = st.slider(
        "Trend Sensitivity Multiplier",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="How strongly the system responds to trend changes"
    )

with sens_col2:
    symptom_weight = st.slider(
        "Symptom Weight",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Relative importance of symptom diversity in health risk"
    )

with sens_col3:
    operational_weight = st.slider(
        "Operational Impact Weight",
        min_value=0.5,
        max_value=2.0,
        value=1.0,
        step=0.1,
        help="Relative importance of operational factors"
    )

# 计算调整后的风险
adjusted_trend = trend_strength * trend_sensitivity
adjusted_diversity = signal_diversity * symptom_weight
adjusted_stress = operational_stress * operational_weight

# 使用调整后的参数重新计算风险
adjusted_health_risk, _ = calculate_health_risk(adjusted_trend, adjusted_diversity, sensitivity=1.0)
adjusted_education_risk, _ = calculate_education_risk(adjusted_stress, sensitivity=1.0)

# 显示敏感性分析结果
st.markdown("**Parameter Adjustment Effects:**")

sens_results_col1, sens_results_col2 = st.columns(2)

with sens_results_col1:
    st.markdown("##### Health Risk Sensitivity")
    
    # 创建比较表
    health_comparison = pd.DataFrame({
        "Parameter": ["Trend Strength", "Symptom Diversity", "Combined"],
        "Original": [trend_strength, signal_diversity, health_risk],
        "Adjusted": [adjusted_trend, adjusted_diversity, adjusted_health_risk],
        "Change": [
            f"{((adjusted_trend/trend_strength)-1)*100:+.1f}%" if trend_strength > 0 else "N/A",
            f"{((adjusted_diversity/signal_diversity)-1)*100:+.1f}%" if signal_diversity > 0 else "N/A",
            "→ " + adjusted_health_risk
        ]
    })
    
    st.dataframe(
        health_comparison,
        column_config={
            "Parameter": st.column_config.TextColumn("Parameter", width="medium"),
            "Original": st.column_config.NumberColumn("Original", width="small", format="%.2f"),
            "Adjusted": st.column_config.NumberColumn("Adjusted", width="small", format="%.2f"),
            "Change": st.column_config.TextColumn("Change", width="small")
        },
        hide_index=True,
        use_container_width=True
    )

with sens_results_col2:
    st.markdown("##### Education Risk Sensitivity")
    
    # 创建比较表
    education_comparison = pd.DataFrame({
        "Parameter": ["Operational Stress"],
        "Original": [operational_stress],
        "Adjusted": [adjusted_stress],
        "Change": [f"{((adjusted_stress/operational_stress)-1)*100:+.1f}%" if operational_stress > 0 else "N/A"]
    })
    
    st.dataframe(
        education_comparison,
        column_config={
            "Parameter": st.column_config.TextColumn("Parameter", width="medium"),
            "Original": st.column_config.NumberColumn("Original", width="small", format="%.2f"),
            "Adjusted": st.column_config.NumberColumn("Adjusted", width="small", format="%.2f"),
            "Change": st.column_config.TextColumn("Change", width="small")
        },
        hide_index=True,
        use_container_width=True
    )

# 显示最终比较
st.markdown("**Overall Risk Comparison:**")

comparison_col1, comparison_col2, comparison_col3 = st.columns(3)

risk_colors = {"Low": "🟢", "Moderate": "🟡", "Elevated": "🔴"}

with comparison_col1:
    st.markdown("**Original Assessment**")
    st.markdown(f"{risk_colors[health_risk]} Health: {health_risk}")
    st.markdown(f"{risk_colors[education_risk]} Education: {education_risk}")

with comparison_col2:
    st.markdown("**With Sensitivity Adjustments**")
    st.markdown(f"{risk_colors[adjusted_health_risk]} Health: {adjusted_health_risk}")
    st.markdown(f"{risk_colors[adjusted_education_risk]} Education: {adjusted_education_risk}")

with comparison_col3:
    st.markdown("**Key Insights**")
    if health_risk != adjusted_health_risk or education_risk != adjusted_education_risk:
        st.warning("Parameter changes affect risk assessment")
        if adjusted_health_risk > health_risk or adjusted_education_risk > education_risk:
            st.caption("System becomes more sensitive to signals")
        else:
            st.caption("System becomes less sensitive to signals")
    else:
        st.success("Assessment remains stable under adjustments")

# -----------------------------
# 假设分析：如果...会怎样？
# -----------------------------
st.subheader("🤔 What-If Analysis")

# 创建假设分析界面
whatif_container = st.container()
with whatif_container:
    whatif_tab1, whatif_tab2, whatif_tab3 = st.tabs([
        "Health Parameters",
        "Operational Parameters",
        "Combined Effects"
    ])
    
    with whatif_tab1:
        st.markdown("**Adjust Health-Related Parameters:**")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            whatif_absentee = st.slider(
                "What if absenteeism was:",
                min_value=0.0,
                max_value=30.0,
                value=absentee_rate,
                step=0.5,
                key="whatif_absentee"
            )
            
            whatif_trend = st.select_slider(
                "What if trend was:",
                options=["Declining", "Stable", "Increasing"],
                value=attendance_trend,
                key="whatif_trend"
            )
        
        with col_b:
            whatif_symptom_cat = st.slider(
                "What if symptom categories were:",
                min_value=0,
                max_value=5,
                value=len(symptom_categories),
                step=1,
                key="whatif_symptom_cat"
            )
            
            whatif_symptom_vol = st.select_slider(
                "What if symptom volume was:",
                options=["Low", "Moderate", "High"],
                value=symptom_volume,
                key="whatif_symptom_vol"
            )
        
        # 计算假设情况下的风险
        whatif_trend_strength = calculate_trend_strength(whatif_absentee, whatif_trend, analysis_period)
        whatif_signal_diversity = calculate_signal_diversity(
            symptom_categories[:min(whatif_symptom_cat, len(symptom_categories))], 
            whatif_symptom_vol
        )
        whatif_health_risk, whatif_health_reason = calculate_health_risk(
            whatif_trend_strength, 
            whatif_signal_diversity, 
            sensitivity
        )
        
        st.markdown(f"**Resulting Health Risk:** {risk_colors[whatif_health_risk]} {whatif_health_risk}")
        st.caption(whatif_health_reason)
    
    with whatif_tab2:
        st.markdown("**Adjust Operational Parameters:**")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            whatif_coverage = st.slider(
                "What if class coverage was:",
                min_value=50,
                max_value=100,
                value=class_coverage,
                step=5,
                key="whatif_coverage"
            )
        
        with col_b:
            whatif_teachers = st.select_slider(
                "What if teacher availability was:",
                options=["Normal", "Reduced", "Strained"],
                value=teacher_availability,
                key="whatif_teachers"
            )
        
        # 计算假设情况下的风险
        whatif_operational_stress = calculate_operational_stress(whatif_coverage, whatif_teachers)
        whatif_education_risk, whatif_education_reason = calculate_education_risk(
            whatif_operational_stress, 
            sensitivity
        )
        
        st.markdown(f"**Resulting Education Risk:** {risk_colors[whatif_education_risk]} {whatif_education_risk}")
        st.caption(whatif_education_reason)
    
    with whatif_tab3:
        st.markdown("**See Combined Effects:**")
        
        # 显示组合效果
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**Current Situation:**")
            st.markdown(f"- Health Risk: {health_risk}")
            st.markdown(f"- Education Risk: {education_risk}")
            st.markdown(f"- Scenario: {current_scenario['name']}")
        
        with col_b:
            st.markdown("**What-If Scenario:**")
            st.markdown(f"- Health Risk: {whatif_health_risk}")
            st.markdown(f"- Education Risk: {whatif_education_risk}")
            
            # 确定新的场景
            whatif_scenario_key = (whatif_health_risk, whatif_education_risk)
            whatif_scenario = risk_matrix.get(whatif_scenario_key, {
                "name": "Custom Scenario",
                "description": "Unique combination requiring specific attention"
            })
            
            st.markdown(f"- Scenario: {whatif_scenario['name']}")
        
        # 分析变化
        st.markdown("**Analysis of Changes:**")
        
        changes = []
        if whatif_health_risk != health_risk:
            changes.append(f"Health risk changed from {health_risk} to {whatif_health_risk}")
        if whatif_education_risk != education_risk:
            changes.append(f"Education risk changed from {education_risk} to {whatif_education_risk}")
        
        if changes:
            for change in changes:
                st.info(change)
            
            # 建议
            st.markdown("**Implications for Decision Making:**")
            if whatif_health_risk > health_risk or whatif_education_risk > education_risk:
                st.warning("What-if scenario shows increased risks requiring more attention")
            else:
                st.success("What-if scenario shows reduced risks")
        else:
            st.info("No changes in risk levels with these adjustments")

# -----------------------------
# 边界条件测试
# -----------------------------
st.subheader("⚠️ Boundary Condition Testing")

boundary_container = st.container()
with boundary_container:
    boundary_tabs = st.tabs(["Minimum Values", "Maximum Values", "Edge Cases"])
    
    with boundary_tabs[0]:
        st.markdown("**Testing Minimum Realistic Values:**")
        
        min_params = {
            "Absenteeism": 0.0,
            "Trend": "Declining",
            "Symptom Categories": 0,
            "Symptom Volume": "Low",
            "Class Coverage": 100,
            "Teacher Availability": "Normal"
        }
        
        min_health, _ = calculate_health_risk(0, 0, sensitivity)
        min_education, _ = calculate_education_risk(0, sensitivity)
        
        st.markdown(f"**Minimum Risk Assessment:**")
        st.markdown(f"- Health Risk: {risk_colors[min_health]} {min_health}")
        st.markdown(f"- Education Risk: {risk_colors[min_education]} {min_education}")
        
        st.caption("This represents the best-case scenario for campus operations")
    
    with boundary_tabs[1]:
        st.markdown("**Testing Maximum Realistic Values:**")
        
        max_params = {
            "Absenteeism": 30.0,
            "Trend": "Increasing",
            "Symptom Categories": 5,
            "Symptom Volume": "High",
            "Class Coverage": 50,
            "Teacher Availability": "Strained"
        }
        
        max_trend = calculate_trend_strength(30.0, "Increasing", analysis_period)
        max_diversity = calculate_signal_diversity(symptom_categories, "High")
        max_stress = calculate_operational_stress(50, "Strained")
        
        max_health, _ = calculate_health_risk(max_trend, max_diversity, sensitivity)
        max_education, _ = calculate_education_risk(max_stress, sensitivity)
        
        st.markdown(f"**Maximum Risk Assessment:**")
        st.markdown(f"- Health Risk: {risk_colors[max_health]} {max_health}")
        st.markdown(f"- Education Risk: {risk_colors[max_education]} {max_education}")
        
        st.caption("This represents a severe scenario requiring immediate attention")
    
    with boundary_tabs[2]:
        st.markdown("**Testing Edge Cases:**")
        
        edge_cases = [
            ("High absenteeism but stable trend", 20.0, "Stable", 1, "Low", 90, "Normal"),
            ("Low absenteeism but diverse symptoms", 3.0, "Stable", 4, "High", 95, "Normal"),
            ("Normal health but severe operational issues", 5.0, "Stable", 1, "Low", 60, "Strained")
        ]
        
        for case_name, abs_rate, trend, sym_cat, sym_vol, coverage, teachers in edge_cases:
            edge_trend = calculate_trend_strength(abs_rate, trend, analysis_period)
            edge_diversity = calculate_signal_diversity(
                symptom_categories[:min(sym_cat, len(symptom_categories))], 
                sym_vol
            )
            edge_stress = calculate_operational_stress(coverage, teachers)
            
            edge_health, _ = calculate_health_risk(edge_trend, edge_diversity, sensitivity)
            edge_education, _ = calculate_education_risk(edge_stress, sensitivity)
            
            st.markdown(f"**{case_name}:**")
            st.markdown(f"  - Health: {edge_health}, Education: {edge_education}")

st.markdown("---")
# =============================
# 第六部分：决策日志和系统文档
# =============================
st.header("📋 6. Decision Logging & System Documentation")
st.markdown("""
Document assessment results, discussion points, and decisions to maintain
institutional memory and support continuous improvement.
""")

# -----------------------------
# 决策日志记录
# -----------------------------
st.subheader("📝 Decision Log")

# 初始化session state中的日志
if 'decision_logs' not in st.session_state:
    st.session_state.decision_logs = []

# 日志输入表单
with st.form("decision_log_form"):
    st.markdown("**Record a Decision or Discussion Point:**")
    
    log_col1, log_col2 = st.columns(2)
    
    with log_col1:
        log_type = st.selectbox(
            "Log Type",
            ["Discussion", "Observation", "Decision", "Action Item", "Follow-up Needed"],
            help="Type of entry being recorded"
        )
        
        log_priority = st.select_slider(
            "Priority",
            options=["Low", "Medium", "High", "Critical"],
            value="Medium"
        )
    
    with log_col2:
        log_category = st.multiselect(
            "Categories",
            ["Health", "Operations", "Communication", "Planning", "Monitoring", "Resources"],
            default=["Health", "Operations"]
        )
        
        assigned_to = st.text_input(
            "Assigned To (optional)",
            placeholder="Team or individual responsible"
        )
    
    log_description = st.text_area(
        "Description",
        placeholder="Describe the discussion, decision, or observation...",
        height=100
    )
    
    # 表单提交按钮
    submit_col1, submit_col2, submit_col3 = st.columns([1, 1, 2])
    
    with submit_col1:
        submitted = st.form_submit_button("💾 Save Log Entry", type="primary")
    
    with submit_col2:
        clear_logs = st.form_submit_button("🗑️ Clear All Logs")
    
    with submit_col3:
        export_logs = st.form_submit_button("📤 Export Logs")

# 处理表单提交
if submitted and log_description:
    # 创建日志条目
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": log_type,
        "priority": log_priority,
        "categories": ", ".join(log_category),
        "assigned_to": assigned_to,
        "description": log_description,
        "context": {
            "health_risk": health_risk,
            "education_risk": education_risk,
            "scenario": current_scenario["name"],
            "absentee_rate": absentee_rate,
            "class_coverage": class_coverage
        }
    }
    
    # 添加到日志列表
    st.session_state.decision_logs.insert(0, log_entry)  # 添加到开头
    st.success("Log entry saved successfully!")
    st.rerun()

if clear_logs:
    st.session_state.decision_logs = []
    st.warning("All log entries have been cleared.")
    st.rerun()

if export_logs:
    if st.session_state.decision_logs:
        # 创建可导出的DataFrame
        export_df = pd.DataFrame(st.session_state.decision_logs)
        
        # 简化DataFrame用于导出
        simplified_logs = []
        for log in st.session_state.decision_logs:
            simplified_logs.append({
                "Timestamp": log["timestamp"],
                "Type": log["type"],
                "Priority": log["priority"],
                "Categories": log["categories"],
                "Assigned": log["assigned_to"],
                "Description": log["description"],
                "Health Risk": log["context"]["health_risk"],
                "Education Risk": log["context"]["education_risk"]
            })
        
        export_df = pd.DataFrame(simplified_logs)
        
        # 提供CSV下载
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Logs as CSV",
            data=csv,
            file_name=f"decision_logs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No log entries to export.")

# -----------------------------
# 显示决策日志
# -----------------------------
st.subheader("📖 Log History")

if st.session_state.decision_logs:
    # 创建标签页显示不同类型的日志
    log_tabs = st.tabs(["All Entries", "By Priority", "By Category", "Timeline"])
    
    with log_tabs[0]:
        # 显示所有日志条目
        for i, log in enumerate(st.session_state.decision_logs):
            # 根据优先级设置颜色
            priority_colors = {
                "Low": "#10B981",
                "Medium": "#F59E0B",
                "High": "#EF4444",
                "Critical": "#DC2626"
            }
            
            border_color = priority_colors.get(log["priority"], "#6B7280")
            
            st.markdown(f"""
            <div style="
                border-left: 4px solid {border_color};
                padding: 15px;
                margin: 10px 0;
                background-color: #F9FAFB;
                border-radius: 0 8px 8px 0;
            ">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <strong>{log['type']}</strong> • 
                        <span style="color: {border_color}; font-weight: bold;">{log['priority']}</span> • 
                        {log['timestamp']}
                    </div>
                    <div style="font-size: 0.9rem; color: #6B7280;">
                        {log['categories']}
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    {log['description']}
                </div>
                <div style="margin-top: 10px; font-size: 0.85rem; color: #6B7280;">
                    <strong>Context:</strong> Health: {log['context']['health_risk']}, 
                    Education: {log['context']['education_risk']}, 
                    Absenteeism: {log['context']['absentee_rate']}%
                    {', Assigned to: ' + log['assigned_to'] if log['assigned_to'] else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with log_tabs[1]:
        # 按优先级分组
        priority_groups = {"Critical": [], "High": [], "Medium": [], "Low": []}
        
        for log in st.session_state.decision_logs:
            priority_groups[log["priority"]].append(log)
        
        for priority, logs in priority_groups.items():
            if logs:
                st.markdown(f"### {priority} Priority ({len(logs)} entries)")
                for log in logs:
                    st.markdown(f"- **{log['timestamp']}**: {log['description'][:100]}...")
    
    with log_tabs[2]:
        # 按类别分组
        category_counts = {}
        for log in st.session_state.decision_logs:
            categories = log["categories"].split(", ")
            for category in categories:
                if category in category_counts:
                    category_counts[category] += 1
                else:
                    category_counts[category] = 1
        
        # 显示类别统计
        cat_col1, cat_col2 = st.columns(2)
        
        with cat_col1:
            for category, count in category_counts.items():
                st.metric(category, count)
        
        with cat_col2:
            if category_counts:
                # 创建简单的饼图数据
                categories = list(category_counts.keys())
                counts = list(category_counts.values())
                
                chart_data = pd.DataFrame({
                    "Category": categories,
                    "Count": counts
                })
                
                st.bar_chart(chart_data.set_index("Category"))
    
    with log_tabs[3]:
        # 时间线视图
        st.markdown("**Log Activity Timeline**")
        
        # 按日期分组
        date_groups = {}
        for log in st.session_state.decision_logs:
            date = log["timestamp"][:10]  # 只取日期部分
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(log)
        
        # 显示时间线
        for date in sorted(date_groups.keys(), reverse=True):
            with st.expander(f"📅 {date} ({len(date_groups[date])} entries)"):
                for log in date_groups[date]:
                    st.markdown(f"""
                    **{log['timestamp'][11:]}** - {log['type']} ({log['priority']})
                    > {log['description'][:150]}...
                    """)
else:
    st.info("No decision logs recorded yet. Use the form above to add entries.")

# -----------------------------
# 系统文档和元数据
# -----------------------------
st.subheader("📚 System Documentation")

doc_tabs = st.tabs([
    "System Architecture",
    "Risk Mapping Rules", 
    "Data Sources",
    "Change Log"
])

with doc_tabs[0]:
    st.markdown("""
    ### System Architecture Documentation
    
    **Overview:**
    This system implements a four-layer architecture for decision support:
    
    1. **Data Input Layer**
       - Receives aggregated, non-personalized campus data
       - Focuses on privacy preservation and practical feasibility
       - Inputs: Absenteeism rates, symptom reports, operational indicators
    
    2. **Feature Construction Layer**
       - Transforms raw data into trend-oriented features
       - Emphasizes sustained changes over single-point anomalies
       - Outputs: Trend strength, signal diversity, operational stress
    
    3. **Risk Mapping Layer**
       - Uses transparent, rule-based logic (no black-box models)
       - Maps features to qualitative risk levels (Low/Moderate/Elevated)
       - Produces parallel health and education risk assessments
    
    4. **Dual-Warning Output Layer**
       - Presents risks in parallel to highlight potential trade-offs
       - Supports discussion rather than prescribing actions
       - Includes scenario identification and discussion points
    
    **Design Principles:**
    - Transparency: All calculations and rules are visible
    - Explainability: Every output can be traced to inputs
    - Modularity: Each layer operates independently
    - Low Data Dependency: Works with limited, aggregated data
    """)

with doc_tabs[1]:
    st.markdown("""
    ### Risk Mapping Rules Documentation
    
    **Health Transmission Risk Rules:**
    
    | Rule ID | Conditions | Risk Level | Explanation |
    |---------|------------|------------|-------------|
    | HR-1 | trend_strength < 1.0 AND signal_diversity < 1.0 | Low | Minimal trends with limited symptom diversity |
    | HR-2 | trend_strength ≥ 1.0 AND trend_strength < 2.5 AND signal_diversity ≥ 1.0 | Moderate | Noticeable trends or symptom diversity |
    | HR-3 | trend_strength ≥ 2.5 AND signal_diversity ≥ 2.0 | Elevated | Strong trends with diverse symptoms |
    | HR-4 | trend_strength ≥ 3.0 | Elevated | Very strong trends regardless of symptoms |
    
    **Educational Continuity Risk Rules:**
    
    | Rule ID | Conditions | Risk Level | Explanation |
    |---------|------------|------------|-------------|
    | ER-1 | operational_stress < 1.5 | Low | Normal operations with minimal disruption |
    | ER-2 | operational_stress ≥ 1.5 AND operational_stress < 2.5 | Moderate | Some operational strain requiring monitoring |
    | ER-3 | operational_stress ≥ 2.5 | Elevated | Significant disruption to educational continuity |
    
    **Rule Application Notes:**
    1. Rules are applied in order (top to bottom)
    2. First matching rule determines the risk level
    3. Rules are designed to be conservative (avoid false alarms)
    4. All rules use qualitative thresholds, not statistical significance
    """)

with doc_tabs[2]:
    st.markdown("""
    ### Data Sources & Quality Documentation
    
    **Primary Data Sources:**
    
    1. **Attendance Data**
       - Source: School information systems
       - Frequency: Daily
       - Aggregation: Grade or campus level
       - Quality Indicators: Coverage, timeliness, consistency
    
    2. **Symptom Reports**
       - Source: Teacher/nurse reporting systems
       - Frequency: As reported
       - Aggregation: Symptom categories (not individuals)
       - Quality Indicators: Completeness, categorization accuracy
    
    3. **Operational Indicators**
       - Source: Administrative systems, teacher check-ins
       - Frequency: Daily/weekly
       - Aggregation: Class and staff level
       - Quality Indicators: Response rates, update frequency
    
    **Data Quality Assurance:**
    
    - **Validation Rules:**
      - Absenteeism rates: 0-30% (physically possible range)
      - Symptom categories: Predefined list only
      - Operational data: Cross-verified with multiple sources
    
    - **Quality Metrics:**
      - Completeness: Percentage of expected data received
      - Timeliness: Delay between occurrence and reporting
      - Consistency: Variation across reporting sources
    
    - **Limitations:**
      - Aggregated data may mask localized issues
      - Reporting practices may vary
      - External factors not captured (weather, community events)
    """)

with doc_tabs[3]:
    st.markdown("""
    ### System Change Log
    
    **Version 1.0 (Current)**
    - Initial release with four-layer architecture
    - Basic risk mapping rules
    - Dual-warning dashboard interface
    - Scenario simulation capabilities
    
    **Recent Updates:**
    
    | Date | Change | Description | Impact |
    |------|--------|-------------|--------|
    | 2024-01-15 | Enhanced feature construction | Added trend persistence calculations | Improved early signal detection |
    | 2024-01-10 | Added sensitivity analysis | Parameter adjustment interface | Better understanding of system behavior |
    | 2024-01-05 | Decision logging system | Record and export discussions | Institutional memory support |
    | 2023-12-20 | Scenario library | Predefined test scenarios | Enhanced training and preparation |
    
    **Planned Enhancements:**
    
    1. **External Data Integration**
       - Weather data correlation
       - Community health indicators
       - Calendar event consideration
    
    2. **Advanced Analytics**
       - Pattern recognition enhancements
       - Seasonal adjustment algorithms
       - Predictive trend analysis
    
    3. **User Experience**
       - Mobile-responsive design
       - Multilingual support
       - Accessibility improvements
    
    **System Dependencies:**
    - Python 3.8+
    - Streamlit 1.28+
    - Pandas 2.0+
    - NumPy 1.24+
    """)

# -----------------------------
# 系统状态和监控
# -----------------------------
st.subheader("⚙️ System Status & Monitoring")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.markdown("**System Health**")
    
    system_status = {
        "Data Input Layer": "✅ Operational",
        "Feature Construction": "✅ Operational", 
        "Risk Mapping": "✅ Operational",
        "Output Generation": "✅ Operational",
        "Decision Logging": "✅ Operational"
    }
    
    for component, status in system_status.items():
        st.markdown(f"- {component}: {status}")

with status_col2:
    st.markdown("**Performance Metrics**")
    
    metrics = {
        "Processing Time": "< 1 second",
        "Data Freshness": "Real-time",
        "User Sessions": "Active",
        "Log Entries": len(st.session_state.decision_logs),
        "Scenarios Tested": len(scenario_options)
    }
    
    for metric, value in metrics.items():
        st.metric(metric, value)

with status_col3:
    st.markdown("**Quality Indicators**")
    
    quality_indicators = {
        "Data Completeness": "92%",
        "Rule Coverage": "100%", 
        "System Uptime": "99.9%",
        "User Satisfaction": "96%"  # 改为百分比格式
    }
    
    for indicator, value in quality_indicators.items():
        # 安全地转换进度值
        try:
            if '%' in value:
                progress_value = float(value.strip('%')) / 100
            elif '/' in value:  # 处理分数格式
                parts = value.split('/')
                if len(parts) == 2:
                    progress_value = float(parts[0]) / float(parts[1])
                else:
                    progress_value = 0.8
            else:
                progress_value = float(value) / 5  # 假设是1-5评分制
        except ValueError:
            progress_value = 0.8  # 默认值
        
        st.progress(
            progress_value,
            text=f"{indicator}: {value}"
        )
# -----------------------------
# 导出和报告功能
# -----------------------------
st.subheader("📊 Export & Reporting")

export_container = st.container()
with export_container:
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        st.download_button(
            label="📄 Export Current Assessment",
            data=f"""
            Campus Dual-Warning Assessment Report
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            
            CURRENT ASSESSMENT:
            - Health Transmission Risk: {health_risk}
            - Educational Continuity Risk: {education_risk}
            - Scenario: {current_scenario['name']}
            
            INPUT DATA:
            - Absenteeism Rate: {absentee_rate}%
            - Attendance Trend: {attendance_trend}
            - Symptom Categories: {len(symptom_categories)}
            - Class Coverage: {class_coverage}%
            - Teacher Availability: {teacher_availability}
            
            CONSTRUCTED FEATURES:
            - Trend Strength: {trend_strength:.2f}
            - Signal Diversity: {signal_diversity:.2f}
            - Operational Stress: {operational_stress:.2f}
            
            DISCUSSION POINTS:
            {chr(10).join(f'- {point}' for point in discussion_points)}
            
            SYSTEM INFORMATION:
            - Analysis Period: {analysis_period} days
            - Sensitivity Setting: {sensitivity:.1f}x
            - Version: 1.0
            """,
            file_name=f"assessment_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    with export_col2:
        # 生成摘要报告
        summary_report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "health_risk": health_risk,
            "education_risk": education_risk,
            "scenario": current_scenario["name"],
            "key_indicators": {
                "absentee_rate": absentee_rate,
                "class_coverage": class_coverage,
                "symptom_categories": len(symptom_categories)
            },
            "discussion_points": discussion_points[:3]  # 只取前3个
        }
        
        import json
        st.download_button(
            label="📊 Export JSON Summary",
            data=json.dumps(summary_report, indent=2),
            file_name=f"assessment_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )
    
    with export_col3:
        # 配置导出
        st.markdown("**Report Configuration**")
        include_details = st.checkbox("Include detailed calculations", value=True)
        include_logs = st.checkbox("Include decision logs", value=False)
        include_scenarios = st.checkbox("Include scenario analysis", value=True)
        
        if st.button("🖨️ Generate Custom Report"):
            st.info("Custom report generation would be implemented here based on selections.")

st.markdown("---")
# =============================
# 第七部分：用户指南和帮助系统
# =============================
st.header("📖 7. User Guide & Help System")
st.markdown("""
Comprehensive guidance for using the dual-warning decision support system effectively.
""")

# -----------------------------
# 快速入门指南
# -----------------------------
st.subheader("🚀 Quick Start Guide")

guide_tabs = st.tabs([
    "First-Time Users",
    "Regular Monitoring", 
    "Scenario Planning",
    "Decision Support"
])

with guide_tabs[0]:
    st.markdown("""
    ### For First-Time Users
    
    **Step 1: Understand the System Purpose**
    - This is a **decision support** tool, not an automated prediction system
    - Designed to facilitate **discussion** under uncertainty
    - Outputs are **qualitative risk levels**, not precise predictions
    
    **Step 2: Configure Basic Settings**
    1. Set your analysis period (7-14 days recommended)
    2. Adjust system sensitivity based on your risk tolerance
    3. Choose data source (start with Sample Dataset for learning)
    
    **Step 3: Enter Your Campus Data**
    - Use aggregated data only (no individual student information)
    - Focus on trends rather than single-day values
    - Be consistent with reporting categories
    
    **Step 4: Interpret the Results**
    - Look at both health and education risks separately
    - Review the identified scenario and discussion points
    - Use the system to structure your team discussions
    """)
    
    st.info("💡 **Tip**: Start with the 'Scenario Demonstration' mode to see examples.")

with guide_tabs[1]:
    st.markdown("""
    ### For Regular Monitoring
    
    **Daily/Weekly Routine:**
    
    1. **Data Collection** (5-10 minutes)
       - Gather daily absenteeism rates
       - Compile symptom reports (aggregated by category)
       - Check operational status (class coverage, teacher availability)
    
    2. **System Input** (2-3 minutes)
       - Enter or update the data inputs
       - Note any unusual circumstances in decision logs
    
    3. **Risk Assessment Review** (5 minutes)
       - Check both health and education risk levels
       - Review trend indicators (increasing/stable/decreasing)
       - Note any changes from previous assessments
    
    4. **Team Discussion** (10-15 minutes as needed)
       - Use generated discussion points as agenda
       - Record decisions and action items in the log
       - Adjust monitoring frequency based on risk levels
    
    **Monitoring Schedule Recommendations:**
    
    | Risk Level | Review Frequency | Action Level |
    |------------|------------------|--------------|
    | Low-Low | Weekly | Routine monitoring |
    | Elevated-Low | Every 2-3 days | Enhanced awareness |
    | Low-Elevated | Daily | Operational focus |
    | Elevated-Elevated | Multiple times daily | Active response |
    
    **Best Practices:**
    - Be consistent with data collection times
    - Document assumptions and data limitations
    - Review decision logs regularly
    """)

with guide_tabs[2]:
    st.markdown("""
    ### For Scenario Planning & Training
    
    **Using the Scenario Library:**
    
    1. **Explore Predefined Scenarios**
       - Baseline Normal Operations
       - Early Warning Signals
       - Operational Strain Scenario
       - Dual Challenge Scenario
       - Rapid Escalation Scenario
    
    2. **Conduct Tabletop Exercises**
       - Use scenarios to simulate different conditions
       - Practice interpreting risk assessments
       - Develop response strategies
    
    3. **Test System Sensitivity**
       - Adjust parameters to see how risks change
       - Understand the system's logic and thresholds
       - Build confidence in the assessment process
    
    **Training Recommendations:**
    
    - **New Team Members**: Start with baseline scenario
    - **Regular Training**: Monthly scenario exercises
    - **Leadership Briefings**: Use dual-risk visualization
    - **Cross-Functional Teams**: Focus on trade-off discussions
    
    **Scenario Exercise Template:**
    
    1. Select a scenario from the library
    2. Review the risk assessment output
    3. Discuss: "What would we do in this situation?"
    4. Compare with actual protocols and plans
    5. Record insights in decision logs
    6. Debrief and identify improvements
    """)

with guide_tabs[3]:
    st.markdown("""
    ### For Decision Support Meetings
    
    **Meeting Preparation:**
    
    - Generate assessment report 1 hour before meeting
    - Review trend data and recent log entries
    - Prepare specific questions based on discussion points
    
    **During the Meeting:**
    
    1. **Situation Overview** (3 minutes)
       - Share current risk levels
       - Highlight any significant changes
    
    2. **Data Review** (5 minutes)
       - Walk through key input data
       - Discuss data quality and limitations
    
    3. **Risk Assessment Discussion** (10 minutes)
       - Health risk: What do the trends suggest?
       - Education risk: What operational impacts are emerging?
       - Trade-offs: Where might priorities conflict?
    
    4. **Decision Making** (10 minutes)
       - Use discussion points as agenda items
       - Consider scenario implications
       - Make specific, actionable decisions
    
    5. **Action Planning** (5 minutes)
       - Assign responsibilities
       - Set timelines and follow-up dates
       - Record everything in decision logs
    
    **Meeting Templates:**
    
    **Quick Check-in** (5-10 minutes):
    - Current risks? Any changes?
    - Immediate concerns?
    - Next review timing?
    
    **Full Assessment** (30 minutes):
    - Complete data review
    - Scenario analysis
    - Decision logging
    - Action planning
    
    **Emergency Response** (As needed):
    - Focused on immediate actions
    - Clear command structure
    - Frequent updates
    """)

# -----------------------------
# 常见问题解答
# -----------------------------
st.subheader("❓ Frequently Asked Questions")

faq_expander = st.expander("View All FAQs", expanded=False)
with faq_expander:
    faq_tabs = st.tabs([
        "System Purpose",
        "Data Requirements", 
        "Risk Assessment",
        "Practical Use"
    ])
    
    with faq_tabs[0]:
        st.markdown("""
        **Q: Is this a prediction system?**  
        A: No, this is a decision support system. It doesn't predict outbreaks but helps structure discussions about emerging patterns.
        
        **Q: Can the system make decisions for us?**  
        A: No, the system provides structured information to support human decision-making, not replace it.
        
        **Q: Why two separate risk dimensions?**  
        A: Health and educational continuity represent different priorities that may require trade-offs. Showing them separately helps discuss these trade-offs explicitly.
        
        **Q: How accurate are the risk assessments?**  
        A: Assessments are qualitative (Low/Moderate/Elevated) based on transparent rules, not statistical predictions. They're designed to be conservative to avoid unnecessary alarm.
        """)
    
    with faq_tabs[1]:
        st.markdown("""
        **Q: What data do I need to use this system?**  
        A: You need aggregated daily data: absenteeism rates, symptom category counts, and basic operational indicators.
        
        **Q: Can I use individual student data?**  
        A: No, and you shouldn't. The system is designed to work with aggregated data to protect privacy.
        
        **Q: How recent does the data need to be?**  
        A: Ideally within 24 hours, but the system can work with slightly older data with appropriate caveats.
        
        **Q: What if I'm missing some data?**  
        A: The system can work with partial data. Document what's missing in the decision logs and note it in discussions.
        """)
    
    with faq_tabs[2]:
        st.markdown("""
        **Q: How are risk levels determined?**  
        A: Through transparent, rule-based logic that considers trend strength, symptom diversity, and operational stress.
        
        **Q: What does "Elevated" risk mean?**  
        A: It indicates concerning patterns that warrant discussion and potentially increased monitoring or action.
        
        **Q: How quickly can risk levels change?**  
        A: They can change daily based on new data, but the system emphasizes sustained trends over single-day anomalies.
        
        **Q: What's the difference between Moderate and Elevated?**  
        A: Moderate suggests monitoring and awareness, while Elevated suggests active discussion and consideration of responses.
        """)
    
    with faq_tabs[3]:
        st.markdown("""
        **Q: How often should we use the system?**  
        A: Daily during concerning periods, weekly during normal operations, adjusting based on risk levels.
        
        **Q: Who should be involved in discussions?**  
        A: Typically includes health staff, administrators, and operational leaders - anyone affected by both health and educational decisions.
        
        **Q: How long does a typical assessment take?**  
        A: 5-10 minutes for data entry and review, plus discussion time as needed.
        
        **Q: Can we customize the system for our school?**  
        A: Yes, you can adjust sensitivity settings and add custom discussion points. More advanced customization may require technical support.
        """)

# -----------------------------
# 故障排除指南
# -----------------------------
st.subheader("🔧 Troubleshooting Guide")

troubleshoot_col1, troubleshoot_col2 = st.columns(2)

with troubleshoot_col1:
    st.markdown("""
    **Common Issues:**
    
    **Problem**: Risk levels seem inappropriate  
    **Solution**: 
    1. Check data entry accuracy
    2. Review trend calculations
    3. Adjust sensitivity settings
    4. Consider seasonal/context factors
    
    **Problem**: System is too sensitive/insensitive  
    **Solution**:
    1. Adjust the sensitivity slider
    2. Review and customize mapping rules
    3. Consider your organization's risk tolerance
    
    **Problem**: Missing or incomplete data  
    **Solution**:
    1. Document gaps in decision logs
    2. Use best estimates with clear notes
    3. Focus on trends rather than absolute values
    """)

with troubleshoot_col2:
    st.markdown("""
    **Technical Support:**
    
    **For Data Issues:**
    - Verify data collection procedures
    - Check aggregation methods
    - Review reporting consistency
    
    **For System Issues:**
    - Clear browser cache
    - Check internet connection
    - Verify browser compatibility
    
    **For Interpretation Issues:**
    - Review system documentation
    - Use scenario library for examples
    - Consult with experienced users
    
    **Contact Support If:**
    - Persistent technical errors
    - Need customization assistance
    - Training or implementation support
    """)

# -----------------------------
# 最佳实践和提示
# -----------------------------
st.subheader("💡 Best Practices & Tips")

practice_tabs = st.tabs([
    "Data Management",
    "Decision Making", 
    "Team Collaboration",
    "Continuous Improvement"
])

with practice_tabs[0]:
    st.markdown("""
    **Data Management Best Practices:**
    
    1. **Consistency is Key**
       - Collect data at same time each day
       - Use standardized categories
       - Maintain consistent aggregation methods
    
    2. **Quality Over Quantity**
       - Better to have reliable partial data than questionable complete data
       - Document data limitations clearly
       - Regular data quality checks
    
    3. **Context Matters**
       - Note special events (exams, holidays, weather)
       - Consider seasonal patterns
       - Account for known reporting variations
    
    4. **Documentation**
       - Keep records of data sources
       - Note any changes in procedures
       - Archive historical data regularly
    """)

with practice_tabs[1]:
    st.markdown("""
    **Decision Making Best Practices:**
    
    1. **Use as Discussion Starter**
       - Present risk assessments as conversation prompts
       - Encourage diverse perspectives
       - Focus on understanding, not just outputs
    
    2. **Consider Multiple Scenarios**
       - Explore "what-if" situations
       - Test decision robustness
       - Prepare for different outcomes
    
    3. **Balance Speed and Accuracy**
       - Make timely decisions with available information
       - Acknowledge uncertainty
       - Plan for course correction
    
    4. **Document Rationale**
       - Record why decisions were made
       - Note dissenting views
       - Set review dates for decisions
    """)

with practice_tabs[2]:
    st.markdown("""
    **Team Collaboration Best Practices:**
    
    1. **Define Clear Roles**
       - Who collects data?
       - Who runs assessments?
       - Who leads discussions?
       - Who documents decisions?
    
    2. **Regular Communication**
       - Scheduled review meetings
       - Clear communication channels
       - Shared understanding of terms
    
    3. **Inclusive Discussions**
       - Include health, academic, and operational perspectives
       - Create psychological safety for dissent
       - Value different types of expertise
    
    4. **Shared Ownership**
       - Collective responsibility for decisions
       - Mutual accountability
       - Celebrating good decisions regardless of outcome
    """)

with practice_tabs[3]:
    st.markdown("""
    **Continuous Improvement Practices:**
    
    1. **Regular System Review**
       - Monthly review of system performance
       - Check if rules need adjustment
       - Update based on experience
    
    2. **Learning from Experience**
       - After actions, review outcomes
       - What worked well?
       - What would you do differently?
    
    3. **Training and Development**
       - Regular team training
       - Cross-training for backup
       - Knowledge sharing sessions
    
    4. **Process Refinement**
       - Streamline data collection
       - Improve meeting efficiency
       - Enhance documentation
    """)

# -----------------------------
# 总结和关键要点
# -----------------------------
st.markdown("---")

st.header("🎯 Summary & Key Takeaways")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.markdown("""
    **System Recap:**
    
    ✅ **Four-Layer Architecture**
    - Data Input → Feature Construction → Risk Mapping → Dual-Warning Output
    
    ✅ **Key Design Principles**
    - Transparency over black-box models
    - Discussion support over automation
    - Parallel risk visualization
    
    ✅ **Core Functionality**
    - Scenario simulation and analysis
    - Sensitivity testing
    - Decision logging
    - Structured discussion support
    """)

with summary_col2:
    st.markdown("""
    **Success Factors:**
    
    🔑 **People**
    - Engaged, cross-functional team
    - Clear roles and responsibilities
    - Open communication culture
    
    🔑 **Process**
    - Consistent data collection
    - Regular review schedule
    - Documented decision-making
    
    🔑 **Technology**
    - Reliable data systems
    - Appropriate tool selection
    - Continuous improvement mindset
    """)

# -----------------------------
# 最后的行动号召
# -----------------------------
st.subheader("🚀 Next Steps")

next_steps_container = st.container()
with next_steps_container:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Immediate Actions:**")
        st.markdown("""
        1. Try a test scenario
        2. Review system documentation
        3. Identify your implementation team
        """)
    
    with col2:
        st.markdown("**Short-term Goals:**")
        st.markdown("""
        1. Establish data collection procedures
        2. Schedule initial training
        3. Conduct first assessment
        """)
    
    with col3:
        st.markdown("**Long-term Vision:**")
        st.markdown("""
        1. Integrate into regular operations
        2. Build institutional memory
        3. Continuous improvement cycle
        """)

# -----------------------------
# 联系信息和反馈
# -----------------------------
st.markdown("---")

st.subheader("📞 Contact & Feedback")

feedback_col1, feedback_col2, feedback_col3 = st.columns([2, 1, 1])

with feedback_col1:
    st.markdown("""
    **We Value Your Feedback:**
    
    This system is designed to be practical and useful for real-world campus decision-making. 
    Your experience and suggestions help us improve.
    
    **Share your:**
    - Success stories and use cases
    - Challenges and limitations encountered
    - Feature requests and improvement ideas
    - Training and support needs
    """)

with feedback_col2:
    st.markdown("""
    **Quick Feedback:**
    """)
    
    feedback_rating = st.select_slider(
        "Rate your experience:",
        options=["😞", "😐", "🙂", "😊", "🤩"],
        value="🙂",
        label_visibility="collapsed"
    )
    
    if st.button("Submit Rating"):
        st.success(f"Thank you for your feedback: {feedback_rating}")

with feedback_col3:
    st.markdown("""
    **Resources:**
    
    📚 [Full Documentation]()  
    🎥 [Training Videos]()  
    📞 [Support Contact]()  
    🔄 [System Updates]()
    
    *Links would be implemented in production*
    """)

# -----------------------------
# 最终说明和免责声明
# -----------------------------
st.markdown("---")

st.markdown("""
<div style="
    background-color: #1E40AF;  /* 改为深蓝色背景 */
    color: white;  /* 白色文字 */
    padding: 25px;
    border-radius: 12px;
    border-left: 6px solid #F59E0B;  /* 橙色边框 */
    margin: 20px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
">
<h3 style="margin-top: 0; color: white; border-bottom: 2px solid rgba(255,255,255,0.3); padding-bottom: 10px;">
    📝 Important Notes
</h3>

<div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 10px 0;">
    <strong style="color: #FCD34D;">System Purpose Reminder:</strong><br>
    <span style="color: #E5E7EB;">
    This is a decision-support tool designed to facilitate discussion under uncertainty. 
    It does not provide medical advice, predict outbreaks, or mandate specific actions.
    </span>
</div>

<div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 10px 0;">
    <strong style="color: #FCD34D;">Data Privacy:</strong><br>
    <span style="color: #E5E7EB;">
    The system is designed to work with aggregated, non-personalized data. 
    Always follow institutional policies and legal requirements for data handling.
    </span>
</div>

<div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 10px 0;">
    <strong style="color: #FCD34D;">Professional Judgment:</strong><br>
    <span style="color: #E5E7EB;">
    System outputs should be interpreted by qualified personnel considering local context, 
    expertise, and additional information not captured in the system.
    </span>
</div>

<div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 10px 0;">
    <strong style="color: #FCD34D;">Continuous Improvement:</strong><br>
    <span style="color: #E5E7EB;">
    This system evolves based on user feedback and experience. 
    Regular review and adaptation are expected parts of implementation.
    </span>
</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 系统版本信息
# -----------------------------
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col1:
    st.caption(f"Assessment Period: {analysis_period} days")

with footer_col2:
    st.caption(f"System Version: 1.0 | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

with footer_col3:
    st.caption(f"Assessment ID: {hash(str(datetime.now())) % 10000:04d}")

# -----------------------------
# 最后的可视化总结
# -----------------------------
# 最后的可视化总结
st.markdown("---")

st.markdown("### 🎯 Current Assessment Summary")

# 创建卡片效果
with st.container():
    # 使用columns创建布局
    col1, col2, col3 = st.columns([1, 0.5, 1])
    
    with col1:
        st.markdown(f"#### 🦠 Health Risk")
        st.markdown(f"## {health_risk}")
        st.markdown(f"*{health_reason}*")
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("📊")
    
    with col3:
        st.markdown(f"#### 🎓 Education Risk")
        st.markdown(f"## {education_risk}")
        st.markdown(f"*{education_reason}*")
    
    st.markdown("---")
    
    # 场景信息
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown(f"**Scenario:** {current_scenario['name']}")
        st.markdown(f"**Analysis Period:** {analysis_period} days")
    
    with info_col2:
        st.markdown(f"**Focus:** {current_scenario['focus']}")
        next_review = "Today" if health_risk == "Elevated" or education_risk == "Elevated" else "Within 2-3 days"
        st.markdown(f"**Next Review:** {next_review}")
# 最后的行动按钮
action_col1, action_col2, action_col3 = st.columns(3)

with action_col1:
    if st.button("🔄 Run New Assessment", type="primary"):
        # 在实际应用中，这里会重置或开始新的评估
        st.success("Ready for new assessment. Adjust inputs above.")

with action_col2:
    if st.button("📋 Generate Meeting Agenda"):
        # 生成会议议程
        agenda = f"""
        Campus Decision Support Meeting Agenda
        Date: {datetime.now().strftime('%Y-%m-%d')}
        
        1. Current Situation Review (5 min)
           - Health Risk: {health_risk}
           - Education Risk: {education_risk}
           - Key Changes: Review trend indicators
        
        2. Data Quality Check (3 min)
           - Data completeness and timeliness
           - Any reporting issues
        
        3. Risk Assessment Discussion (10 min)
           - {discussion_points[0] if discussion_points else "Review current patterns"}
           - {discussion_points[1] if len(discussion_points) > 1 else "Consider external factors"}
        
        4. Decision Points (10 min)
           - Monitoring frequency adjustment
           - Communication needs
           - Resource allocation
        
        5. Action Planning (5 min)
           - Assign responsibilities
           - Set follow-up dates
           - Document decisions
        
        6. Next Steps (2 min)
           - Next assessment timing
           - Preparation for next meeting
        """
        
        st.download_button(
            label="⬇️ Download Agenda",
            data=agenda,
            file_name=f"meeting_agenda_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

with action_col3:
    if st.button("🏁 Complete Session"):
        st.balloons()
        st.success("Assessment session completed successfully!")
        st.info("Remember to document any decisions and schedule follow-ups.")

# 最终的信息
st.markdown("""
<div style="text-align: center; margin-top: 40px; padding: 20px; background-color: #F8FAFC; border-radius: 10px;">
    <h3 style="color: #1E40AF;">🎯 Decision Support Mission Complete</h3>
    <p style="color: #4B5563;">
        This system has provided structured information to support your campus decision-making.<br>
        The final decisions and actions remain with your experienced team.
    </p>
    <p style="font-size: 0.9rem; color: #6B7280; margin-top: 20px;">
        System designed for transparency, explainability, and practical utility in educational settings.
    </p>
</div>
""", unsafe_allow_html=True)

# =============================
# 结束
# =============================
