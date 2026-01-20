import streamlit as st
import pandas as pd
from apify_client import ApifyClient
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="TITAN SCOUT v3.1", page_icon="📡", layout="wide")

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

# --- PHONE CLEANING ENGINE ---
def clean_and_format_phone(phone_raw):
    if pd.isna(phone_raw): return None
    digits = re.sub(r'\D', '', str(phone_raw))
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    else:
        return None

def is_likely_mobile(phone_clean):
    if not phone_clean: return False
    toll_free_prefixes = ['800', '888', '877', '866', '855', '844', '833']
    if len(phone_clean) >= 5:
        area_code = phone_clean[2:5]
        if area_code in toll_free_prefixes:
            return False
    return True

# --- SCRIPT ENGINE ---
def generate_titan_script(row, city):
    name = str(row.get('Name', 'Business')).replace('"', '').replace("'", "")
    try:
        rating = float(row.get('Rating', 0))
    except:
        rating = 0.0
    
    if rating >= 4.9:
        return f"Hey {name}, saw your perfect rating in {city}. You clearly dominate the market. We are rolling out a new AI Standard for elite firms to handle call overflow. Is this the owner?"
    elif rating >= 4.0:
        return f"Hey {name}, I did a revenue audit on roofers in {city}. You're missing about $30k/mo in storm leads compared to the 5-star guys with AI answering. I have the report. Want to see it?"
    else:
        return "SKIP - LOW RATING"

if check_password():
    st.title("📡 TITAN SCOUT [V3.1 - CRASH PROOF]")
    
    with st.sidebar:
        st.header("🔑 CONTROL PANEL")
        apify_api_key = st.text_input("Apify API Key", type="password")
        
        module_choice = st.radio("Select Module:", ["MODULE A: Google Maps Hunter"])

    if module_choice == "MODULE A: Google Maps Hunter":
        st.subheader("MODULE A: MARKET SEGMENTATION SCAN")
        c1, c2 = st.columns(2)
        with c1: search_keyword = st.text_input("Target (e.g., Roofing)")
        with c2: search_location = st.text_input("City (e.g., Dallas)")

        if st.button("🚀 DEPLOY SCOUT"):
            if not apify_api_key:
                st.error("MISSING API KEY")
            else:
                status = st.empty()
                status.text("⚡ INITIALIZING SATELLITE SCAN...")
                try:
                    client = ApifyClient(apify_api_key)
                    
                    run_input = {
                        "searchStringsArray": [f"{search_keyword} in {search_location}"], 
                        "maxCrawlerPagination": 2, 
                        "zoom": 14
                    }
                    run = client.actor("compass/crawler-google-places").call(run_input=run_input)
                    
                    # ERROR HANDLING: CHECK IF DATASET EXISTS
                    if not run:
                        st.error("Scraper failed to start.")
                    else:
                        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
                        
                        if dataset_items:
                            df = pd.DataFrame(dataset_items)
                            
                            # DEBUG: Show raw columns if something breaks
                            with st.expander("Show Raw Data (Debug)"):
                                st.write(df.head())
                                st.write(f"Columns Found: {list(df.columns)}")

                            # --- ROBUST COLUMN MAPPING ---
                            # This fixes the "Missing Key" errors
                            clean_df = pd.DataFrame()
                            
                            # Map Name
                            if 'title' in df.columns: clean_df['Name'] = df['title']
                            elif 'name' in df.columns: clean_df['Name'] = df['name']
                            else: clean_df['Name'] = "Unknown Business"

                            # Map Phone
                            if 'phone' in df.columns: clean_df['Phone'] = df['phone']
                            elif 'phoneNumber' in df.columns: clean_df['Phone'] = df['phoneNumber']
                            else: clean_df['Phone'] = None
                            
                            # Map Rating
                            if 'totalScore' in df.columns: clean_df['Rating'] = df['totalScore']
                            elif 'rating' in df.columns: clean_df['Rating'] = df['rating']
                            else: clean_df['Rating'] = 0.0

                            # Map Email (Handle Missing)
                            if 'email' in df.columns: clean_df['Email'] = df['email']
                            elif 'emails' in df.columns: clean_df['Email'] = df['emails']
                            else: clean_df['Email'] = "N/A"

                            # --- PROCESSING ---
                            # 1. Drop rows with no phone
                            clean_df = clean_df.dropna(subset=['Phone'])
                            
                            # 2. Clean Phone
                            clean_df['Clean_Phone'] = clean_df['Phone'].apply(clean_and_format_phone)
                            
                            # 3. Filter Landlines
                            clean_df['Is_Mobile_Likely'] = clean_df['Clean_Phone'].apply(is_likely_mobile)
                            
                            targets = clean_df[
                                (clean_df['Clean_Phone'].notna()) & 
                                (clean_df['Is_Mobile_Likely'] == True)
                            ].copy()
                            
                            # 4. Generate Scripts
                            targets['SMS_Script'] = targets.apply(lambda row: generate_titan_script(row, search_location), axis=1)
                            targets = targets[targets['SMS_Script'] != "SKIP - LOW RATING"]

                            # --- DISPLAY ---
                            status.success(f"✅ TARGETS ACQUIRED: {len(targets)}")
                            st.caption(f"Filtered {len(clean_df) - len(targets)} landlines/bad numbers.")
                            
                            st.dataframe(targets[['Name', 'Rating', 'Clean_Phone', 'Email', 'SMS_Script']], use_container_width=True)
                            
                            csv = targets.to_csv(index=False).encode('utf-8')
                            st.download_button("⬇️ DOWNLOAD MISSION FILE (CSV)", csv, "titan_mission_file.csv", "text/csv")
                            
                        else:
                            st.warning("No data found. Try a different city.")
                except Exception as e:
                    st.error(f"CRITICAL ERROR: {e}")
