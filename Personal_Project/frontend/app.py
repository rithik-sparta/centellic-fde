import streamlit as st

ask_page = st.Page("ask.py", title="Ask", icon=":material/question_mark:")
search_page = st.Page("search.py", title="Search", icon=":material/search:")
summary_page = st.Page("summary.py", title="Summary", icon=":material/description:")
credit_assessment_page = st.Page("credit_assessment.py", title="Credit Assessment", icon=":material/lab_profile:")

pg = st.navigation([ask_page, search_page, summary_page, credit_assessment_page])
st.set_page_config(page_title="Credit Analysis", page_icon=":material/business_chip:")
pg.run()
