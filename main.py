import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(layout='wide', page_title='StartUp Analysis')

# Check if the file exists to avoid runtime errors
file_path = 'startup_cleaned.csv'

if not os.path.exists(file_path):
    st.error(f"File '{file_path}' not found. Please make sure the file is available in the project directory.")
    st.stop()

# Load the data
try:
    df = pd.read_csv(file_path)
    st.success("Data loaded successfully!")
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

# Fix potential date parsing issues
try:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
except Exception as e:
    st.error(f"Error parsing 'date' column: {e}")
    df['date'] = pd.NaT

# Additional preprocessing steps
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year


def load_overall_analysis():
    st.title('Overall Analysis')

    # Check if required columns exist
    if 'amount' not in df.columns:
        st.error("'amount' column not found in the dataset")
        return

    if 'startup' not in df.columns:
        st.error("'startup' column not found in the dataset")
        return

    # Total investment amount
    total = round(df['amount'].sum())

    # Max amount infused in any single startup
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]

    # Average ticket size
    avg_funding = df.groupby('startup')['amount'].sum().mean()

    # Total funded startups
    num_startups = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric('Total', f"{total} Cr")
    with col2:
        st.metric('Max', f"{max_funding} Cr")
    with col3:
        st.metric('Avg', f"{round(avg_funding)} Cr")
    with col4:
        st.metric('Funded Startups', num_startups)

    st.header('MoM graph')
    selected_option = st.selectbox('Select Type', ['Total', 'Count'])

    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')

    fig3, ax3 = plt.subplots(figsize=(12, 6))
    ax3.plot(temp_df['x_axis'], temp_df['amount'])
    ax3.set_xlabel('Month-Year')
    ax3.set_ylabel('Amount in CR')
    ax3.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig3)


def load_startup_details(startup):
    st.title(f'{startup} Analysis')

    if 'startup' not in df.columns:
        st.error("'startup' column not found in the dataset")
        return

    # Filter data for the selected startup
    startup_df = df[df['startup'] == startup]

    if startup_df.empty:
        st.warning(f"No data found for startup: {startup}")
        return

    # Display basic info
    col1, col2, col3 = st.columns(3)

    with col1:
        total_funding = startup_df['amount'].sum()
        st.metric('Total Funding', f"{total_funding} Cr")

    with col2:
        funding_rounds = len(startup_df)
        st.metric('Funding Rounds', funding_rounds)

    with col3:
        if 'vertical' in startup_df.columns:
            vertical = startup_df['vertical'].iloc[0] if not startup_df['vertical'].isna().all() else "N/A"
            st.metric('Vertical', vertical)

    # Display funding history
    st.subheader('Funding History')
    display_columns = ['date', 'round', 'amount', 'investors']
    available_columns = [col for col in display_columns if col in startup_df.columns]
    st.dataframe(startup_df[available_columns].sort_values('date', ascending=False))


def load_investor_details(investor):
    st.title(investor)

    if 'investors' not in df.columns:
        st.error("'investors' column not found in the dataset")
        return

    # Filter investments by the selected investor (case-insensitive)
    investor_df = df[df['investors'].str.contains(investor, na=False, case=False)]

    if investor_df.empty:
        st.warning(f"No investments found for investor: {investor}")
        return

    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        total_investment = investor_df['amount'].sum()
        st.metric('Total Investment', f"{total_investment} Cr")
    with col2:
        num_investments = len(investor_df)
        st.metric('Number of Investments', num_investments)
    with col3:
        num_startups = investor_df['startup'].nunique()
        st.metric('Unique Startups', num_startups)

    # Load the recent 5 investments of the investor
    display_columns = ['date', 'startup', 'vertical', 'city', 'round', 'amount']
    available_columns = [col for col in display_columns if col in investor_df.columns]
    last5_df = investor_df[available_columns].head()

    st.subheader('Most Recent Investments')
    st.dataframe(last5_df)

    col1, col2 = st.columns(2)

    with col1:
        # Biggest investments
        big_series = (
            investor_df.groupby('startup')['amount']
            .sum()
            .sort_values(ascending=False)
            .head()
        )

        if not big_series.empty and len(big_series) > 0:
            st.subheader('Biggest Investments')
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(big_series.index, big_series.values)
                ax.set_xlabel('StartUps')
                ax.set_ylabel('Funding Amount (Cr)')
                ax.tick_params(axis='x', rotation=45)

                # Add value labels on bars
                for bar, value in zip(bars, big_series.values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{value:.1f}', ha='center', va='bottom')

                st.pyplot(fig)
                plt.close(fig)
            except Exception as e:
                st.error(f"Error creating bar chart: {str(e)}")
                plt.close('all')
        else:
            st.warning("No investment data available for bar chart")

    with col2:
        if 'vertical' in investor_df.columns:
            vertical_series = investor_df.groupby('vertical')['amount'].sum()
            # Remove any NaN or zero values
            vertical_series = vertical_series[vertical_series > 0]

            if not vertical_series.empty and len(vertical_series) > 0:
                st.subheader('Sectors Invested In')
                try:
                    fig1, ax1 = plt.subplots(figsize=(8, 8))
                    # Only create pie chart if we have valid data
                    if vertical_series.sum() > 0:
                        ax1.pie(vertical_series.values, labels=vertical_series.index, autopct="%0.01f%%")
                        st.pyplot(fig1)
                    else:
                        st.warning("No valid sector data for pie chart")
                    plt.close(fig1)
                except Exception as e:
                    st.error(f"Error creating pie chart: {str(e)}")
                    plt.close('all')
            else:
                st.warning("No sector data available for pie chart")

    # YoY Investment
    year_series = investor_df.groupby('year')['amount'].sum()
    year_series = year_series[year_series > 0]  # Remove zero values

    if not year_series.empty and len(year_series) > 0:
        st.subheader('YoY Investment')
        try:
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            ax2.plot(year_series.index, year_series.values, marker='o', linewidth=2, markersize=8)
            ax2.set_xlabel('Year')
            ax2.set_ylabel('Investment Amount (Cr)')
            ax2.grid(True, alpha=0.3)

            # Add value labels on points
            for x, y in zip(year_series.index, year_series.values):
                ax2.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0, 10), ha='center')

            st.pyplot(fig2)
            plt.close(fig2)
        except Exception as e:
            st.error(f"Error creating line chart: {str(e)}")
            plt.close('all')
    else:
        st.warning("No year-over-year data available for line chart")


# Sidebar
st.sidebar.title('Startup Funding Analysis')
option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'StartUp':
    if 'startup' in df.columns:
        startup_list = sorted(df['startup'].unique().tolist())
        selected_startup = st.sidebar.selectbox('Select StartUp', startup_list)
        btn1 = st.sidebar.button('Find StartUp Details')
        if btn1:
            load_startup_details(selected_startup)
    else:
        st.error("'startup' column not found in the dataset")

else:  # Investor option
    if 'investors' in df.columns:
        # Extract unique investors from comma-separated values
        all_investors = []
        for investors_str in df['investors'].dropna():
            if isinstance(investors_str, str):
                # Split by comma and clean up whitespace
                investors = [inv.strip() for inv in investors_str.split(',')]
                all_investors.extend(investors)

        # Remove empty strings and get unique investors
        investor_list = sorted(set([inv for inv in all_investors if inv]))

        if investor_list:
            selected_investor = st.sidebar.selectbox('Select Investor', investor_list)
            btn2 = st.sidebar.button('Find Investor Details')
            if btn2:
                load_investor_details(selected_investor)
        else:
            st.error("No investors found in the dataset")
    else:
        st.error("'investors' column not found in the dataset")
