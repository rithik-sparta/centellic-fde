import streamlit as st

ask_page = st.Page("ask.py", title="Ask", icon=":material/question_mark:")
search_page = st.Page("search.py", title="Search", icon=":material/search:")
summary_page = st.Page("summary.py", title="Summary", icon=":material/description:")

pg = st.navigation([ask_page, search_page, summary_page])
st.set_page_config(page_title="Firm Intelligence", page_icon=":material/business_chip:")
pg.run()


# # ---------------------------------------------------------------------------
# # Feature 1: Ask (agent, tool-use loop)
# # ---------------------------------------------------------------------------
# st.header("Ask")

# question = st.text_input("Ask a question about the firms", key="ask_question")

# if st.button("Ask", key="ask_button"):
#     if not question.strip():
#         st.warning("Type a question first.")
#     else:
#         try:
#             response = httpx.post(
#                 f"{API_BASE_URL}/knowledge/ask_with_tools",
#                 json={"question": question},
#                 timeout=60,
#             )
#             response.raise_for_status()
#             result = response.json()

#             if result.get("completed"):
#                 st.write(result.get("answer", ""))
#             else:
#                 st.warning(
#                     "The agent did not finish in time (hit its iteration limit) "
#                     "before an answer could be produced."
#                 )

#             st.caption(
#                 f"Tool calls made: {result.get('tool_calls_made', 'n/a')} | "
#                 f"Input tokens: {result.get('input_tokens', 'n/a')} | "
#                 f"Output tokens: {result.get('output_tokens', 'n/a')}"
#             )
#         except httpx.HTTPStatusError as e:
#             st.error(f"Request failed ({e.response.status_code}): {e.response.text}")
#         except httpx.RequestError as e:
#             st.error(f"Could not reach the API: {e}")

# st.divider()

# # ---------------------------------------------------------------------------
# # Feature 2: Search only (retrieval, no generation)
# # ---------------------------------------------------------------------------
# st.header("Search only")

# search_query = st.text_input("Search the knowledge base", key="search_query")

# if st.button("Search", key="search_button"):
#     if not search_query.strip():
#         st.warning("Type a search query first.")
#     else:
#         try:
#             response = httpx.post(
#                 f"{API_BASE_URL}/knowledge/search",
#                 json={"question": search_query},
#                 timeout=30,
#             )
#             response.raise_for_status()
#             result = response.json()
#             results = result.get("results", [])

#             if not results:
#                 st.info("No results found.")
#             else:
#                 for hit in results:
#                     st.write(f"**{hit.get('title')}** — score: {hit.get('score')}")
#         except httpx.HTTPStatusError as e:
#             if e.response.status_code == 409:
#                 st.warning(
#                     "The knowledge index has not been built yet. "
#                     "Build it before searching."
#                 )
#             else:
#                 st.error(f"Search failed ({e.response.status_code}): {e.response.text}")
#         except httpx.RequestError as e:
#             st.error(f"Could not reach the API: {e}")

# st.divider()

# # ---------------------------------------------------------------------------
# # Feature 3: Streaming summary
# # ---------------------------------------------------------------------------
# st.header("Streaming summary")

# firm_id = st.number_input("Firm id", min_value=1, step=1, key="firm_id")

# if st.button("Get summary", key="summary_button"):
#     placeholder = st.empty()
#     try:
#         text = ""
#         with httpx.stream(
#             "GET",
#             f"{API_BASE_URL}/firms/{int(firm_id)}/stream",
#             timeout=60,
#         ) as response:
#             if response.status_code != 200:
#                 response.read()
#                 st.error(f"Request failed ({response.status_code}): {response.text}")
#             else:
#                 for chunk in response.iter_text():
#                     text += chunk
#                     placeholder.write(text)
#     except httpx.RequestError as e:
#         st.error(f"Could not reach the API: {e}")
