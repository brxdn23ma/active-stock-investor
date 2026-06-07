from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

DB_USER = st.secrets.get("DB_USER", os.getenv("DB_USER"))
DB_PASSWORD = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD"))
DB_HOST = st.secrets.get("DB_HOST", os.getenv("DB_HOST"))
DB_PORT = st.secrets.get("DB_PORT", os.getenv("DB_PORT"))
DB_NAME = st.secrets.get("DB_NAME", os.getenv("DB_NAME"))

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)