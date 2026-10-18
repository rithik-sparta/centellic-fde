import httpx
import streamlit as st
from config import API_BASE_URL

# ---------------------------------------------------------------------------
# Feature 4: Borrower Credit Assessment (agent, tool-use loop)
# ---------------------------------------------------------------------------
st.header("Borrower Credit Assessment")

borrower_id = str(st.number_input("Borrower id", min_value=1, step=1, key="assess_borrower-id_input"))
if len(borrower_id) > 1:
    borrower_id = "b-"+borrower_id
else:
    borrower_id = "b-0"+borrower_id

if st.button("Assess", key="assess_button"):
    try:
        response = httpx.post(
            f"{API_BASE_URL}/borrowers/{borrower_id}/credit_assessment",
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()

        if result.get("completed"):
            st.write(result.get("output", ""))
        else:
            st.warning(
                "The agent did not finish in time (hit its iteration limit) "
                "before an answer could be produced."
            )

        st.caption(
            f"Tool calls made: {result.get('tool_calls_made', 'n/a')} | "
            f"Input tokens: {result.get('input_tokens', 'n/a')} | "
            f"Output tokens: {result.get('output_tokens', 'n/a')}"
        )
    except httpx.HTTPStatusError as e:
        st.error(f"Request failed ({e.response.status_code}): {e.response.text}")
    except httpx.RequestError as e:
        st.error(f"Could not reach the API: {e}")

st.divider()