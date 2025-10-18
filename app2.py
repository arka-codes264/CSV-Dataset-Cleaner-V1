import streamlit as st
import pandas as pd
import os
from uuid import uuid4
from datetime import datetime

DATA_DIR = "app_data/cleaned"
os.makedirs(DATA_DIR, exist_ok=True)

def simple_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    # Example cleaning steps - replace with your real pipeline
    df = df.copy()
    # normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    # fill numeric NaNs with median
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())
    # fill object cols with empty string
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("")
    # add a sample derived column (example)
    if "issue_price" in df.columns and "listing_price" in df.columns:
        df["listing_gain_percent"] = ((df["listing_price"] - df["issue_price"]) / df["issue_price"]) * 100
    return df

def save_cleaned(df: pd.DataFrame) -> str:
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"cleaned_{ts}_{uuid4().hex}.csv"
    path = os.path.join(DATA_DIR, fname)
    df.to_csv(path, index=False)
    return path

st.title("Upload CSV -> Clean -> Use (Dounload)")

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
save_to_disk = st.checkbox("Save cleaned CSV to server (create csv2)", value=True)

if uploaded:
    raw_df = pd.read_csv(uploaded)
    st.subheader("Raw Data Preview")
    st.write(raw_df.head())

    # run cleaning pipeline
    cleaned_df = simple_cleaning(raw_df)

    st.subheader("Cleaned Data Preview")
    st.write(cleaned_df.head())

    # store cleaned df in session state so other UI parts can reuse it
    st.session_state["cleaned_df"] = cleaned_df

    if save_to_disk:
        cleaned_path = save_cleaned(cleaned_df)
        st.success(f"Cleaned CSV saved at: {cleaned_path}")
        # keep path in session for downstream usage
        st.session_state["cleaned_path"] = cleaned_path

        # let user download the cleaned CSV
        with open(cleaned_path, "rb") as f:
            st.download_button("Download cleaned CSV", f, file_name=os.path.basename(cleaned_path))
    else:
        # provide download from memory
        csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download cleaned CSV (in-memory)", csv_bytes, file_name="cleaned.csv")

    # Example: use the cleaned_df for plotting or modeling
    st.subheader("Simple Stats from cleaned data")
    st.write(cleaned_df.describe())
