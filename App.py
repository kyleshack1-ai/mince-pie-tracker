import streamlit as st
import pandas as pd
import os

# --- PAGE SETUP ---
st.set_page_config(page_title="Mince Pie Rater", page_icon="🥧", layout="centered")

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
    # Convert new review to DataFrame and concatenate
    new_df = pd.DataFrame([review_dict])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- EMOJI LOGIC ---
def get_xmas_emoji(score):
    if score <= 1.5: return "❄️ (Scrooge Level)"
    elif score <= 3.0: return "⛄ (Average Snowman)"
    elif score <= 4.0: return "🦌 (Solid Reindeer)"
    else: return "🎅 (Top Tier Santa)"

# --- APP LAYOUT ---
st.title("🎄 The Family Mince Pie Rater")

tab1, tab2 = st.tabs(["📝 Rate a Pie", "🏆 Live Leaderboard"])

# --- TAB 1: RATING FORM ---
with tab1:
    with st.form("rating_form", clear_on_submit=True):
        st.subheader("Log a New Review")
        
        col1, col2 = st.columns(2)
        with col1:
            reviewer = st.text_input("Who is reviewing?")
        with col2:
            pie_name = st.text_input("Pie Brand / Name (e.g. Co-op Irresistible)")
            
        cost = st.number_input("Box Price (£) - Optional", min_value=0.0, step=0.10, format="%.2f")
        
        st.markdown("### The Metrics (0 = ❄️, 5 = 🎅)")
        price_score = st.slider("Price / Value", 0.0, 5.0, 2.5, 0.5)
        filling_score = st.slider("Filling Quality & Amount", 0.0, 5.0, 2.5, 0.5)
        crust_score = st.slider("Crust / Pastry Texture", 0.0, 5.0, 2.5, 0.5)
        booze_score = st.slider("Booziness Factor", 0.0, 5.0, 2.5, 0.5)
        
        buy_again = st.checkbox("✅ Would you buy this again?")
        notes = st.text_area("Tasting Notes (e.g., Pastry too crumbly, fell on jumper...)")
        
        submitted = st.form_submit_button("Lock in Score 🎅")
        
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
                st.success(f"Review for {pie_name} saved! Overall Score: {overall:.1f} {get_xmas_emoji(overall)}")

# --- TAB 2: LEADERBOARD ---
with tab2:
    df = load_data()
    
    if df.empty:
        st.info("No pies rated yet. Get the kettle on!")
    else:
        st.subheader("Current Standings 🏆")
        
        # Group by pie and calculate stats
        pie_stats = df.groupby("Pie_Name").agg(
            Avg_Score=('Overall_Score', 'mean'),
            Review_Count=('Reviewer', 'count'),
            Max_Score=('Overall_Score', 'max'),
            Min_Score=('Overall_Score', 'min')
        ).reset_index()
        
        # Sort by highest average
        pie_stats = pie_stats.sort_values(by="Avg_Score", ascending=False).reset_index(drop=True)
        
        for index, row in pie_stats.iterrows():
            pie = row['Pie_Name']
            avg = row['Avg_Score']
            count = row['Review_Count']
            
            # Volatility check: Variance of 1.5 or more between family members
            is_volatile = count > 1 and (row['Max_Score'] - row['Min_Score']) >= 1.5
            
            medal = "🥇" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else "🥧"
            feud_flag = " ⚠️ **FAMILY FEUD**" if is_volatile else ""
            
            # Expander for each pie
            with st.expander(f"{medal} {pie} - Avg: {avg:.2f} {get_xmas_emoji(avg)}{feud_flag} ({count} reviews)"):
                
                # Get individual reviews for this pie
                pie_reviews = df[df['Pie_Name'] == pie]
                
                for _, rev in pie_reviews.iterrows():
                    st.markdown(f"**{rev['Reviewer']}** rated it **{rev['Overall_Score']:.1f}**")
                    if pd.notna(rev['Cost']) and rev['Cost'] > 0:
                        st.caption(f"Cost logged: £{rev['Cost']:.2f}")
                        
                    buy_text = "✅ Buy Again" if rev['Buy_Again'] else "❌ Do Not Buy"
                    st.caption(buy_text)
                    
                    if pd.notna(rev['Notes']) and rev['Notes'].strip():
                        st.markdown(f"*{rev['Notes']}*")
                    
                    # Score breakdown layout
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Price", f"{rev['Price_Score']:.1f}")
                    c2.metric("Filling", f"{rev['Filling_Score']:.1f}")
                    c3.metric("Crust", f"{rev['Crust_Score']:.1f}")
                    c4.metric("Booze", f"{rev['Booze_Score']:.1f}")
                    st.divider()
          
