import altair as alt
import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta
import numpy as np

# Set Streamlit page config with dark theme
st.set_page_config(
    page_title="Transaction Analytics",
    page_icon="📈",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stSelectbox, .stDateInput {
        margin-bottom: 1rem;
    }
    .chart-container {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Page header with metrics
st.title("📊 Enhanced Transaction Analytics Dashboard")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("📋 Filters")
    
    # File uploader with better error handling
    df_file = st.file_uploader("Upload Transactions CSV", type=['csv'])
    if not df_file:
        st.warning("⚠️ Please upload a CSV file to proceed.")
        st.stop()
    
    try:
        df = pd.read_csv(df_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")
        st.stop()
    
    # Enhanced filters
    PaymentStatus = st.selectbox(
        'Payment Status:',
        ['All'] + sorted(df['Type'].unique().tolist())
    )
    
    PaymentMethod = st.selectbox(
        'Payment Method:',
        ['All'] + sorted(df['Transaction_Type'].unique().tolist())
    )
    
    PaymentApplication = st.selectbox(
        'Payment Application:',
        ['All'] + sorted(df['Source'].unique().tolist())
    )
    
    PaymentCountry = st.selectbox(
        'Payment Country:',
        ['All'] + sorted(df['Country'].unique().tolist())
    )
    
    # Date range with validation
    st.subheader("📅 Date Range")
    default_start_date = date.today() - timedelta(days=180)
    StartDate = st.date_input("Start Date", default_start_date)
    EndDate = st.date_input("End Date", date.today())
    
    if StartDate > EndDate:
        st.error("Error: Start date must be before end date")
        st.stop()

# Data preprocessing
@st.cache_data
def process_data(df):
    # Drop unnecessary columns
    drop_columns = ['Transaction_ID', 'Auth_code']
    df.drop(columns=[col for col in drop_columns if col in df.columns], inplace=True, errors='ignore')
    
    # Basic cleaning
    df = df[df.get('Success', 0) == 1]
    df['Transaction_Notes'].fillna("N/A", inplace=True)
    df['Day'] = pd.to_datetime(df['Day'], errors='coerce')
    df.dropna(subset=['Day'], inplace=True)
    
    # Select and transform columns
    df = df[['Total', 'Transaction_Type', 'Type', 'Country', 'Source', 'Day']]
    df['int_created_date'] = df['Day'].dt.strftime('%Y-%m')
    
    return df

df = process_data(df)

# Apply filters
def apply_filters(df, filters, start_date, end_date):
    for col, value in filters.items():
        if value != 'All':
            df = df[df[col] == value]
    
    df = df[
        (df['Day'] >= pd.to_datetime(start_date)) & 
        (df['Day'] <= pd.to_datetime(end_date))
    ]
    return df

filters = {
    'Type': PaymentStatus,
    'Transaction_Type': PaymentMethod,
    'Source': PaymentApplication,
    'Country': PaymentCountry,
}

df_filtered = apply_filters(df, filters, StartDate, EndDate)

# Display key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Transactions", f"{len(df_filtered):,}")
with col2:
    st.metric("Total Volume", f"${df_filtered['Total'].sum():,.2f}")
with col3:
    st.metric("Average Transaction", f"${df_filtered['Total'].mean():,.2f}")
with col4:
    st.metric("Success Rate", f"{(len(df_filtered)/len(df)*100):.1f}%")

# Enhanced chart creation function
def create_chart(data, chart_type, x_field, y_field, title, color=None):
    # Handle axis titles
    x_title = x_field.split(':')[0] if ':' in x_field else x_field
    y_title = y_field.split(':')[0] if ':' in y_field else y_field
    
    base = alt.Chart(data).encode(
        x=alt.X(x_field, title=x_title),
        y=alt.Y(y_field, title=y_title),
        tooltip=[
            alt.Tooltip(x_field.split(':')[0], title='Period'),
            alt.Tooltip(y_field.split(':')[0], title='Value', format=',.2f')
        ]
    ).properties(
        title=title,
        width="container",
        height=400
    )
    
    if chart_type == "bar":
        return base.mark_bar(cornerRadius=5).encode(
            color=color or alt.value("#4CAF50")
        )
    elif chart_type == "line":
        return base.mark_line(point=True).encode(
            color=color or alt.value("#2196F3")
        )
    elif chart_type == "area":
        return base.mark_area(opacity=0.6).encode(
            color=color or alt.value("#FF9800")
        )

# Create enhanced visualizations
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Transaction Distribution",
    "📈 Time Series Analysis",
    "💰 Volume Analysis",
    "📉 Payment Types"
])

with tab1:
    hist = create_chart(
        df_filtered,
        "bar",
        'Total:Q',
        'count():Q',
        "Transaction Amount Distribution"
    )
    st.altair_chart(hist, use_container_width=True)

with tab2:
    monthly_trend = create_chart(
        df_filtered,
        "line",
        'int_created_date:O',
        'mean(Total):Q',
        "Average Transaction Amount Over Time"
    )
    st.altair_chart(monthly_trend, use_container_width=True)

with tab3:
    volume_chart = create_chart(
        df_filtered,
        "area",
        'int_created_date:O',
        'sum(Total):Q',
        "Total Transaction Volume by Month",
        alt.Color('Type:N', scale=alt.Scale(scheme='category20b'))
    )
    st.altair_chart(volume_chart, use_container_width=True)

with tab4:
    payment_types = alt.Chart(df_filtered).mark_arc().encode(
        theta='count():Q',
        color=alt.Color('Type:N', scale=alt.Scale(scheme='category20c')),
        tooltip=['Type:N', 'count():Q']
    ).properties(
        title="Payment Type Distribution",
        width=400,
        height=400
    )
    st.altair_chart(payment_types, use_container_width=True)

# Add data table with sorting and filtering
st.markdown("### 📑 Detailed Transaction Data")
st.dataframe(
    df_filtered.sort_values('Day', ascending=False)
    .drop('int_created_date', axis=1)
    .style.format({'Total': '${:,.2f}'})
)


