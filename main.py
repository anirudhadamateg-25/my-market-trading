import streamlit as st
import pandas as pd

st.title("VCapitals Trade Study")
st.write("This is a simple Data Analysis Application.") 
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


    # Display the metric
    col1, col2, col3,col4 = st.columns(4)
    #col1.metric("Total Capital", f"₹{capital:,.2f}")
    col2.metric("Total Turnover", f"₹{total_turnover:,.2f}")
    col3.metric("Total Realised Gains", f"₹{total_gained_profit:,.2f}")
    col4.metric("Avg Percentage Gains", f"{avg_percentage:.2f}%")



    st.dataframe(filtered_data)
    st.write(f"Filtered Data: {filtered_data.shape[0]} rows and {filtered_data.shape[1]} columns.")


    # Download button for filtered data
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_data.csv',
        mime='text/csv',
    )   
    # Additional Charts
    st.subheader("Additional Charts")       
    col1, col2 = st.columns(2)
    with col1:
        st.write("Strategy Distribution")
        strategy_counts = filtered_data['STRATEGY'].value_counts()
        st.bar_chart(strategy_counts)
    with col2:
        st.write("Platform Distribution")
        platform_counts = filtered_data['PLATFORM'].value_counts()
        st.bar_chart(platform_counts)   
 
 

    

    
