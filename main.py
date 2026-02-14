import streamlit as st
import pandas as pd
from chat_component import render_stock_chat
from openai import OpenAI

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


st.sidebar.title("VCapitals Analysis") 
st.sidebar.divider()


# Page navigation
st.set_page_config(layout="wide")
page = st.sidebar.radio("📊 Menu", ["Live Position","Dashboard","Strategy","AI Analyst"])

if page == "Dashboard":
    st.title("Dashboard")
    

    # Load data from Google Sheets
    data = pd.read_csv(st.secrets["data"]["csv_url"],skip_blank_lines=True,skiprows=2,usecols=["ENTRY DATE", "EXIT DATE", "SCRIPT", "STRATEGY", "PLATFORM", "INVESTED", "PROFIT/ABS","PROFIT/%","EQUITY CURVE"])
    


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
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        col1.metric("Total Target", f"₹{(capital *30/100)/100000:,.1f}L", help=f"Value: {capital *30/100:,.2f}")
        col2.metric("Remaining Target", f"₹{((capital *30/100) - total_gained_profit)/100000:,.1f}L", help=f"Value: {(capital *30/100) - total_gained_profit:,.2f}")
        col3.metric("Total Realised Gains", f"₹{total_gained_profit/100000:,.1f}L", help=f"Value: {total_gained_profit:,.2f}")
        col4.metric("Total Turnover", f"₹{total_turnover/100000:,.1f}L", help=f"Value: {total_turnover:,.2f}")
        col5.metric("Avg Percentage Gains", f"{avg_percentage:.2f}%")
        col6.metric("Max Return Trade", f"₹{max_return_trade/1000:,.2f}k", help=f"Value: ₹{max_return_trade:,.2f}")
        col7.metric("Min Return Trade", f"₹{min_return_trade/1000:,.2f}k", help=f"Value: ₹{min_return_trade:,.2f}")
        col8.metric("Total Trades", f"{filtered_data.shape[0]}")

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
                monthly_profit_stockwise.groupby("SCRIPT", as_index=False)
                    .agg(
                        TOTAL_PROFIT_ABS=("PROFIT/ABS", "sum"),
                        AVG_PROFIT_PCT=("PROFIT/%", "mean")
                    )
                    .sort_values("SCRIPT")                    
            )

            st.dataframe(
                    monthly_profit_stockwise,
                    column_config={
                        "TOTAL_PROFIT_ABS": st.column_config.NumberColumn(
                            "Total Realised Gains",
                            format="₹%.2f"
                        ),
                        "AVG_PROFIT_PCT": st.column_config.NumberColumn(
                            "Avg Profit %",
                            format="%.2f%%"
                        )
                    },
                    use_container_width=True
            )

# ...existing code...
elif page == "Live Position": 
    st.title("Live Position")

    
    try:
        # Read live position data from Google Sheets
        live_data = pd.read_csv(st.secrets["data"]["csv_live_url"],skip_blank_lines=True,skiprows=25,usecols=["Stock", "Strategy Name", "Market Cap", "Broker", "Gain","Current Value","Invested Value","Target Price","Potential Gain","Remaining Gain"])
        live_data = live_data.iloc[25:48]  # Limit to first 48 rows

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
            platform_counts = filtered_data['Broker'].value_counts()
            st.bar_chart(platform_counts)  

    except Exception as e:
        st.error("Error loading live position data")
# ...existing code...

elif page == "AI Analyst":
    api_key = st.secrets["aikey"]["api_key"]
    model = "gpt-4o-mini"

    # Chat box at the bottom
    if api_key:       
        render_stock_chat(api_key, model)
    else:
        st.info("👈 Subscribe to Plan")
 
elif page == "Strategy":
    with st.expander("Reverse Head & Shoulders"):
        st.markdown("""
        In a world full of **complex indicators**, we keep it **simple** by focusing on  **Price Action** and **Quality**.
        Most textbooks teach the Reverse Head & Shoulders (RHS) pattern in a way that leads to many **fake-outs**.
        This approach uses **strict filters** so we only participate in **high-probability trades**. """)

        st.divider()

        # --------------------------------------------------
        # Section 1
        # --------------------------------------------------
        st.subheader("🧬 1. The Anatomy of a Perfect Pattern")

        st.markdown("""
        A standard Reverse Head & Shoulders has:
        - A **Left Shoulder**
        - A **Head** (the lowest point)
        - A **Right Shoulder**

        However, for us to consider it a **RHS**, it must meet **strict criteria**. """)

        st.subheader("📏 The 180-Degree Neckline")
        st.markdown("""
        - The **neckline must be flat and horizontal**
        - No upward or downward slope is allowed
        - A flat line clearly shows **where the seller is sitting**
        """)

        st.subheader("🔗 The Three Connection Points")
        st.markdown("""
        The horizontal neckline must **perfectly touch**:
        1. The start of the **Left Shoulder**
        2. The peak **after the Head**
        3. The start of the **Right Shoulder**
        """)

        st.divider()

        # --------------------------------------------------
        # Section 2
        # --------------------------------------------------
        st.subheader("💎 2. The Fundamental Filter")

        st.markdown("""
        We **never apply technical patterns to junk stocks**.
        This strategy is applied **only** to companies that are:
        """)

        st.markdown("""
        - 💼 **Financially stable businesses**
        """)

        st.info("""
        📌 If the **business quality is weak**,  the chart pattern will eventually **fail**.
            **Business first. Chart second.**   """)

        st.divider()

        # --------------------------------------------------
        # Section 3
        # --------------------------------------------------
        st.subheader("🚀 3. The “Early” Entry Strategy")

        st.markdown(""" Most traders wait for a **neckline breakout**.   We don’t. """)

        st.markdown("""
        ### What we look for instead:
        - A **Base Formation** inside the **Right Shoulder**
        - Small consolidation
        - Followed by a **strong Green Candle 🕯️ (closing basis)**
        """)

        st.success("""
        ✅ This gives:
        - Better entry price  
        - Smaller stop-loss  
        - Higher risk-reward
        """)

        st.divider()

st.sidebar.divider()

# Add logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()

st.sidebar.title("Terms and Conditions:")
st.sidebar.text("All Data is Personal Trade data and not advisory in any form.") 
st.sidebar.text("All rights reserved to Anirudha Damate.") 