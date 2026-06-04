import streamlit as st
import pandas as pd
from anthropic import Anthropic

st.set_page_config(page_title="AI Multi-Store Analyst", layout="wide")

st.title("AI Multi-Store Analyst")
st.write("Upload Shopify / GA4 / SEO CSV files and let Claude generate an operations analysis report.")

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

def summarize_csv(file, name):
    if file is not None:
        df = pd.read_csv(file)
        st.subheader(name)
        st.dataframe(df.head(20))
        summary = f"""
{name}
Columns: {list(df.columns)}
Rows: {len(df)}
Sample Data:
{df.head(20).to_string()}
"""
        return summary
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

            client = Anthropic(api_key=api_key)

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

            message = client.messages.create(
                model=model,
                max_tokens=3000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            st.subheader("Claude Analysis Report")
            st.write(message.content[0].text)

        except Exception as e:
            st.error(f"Error: {e}")
