import streamlit as st
import pandas as pd
from apify_client import ApifyClient
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="TITAN SCOUT v3.0", page_icon="📡", layout="wide")

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
    """Converts (123) 456-7890 to +11234567890"""
    if pd.isna(phone_raw): return None
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', str(phone_raw))
    
    # US Number Logic
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    else:
        return None # Invalid length

def is_likely_mobile(phone_clean):
    """Filters out Toll-Free numbers (800, 888, etc) which are definitely Landlines."""
    if not phone_clean: return False
    
    # Check for US Toll-Free prefixes (after the +1)
    toll_free_prefixes = ['800', '888', '877', '866', '855', '844', '833']
    
    # phone_clean format is +1XXXXXXXXXX. 
    # Area code is at index 2:5 (after +1)
    area_code = phone_clean[2:5]
    
    if area_code in toll_free_prefixes:
        return False # It is a business landline
    return True # It MIGHT be a mobile (Standard Area Code)

# --- SCRIPT ENGINE ---
def generate_titan_script(row, city):
    name = str(row['Name']).replace('"', '').replace("'", "")
    rating = float(row['Rating']) if pd.notnull(row['Rating']) else 0.0
    
    if rating >= 4.9:
        return f"Hey {name}, saw your perfect rating in {city}. You clearly dominate the market. We are rolling out a new AI Standard for elite firms to handle call overflow. Is this the owner?"
    elif rating >= 4.0:
        return f"Hey {name}, I did a revenue audit on roofers in {city}. You're missing about $30k/mo in storm leads compared to the 5-star guys with AI answering. I have the report. Want to see it?"
    else:
        return "SKIP - LOW RATING"

if check_password():
    st.title("📡 TITAN SCOUT [V3.0 - CLEANER ENABLED]")
    
    with st.sidebar:
        st.header("🔑 CONTROL PANEL")
        apify_api_key = st.text_input("Apify API Key", type="password")
        st.caption("Enter Key to Activate Scanner")
        
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
                    dataset = client.dataset(run["defaultDatasetId"]).list_items().items
                    
                    if dataset:
                        df = pd.DataFrame(dataset)
                        
                        # 2. CLEAN & PROCESS DATA
                        # Added 'email' to the fetch list
                        required_cols = ['title', 'totalScore', 'phone', 'url', 'email'] # Note: Apify might output 'email' or 'emails'
                        available_cols = [c for c in df.columns if c in ['title', 'totalScore', 'phone', 'url', 'email']]
                        
                        if len(available_cols) > 0:
                            clean_df = df[available_cols].copy()
                            rename_map = {'title': 'Name', 'totalScore': 'Rating', 'phone': 'Phone', 'url': 'Map Link', 'email': 'Email'}
                            clean_df.rename(columns={k: v for k, v in rename_map.items() if k in clean_df.columns}, inplace=True)
                            
                            # 3. APPLY CLEANING
                            clean_df['Clean_Phone'] = clean_df['Phone'].apply(clean_and_format_phone)
                            clean_df['Is_Mobile_Likely'] = clean_df['Clean_Phone'].apply(is_likely_mobile)
                            
                            # 4. FILTER JUNK
                            # Keep only rows with valid phones AND likely mobiles
                            targets = clean_df[
                                (clean_df['Clean_Phone'].notna()) & 
                                (clean_df['Is_Mobile_Likely'] == True)
                            ].copy()
                            
                            # 5. GENERATE SCRIPTS
                            targets['SMS_Script'] = targets.apply(lambda row: generate_titan_script(row, search_location), axis=1)
                            targets = targets[targets['SMS_Script'] != "SKIP - LOW RATING"]

                            # 6. DISPLAY RESULTS
                            status.success(f"✅ TARGETS ACQUIRED: {len(targets)}")
                            st.caption("Removed Toll-Free (800) numbers and Invalid formats.")
                            
                            st.dataframe(targets[['Name', 'Rating', 'Clean_Phone', 'Email', 'SMS_Script']], use_container_width=True)
                            
                            # Download Button
                            csv = targets.to_csv(index=False).encode('utf-8')
                            st.download_button("⬇️ DOWNLOAD MISSION FILE (CSV)", csv, "titan_mission_file.csv", "text/csv")
                            
                        else:
                            st.warning("Data found, but columns missing.")
                    else:
                        st.warning("No targets found.")
                except Exception as e:
                    st.error(f"ERROR: {e}")
