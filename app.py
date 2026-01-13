import streamlit as st
import pandas as pd
from apify_client import ApifyClient

# --- CONFIGURATION ---
st.set_page_config(page_title="TITAN SCOUT", page_icon="📡", layout="wide")

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
        st.info("Purchase Access Code on Gumroad to unlock.")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🛑 ENTER ACCESS CODE", type="password", on_change=password_entered, key="password")
        st.error("⛔ ACCESS DENIED.")
        return False
    else:
        return True

if check_password():
    # --- MAIN APP LOGIC ---
    st.title("📡 TITAN SCOUT [RECON DIVISION]")
    
    with st.sidebar:
        st.header("🔑 CREDENTIALS")
        apify_api_key = st.text_input("Apify API Key", type="password")
        st.caption("Get your key at console.apify.com")
        st.divider()
        module_choice = st.radio("Select Module:", ["MODULE A: Google Maps Hunter", "MODULE B: Instagram Scout"])

    # --- MODULE A ---
    if module_choice == "MODULE A: Google Maps Hunter":
        st.subheader("MODULE A: DISTRESSED BUSINESS FINDER")
        c1, c2 = st.columns(2)
        with c1: search_keyword = st.text_input("Target (e.g., Med Spa)")
        with c2: search_location = st.text_input("City (e.g., Miami)")

        if st.button("🚀 DEPLOY SCOUT"):
            if not apify_api_key:
                st.error("MISSING API KEY")
            else:
                status = st.empty()
                status.text("⚡ INITIALIZING...")
                try:
                    client = ApifyClient(apify_api_key)
                    run_input = {"searchStringsArray": [f"{search_keyword} in {search_location}"], "maxCrawlerPagination": 1, "zoom": 14}
                    run = client.actor("compass/crawler-google-places").call(run_input=run_input)
                    dataset = client.dataset(run["defaultDatasetId"]).list_items().items
                    
                    if dataset:
                        df = pd.DataFrame(dataset)
                        clean_df = df.get(['title', 'totalScore', 'phone', 'url'], pd.DataFrame())
                        if not clean_df.empty:
                            clean_df.columns = ['Name', 'Rating', 'Phone', 'Map Link']
                            targets = clean_df[(clean_df['Rating'] < 4.2) & (clean_df['Phone'].notna())]
                            status.success(f"✅ FOUND {len(targets)} TARGETS.")
                            st.dataframe(targets, use_container_width=True)
                        else:
                            st.warning("Data found but incomplete. Try a different city.")
                    else:
                        st.warning("No targets found.")
                except Exception as e:
                    st.error(f"ERROR: {e}")

    # --- MODULE B ---
    elif module_choice == "MODULE B: Instagram Scout":
        st.subheader("MODULE B: INFLUENCER SCOUT")
        insta_query = st.text_input("Hashtag (e.g., #MiamiFitness)")
        if st.button("🚀 DEPLOY INSTA SCOUT"):
            if not apify_api_key: st.error("MISSING API KEY")
            else:
                st.info("Instagram Scraper Initiated... (This may take a moment)")
                # Placeholder logic for demo purposes
                st.success("✅ FOUND 12 ACTIVE INFLUENCERS (DEMO MODE)")
