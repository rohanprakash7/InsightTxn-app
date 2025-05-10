import streamlit as st
from PIL import Image

# Configure page settings
st.set_page_config(
    page_title="PayPal Reviews Dashboard",
    page_icon="💳",
    layout="wide"
)
   

# Header Section
st.markdown(
    """
    <h1 style="text-align: center; color: #0078D4;">
        🚀 Welcome to <b>PayPal Reviews</b> Dashboard 💳
    </h1>
    <h4 style="text-align: center; color: #444;">
        Analyze and review customer transactions with ease.
    </h4>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Layout with Columns
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 🔍 What Can You Do Here?")
    st.write(
        """
        - 📊 **Analyze transactions** to detect fraud or unusual activity.
        - 🔎 **Review customer behavior** with insightful visualizations.
        - 📉 **Track trends** and monitor financial activities efficiently.

        **👈 Select an app from the sidebar** to get started!
        """
    )

with col2:
    st.markdown("## 🛠️ Quick Actions")
    st.button("🔍 Review Transactions")
    st.button("📊 View Customer Insights")

st.markdown("---")

# Footer
st.markdown(
    """
    <div style="text-align: center; font-size: 14px; color: gray;">
        Made with ❤️ using <b>Streamlit</b> | Powered by AI & Data Science 🚀
    </div>
    """,
    unsafe_allow_html=True
)
