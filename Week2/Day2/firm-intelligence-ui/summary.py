import httpx
import streamlit as st

from config import API_BASE_URL

# ---------------------------------------------------------------------------
# Feature 3: Streaming summary
# ---------------------------------------------------------------------------
st.header("Streaming summary")

firm_id = st.number_input("Firm id", min_value=1, step=1, key="summary_firm-id_input")

if st.button("Get summary", key="summary_button"):
    placeholder = st.empty()
    try:
        text = ""
        with httpx.stream(
            "GET",
            f"{API_BASE_URL}/firms/{int(firm_id)}/stream",
            timeout=60,
        ) as response:
            if response.status_code != 200:
                response.read()
                st.error(f"Request failed ({response.status_code}): {response.text}")
            else:
                for chunk in response.iter_text():
                    text += chunk
                    placeholder.write(text)
    except httpx.RequestError as e:
        st.error(f"Could not reach the API: {e}")