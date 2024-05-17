import streamlit as st
import pickle
import pandas as pd 
import requests
import time

def fetch_poster(movie_id, max_retries=3):
    for _ in range(max_retries):
        try:
            response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=ff9f09bec0fd2cdf3926d480832b3746&language=en-US')
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                return None
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.ConnectionError) and isinstance(e.__cause__, ConnectionResetError):
                continue  # Ignore ConnectionResetError and retry
            
            time.sleep(1)  # Add a short delay before retrying
    
    return None

# Load movie data and similarity matrix
movies_list = pd.read_pickle('movies.pkl')
similarity = pd.read_pickle('similarity.pkl')

def recommend(movie):
    try:
        # Get the index of the selected movie
        movie_index = movies_list[movies_list['title'] == movie].index[0]
        # Get similarity scores for the selected movie
        distances = similarity[movie_index]
        # Sort the movies based on similarity (excluding the selected movie)
        sorted_movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        # Extract titles of recommended movies and their posters
        recommended_movies = []
        recommended_posters = []
        for i in sorted_movies:
            movie_index = i[0]
            movie_id = movies_list.iloc[movie_index]['id']
            movie_title = movies_list.iloc[movie_index]['title']
            recommended_movies.append(movie_title)
            poster_url = fetch_poster(movie_id)
            recommended_posters.append(poster_url)
        return recommended_movies, recommended_posters
    except IndexError:
        st.error("Movie not found in the dataset.")
        return [], []

st.title("Movie Recommendation System")

selected_movie = st.selectbox("Select a movie:", movies_list['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie)
    if names:
        cols = st.columns(5)
        for i in range(min(5, len(names))):
            with cols[i]:
                st.text(names[i])
                if posters[i]:
                    st.image(posters[i], use_column_width='auto')
                else:
                    st.write("Poster not available")
