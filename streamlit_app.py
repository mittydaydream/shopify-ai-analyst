import streamlit as st
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="AI Multi-Store Analyst", layout="wide")

st.title("AI Multi-Store Analyst")
st.write("Upload Shopify / GA4 / Search Console CSV files and let Claude generate an operations analysis report.")

st.sidebar.header("Settings")

store_name = st.sidebar.text_input("Store / Brand Name", "Pinty")

analysis_period = st.sidebar.selectbox(
    "Analysis Period",
    ["Yesterday", "Last 7 Days", "Last 30 Days", "Custom"]
)

analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    [
        "Overall Business Analysis",
        "Sales Analysis",
        "Traffic & Conversion Analysis",
        "Product Performance Analysis",
        "SEO Analysis",
        "Page Quality Analysis"
    ]
)

st.header("1. Upload Data")

shopify_file = st.file_uploader("Upload Shopify CSV", type=["csv"])
ga4_file = st.file_uploader("Upload GA4 CSV", type=["csv"])
gsc_file = st.file_uploader("Upload Search Console CSV", type=["csv"])

data_summary = ""


def clean_text(value):
    text = str(value)
    text = text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    text = text.replace("\x00", "")
    return text


def summarize_csv(file, name):
    if file is None:
        return ""

    try:
        file.seek(0)

        try:
            df = pd.read_csv(
                file,
                sep=None,
                engine="python",
                encoding="utf-8-sig"
            )
        except Exception:
            file.seek(0)
            df = pd.read_csv(
                file,
                engine="python",
                encoding="utf-8-sig",
                on_bad_lines="skip"
            )

        df = df.astype(str).map(clean_text)

        st.subheader(name)
        st.write(f"Rows: {len(df)} | Columns: {len(df.columns)}")
        st.dataframe(df.head(20))

        safe_sample = df.head(20).to_string()
        safe_sample = clean_text(safe_sample)

        summary = f"""
{name}

Columns:
{list(df.columns)}

Rows:
{len(df)}

Sample Data:
{safe_sample}
"""

        return summary

    except Exception as e:
        st.error(f"{name} 文件读取失败: {e}")
        return ""


data_summary += summarize_csv(shopify_file, "Shopify Data")
data_summary += summarize_csv(ga4_file, "GA4 Data")
data_summary += summarize_csv(gsc_file, "Search Console Data")

st.header("2. Generate Claude Analysis")

if st.button("Generate Analysis"):
    if not data_summary:
        st.warning("Please upload at least one CSV file.")
    else:
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
            model = st.secrets.get("CLAUDE_MODEL", "claude-3-5-haiku-latest")

api_key = st.secrets["OPENAI_API_KEY"]
model = st.secrets.get("OPENAI_MODEL", "gpt-5-mini")

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "You are a senior ecommerce operations analyst."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
)

st.subheader("AI Analysis Report")
st.write(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Error: {e}")
