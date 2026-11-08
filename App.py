import streamlit as st
import pandas as pd
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Mince Pie Rater", page_icon="🥧", layout="centered")

# --- CUSTOM CSS FOR APP STYLING ---
st.markdown("""
    <style>
    /* Hide default Streamlit headers and footers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make the form look like a native app card */
    div[data-testid="stForm"] {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #333;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    /* Style the main submit button */
    .stButton>button {
        background-color: #d4af37 !important;
        color: #000 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 10px 20px !important;
        width: 100% !important;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #f3c736 !important;
    }
    
    /* Tweak text inputs */
    input[type="text"], input[type="number"], textarea {
        background-color: #2a2a2a !important;
        color: #fff !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

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
    if score <= 1.5: return "🤢"
    elif score <= 3.0: return "😐"
    elif score <= 4.0: return "😋"
    else: return "🤤"

# --- APP LAYOUT ---
st.title("🥧 The Mince Pie Rater")

tab1, tab2 = st.tabs(["📝 Rate", "🏆 Leaderboard"])

# --- TAB 1: RATING FORM ---
with tab1:
    df = load_data()
    
    # 1. Build the Autocomplete List
    # Start with the seed list of heavy hitters
    seed_pies = [
        "Aldi Specially Selected", "Asda Extra Special", 
        "Co-op Irresistible", "M&S Collection", 
        "Mr Kipling", "Tesco Finest"
    ]
    
    # Combine with any pies already saved in the CSV database
    if not df.empty:
        saved_pies = df["Pie_Name"].unique().tolist()
        combined_list = sorted(list(set(seed_pies + saved_pies)))
    else:
        combined_list = sorted(seed_pies)
        
    combined_list.append("➕ Add a new pie...")

    with st.form("rating_form", clear_on_submit=True):
        st.subheader("Log a Review")
        
        reviewer = st.text_input("Reviewer Name", placeholder="e.g. Kyle")
        
        # 2. The Smart Dropdown
        selected_pie = st.selectbox("Pie Brand / Name", combined_list)
        
        # If they select "Add a new pie", reveal a blank text box
        if selected_pie == "➕ Add a new pie...":
            pie_name = st.text_input("Type the new pie name")
        else:
            pie_name = selected_pie
            
        cost = st.number_input("Box Price (£) - Optional", min_value=0.0, step=0.10, format="%.2f")
        
        st.markdown("---")
        
        # 3. Dynamic Emoji Sliders
        # Streamlit updates these values as soon as you release the drag
        price_score = st.slider("Price / Value", 0.0, 5.0, 2.5, 0.5)
        st.caption(f"**Score:** {price_score} {get_emoji(price_score)}")
        
        filling_score = st.slider("Filling Quality & Amount", 0.0, 5.0, 2.5, 0.5)
        st.caption(f"**Score:** {filling_score} {get_emoji(filling_score)}")
        
        crust_score = st.slider("Crust / Pastry Texture", 0.0, 5.0, 2.5, 0.5)
        st.caption(f"**Score:** {crust_score} {get_emoji(crust_score)}")
        
        booze_score = st.slider("Booziness Factor", 0.0, 5.0, 2.5, 0.5)
        st.caption(f"**Score:** {booze_score} {get_emoji(booze_score)}")
        
        st.markdown("---")
        
        buy_again = st.checkbox("✅ Would you buy this again?")
        notes = st.text_area("Tasting Notes", placeholder="Pastry fell apart, filling was great...")
        
        submitted = st.form_submit_button("Lock in Score")
        
        if submitted:
            if not reviewer or not pie_name:
                st.error("Please enter both your name and the pie name!")
            else:
                overall = (price_score + filling_score + crust_score + booze_score) / 4
                
                new_review = {
                    "Reviewer": reviewer.strip(),
                    "Pie_Name": pie_name.strip(),
                    "Cost": cost,
                    "Price_Score": price_score,
                    "Filling_Score": filling_score,
                    "Crust_Score": crust_score,
                    "Booze_Score": booze_score,
                    "Overall_Score": round(overall, 2),
                    "Buy_Again": buy_again,
                    "Notes": notes
                }
                save_review(new_review)
                st.success(f"Score locked! Overall: {overall:.1f} {get_emoji(overall)}")
                st.rerun()

# --- TAB 2: LEADERBOARD ---
with tab2:
    df = load_data()
    
    if df.empty:
        st.info("No pies rated yet.")
    else:
        # Calculate stats for the leaderboard
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
            
            # Volatility logic
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
