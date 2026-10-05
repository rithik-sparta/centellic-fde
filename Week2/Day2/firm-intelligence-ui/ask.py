import httpx
import streamlit as st

from config import API_BASE_URL

# ---------------------------------------------------------------------------
# Feature 1: Ask (agent, tool-use loop)
# ---------------------------------------------------------------------------
st.header("Ask")

question = st.text_input("Ask a question about the firms", key="ask_input")

if st.button("Ask", key="ask_button"):
    if not question.strip():
        st.warning("Type a question first.")
    else:
        try:
            response = httpx.post(
                f"{API_BASE_URL}/knowledge/ask_with_tools",
                json={"question": question},
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()

            if result.get("completed"):
                st.write(result.get("answer", ""))
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