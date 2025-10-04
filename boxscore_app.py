import streamlit as st
import json
import os

# --- Player class ---
class Player:
    def __init__(self, name: str, points=0, rebounds=0, assists=0):
        self.name = name
        self.points = points
        self.rebounds = rebounds
        self.assists = assists

    def to_dict(self):
        return {
            "name": self.name,
            "points": self.points,
            "rebounds": self.rebounds,
            "assists": self.assists
        }

    @classmethod
    def from_dict(cls, data):
        # fallback: if data is a string, create a Player with that name
        if isinstance(data, str):
            return cls(name=data)
        elif isinstance(data, dict):
            return cls(**data)
        else:
            raise ValueError(f"Unexpected player data format: {data}")

# --- File and helpers ---
PLAYER_FILE = "players.json"

def load_players():
    """Safely load players from file, handling all cases."""
    if not os.path.exists(PLAYER_FILE):
        return []  # No file yet

    try:
        with open(PLAYER_FILE, "r") as f:
            data = json.load(f)

            # handle empty or malformed data
            if not isinstance(data, list):
                return []

            players = []
            for entry in data:
                try:
                    players.append(Player.from_dict(entry))
                except Exception as e:
                    print(f"Skipping invalid entry: {entry} ({e})")
            return players
    except (json.JSONDecodeError, FileNotFoundError):
        # file exists but is empty or broken
        return []

def save_players(players):
    with open(PLAYER_FILE, "w") as f:
        json.dump([p.to_dict() for p in players], f, indent=2)

# --- Streamlit setup ---
if "players" not in st.session_state:
    st.session_state.players = load_players()

# --- Sidebar ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Add Game", "Player Stats"])

# --- Page 1: Add Game ---
if page == "Add Game":
    st.title("Add Game")

    player_name = st.text_input("Enter player name")

    if st.button("Add Player") and player_name:
        if not any(p.name == player_name for p in st.session_state.players):
            new_player = Player(player_name)
            st.session_state.players.append(new_player)
            save_players(st.session_state.players)
            st.success(f"Player '{player_name}' added!")
        else:
            st.warning(f"'{player_name}' already exists!")

    st.markdown("### Current Roster:")
    if st.session_state.players:
        for p in st.session_state.players:
            st.write(f"👤 {p.name}")
    else:
        st.info("No players yet. Add one above!")

# --- Page 2: Player Stats ---
elif page == "Player Stats":
    st.title("Player Stats")

    if st.session_state.players:
        for p in st.session_state.players:
            st.write(f"**{p.name}** — Points: {p.points}, Rebounds: {p.rebounds}, Assists: {p.assists}")
    else:
        st.info("No players yet. Add some on the 'Add Game' page.")
