import streamlit as st
import components.authenticate as authenticate
st.set_page_config(
    page_title="TA",
    page_icon="👾",
    layout="wide",
)


# Check authentication when user lands on the home page.
authenticate.set_st_state_vars()

# Add login/logout buttons
if st.session_state["authenticated"]:
    authenticate.button_logout()
else:
    authenticate.button_login()

st.markdown("COMING SOON ! ")