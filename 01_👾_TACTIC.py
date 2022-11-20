import streamlit as st
import components.authenticate as authenticate
import boto3

import os
import io


st.set_page_config(
    page_title="TACTIC",
    page_icon="👾",
    layout="wide",
)

# Check authentication when user lands on the home page.
login = authenticate.set_st_state_vars()
st.warning(login)

# Add login/logout buttons
if st.session_state["authenticated"]:
    authenticate.button_logout()
else:
    authenticate.button_login()


st.markdown("Football Video Analytics Powered by Artificial Intelligence")

st.header("Hello, Welcome to our Demo Portal !")
