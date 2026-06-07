from sqlalchemy import create_engine
import streamlit as st

DATABASE_URL = st.secrets["DATABASE_URL"]

print("USING DATABASE:", DATABASE_URL[:60])

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)