import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings
import seaborn as sns
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Indian startups",page_icon=":bar_chart:",layout="wide")
st.title(" :bar_chart: Indian startups analysis")
st.markdown("<style>div.block-container{padding-top:2rem;}</styles",unsafe_allow_html=True)

f1 = st.file_uploader(":file-folder: Upload as file",type=(["csv","txt","xlsx"]))
if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    os.chdir("C:/Users/anhin/PycharmProjects/PythonProject2")
    df = pd.read_csv("final_deta_csv.csv",encoding = "ISO-8859-1")
    df.drop(columns=["Unnamed: 0"],inplace=True)
    st.write(df.head())

st.sidebar.header("startup funding analysis:")
select = st.sidebar.selectbox("select ones",([" ","overall analysis","Startup","Investors", "Startup Locations"]))
if select == "overall analysis":
    st.title("Overall analysis")
    total_amount = round(df['amount'].sum())
    max_invest = df["amount"].max()
    avg_invest = round(df["amount"].mean())
    Total_startups = df["startup"].nunique()

    col1, col2,col3,col4 = st.columns(4)
    with col1:
        st.metric("total invest ",total_amount,"CR")
    with col2:
        st.metric("Max Invest",max_invest,"CR")

    with col3:
        st.metric("Average Invest",avg_invest,"CR")

    with col4:
        st.metric("Total Startups",Total_startups)



    st.title("MoM Graph")
    option = st.selectbox("select ones",["","Month wise Investment","Month wise Startups"])
    st.sidebar.selectbox("select startups",df["startup"].unique())
    col1,col2 = st.columns(2)
    # Ensure the date column is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')



    if option == "Month wise Investment":
            st.subheader("Month wise Investment")

            temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
            month = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)
            temp_df['X_axis'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)
            import plotly.express as px

            fig = px.line(temp_df, x='X_axis', y='amount')
            st.write(fig)
    else:
            st.subheader("Month wise Startups")
            st_count = df.groupby(['year', 'month'])['startup'].count().reset_index()
            df['month_year'] = df['month'].astype(str) + '-' + df['year'].astype(str)

            fig = px.line(df, x='month_year', y='st_count')

            fig.update_layout(title='Startup Count over Time',
                              xaxis_title='Month-Year',
                              yaxis_title='Startup Count')

            st.write(fig)
    col1,col2 = st.columns(2)
    with col1:
        vertical_counts = df.groupby('vertical')['startup'].count()

        vertical_percentages = vertical_counts / vertical_counts.sum() * 100

        filtered_verticals = vertical_percentages[vertical_percentages >= 0.1]

        fig1 = px.pie(values=filtered_verticals.values,
                      names=filtered_verticals.index,
                      title='Distribution of Startups Across Verticals (>=0.1%)',
                      hole=0.3)

        fig1.update_traces(textposition='none')  # Hide percentage labels
        fig1.update_layout(width=800, height=600)  # Increase size

        st.write(fig1)
    with col2:

        round_counts = df.groupby('round')['startup'].count()
        round_counts = round_counts[round_counts > 1]
        st.markdown("<style>div.block-container{padding-top:4rem;}</styles", unsafe_allow_html=True)

        fig2 = px.pie(values=round_counts.values,
                     names=round_counts.index,
                     title='Distribution of Funding Rounds (Excluding Single Contributions)')
        fig2.update_traces(textposition='none')
        st.write(fig2)










elif select == "Investors":
    st.subheader("Investors analysis")
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('Find Investor Details')
    st.header(selected_investor)

    st.subheader("Most Recent investments")
    recent_investments = df[df['investors'].str.contains(selected_investor, na=False)].sort_values(by='date',
                                                                                             ascending=False).head(5)

    # Display the results
    st.write(recent_investments[['date', 'startup', 'vertical', 'subvertical', 'city', 'investors', 'round', 'amount']])

    col1,col2 = st.columns(2)
    with col1:
        investor_df = df[df['investors'].str.contains(selected_investor, na=False)]


        vertical_investment = investor_df.groupby('vertical')['amount'].sum()


        fig3 = px.bar(x=vertical_investment.index, y=vertical_investment.values,
                     labels={'x': 'Vertical', 'y': 'Total Investment Amount'},
                     title=f'Investment by {selected_investor} in Different Verticals')
        st.write(fig3)

    with col2:
        import plotly.express as px
        investor_df = df[df['investors'].str.contains(selected_investor, na=False)]

        if investor_df.empty:
            print(f"No investments found for investor: {selected_investor}")
        else:
            startup_investment = investor_df.groupby('startup')['amount'].sum()

            fig4 = px.pie(values=startup_investment.values,
                         names=startup_investment.index,
                         title=f'Investment Distribution of {selected_investor} across Startups')
            st.write(fig4)

    investor_df = df[df['investors'].str.contains(selected_investor, na=False)]

    if investor_df.empty:
        print(f"No investments found for investor: {selected_investor}")
    else:
        yearly_investment = investor_df.groupby('year')['amount'].sum()

        fig5 = px.line(x=yearly_investment.index, y=yearly_investment.values,
                      labels={'x': 'Year', 'y': 'Total Investment Amount'},
                      title=f'Year-on-Year Investment by {selected_investor}')
        st.write(fig5)



elif select == "Startup":
    st.subheader("Startups Analysis")
    selected_startup = st.sidebar.selectbox('Select startup', sorted(set(df['startup'].str.split(',').sum())))
    btn2 = st.sidebar.button('Find Startup Details')
    st.subheader(selected_startup)
    col1,col2 = st.columns(2)


    if btn2 == True:

        with col1:
            startup_df = df[df['startup'] == selected_startup]

            if startup_df.empty:
                print(f"No data found for startup: {selected_startup}")
            else:
                vertical_counts = startup_df.groupby('vertical')['startup'].count()
                fig6 = px.pie(values=vertical_counts.values,
                             names=vertical_counts.index,
                             title=f'Distribution of Investments for {selected_startup} across Verticals')
                st.write(fig6)

        with col2:
            startup_df = df[df['startup'] == selected_startup]

            if startup_df.empty:
                print(f"No data found for startup: {selected_startup}")
            else:
                vertical_counts = startup_df.groupby('subvertical')['startup'].count()
                fig7 = px.pie(values=vertical_counts.values,
                              names=vertical_counts.index,
                              title=f'Distribution of Investments for {selected_startup} across Verticals')
                st.write(fig7)

        startup_df = df[df['startup'] ==selected_startup ]
        if startup_df.empty:
            print(f"No data found for startup: {selected_startup}")
        else:
            startup_df['month_year'] = startup_df['month'].astype(str) + '-' + startup_df['year'].astype(str)
            monthly_investment = startup_df.groupby('month_year')['amount'].sum().reset_index()

            fig8 = px.line(monthly_investment, x='month_year', y='amount',
                          labels={'month_year': 'Month-Year', 'amount': 'Total Investment Amount'},
                          title=f'Month-on-Month Investment for {selected_startup}')
            st.write(fig8)







