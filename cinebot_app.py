import streamlit as st
import pandas as pd

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    return pd.read_csv("final_movies.csv")

df = load_data()

# ---------- CONFIG ----------
st.set_page_config(layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0b0b0b, #1a1a1a);
}

/* Title */
.main-title {
    text-align:center;
    font-size:50px;
    color: gold;
}

/* Button */
.stButton>button {
    background: linear-gradient(90deg, gold, orange);
    color: black;
    border-radius: 10px;
    border: none;
}

/* Movie Card */
.movie-card {
    background: linear-gradient(145deg, rgba(0,0,0,0.8), rgba(30,30,30,0.9));
    padding:20px;
    border-radius:15px;
    margin-bottom:15px;
    border:1px solid rgba(255,215,0,0.3);
    box-shadow: 0 0 15px rgba(255,215,0,0.2);
    transition: 0.3s;
}
.movie-card:hover {
    transform: scale(1.02);
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

    st.markdown("<h1 class='main-title'>🎬 CINEBOT</h1>", unsafe_allow_html=True)

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

# ---------- CHAT MOOD ----------
def detect_mood(text):
    text = text.lower()

    if "sad" in text:
        return "emotional"
    elif "happy" in text:
        return "feel-good"
    elif "love" in text:
        return "romantic"
    elif "action" in text:
        return "action"
    elif "thrill" in text:
        return "thriller"

    return None

# ---------- FILTER FUNCTION ----------
def get_movies():
    data = df.copy()

    if st.session_state.mode == "chat":
        mood = st.session_state.genre
        data = data[data["mood"].str.lower() == mood]

    elif st.session_state.mode == "filter":
        genre = st.session_state.genre
        data = data[data["genre"].str.lower() == genre.lower()]

    return data.sort_values(by="rating", ascending=False).head(20)

# ---------- SIDEBAR ----------
st.sidebar.title("🎛 Preferences")

genre = st.sidebar.selectbox("Genre", ["Select","Action","Comedy","Romance","Drama","Thriller"])

if st.sidebar.button("Recommend Movies"):
    if genre != "Select":
        st.session_state.genre = genre
        st.session_state.mode = "filter"

# ---------- MAIN ----------
st.markdown("<h1 class='main-title'>🍿 CINEBOT</h1>", unsafe_allow_html=True)

col_main, col_chat = st.columns([3,1])

# ---------- CHAT ----------
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

# ---------- DISPLAY ----------
def show_movies(title, data):
    st.subheader(title)

    if data.empty:
        st.warning("No movies found")
        return

    cols = st.columns(2)

    for i, row in data.iterrows():
        with cols[i % 2]:
            st.markdown(f"""
            <div class="movie-card">
                <h3>🎬 {row['title']}</h3>
                ⭐ {row['rating']} <br>
                🎭 {row['genre']} <br>
                🌐 {row['language']} <br>
                😊 Mood: {row['mood']} <br>
                📅 Year: {row['year']}
            </div>
            """, unsafe_allow_html=True)

# ---------- LOGIC ----------
with col_main:

    if st.session_state.mode in ["chat","filter"]:
        movies = get_movies()
        show_movies("🎬 Recommended Movies", movies)

    else:
        trending = df.sort_values(by="popularity", ascending=False).head(20)
        show_movies("🔥 Trending Movies", trending)