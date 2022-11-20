import streamlit as st
import components.authenticate as authenticate
import boto3
from dotenv import load_dotenv
import os
import io


st.set_page_config(
    page_title="TACTIC",
    page_icon="👾",
    layout="wide",
)
load_dotenv()
# Check authentication when user lands on the home page.
authenticate.set_st_state_vars()

# Add login/logout buttons
if st.session_state["authenticated"]:
    authenticate.button_logout()
else:
    authenticate.button_login()


st.markdown("Football Video Analytics Powered by Artificial Intelligence")

st.header("Hello, Welcome to our Demo Portal !")
