import streamlit as st
from pymongo import MongoClient

# Connect to MongoDB using Streamlit secrets
MONGO_URI = st.secrets["mongo"]["uri"]
client = MongoClient(MONGO_URI)
db = client["ox_game_db"]
users = db["users"]

def signup(username, password):
    if users.find_one({"username": username}):
        st.warning("Username already exists!")
        return
    users.insert_one({"username": username, "password": password})
    st.success("Account created! Please log in.")

def login(username, password):
    user = users.find_one({"username": username, "password": password})
    if user:
        st.session_state["user"] = username
        st.success(f"Welcome, {username}!")
    else:
        st.error("Invalid username or password.")

def check_winner(board):
    wins = [(0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6),(0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] and board[a] != "":
            return board[a]
    return None

def reset_game():
    st.session_state.board = [""] * 9
    st.session_state.turn = "X"

def play_game():
    st.title("OX Game 🎮")
    if "board" not in st.session_state:
        reset_game()

    board = st.session_state.board
    turn = st.session_state.turn

    cols = st.columns(3)
    for i in range(9):
        if cols[i % 3].button(board[i] or " ", key=i):
            if board[i] == "":
                board[i] = turn
                winner = check_winner(board)
                if winner:
                    st.success(f"{winner} wins! 🎉")
                    reset_game()
                elif "" not in board:
                    st.info("It's a draw! 🤝")
                    reset_game()
                else:
                    st.session_state.turn = "O" if turn == "X" else "X"

    st.write(f"Turn: **{st.session_state.turn}**")
    if st.button("Reset Game"):
        reset_game()

st.sidebar.title("OX Game Login")
menu = ["Login", "Sign Up"]
choice = st.sidebar.radio("Select", menu)

if "user" not in st.session_state:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if choice == "Sign Up":
        if st.sidebar.button("Create Account"):
            signup(username, password)
    else:
        if st.sidebar.button("Login"):
            login(username, password)
else:
    st.sidebar.success(f"Logged in as {st.session_state['user']}")
    if st.sidebar.button("Logout"):
        del st.session_state["user"]

if "user" in st.session_state:
    play_game()
else:
    st.title("Welcome to OX Game 👋")
    st.write("Please log in or sign up using the sidebar to start playing.")
