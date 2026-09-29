import httpx
import streamlit as st

from config import API_BASE_URL

# ---------------------------------------------------------------------------
# Feature 2: Search only (retrieval, no generation)
# ---------------------------------------------------------------------------
st.header("Search only")

search_query = st.text_input("Search the knowledge base", key="search_input")

if st.button("Search", key="search_button"):
    if not search_query.strip():
        st.warning("Type a search query first.")
    else:
        try:
            response = httpx.post(
                f"{API_BASE_URL}/knowledge/search",
                json={"question": search_query},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            results = result.get("results", [])

            if not results:
                st.info("No results found.")
            else:
                for hit in results:
                    st.write(f"**{hit.get('title')}** — score: {hit.get('score')}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                st.warning(
                    "The knowledge index has not been built yet. "
                    "Build it before searching."
                )
            else:
                st.error(f"Search failed ({e.response.status_code}): {e.response.text}")
        except httpx.RequestError as e:
            st.error(f"Could not reach the API: {e}")

st.divider()