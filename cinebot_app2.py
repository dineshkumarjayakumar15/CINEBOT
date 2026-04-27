import streamlit as st
import requests
import os
from dotenv import load_dotenv

# ---------- LOAD API ----------
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

# ---------- CONFIG ----------
st.set_page_config(layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1505685296765-3a2736de412f");
    background-size: cover;
    background-attachment: fixed;
}

.overlay {
    background: rgba(0,0,0,0.85);
    padding: 20px;
    border-radius: 10px;
}

h1, h2, h3 {
    color: gold;
}

.stButton>button {
    background: linear-gradient(90deg, gold, orange);
    border: none;
    color: black;
    border-radius: 10px;
}

.chat-box {
    height: 400px;
    overflow-y: auto;
    background: rgba(255,255,255,0.05);
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "mode" not in st.session_state:
    st.session_state.mode = "default"

if "genre" not in st.session_state:
    st.session_state.genre = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- LOGIN ----------
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;color:gold;'>🎬 CINEBOT</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### Login")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Enter"):
            if user == "admin" and pwd == "password123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid login")

    st.stop()

# ---------- GENRE ----------
GENRE_MAP = {
    "Action": 28,
    "Comedy": 35,
    "Romance": 10749,
    "Drama": 18,
    "Horror": 27
}

# ---------- FETCH ----------
def fetch_movies(genre_id=None):
    movies = []
    try:
        for page in range(1,4):  # fetch more movies
            url = "https://api.themoviedb.org/3/discover/movie"
            params = {
                "api_key": API_KEY,
                "sort_by": "popularity.desc",
                "page": page
            }
            if genre_id:
                params["with_genres"] = genre_id

            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            movies.extend(res.json().get("results", []))

        return movies[:20]

    except:
        st.error("⚠️ API Error. Check key or internet.")
        return []

# ---------- CHAT ----------
def detect_mood(text):
    text = text.lower()

    if "sad" in text:
        return "Drama"
    elif "happy" in text:
        return "Comedy"
    elif "love" in text:
        return "Romance"
    elif "action" in text:
        return "Action"
    elif "scary" in text:
        return "Horror"

    return None

# ---------- SIDEBAR ----------
st.sidebar.title("🎛 Preferences")

genre = st.sidebar.selectbox("Genre", ["Select","Action","Comedy","Romance","Drama","Horror"])

if st.sidebar.button("Recommend Movies"):
    if genre != "Select":
        st.session_state.genre = genre
        st.session_state.mode = "filter"

# ---------- MAIN LAYOUT ----------
st.markdown("<h1>🍿 CINEBOT</h1>", unsafe_allow_html=True)

col_main, col_chat = st.columns([3,1])

# ---------- CHAT PANEL ----------
with col_chat:
    st.subheader("💬 Chat")

    user_input = st.text_input("Say something")

    if st.button("Send"):
        if user_input:
            mood = detect_mood(user_input)
            if mood:
                st.session_state.genre = mood
                st.session_state.mode = "chat"
                reply = f"Got it! Showing {mood} movies 🎬"
            else:
                reply = "Try words like sad, happy, love, action"

            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Bot", reply))

    for sender, msg in st.session_state.chat_history:
        st.write(f"**{sender}:** {msg}")

# ---------- MOVIE DISPLAY ----------
def show_movies(title, movies):
    st.subheader(title)

    if not movies:
        st.warning("No movies found")
        return

    cols = st.columns(5)
    for i, m in enumerate(movies):
        if m.get("poster_path"):
            img = f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
            with cols[i % 5]:
                st.image(img, use_container_width=True)
                st.caption(f"{m['title']} ⭐ {m['vote_average']}")

# ---------- LOGIC ----------
with col_main:

    if st.session_state.mode == "chat":
        gid = GENRE_MAP.get(st.session_state.genre)
        movies = fetch_movies(gid)
        show_movies(f"🎭 Based on mood: {st.session_state.genre}", movies)

    elif st.session_state.mode == "filter":
        gid = GENRE_MAP.get(st.session_state.genre)
        movies = fetch_movies(gid)
        show_movies(f"🎯 Filter: {st.session_state.genre}", movies)

    else:
        # default homepage
        trending = fetch_movies()
        show_movies("🔥 Trending", trending)