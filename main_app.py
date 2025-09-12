import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(layout="wide", page_title="Club Elo Dashboard")



@st.cache_data
def load_data(filepath):
    """
    Loads the Elo ratings data from a CSV file, converts the 'date' column
    to datetime objects, and filters for the top 5 European leagues.
    """
    try:
        df = pd.read_csv(filepath)
       
        df['date'] = pd.to_datetime(df['date'])
        
        
        top_leagues = ['GER', 'ESP', 'ENG', 'FRA', 'ITA']
        
        
        filtered_df = df[df['country'].isin(top_leagues)].copy()
        
        return filtered_df
    except FileNotFoundError:
        # If the CSV file isn't found, display an error message.
        st.error(f"Error: The file '{filepath}' was not found. Please make sure it's in the same folder as the script.")
        return None

#main
elo_data = load_data('EloRatings.csv')


st.title("⚽ Club Elo Ratings Dashboard")
st.markdown("""
This dashboard visualizes the Club Elo ratings for teams in the top 5 European leagues (England, Spain, Germany, Italy, and France).
Use the sidebar to select specific clubs to analyze.
""")


if elo_data is not None:
    st.sidebar.header("Filter Options")
   
    club_list = sorted(elo_data['club'].unique())
    
    default_clubs = ['Man City', 'Real Madrid', 'Bayern', 'PSG', 'Inter']
    selected_clubs = st.sidebar.multiselect(
        'Select clubs to display:',
        options=club_list,
        default=[club for club in default_clubs if club in club_list] 
    )

    
    if not selected_clubs:
        st.warning("Please select at least one club from the sidebar to see the visualizations.")
    else:
        subset_data = elo_data[elo_data['club'].isin(selected_clubs)]

        st.header("Elo Ratings Over Time")
        
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
        
        latest_ratings = subset_data.sort_values('date').drop_duplicates('club', keep='last')

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
        
        st.header("Filtered Club Data")
        st.dataframe(subset_data)
