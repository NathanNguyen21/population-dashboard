import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
# Set the layout and title for the Streamlit page.
st.set_page_config(layout="wide", page_title="MovieLens Ratings Dashboard")

# --- Data Loading and Caching ---
# Use st.cache_data to load and process the data only once, which improves performance.
@st.cache_data
def load_data(filepath):
    """
    Loads the MovieLens ratings data from a CSV file.
    """
    try:
        df = pd.read_csv(filepath)
        # The 'genres' column contains pipe-separated values. We'll handle this later
        # for specific questions that require analyzing individual genres.
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{filepath}' was not found. Please make sure it's in the same folder as the script.")
        return None

# --- Main Application ---

# Load the data using the function defined above.
# The user must place their 'movie_ratings.csv' file in the same directory.
movie_data = load_data('movie_ratings.csv')

# Main title of the dashboard
st.title("🎬 MovieLens 200k Ratings Analysis")
st.markdown("This dashboard explores the MovieLens dataset to uncover insights about movie genres, ratings, and trends over time.")

if movie_data is not None:
    
    # --- Question 1: Genre Breakdown ---
    st.header("1. What is the breakdown of movie genres?")
    st.markdown("This chart shows the total number of ratings given to movies in each genre.")
    
    # To count genres, we need to handle the pipe-separated 'genres' column.
    # First, we drop rows where 'genres' is missing to avoid errors.
    genres_df = movie_data.dropna(subset=['genres']).copy()
    # We split the string into a list of genres for each row.
    genres_df['genres'] = genres_df['genres'].str.split('|')
    # The 'explode' function creates a new row for each genre in the list,
    # duplicating the other information for that rating.
    exploded_genres = genres_df.explode('genres')
    
    # Now we can simply count the occurrences of each genre.
    genre_counts = exploded_genres['genres'].value_counts()
    
    fig1 = px.bar(
        genre_counts,
        x=genre_counts.index,
        y=genre_counts.values,
        title="Total Ratings per Genre",
        labels={'x': 'Genre', 'y': 'Number of Ratings'}
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- Question 2: Highest Rated Genres ---
    st.header("2. Which genres have the highest viewer satisfaction?")
    st.markdown("This chart displays the average rating for each genre, sorted from highest to lowest.")
    
    # We can reuse the 'exploded_genres' DataFrame from the previous question.
    # We group by genre and calculate the mean of the 'rating' for each.
    avg_genre_ratings = exploded_genres.groupby('genres')['rating'].mean().sort_values(ascending=False)
    
    fig2 = px.bar(
        avg_genre_ratings,
        x=avg_genre_ratings.values,
        y=avg_genre_ratings.index,
        orientation='h', # Horizontal bar chart
        title="Average Rating by Genre",
        labels={'x': 'Average Rating (1-5)', 'y': 'Genre'}
    )
    fig2.update_layout(yaxis={'categoryorder':'total ascending'}) # Sorts the y-axis to match the data
    st.plotly_chart(fig2, use_container_width=True)

    # --- Question 3: Mean Rating Across Release Years ---
    st.header("3. How does mean rating change across movie release years?")
    st.markdown("This line chart illustrates the trend of average movie ratings based on their release year.")
    
    # Group the original data by 'year' and calculate the mean 'rating'.
    # We drop NaN values in 'year' and convert it to an integer for a cleaner axis.
    yearly_ratings = movie_data.dropna(subset=['year']).copy()
    yearly_ratings['year'] = yearly_ratings['year'].astype(int)
    avg_rating_by_year = yearly_ratings.groupby('year')['rating'].mean().reset_index()

    fig3 = px.line(
        avg_rating_by_year,
        x='year',
        y='rating',
        title='Average Movie Rating by Release Year',
        labels={'year': 'Release Year', 'rating': 'Average Rating'}
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # --- Question 4: Best-Rated Movies with Minimum Ratings ---
    st.header("4. What are the best-rated movies?")
    st.markdown("To find the best movies, we calculate the average rating and the total number of ratings for each title. This avoids rewarding movies with a single 5-star rating.")

    # We group by 'title' and aggregate to get both the count and mean of ratings.
    movie_stats = movie_data.groupby('title')['rating'].agg(['count', 'mean']).reset_index()
    
    # Use columns to display the two lists side-by-side.
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 5 (at least 50 ratings)")
        # Filter for movies with at least 50 ratings, then sort by mean rating.
        top_50 = movie_stats[movie_stats['count'] >= 50].sort_values('mean', ascending=False).head(5)
        st.dataframe(top_50.reset_index(drop=True))

    with col2:
        st.subheader("Top 5 (at least 150 ratings)")
        # Filter for movies with at least 150 ratings, then sort by mean rating.
        top_150 = movie_stats[movie_stats['count'] >= 150].sort_values('mean', ascending=False).head(5)
        st.dataframe(top_150.reset_index(drop=True))
