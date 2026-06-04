import streamlit as st
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="AI Multi-Store Analyst", layout="wide")

st.title("AI Multi-Store Analyst")
st.write("Upload Shopify / GA4 / Search Console CSV files and let GPT generate an operations analysis report.")

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

        safe_sample = clean_text(df.head(20).to_string())

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

st.header("2. Generate GPT Analysis")

if st.button("Generate Analysis"):
    if not data_summary:
        st.warning("Please upload at least one CSV file.")
    else:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
            model = st.secrets.get("OPENAI_MODEL", "gpt-5-mini")

            client = OpenAI(api_key=api_key)

            prompt = f"""
You are a senior e-commerce operations analyst.

The user operates multiple Shopify stores and wants practical business insights.

Please analyze the uploaded data.

Store / Brand:
{store_name}

Analysis Period:
{analysis_period}

Analysis Type:
{analysis_type}

Data:
{data_summary}

Please output the report in Chinese.

Report structure:
1. 核心结论
2. 销售表现
3. 流量与转化率表现
4. 产品表现
5. SEO / 页面表现
6. 发现的问题
7. 优先级行动清单
8. 下周建议

Please be practical, specific, and suitable for a Shopify operator.
If the data is incomplete, clearly explain what is missing.
"""

            prompt = clean_text(prompt)

            response = client.responses.create(
                model=model,
                input=prompt
            )

            st.subheader("GPT Analysis Report")
            st.write(response.output_text)

        except Exception as e:
            st.error(f"Error: {e}")
