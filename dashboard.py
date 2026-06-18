import streamlit as st
import requests
import plotly.graph_objects as go

# --- Config ---
st.set_page_config(page_title="AI Interview Coach", layout="wide", page_icon="🎙️")
API_URL = "https://interview-api-backend.onrender.com/api"

# --- Premium Custom CSS (Dark/Red Brutalist Theme) ---
st.markdown("""
<style>
    /* Hide Streamlit default branding to make it look like a standalone app */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background and typography */
    .stApp {
        background-color: #0D0D0D;
        color: #F2F2F2;
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
    }
    
    /* Custom Hero Header Styling */
    .hero-container {
        padding: 2rem 0 3rem 0;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        text-transform: uppercase;
        line-height: 1.1;
        letter-spacing: -2px;
        margin-bottom: 10px;
    }
    .hero-highlight {
        background-color: #FF2A3A;
        color: white;
        padding: 5px 15px;
        display: inline-block;
        transform: skew(-5deg);
    }
    
    /* Styling the Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        border-bottom: 2px solid #262626;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border: none;
        color: #808080;
        font-weight: 600;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stTabs [aria-selected="true"] {
        color: #FF2A3A !important;
        border-bottom: 3px solid #FF2A3A;
    }
    
    /* Primary Action Button (Matches the 'LEARN NOW' vibe) */
    .stButton>button[kind="primary"] {
        background-color: #FF2A3A;
        color: white;
        border: none;
        border-radius: 4px;
        height: 54px;
        font-weight: 800;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        transition: all 0.2s ease;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #E61E2D;
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(255, 42, 58, 0.2);
    }
    
    /* Custom Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1A1A1A;
        border: 1px solid #333333;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricValue"] {
        color: #FF2A3A;
        font-weight: 800;
    }
    
    /* Expander/Roadmap Styling */
    .streamlit-expanderHeader {
        background-color: #1A1A1A;
        border-radius: 4px;
        border: 1px solid #333333;
        color: #F2F2F2;
        font-weight: 600;
    }
    
    /* Text Inputs & File Uploader */
    .stTextInput>div>div>input {
        background-color: #1A1A1A;
        color: white;
        border: 1px solid #333333;
        border-radius: 4px;
    }
    [data-testid="stFileUploader"] {
        background-color: #1A1A1A;
        border: 1px dashed #404040;
        border-radius: 8px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def plot_radar_chart(scores):
    categories = ['Technical Accuracy', 'Completeness', 'Clarity', 'Depth', 'Relevance']
    values = [
        scores.get('technical_accuracy', 0),
        scores.get('completeness', 0),
        scores.get('clarity', 0),
        scores.get('depth', 0),
        scores.get('relevance', 0)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(255, 42, 58, 0.2)', # Red transparent fill
        line=dict(color='#FF2A3A', width=3), # Solid red line
        marker=dict(color='#FFFFFF', size=8)
    ))
    
    # Dark Mode Brutalist Radar Styling
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#A6A6A6', size=12),
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True, 
                range=[0, 10], 
                gridcolor='#333333', 
                linecolor='#333333',
                tickfont=dict(color='#666666')
            ),
            angularaxis=dict(
                gridcolor='#333333', 
                linecolor='#333333'
            )
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    return fig

# --- Main UI ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">AI INTERVIEW <br><span class="hero-highlight">INTELLIGENCE</span></div>
    <p style="color: #808080; font-size: 1.2rem; max-width: 600px;">Upload your mock interview answers and get instant, technical scoring and personalized roadmaps.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Target Mock", "Session History"])

# === TAB 1: NEW SESSION ===
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_input, col_upload = st.columns([1, 1])
    with col_input:
        st.markdown("#### 1. Target Question")
        question = st.text_input("", value="Tell me about yourself.", placeholder="e.g. Walk me through a complex algorithmic problem you solved.")
    with col_upload:
        st.markdown("#### 2. Response Audio")
        audio_file = st.file_uploader("", type=['wav', 'mp3', 'm4a'], label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Analyze Interview", type="primary", use_container_width=True) and audio_file:
        with st.spinner("Processing audio, extracting features, and generating AI feedback..."):
            files = {"audio": (audio_file.name, audio_file.getvalue(), audio_file.type)}
            data = {"question": question}
            
            try:
                response = requests.post(f"{API_URL}/analyze", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis Complete!")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # --- Results Layout ---
                    col1, padding, col2 = st.columns([1.2, 0.1, 1])
                    
                    with col1:
                        st.markdown("#### TECHNICAL RADAR")
                        st.plotly_chart(plot_radar_chart(result['scores']), use_container_width=True)
                        
                        st.markdown("#### DELIVERY METRICS")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Pace (WPM)", f"{result['audio_features']['speaking_rate_wpm']}")
                        m2.metric("Filler Words", result['audio_features']['filler_word_count'])
                        m3.metric("Pauses", result['audio_features']['pause_count'])
                        
                    with col2:
                        st.markdown("#### AI COACH FEEDBACK")
                        st.info(f"**Insight:** {result['scores']['feedback']}")
                        st.markdown(f"**🟢 Strengths:** {result['scores']['strengths']}")
                        st.markdown(f"**🔴 Weaknesses:** {result['scores']['weaknesses']}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("#### ACTION PLAN")
                        for idx, item in enumerate(result['roadmap']):
                            with st.expander(f"{idx+1}. {item['title']} ({item['priority'].upper()})"):
                                st.write(f"**Skill Area:** {item['skill_area']}")
                                st.write(item['description'])
                                st.caption(f"Estimated effort: {item['estimated_hours']} hours")
                    
                    st.divider()
                    st.markdown("#### RAW TRANSCRIPT")
                    st.write(f"> *\"{result['transcript']}\"*")
                    
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")

# === TAB 2: HISTORY ===
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("#### PAST SESSIONS")
    with col2:
        refresh = st.button("Refresh", use_container_width=True)
        
    if refresh or True: 
        try:
            res = requests.get(f"{API_URL}/sessions")
            if res.status_code == 200:
                sessions = res.json()
                if not sessions:
                    st.info("No past sessions found. Start practicing!")
                else:
                    for s in sessions:
                        with st.container():
                            st.markdown(f"""
                            <div style="background-color: #1A1A1A; padding: 15px 20px; border-radius: 4px; border-left: 4px solid #FF2A3A; margin-bottom: 10px;">
                                <h5 style="margin: 0; color: #F2F2F2; text-transform: uppercase;">{s['title']}</h5>
                                <p style="margin: 5px 0 0 0; color: #808080; font-size: 0.9rem;">Date: {s['started_at'][:10]} &nbsp;|&nbsp; Score: <strong style="color: #FF2A3A;">{s['overall_score']}/100</strong></p>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.error("Could not fetch history.")
        except Exception as e:
            st.error("Backend offline. Make sure Uvicorn is running!")
