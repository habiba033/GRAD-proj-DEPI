# ==================================================
# Cardiovascular Risk Dashboard - Streamlit App
# ==================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Cardiovascular Risk Dashboard",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# STYLING (Dark Theme + Glassmorphism)
# ==================================================
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0e0;
    }
    .stApp {background: transparent;}
    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif;
        color: #ff6b6b;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255,107,107,0.3);
    }
    .stMetric > div {
        color: #ff6b6b;
        font-weight: bold;
    }
    .pulse {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% {transform: scale(1);}
        50% {transform: scale(1.05);}
        100% {transform: scale(1);}
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data
def load_data():
    path = r"C:\Users\habib\OneDrive\المستندات\Graduation Project\GRAD-proj-DEPI\Cardiovascular Diseases Risk Prediction Dataset export 2025-10-15 21-12-56.csv"
    df = pd.read_csv(path)
    return df

df = load_data()

# ==================================================
# SIDEBAR FILTERS
# ==================================================
st.sidebar.title("🔍 Filters")

age_filter = st.sidebar.multiselect(
    "Age Category",
    options=sorted(df['Age_Category'].unique()),
    default=sorted(df['Age_Category'].unique())
)

sex_filter = st.sidebar.multiselect(
    "Sex",
    options=df['Sex'].unique(),
    default=df['Sex'].unique()
)

smoking_filter = st.sidebar.multiselect(
    "Smoking History",
    options=df['Smoking_History'].unique(),
    default=df['Smoking_History'].unique()
)

# Apply filters
mask = (
    df['Age_Category'].isin(age_filter) &
    df['Sex'].isin(sex_filter) &
    df['Smoking_History'].isin(smoking_filter)
)
df_filtered = df[mask].copy()

# ==================================================
# HEADER
# ==================================================
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("<h1 class='pulse'>❤️ Heart</h1>", unsafe_allow_html=True)
with col2:
    st.markdown(
        "<h3 style='margin-top: 1.5rem; color:#ff9f9f;'>Cardiovascular Risk Dashboard</h3>",
        unsafe_allow_html=True
    )
st.markdown("---")

# ==================================================
# KPI METRICS
# ==================================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total = len(df_filtered)
heart_prev = (df_filtered['Heart_Disease'] == 'Yes').mean() * 100
checkup_recent = (df_filtered['Checkup'] == 'Within the past year').mean() * 100
avg_bmi = df_filtered['BMI'].mean()

with kpi1:
    st.metric("Total Participants", f"{total:,}")
with kpi2:
    st.metric("Heart Disease Prevalence", f"{heart_prev:.2f}%")
with kpi3:
    st.metric("Recent Checkup Rate", f"{checkup_recent:.1f}%")
with kpi4:
    st.metric("Average BMI", f"{avg_bmi:.1f}")

st.markdown("---")

# ==================================================
# TABS SECTION
# ==================================================
tab1, tab2 = st.tabs(["📊 Demographics", "🧬 Risk Factors"])

# ==================================================
# TAB 1 – DEMOGRAPHICS
# ==================================================
with tab1:
    col1, col2 = st.columns(2)

    # --------------------------
    # AGE DISTRIBUTION
    # --------------------------
    with col1:
        age_heart = df_filtered.groupby('Age_Category')['Heart_Disease'].value_counts(normalize=True).unstack()
        age_heart_pct = (age_heart.get('Yes', pd.Series([0]*len(age_heart))) * 100).round(1)

        age_order = ['18-24','25-29','30-34','35-39','40-44','45-49','50-54',
                     '55-59','60-64','65-69','70-74','75-79','80+']

        age_counts = df_filtered['Age_Category'].value_counts().reindex(age_order, fill_value=0)
        age_heart_pct = age_heart_pct.reindex(age_order, fill_value=0)

        colors = px.colors.sequential.Tealgrn + px.colors.sequential.Reds
        color_map = {age: colors[i % len(colors)] for i, age in enumerate(age_order)}

        fig_age = go.Figure()
        fig_age.add_trace(go.Bar(
            x=age_counts.index,
            y=age_counts.values,
            marker_color=[color_map[a] for a in age_counts.index],
            hovertemplate="<b>%{x}</b><br>Participants: %{y:,}<br>Heart Disease: %{customdata:.1f}%<extra></extra>",
            customdata=age_heart_pct.values
        ))
        fig_age.update_layout(
            title="Age Group Distribution & Heart Disease Risk",
            xaxis_title="Age Group",
            yaxis_title="Participants",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis_tickangle=-45,
            font=dict(family="Arial", size=12),
            margin=dict(l=40, r=40, t=60, b=60)
        )
        st.plotly_chart(fig_age, use_container_width=True)

    # --------------------------
    # SEX DISTRIBUTION
    # --------------------------
    with col2:
        sex_counts = df_filtered['Sex'].value_counts()
        sex_heart_pct = (
            df_filtered.groupby('Sex')['Heart_Disease'].value_counts(normalize=True)
            .unstack().get('Yes', pd.Series([0]*len(sex_counts))) * 100
        ).round(1)

        colors_pie = ['#4e79a7', '#f28e2c']
        fig_pie = go.Figure(data=[go.Pie(
            labels=sex_counts.index,
            values=sex_counts.values,
            hole=0.4,
            marker_colors=colors_pie,
            textinfo='label+percent',
            hovertemplate="<b>%{label}</b><br>Participants: %{value:,}<br>Heart Disease: %{customdata:.1f}%<extra></extra>",
            customdata=sex_heart_pct.reindex(sex_counts.index).values
        )])
        fig_pie.update_layout(
            title="Sex Distribution & Heart Disease Prevalence",
            showlegend=False,
            font=dict(family="Arial", size=12),
            margin=dict(l=40, r=40, t=60, b=40),
            annotations=[dict(text='Sex', x=0.5, y=0.5, font_size=14, showarrow=False, font=dict(color="#aaa"))]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ==================================================
# TAB 2 – RISK FACTORS
# ==================================================
with tab2:
    st.markdown("### 🧩 Risk Factor Impact on Heart Disease")

    factors = ['Exercise', 'Smoking_History', 'Diabetes', 'Arthritis', 'Depression']
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[f.replace('_', ' ') for f in factors],
        specs=[[{"type": "bar"}] * 3] * 2,
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    colors = {'Yes': '#ff6b6b', 'No': '#4ecdc4', 'No Answer': '#95a5a6', 'Unknown': '#95a5a6'}

    row, col = 1, 1
    for factor in factors:
        data = df_filtered.groupby(factor)['Heart_Disease'].value_counts(normalize=True).unstack()
        yes_rate = (data.get('Yes', pd.Series([0]*len(data))) * 100).round(1)

        for label in yes_rate.index:
            color = colors.get(label, '#95a5a6')
            fig.add_trace(
                go.Bar(
                    x=[label],
                    y=[yes_rate[label]],
                    marker_color=color,
                    hovertemplate="<b>%{x}</b><br>Heart Disease: <b>%{y:.1f}%</b><extra></extra>",
                    showlegend=False
                ),
                row=row, col=col
            )
        col += 1
        if col > 3:
            col = 1
            row += 1

    fig.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=11),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    fig.add_annotation(
        text="Each bar shows Heart Disease % for Yes/No",
        xref="paper", yref="paper",
        x=0.5, y=1.08, showarrow=False,
        font=dict(size=12, color="#aaa"), align='center'
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.9rem;'>
    © 2025 Cardiovascular Risk Dashboard | Developed by Habiba Nasser 💻
</div>
""", unsafe_allow_html=True)
