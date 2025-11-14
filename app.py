import streamlit as st
from pymongo import MongoClient

# --------------------- DB CONNECTION ---------------------
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI)
db = client["game"]
users_collection = db["users"]
tournament_collection = db["tournaments"]

# --------------------- GAME LOGIC ---------------------
def check_winner(board):
    win_positions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in win_positions:
        if board[a] == board[b] == board[c] and board[a] != "":
            return board[a]
    return None


# --------------------- ADMIN PAGE ---------------------
def admin_page():
    st.title("Admin Dashboard")

    # Logout button
    if st.button("Logout Admin"):
        st.session_state["admin"] = False
        st.rerun()

    st.subheader("Registered Users (Auto Loaded)")

    # Automatically show all users
    users = list(users_collection.find({}, {"_id": 0}))
    st.table(users)

    st.write("---")

    # Buttons to show creator and tournaments
    col1, col2 = st.columns(2)

    with col1:
        show_create = st.button("Create New User")

    with col2:
        show_tournaments = st.button("View Tournament Results")

    # CREATE NEW USER
    if show_create:
        st.subheader("Create User")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        fullname = st.text_input("Full Name")

        if st.button("Save User"):
            if users_collection.find_one({"username": new_username}):
                st.error("User already exists!")
            else:
                users_collection.insert_one({
                    "username": new_username,
                    "password": new_password,
                    "name": fullname
                })
                st.success("User created successfully!")
                st.rerun()

    # TOURNAMENT RESULTS
    if show_tournaments:
        st.subheader("Tournament Results")
        games = list(tournament_collection.find({}, {"_id": 0}))
        st.table(games)


# --------------------- USER GAME PAGE ---------------------
def user_game_page():
    st.title("OX Game (Two Players)")

    # If users logged in, show logout button
    if st.session_state.get("players"):
        if st.button("Logout Players"):
            del st.session_state["players"]
            del st.session_state["board"]
            del st.session_state["turn"]
            st.rerun()

    # If not logged in -> show login form
    if not st.session_state.get("players"):
        st.subheader("Player Login")
        col1, col2 = st.columns(2)

        with col1:
            p1_name = st.text_input("Player 1 Name")
            p1_username = st.text_input("Player 1 Username")
            p1_password = st.text_input("Player 1 Password", type="password")

        with col2:
            p2_name = st.text_input("Player 2 Name")
            p2_username = st.text_input("Player 2 Username")
            p2_password = st.text_input("Player 2 Password", type="password")

        if st.button("Login Players"):
            user1 = users_collection.find_one({"username": p1_username, "password": p1_password})
            user2 = users_collection.find_one({"username": p2_username, "password": p2_password})

            if not user1 or not user2:
                st.error("Invalid login for one or both players!")
                return

            st.session_state["players"] = {
                "X": user1["name"],
                "O": user2["name"]
            }
            st.session_state["board"] = [""] * 9
            st.session_state["turn"] = "X"
            st.rerun()

    # ---------------- GAME AREA ----------------
    if "players" in st.session_state:

        st.subheader(f"Turn: {st.session_state['turn']} ({st.session_state['players'][st.session_state['turn']]})")

        # Restart game button
        if st.button("Restart Game"):
            st.session_state["board"] = [""] * 9
            st.session_state["turn"] = "X"
            st.rerun()

        cols = st.columns(3)
        for i in range(9):
            if cols[i % 3].button(st.session_state["board"][i] or " ", key=f"cell_{i}"):
                if st.session_state["board"][i] == "":
                    st.session_state["board"][i] = st.session_state["turn"]
                    winner = check_winner(st.session_state["board"])

                    if winner:
                        winner_name = st.session_state["players"][winner]

                        st.success(f"{winner_name} wins!")

                        tournament_collection.insert_one({
                            "winner": winner_name,
                            "symbol": winner
                        })

                        st.balloons()
                        return

                    st.session_state["turn"] = "O" if st.session_state["turn"] == "X" else "X"
                    st.rerun()


# --------------------- MAIN APP ---------------------
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select", ["Admin Login", "User Game"])

    # ---------------- ADMIN LOGIN ----------------
    if page == "Admin Login":
        st.title("Admin Login")

        # If NOT logged in, show login form
        if not st.session_state.get("admin"):
            username = st.text_input("Admin Username")
            password = st.text_input("Admin Password", type="password")

            if st.button("Login"):
                if username == "kapil" and password == "kapil01":
                    st.session_state["admin"] = True
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")

        # If logged in, show admin dashboard
        if st.session_state.get("admin"):
            admin_page()

    # ---------------- USER GAME ----------------
    elif page == "User Game":
        user_game_page()


if __name__ == "__main__":
    main()
