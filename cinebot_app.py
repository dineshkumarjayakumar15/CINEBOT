import streamlit as st
import pandas as pd

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="CINEBOT", layout="wide")

# -----------------------
# CUSTOM STYLE (Dark + Glow UI)
# -----------------------
st.markdown("""
<style>
body {
    background-color: #0A0A0B;
    color: white;
}

.stApp {
    background: linear-gradient(135deg, #0A0A0B, #111827);
}

.chat-user {
    background: #7f1d1d;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    text-align: right;
}

.chat-bot {
    background: #1f2937;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data
def load_data():
    return pd.read_csv("final_movies.csv")

df = load_data()

# -----------------------
# SESSION STATE
# -----------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "filters" not in st.session_state:
    st.session_state.filters = {
        "genre": None,
        "language": None,
        "mood": None
    }

# -----------------------
# TITLE
# -----------------------
st.markdown("<h1 style='text-align:center;'>CINEBOT</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Conversational Movie Recommendation System</p>", unsafe_allow_html=True)

# -----------------------
# LAYOUT
# -----------------------
left, right = st.columns([1, 3])

# -----------------------
# LEFT PANEL (FILTERS)
# -----------------------
with left:
    st.subheader("Preferences")

    genre = st.selectbox("Genre", ["Any"] + sorted(df["genre"].dropna().unique()))
    language = st.selectbox("Language", ["Any"] + sorted(df["language"].dropna().unique()))
    mood = st.selectbox("Mood", ["Any"] + sorted(df["mood"].dropna().unique()))
    rating = st.slider("Minimum Rating", 0.0, 10.0, 7.0)

    if st.button("Suggest Movies"):
        st.session_state.filters["genre"] = None if genre == "Any" else genre
        st.session_state.filters["language"] = None if language == "Any" else language
        st.session_state.filters["mood"] = None if mood == "Any" else mood

        results = df.copy()

        if st.session_state.filters["genre"]:
            results = results[results["genre"] == st.session_state.filters["genre"]]

        if st.session_state.filters["language"]:
            results = results[results["language"] == st.session_state.filters["language"]]

        if st.session_state.filters["mood"]:
            results = results[results["mood"] == st.session_state.filters["mood"]]

        results = results[results["rating"] >= rating]
        results = results.sort_values(by="rating", ascending=False).head(5)

        st.session_state.chat.append({
            "role": "bot",
            "text": format_results(results)
        })

    if st.button("Reset Chat"):
        st.session_state.chat = []

# -----------------------
# FORMAT RESULT
# -----------------------
def format_results(results):
    if results.empty:
        return "No movies found. Try different filters."

    text = "Recommended Movies:\n\n"
    for _, row in results.iterrows():
        text += f"{row['title']} ({row['year']}) - {row['genre']} - {row['language']} - ⭐ {row['rating']}\n"
    return text

# -----------------------
# CHAT LOGIC
# -----------------------
def chatbot_response(user_input):
    text = user_input.lower()

    if "thriller" in text:
        st.session_state.filters["genre"] = "Thriller"

    if "tamil" in text:
        st.session_state.filters["language"] = "Tamil"

    if "dark" in text:
        st.session_state.filters["mood"] = "Dark"

    results = df.copy()

    if st.session_state.filters["genre"]:
        results = results[results["genre"] == st.session_state.filters["genre"]]

    if st.session_state.filters["language"]:
        results = results[results["language"] == st.session_state.filters["language"]]

    if st.session_state.filters["mood"]:
        results = results[results["mood"] == st.session_state.filters["mood"]]

    results = results.sort_values(by="rating", ascending=False).head(5)

    return format_results(results)

# -----------------------
# RIGHT PANEL (CHAT)
# -----------------------
with right:
    st.subheader("CINEBOT Chat")

    for msg in st.session_state.chat:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-user'>{msg['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'>{msg['text']}</div>", unsafe_allow_html=True)

    user_input = st.text_input("Type your message...")

    if st.button("Send") and user_input:
        st.session_state.chat.append({"role": "user", "text": user_input})

        response = chatbot_response(user_input)

        st.session_state.chat.append({"role": "bot", "text": response})