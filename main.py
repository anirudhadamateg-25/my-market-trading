import streamlit as st
import pandas as pd

st.title("Dashboard")
st.subheader("VCapitals Trade Data Analysis") 
st.set_page_config(layout="wide")

# Load data from Google Sheets
data = pd.read_csv("https://docs.google.com/spreadsheets/d/1QEi3eh-q18sjjy1P2SFiCy32AMu3-u3IFZa2BUM-7Ss/export?format=csv")

st.write(f"Data Loaded: {data.shape[0]} rows and {data.shape[1]} columns.")
#st.write("Data Preview:")
#st.dataframe(data.head())

if data.empty:
    st.write("No data available.")
else:
    #print( data.columns)

    #sidebar for strategy selection
    platform_options = ["All"] + list(data['PLATFORM'].unique())
    selected_platform = st.sidebar.selectbox("Select a Platform", platform_options)
    strategy_options = ["All"] + list(data['STRATEGY'].unique())
    selected_strategy = st.sidebar.selectbox("Select a Strategy", strategy_options)
    #show_strategy_bar_chart = st.sidebar.checkbox("Show Strategy Bar Chart", value=True)
    
    #old bar chart imlementation
    #if show_strategy_bar_chart:
        #strategy_counts = data['STRATEGY'].value_counts()
        #st.bar_chart(strategy_counts)
    
    #show_profit_line_chart = st.sidebar.checkbox("Show Profit Line Chart", value=True)
    #if show_profit_line_chart:
        #profit_data = data.groupby('EXIT DATE')['EQUITY CURVE'].sum().reset_index()
        #profit_data['EXIT DATE'] = pd.to_datetime(profit_data['EXIT DATE']).dt.to_period('M').dt.to_timestamp()
        #profit_data = profit_data.groupby('EXIT DATE')['EQUITY CURVE'].sum().reset_index()    
        #st.line_chart(profit_data.rename(columns={'EXIT DATE': 'index'}).set_index('index'))
    
    
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
    col1, col2, col3,col4,col5,col6 = st.columns(6)
    #col1.metric("Total Capital", f"₹{capital:,.2f}")
    col2.metric("Total Turnover", f"₹{total_turnover/100000:,.1f}L",help=f"Value: {total_turnover:,.2f}")
    col3.metric("Total Realised Gains", f"₹{total_gained_profit/100000:,.1f}L",help=f"Value: {total_gained_profit:,.2f}")
    col4.metric("Avg Percentage Gains", f"{avg_percentage:.2f}%")
    col5.metric("Max Return Trade", f"₹{max_return_trade:,.2f}")
    col6.metric("Min Return Trade", f"₹{min_return_trade:,.2f}")
    

    st.dataframe(filtered_data, hide_index=True)
    st.write(f"Filtered Data: {filtered_data.shape[0]} rows and {filtered_data.shape[1]} columns.")

    st.subheader("All Data is personal trade data and not advisory in any form.") 
    st.subheader("All rights reserved to VCapitals(Anirudha Damate).") 
    
    # Download button for filtered data
    #csv = filtered_data.to_csv(index=False).encode('utf-8')
    # st.download_button(
    #     label="Download Filtered Data as CSV",
    #     data=csv,
    #     file_name='filtered_data.csv',
    #     mime='text/csv',
    # )   
    
    # Additional Charts
    st.subheader("Additional Charts")       
    col1, col2,col3 = st.columns(3)
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
        
            
      
 
 

    

    
