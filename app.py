import streamlit as st
import pandas as pd
from apify_client import ApifyClient

# --- CONFIGURATION ---
st.set_page_config(page_title="TITAN SCOUT v2.0", page_icon="📡", layout="wide")

# --- TITAN AESTHETIC ---
st.markdown("""
    <style>
    .stApp {background-color: #0e1117; color: #c9d1d9;}
    .stButton>button {background-color: #21262d; color: #58a6ff; border: 1px solid #30363d; width: 100%;}
    .stTextInput>div>div>input {background-color: #0d1117; color: #c9d1d9;}
    h1 {color: #58a6ff;}
    </style>
    """, unsafe_allow_html=True)

# --- SECURITY LOCK ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == "TITAN2026": 
            st.session_state["password_correct"] = True
            del st.session_state["password"]  
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🛑 ENTER ACCESS CODE", type="password", on_change=password_entered, key="password")
        st.info("Titan Systems Internal Tool.")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🛑 ENTER ACCESS CODE", type="password", on_change=password_entered, key="password")
        st.error("⛔ ACCESS DENIED.")
        return False
    else:
        return True

# --- INTELLIGENT SCRIPTING ENGINE ---
def generate_titan_script(row, city):
    name = str(row['Name']).replace('"', '').replace("'", "")
    rating = float(row['Rating']) if pd.notnull(row['Rating']) else 0.0
    
    # STRATEGY A: THE ELITE (4.9 - 5.0 Stars) -> Sell "The Future"
    if rating >= 4.9:
        return f"Hey {name}, saw your perfect rating in {city}. You clearly dominate the market. We are rolling out a new AI Standard for elite firms to handle call overflow. Is this the owner?"
    
    # STRATEGY B: THE GROWTH (4.0 - 4.8 Stars) -> Sell "The Fix"
    elif rating >= 4.0:
        return f"Hey {name}, I did a revenue audit on roofers in {city}. You're missing about $30k/mo in storm leads compared to the 5-star guys with AI answering. I have the report. Want to see it?"
    
    # STRATEGY C: THE RISK (< 4.0 Stars) -> Skip or Reputation Mgmt
    else:
        return "SKIP - LOW RATING"

if check_password():
    # --- MAIN APP LOGIC ---
    st.title("📡 TITAN SCOUT [NEURO-LINK ENABLED]")
    
    with st.sidebar:
        st.header("🔑 CONTROL PANEL")
        apify_api_key = st.text_input("Apify API Key", type="password")
        st.caption("Enter Key to Activate Scanner")
        st.divider()
        module_choice = st.radio("Select Module:", ["MODULE A: Google Maps Hunter", "MODULE B: Instagram Scout"])

    # --- MODULE A ---
    if module_choice == "MODULE A: Google Maps Hunter":
        st.subheader("MODULE A: MARKET SEGMENTATION SCAN")
        st.caption("Scrapes Google Maps -> Segments Leads -> Generates Custom AI Scripts")
        
        c1, c2 = st.columns(2)
        with c1: search_keyword = st.text_input("Target (e.g., Roofing, Dentist)")
        with c2: search_location = st.text_input("City (e.g., Dallas)")

        if st.button("🚀 DEPLOY SCOUT"):
            if not apify_api_key:
                st.error("MISSING API KEY")
            else:
                status = st.empty()
                status.text("⚡ INITIALIZING SATELLITE SCAN...")
                try:
                    client = ApifyClient(apify_api_key)
                    
                    # 1. RUN THE CRAWLER
                    run_input = {
                        "searchStringsArray": [f"{search_keyword} in {search_location}"], 
                        "maxCrawlerPagination": 2, 
                        "zoom": 14
                    }
                    run = client.actor("compass/crawler-google-places").call(run_input=run_input)
                    dataset = client.dataset(run["defaultDatasetId"]).list_items().items
                    
                    if dataset:
                        df = pd.DataFrame(dataset)
                        
                        # 2. CLEAN & PROCESS DATA
                        required_cols = ['title', 'totalScore', 'phone', 'url']
                        available_cols = [c for c in required_cols if c in df.columns]
                        
                        if len(available_cols) > 0:
                            clean_df = df[available_cols].copy()
                            rename_map = {'title': 'Name', 'totalScore': 'Rating', 'phone': 'Phone', 'url': 'Map Link'}
                            clean_df.rename(columns={k: v for k, v in rename_map.items() if k in clean_df.columns}, inplace=True)
                            
                            # Filter: Must have phone number
                            targets = clean_df[clean_df['Phone'].notna()].copy()
                            
                            # 3. APPLY TITAN LOGIC (The New Automation)
                            targets['SMS_Script'] = targets.apply(lambda row: generate_titan_script(row, search_location), axis=1)
                            
                            # Remove "SKIP" rows
                            targets = targets[targets['SMS_Script'] != "SKIP - LOW RATING"]

                            # 4. DISPLAY RESULTS
                            status.success(f"✅ TARGETS ACQUIRED: {len(targets)}")
                            
                            st.subheader("🎯 ELITE TIER (5.0 Stars) - 'The Future'")
                            st.dataframe(targets[targets['Rating'] >= 4.9], use_container_width=True)
                            
                            st.subheader("📈 GROWTH TIER (<4.9 Stars) - 'The Fix'")
                            st.dataframe(targets[targets['Rating'] < 4.9], use_container_width=True)
                            
                            # Download Button
                            csv = targets.to_csv(index=False).encode('utf-8')
                            st.download_button("⬇️ DOWNLOAD MISSION FILE (CSV)", csv, "titan_mission_file.csv", "text/csv")
                            
                        else:
                            st.warning("Data found, but standard columns missing. Try a broader search.")
                    else:
                        st.warning("No targets found. Check spelling or location.")
                except Exception as e:
                    st.error(f"ERROR: {e}")

    # --- MODULE B ---
    elif module_choice == "MODULE B: Instagram Scout":
        st.subheader("MODULE B: INFLUENCER SCOUT")
        st.info("System Offline. Focus on Module A.")
