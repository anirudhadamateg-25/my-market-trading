import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

# Authentication check
if not st.session_state.authenticated:
    st.title("VCapitals Trade Data Analysis")
    st.info("👈Please login using the sidebar to access the dashboard.")
    
    # Login form in sidebar
    with st.sidebar:
        st.title("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                # Check credentials against secrets
                try:
                    if username in st.secrets["passwords"] and st.secrets["passwords"][username] == password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except Exception as e:
                    st.error("⚠️ Config error")
    
    st.stop()  # Stop execution if not authenticated


# Add logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()
st.sidebar.divider()

# Page navigation
st.set_page_config(layout="wide")
page = st.sidebar.radio("📊 Menu", ["Dashboard", "Live Position"])

if page == "Dashboard":
    st.title("Dashboard")
    st.subheader("VCapitals Trade Data Analysis") 

    # Load data from Google Sheets
    data = pd.read_csv(st.secrets["data"]["csv_url"])

    st.write(f"Data Loaded: {data.shape[0]} rows and {data.shape[1]} columns.")

    if data.empty:
        st.write("No data available.")
    else:
        # Sidebar for strategy selection
        platform_options = ["All"] + list(data['PLATFORM'].unique())
        selected_platform = st.sidebar.selectbox("Select a Platform", platform_options)
        strategy_options = ["All"] + list(data['STRATEGY'].unique())
        selected_strategy = st.sidebar.selectbox("Select a Strategy", strategy_options)
        
        filtered_data = data
        if selected_platform != "All":
            filtered_data = filtered_data[filtered_data['PLATFORM'] == selected_platform]
        if selected_strategy != "All":
            filtered_data = filtered_data[filtered_data['STRATEGY'] == selected_strategy]

        # Define your KPI values
        capital = 900000
        total_turnover = filtered_data['INVESTED'].sum()
        total_gained_profit = filtered_data['PROFIT/ABS'].sum()
        avg_percentage = total_gained_profit / capital * 100 if total_turnover != 0 else 0

        max_return_trade = filtered_data['PROFIT/ABS'].max()
        min_return_trade = filtered_data['PROFIT/ABS'].min()

        # Display the metric
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col2.metric("Total Turnover", f"₹{total_turnover/100000:,.1f}L", help=f"Value: {total_turnover:,.2f}")
        col3.metric("Total Realised Gains", f"₹{total_gained_profit/100000:,.1f}L", help=f"Value: {total_gained_profit:,.2f}")
        col4.metric("Avg Percentage Gains", f"{avg_percentage:.2f}%")
        col5.metric("Max Return Trade", f"₹{max_return_trade:,.2f}")
        col6.metric("Min Return Trade", f"₹{min_return_trade:,.2f}")
        
        st.dataframe(filtered_data, hide_index=True, use_container_width=True, column_config={}, key="filtered_data_table")
        st.write(f"Filtered Data: {filtered_data.shape[0]} rows and {filtered_data.shape[1]} columns.")
        
        # Additional Charts
        st.subheader("Additional Charts")       
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Strategy Distribution")
            strategy_counts = filtered_data['STRATEGY'].value_counts()
            st.bar_chart(strategy_counts)
        with col2:
            st.write("Platform Distribution")
            platform_counts = filtered_data['PLATFORM'].value_counts()
            st.bar_chart(platform_counts)   
        with col3:
            st.write("Monthly Realised Gains")
            monthly_profit = filtered_data.copy()
            monthly_profit["EXIT DATE"] = pd.to_datetime(monthly_profit["EXIT DATE"], errors="coerce")
            monthly_profit = monthly_profit.dropna(subset=["EXIT DATE"])
            monthly_profit["Month"] = monthly_profit["EXIT DATE"].dt.to_period("M").astype(str)
            monthly_profit = (
                monthly_profit.groupby("Month")["PROFIT/ABS"].sum().reset_index()
                .sort_values("Month")
            )
            st.bar_chart(monthly_profit.set_index("Month")[["PROFIT/ABS"]])   

        with st.expander("Stockwise Realised Gains"):  
            monthly_profit_stockwise = filtered_data.copy()     
            monthly_profit_stockwise = (
                monthly_profit_stockwise.groupby("SCRIPT")["PROFIT/ABS"].sum().reset_index()
                .sort_values("SCRIPT")
            )
            st.dataframe(monthly_profit_stockwise.rename(columns={"SCRIPT": "Stock", "PROFIT/ABS": "Total Profit"}), hide_index=True)


# ...existing code...
elif page == "Live Position":
    st.title("Live Position")

    
    try:
        # Read live position data from Google Sheets
        live_data = pd.read_csv(st.secrets["data"]["csv_live_url"])
        
        
    
        # Sidebar for strategy selection
        platform_options = ["All"] + list(live_data['Market Cap'].unique())
        selected_platform = st.sidebar.selectbox("Select a Market Cap", platform_options)
        strategy_options = ["All"] + list(live_data['Strategy Name'].unique())
        selected_strategy = st.sidebar.selectbox("Select a Strategy", strategy_options)
        
        filtered_data = live_data
        if selected_platform != "All":
            filtered_data = filtered_data[filtered_data['Market Cap'] == selected_platform]
        if selected_strategy != "All":
            filtered_data = filtered_data[filtered_data['Strategy Name'] == selected_strategy]

        st.write(f"Data Loaded: {filtered_data.shape[0]} rows and {filtered_data.shape[1]} columns.")
        # Define your KPI values
           
        
        if "Gain" in filtered_data.columns:
            filtered_data["Gain"] = pd.to_numeric(filtered_data["Gain"], errors="coerce")
            top_gainer = filtered_data["Gain"].max()
            top_looser = filtered_data["Gain"].min()
        else:
            top_gainer = None
            top_looser = None

        # Display the metric
        col1, col2, col3,col4 = st.columns(4)       
      
        col3.metric("Top Gainer", f"₹{top_gainer:,.2f}%" if top_gainer is not None else "N/A", help=f"Value: ₹{top_gainer:,.2f}" if top_gainer is not None else "N/A")
        col4.metric("Top Looser", f"₹{top_looser:,.2f}%" if top_looser is not None else "N/A", help=f"Value: ₹{top_looser:,.2f}" if top_looser is not None else "N/A")

        st.dataframe(filtered_data, hide_index=True, use_container_width=True)       

        # Additional Charts
        st.subheader("Additional Charts")       
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Strategy Distribution")
            strategy_counts = filtered_data['Strategy Name'].value_counts()
            st.bar_chart(strategy_counts)
        with col2:
            st.write("Market Cap Distribution")
            platform_counts = filtered_data['Market Cap'].value_counts()
            st.bar_chart(platform_counts)
        with col3:
            st.write("Platform Distribution")
            platform_counts = filtered_data['broker'].value_counts()
            st.bar_chart(platform_counts)  

    except Exception as e:
        st.error("Error loading live position data")
# ...existing code...

st.sidebar.divider()

st.sidebar.title("Terms and Conditions:")
st.sidebar.text("All Data is Personal Trade data and not advisory in any form.") 
st.sidebar.text("All rights reserved to Anirudha Damate.") 