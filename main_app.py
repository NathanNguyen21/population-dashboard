import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
# Set the layout and title for the Streamlit page.
st.set_page_config(layout="wide", page_title="Club Elo Dashboard")


# --- Data Loading and Caching ---
# Use st.cache_data to load the data only once, which improves performance.
@st.cache_data
def load_data(filepath):
    """
    Loads the Elo ratings data from a CSV file, converts the 'date' column
    to datetime objects, and filters for the top 5 European leagues.
    """
    try:
        df = pd.read_csv(filepath)
        # Convert the 'date' column to a proper datetime format.
        df['date'] = pd.to_datetime(df['date'])
        
        # Define the list of country codes for the leagues we want to keep.
        # Note: England is represented by 'ENG'. I've assumed this based on common datasets.
        # If your data uses a different code, you can change it here.
        top_leagues = ['GER', 'ESP', 'ENG', 'FRA', 'ITA']
        
        # Filter the DataFrame to only include clubs from the specified countries.
        filtered_df = df[df['country'].isin(top_leagues)].copy()
        
        return filtered_df
    except FileNotFoundError:
        # If the CSV file isn't found, display an error message.
        st.error(f"Error: The file '{filepath}' was not found. Please make sure it's in the same folder as the script.")
        return None

# --- Main Application ---

# Load the data using the function defined above.
# The user must place their 'EloRatings.csv' file in the same directory.
elo_data = load_data('/workspaces/population-dashboard/data/EloRatings.csv')

# Main title of the dashboard
st.title("⚽ Club Elo Ratings Dashboard")
st.markdown("""
This dashboard visualizes the Club Elo ratings for teams in the top 5 European leagues (England, Spain, Germany, Italy, and France).
Use the sidebar to select specific clubs to analyze.
""")


if elo_data is not None:
    # --- Sidebar for User Input ---
    st.sidebar.header("Filter Options")

    # Get a sorted, unique list of club names for the multi-select widget.
    club_list = sorted(elo_data['club'].unique())
    
    # Create a multi-select widget in the sidebar.
    # We'll pre-select a few popular clubs as a default example.
    default_clubs = ['Man City', 'Real Madrid', 'Bayern', 'PSG', 'Inter']
    selected_clubs = st.sidebar.multiselect(
        'Select clubs to display:',
        options=club_list,
        default=[club for club in default_clubs if club in club_list] # Ensure defaults exist
    )

    # --- Data Filtering based on Selection ---
    if not selected_clubs:
        # If no clubs are selected, show a message prompting the user.
        st.warning("Please select at least one club from the sidebar to see the visualizations.")
    else:
        # Filter the main DataFrame to only include data for the clubs the user has chosen.
        subset_data = elo_data[elo_data['club'].isin(selected_clubs)]

        # --- Visualizations ---
        st.header("Elo Ratings Over Time")
        
        # 1. Scatter Plot
        # This plot shows the Elo rating for each selected club over the years.
        # It's great for seeing the historical performance and trends.
        fig_scatter = px.scatter(
            subset_data,
            x='date',
            y='elo',
            color='club',
            title='Club Elo Rating Progression',
            labels={'date': 'Date', 'elo': 'Elo Rating', 'club': 'Club'},
            hover_name='club',
            hover_data={'elo': ':.2f', 'date': '|%B %d, %Y'}
        )
        fig_scatter.update_layout(legend_title_text='Clubs')
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.header("Latest Elo Rating Comparison")
        
        # 2. Bubble Chart
        # To create the bubble chart, we first need to find the most recent rating for each club.
        # We sort by date and then remove duplicates, keeping only the last entry for each club.
        latest_ratings = subset_data.sort_values('date').drop_duplicates('club', keep='last')

        # This chart compares the latest Elo ratings of the selected clubs.
        # The size of the bubble also represents the Elo rating, making it easy to spot top teams.
        fig_bubble = px.scatter(
            latest_ratings,
            x='country',
            y='elo',
            size='elo',  # Bubble size is proportional to the Elo rating
            color='country',
            title='Latest Elo Ratings by Country',
            labels={'country': 'Country', 'elo': 'Latest Elo Rating'},
            hover_name='club',
            size_max=60  # Adjust the maximum bubble size for better visualization
        )
        st.plotly_chart(fig_bubble, use_container_width=True)
        
        # --- Display Raw Data ---
        # It's good practice to also show the data being plotted.
        st.header("Filtered Club Data")
        st.dataframe(subset_data)
