import httpx
import streamlit as st
from config import API_BASE_URL

# ---------------------------------------------------------------------------
# Feature 3: Streaming summary
# ---------------------------------------------------------------------------
st.header("Streaming summary")

borrower_id = str(st.number_input("Borrower id", min_value=1, step=1, key="summarise_borrower-id_input"))
if len(borrower_id) > 1:
    borrower_id = "b-"+borrower_id
else:
    borrower_id = "b-0"+borrower_id

if st.button("Get summary", key="summary_button"):
    placeholder = st.empty()
    try:
        text = ""
        with httpx.stream(
            "POST",
            f"{API_BASE_URL}/borrowers/{borrower_id}/stream_summary",
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