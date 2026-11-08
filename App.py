import streamlit as st
import pandas as pd
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Mince Pie Rater", page_icon="🥧", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #121212; }
    .stButton>button {
        background-color: #d4af37 !important;
        color: #000 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        padding: 12px !important;
        width: 100% !important;
        border: none !important;
    }
    .stButton>button:hover { background-color: #f3c736 !important; }
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'p_score' not in st.session_state: st.session_state.p_score = 2.5
if 'f_score' not in st.session_state: st.session_state.f_score = 2.5
if 'c_score' not in st.session_state: st.session_state.c_score = 2.5
if 'b_score' not in st.session_state: st.session_state.b_score = 2.5
if 'pie_cost' not in st.session_state: st.session_state.pie_cost = 0.0
if 'notes_txt' not in st.session_state: st.session_state.notes_txt = ""
if 'buy_chk' not in st.session_state: st.session_state.buy_chk = False
if 'reviewer' not in st.session_state: st.session_state.reviewer = ""

# --- DATA MANAGEMENT ---
DATA_FILE = "mince_pie_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Reviewer", "Pie_Name", "Cost", "Price_Score", 
            "Filling_Score", "Crust_Score", "Booze_Score", 
            "Overall_Score", "Buy_Again", "Notes"
        ])

def save_review(review_dict):
    df = load_data()
    new_df = pd.DataFrame([review_dict])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- DYNAMIC EMOJI LOGIC ---
def get_emoji(score):
    if score == 0.0: return "🤢"
    elif score <= 1.5: return "🫪"
    elif score <= 3.0: return "😐"
    elif score <= 4.5: return "😃"
    else: return "🎅🏼"

# --- APP LAYOUT ---
st.title("🥧 The Mince Pie Rater")

tab1, tab2 = st.tabs(["📝 Rate a Pie", "🏆 Leaderboard"])

# --- TAB 1: RATING UI ---
with tab1:
    df = load_data()
    
    st.session_state.reviewer = st.text_input("Reviewer Name", value=st.session_state.reviewer, placeholder="e.g. Kyle")
    
    # Smart Auto-Syncing Pie List
    default_pies = [
        "Aldi Specially Selected", 
        "Asda Extra Special", 
        "Co-op Irresistible", 
        "M&S Collection", 
        "Mr Kipling", 
        "Tesco Finest",
        "Waitrose No.1"
    ]
    
    if not df.empty and "Pie_Name" in df.columns:
        submitted_pies = df["Pie_Name"].dropna().unique().tolist()
    else:
        submitted_pies = []
        
    master_pie_list = sorted(list(set(default_pies + submitted_pies)))
    master_pie_list.insert(0, "✨ Type a new pie name...")

    selected_pie = st.selectbox("Pie Brand / Name", master_pie_list)
    
    if selected_pie == "✨ Type a new pie name...":
        pie_name = st.text_input("Enter exact pie name (e.g., Co-op Irresistible):", placeholder="Keep naming consistent!")
    else:
        pie_name = selected_pie
        
    st.number_input("Box Price (£) - Optional", min_value=0.0, step=0.10, format="%.2f", key="pie_cost")
    
    st.markdown("---")
    
    # Sliders
    c1, c2 = st.columns([4, 1])
    with c1: st.slider("Price / Value", 0.0, 5.0, step=0.5, key="p_score")
    with c2: st.markdown(f"<div style='font-size:2.2rem; text-align:center; padding-top:1.5rem;'>{get_emoji(st.session_state.p_score)}</div>", unsafe_allow_html=True)

    c3, c4 = st.columns([4, 1])
    with c3: st.slider("Filling Quality & Amount", 0.0, 5.0, step=0.5, key="f_score")
    with c4: st.markdown(f"<div style='font-size:2.2rem; text-align:center; padding-top:1.5rem;'>{get_emoji(st.session_state.f_score)}</div>", unsafe_allow_html=True)

    c5, c6 = st.columns([4, 1])
    with c5: st.slider("Crust / Pastry Texture", 0.0, 5.0, step=0.5, key="c_score")
    with c6: st.markdown(f"<div style='font-size:2.2rem; text-align:center; padding-top:1.5rem;'>{get_emoji(st.session_state.c_score)}</div>", unsafe_allow_html=True)

    c7, c8 = st.columns([4, 1])
    with c7: st.slider("Booziness Factor", 0.0, 5.0, step=0.5, key="b_score")
    with c8: st.markdown(f"<div style='font-size:2.2rem; text-align:center; padding-top:1.5rem;'>{get_emoji(st.session_state.b_score)}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.checkbox("✅ Would you buy this again?", key="buy_chk")
    st.text_area("Tasting Notes", placeholder="Pastry fell apart, filling was great...", key="notes_txt")
    
    if st.button("Lock in Score 🎅🏼"):
        if not st.session_state.reviewer or not pie_name or pie_name == "✨ Type a new pie name...":
            st.error("Please enter your name and a valid pie name!")
        else:
            overall = (st.session_state.p_score + st.session_state.f_score + st.session_state.c_score + st.session_state.b_score) / 4
            
            new_review = {
                "Reviewer": st.session_state.reviewer.strip(),
                "Pie_Name": pie_name.strip(),
                "Cost": st.session_state.pie_cost,
                "Price_Score": st.session_state.p_score,
                "Filling_Score": st.session_state.f_score,
                "Crust_Score": st.session_state.c_score,
                "Booze_Score": st.session_state.b_score,
                "Overall_Score": round(overall, 2),
                "Buy_Again": st.session_state.buy_chk,
                "Notes": st.session_state.notes_txt
            }
            save_review(new_review)
            
            # Safely clear keys so widgets reset to defaults on rerun
            for k in ['p_score', 'f_score', 'c_score', 'b_score', 'pie_cost', 'notes_txt', 'buy_chk']:
                if k in st.session_state:
                    del st.session_state[k]
            
            st.toast(f"Score locked! Overall: {overall:.1f} {get_emoji(overall)}", icon="🥧")
            st.rerun()

# --- TAB 2: LEADERBOARD ---
with tab2:
    df = load_data()
    
    if df.empty:
        st.info("No pies rated yet. Get the kettle on!")
    else:
        pie_stats = df.groupby("Pie_Name").agg(
            Avg_Score=('Overall_Score', 'mean'),
            Review_Count=('Reviewer', 'count'),
            Max_Score=('Overall_Score', 'max'),
            Min_Score=('Overall_Score', 'min')
        ).reset_index()
        
        pie_stats = pie_stats.sort_values(by="Avg_Score", ascending=False).reset_index(drop=True)
        
        for index, row in pie_stats.iterrows():
            pie = row['Pie_Name']
            avg = row['Avg_Score']
            count = row['Review_Count']
            
            is_volatile = count > 1 and (row['Max_Score'] - row['Min_Score']) >= 1.5
            medal = "🥇" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else "🥧"
            feud_flag = " ⚠️ **FAMILY FEUD**" if is_volatile else ""
            
            with st.expander(f"{medal} {pie} - {avg:.1f} {get_emoji(avg)}{feud_flag} ({count} reviews)"):
                pie_reviews = df[df['Pie_Name'] == pie]
                
                for _, rev in pie_reviews.iterrows():
                    st.markdown(f"**{rev['Reviewer']}**")
                    if pd.notna(rev['Cost']) and rev['Cost'] > 0:
                        st.caption(f"Cost logged: £{rev['Cost']:.2f}")
                        
                    st.caption("✅ Buy Again" if rev['Buy_Again'] else "❌ Do Not Buy")
                    
                    if pd.notna(rev['Notes']) and rev['Notes'].strip():
                        st.markdown(f"*{rev['Notes']}*")
                    
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Price", f"{rev['Price_Score']:.1f}")
                    c2.metric("Fill", f"{rev['Filling_Score']:.1f}")
                    c3.metric("Crust", f"{rev['Crust_Score']:.1f}")
                    c4.metric("Booze", f"{rev['Booze_Score']:.1f}")
                    c5.metric("Avg", f"{rev['Overall_Score']:.1f}")
                    st.divider()
