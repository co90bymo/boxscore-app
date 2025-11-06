import streamlit as st
import pandas as pd
import json
import os
from game_logic import run_game  # import the extracted function

# -------------------
# Configuration
# -------------------
IS_ADMIN = False  # Set True for admin
PLAYER_FILE = "players.json"
GAME_FILE = "games.json"

# -------------------
# Player class
# -------------------
class Player:
    def __init__(self, name: str, games=0, mins=0, assists=0, dreb=0, oreb=0, turnovers=0, steals=0, blocks=0,
                 two_pta=0, two_ptm=0, three_pta=0, three_ptm=0, fta=0, ftm=0, plus_minus=0, pf=0):
        self.games = games
        self.name = name
        self.mins = mins
        self.assists = assists
        self.dreb = dreb
        self.oreb = oreb
        self.turnovers = turnovers
        self.steals = steals
        self.blocks = blocks
        self.two_pta = two_pta
        self.two_ptm = two_ptm
        self.three_pta = three_pta
        self.three_ptm = three_ptm
        self.fta = fta
        self.ftm = ftm
        self.plus_minus = plus_minus
        self.pf = pf

    def to_dict(self):
        return {
            "PLAYER": self.name,
            "GAMES": self.games,
            "MIN": self.mins,
            "AST": self.assists,
            "OREB": self.dreb,
            "DREB": self.oreb,
            "TO": self.turnovers,
            "STL": self.steals,
            "BLK": self.blocks,
            "2PTA": self.two_pta,
            "2PTM": self.two_ptm,
            "3PTA": self.three_pta,
            "3PTM": self.three_ptm,
            "FTA": self.fta,
            "FTM": self.ftm,
            "+/-": self.plus_minus,
            "PF": self.pf
        }

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, str):
            return cls(name=data)
        elif isinstance(data, dict):
            return cls(
                name=data.get("PLAYER", ""),
                games=data.get("GAMES", 0),
                mins=data.get("MIN", 0),
                assists=data.get("AST", 0),
                dreb=data.get("DREB", 0),
                oreb=data.get("OREB", 0),
                turnovers=data.get("TO", 0),
                steals=data.get("STL", 0),
                blocks=data.get("BLK", 0),
                two_pta=data.get("2PTA", 0),
                two_ptm=data.get("2PTM", 0),
                three_pta=data.get("3PTA", 0),
                three_ptm=data.get("3PTM", 0),
                fta=data.get("FTA", 0),
                ftm=data.get("FTM", 0),
                plus_minus=data.get("+/-", 0),
                pf=data.get("PF", 0)
            )
        else:
            raise ValueError(f"Unexpected player data format: {data}")

# -------------------
# Game class
# -------------------
class Game:
    def __init__(self, game_id, name, players=None):
        self.game_id = game_id
        self.name = name
        self.players = players if players else []
        self.finished = False

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "name": self.name,
            "players": [p.to_dict() for p in self.players],
            "finished": self.finished
        }

    @classmethod
    def from_dict(cls, data):
        players = [Player.from_dict(p) for p in data.get("players", [])]
        game = cls(game_id=data["game_id"], name=data["name"], players=players)
        game.finished = data.get("finished", False)
        return game

# -------------------
# Helper functions
# -------------------
def load_players():
    if not os.path.exists(PLAYER_FILE):
        return []
    try:
        with open(PLAYER_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return [Player.from_dict(entry) for entry in data]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_players(players):
    with open(PLAYER_FILE, "w") as f:
        json.dump([p.to_dict() for p in players], f, indent=2)

def load_games():
    if not os.path.exists(GAME_FILE):
        return []
    try:
        with open(GAME_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return [Game.from_dict(entry) for entry in data]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_games(games):
    with open(GAME_FILE, "w") as f:
        json.dump([g.to_dict() for g in games], f, indent=2)

def get_player_total_stat(player_name, stat):
    """
    Returns the aggregated value of a specific stat for a given player across all games.
    Automatically loads GAME_FILE if it's a path string.
    """
    global GAME_FILE

    # Load the JSON if GAME_FILE is a string path
    if isinstance(GAME_FILE, str):
        with open(GAME_FILE, "r", encoding="utf-8") as f:
            GAME_FILE = json.load(f)

    total = 0

    for game in GAME_FILE:
        if not isinstance(game, dict):
            continue  # skip anything malformed

        if not game.get("finished", True):
            continue

        for p in game.get("players", []):
            if p.get("PLAYER") == player_name:
                total += p.get(stat, 0)

    return total



# -------------------
# Streamlit setup
# -------------------
if "players" not in st.session_state:
    st.session_state.players = load_players()

if "games" not in st.session_state:
    st.session_state.games = load_games()

if "current_game" not in st.session_state:
    st.session_state.current_game = None

if "selected_players_temp" not in st.session_state:
    st.session_state.selected_players_temp = []

if "confirm_end_game" not in st.session_state:
    st.session_state.confirm_end_game = False

# -------------------
# Sidebar navigation
# -------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Add Game", "Player Stats", "Box Scores"])

# -------------------
# Page 1: Add Game
# -------------------
if page == "Add Game":
    st.title("Add Game")

    if IS_ADMIN:
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
                col1, col2 = st.columns([3,1])
                col1.write(f"👤 {p.name}")
                if col2.button("Remove", key=f"remove_{p.name}"):
                    st.session_state.players.remove(p)
                    save_players(st.session_state.players)
                    st.rerun()
        else:
            st.info("Roster is empty. Add players above.")
    else:
        st.info("You are in read-only mode. You cannot add or remove players.")
        st.markdown("### Current Roster:")
        if st.session_state.players:
            for p in st.session_state.players:
                st.write(f"👤 {p.name}")
        else:
            st.info("No players yet. Admin needs to add players.")

    # Game creation
    if IS_ADMIN:
        if st.session_state.current_game is None:
            game_name_input = st.text_input("Enter game name")
            if game_name_input:
                st.markdown("### Select Players")

                available_players = [
                    p.name for p in st.session_state.players
                    if p.name not in st.session_state.selected_players_temp
                ]
                selected_players = st.session_state.selected_players_temp

                if available_players:
                    st.markdown("**Available Players:**")
                    cols = st.columns(5)
                    for i, name in enumerate(available_players):
                        if cols[i % 5].button(name, key=f"select_{name}"):
                            st.session_state.selected_players_temp.append(name)
                            st.rerun()
                else:
                    st.info("All players selected.")

                if selected_players:
                    st.markdown("**✅ Selected Players:**")
                    cols_selected = st.columns(5)
                    for i, name in enumerate(selected_players):
                        if cols_selected[i % 5].button(f"❌ {name}", key=f"deselect_{name}"):
                            st.session_state.selected_players_temp.remove(name)
                            st.rerun()

                if st.session_state.selected_players_temp:
                    if st.button("Confirm Players"):
                        new_game_id = len(st.session_state.games) + 1
                        selected_objs = [
                            p for p in st.session_state.players
                            if p.name in st.session_state.selected_players_temp
                        ]
                        st.session_state.current_game = Game(
                            game_id=new_game_id,
                            name=game_name_input,
                            players=selected_objs
                        )
                        st.session_state.selected_players_temp = []
                        st.success(f"Game '{game_name_input}' started!")
                        st.rerun()
        else:
            # Call the extracted in-game logic
            run_game(st.session_state.current_game, save_games, save_players)

    # Display all games
    st.markdown("### All Games:")
    if st.session_state.games:
        for g in st.session_state.games:
            col1, col2 = st.columns([3,1])
            col1.write(f"🏀 {g.name} (ID: {g.game_id})")
            if IS_ADMIN and col2.button("Delete", key=f"del_game_{g.game_id}"):
                st.session_state.games.remove(g)
                save_games(st.session_state.games)
                st.success(f"Game '{g.name}' deleted!")
                st.rerun()
    else:
        st.info("No games yet.")

# -------------------
# Page 2: Player Stats
# -------------------


elif page == "Player Stats":
    st.title("Player Stats")

    view_mode = st.radio("Display Mode", ["Total", "Per Game"], horizontal=True)

    def fmt(val):
        """Formats numbers cleanly: removes .0 if present."""
        if isinstance(val, (int, float)):
            if val == int(val):
                return int(val)
            else:
                return round(val, 1)
        return val

    if st.session_state.players:
        player_data = []

        for p in st.session_state.players:
            d = p.to_dict()
            games =  get_player_total_stat(player_name=p.name, stat="GAMES")
            scale = 1 if view_mode == "Total" else games

            # Scale basic stats
            for key in ["MIN", "AST", "OREB", "DREB", "TO", "STL", "BLK", "PF", "+/-"]:
                d[key] = d.get(key, 0) / scale

            # Shooting stats
            two_ptm = get_player_total_stat(player_name=p.name, stat="2PTM") / scale
            two_pta = get_player_total_stat(player_name=p.name, stat="2PTA") / scale
            three_ptm = get_player_total_stat(player_name=p.name, stat="3PTM") / scale
            three_pta = get_player_total_stat(player_name=p.name, stat="3PTA") / scale
            ftm = get_player_total_stat(player_name=p.name, stat="FTM") / scale
            fta = get_player_total_stat(player_name=p.name, stat="FTA") / scale

            # Percentages
            two_pt_pct = (two_ptm / two_pta * 100) if two_pta > 0 else 0
            three_pt_pct = (three_ptm / three_pta * 100) if three_pta > 0 else 0
            fg_makes = two_ptm + three_ptm
            fg_attempts = two_pta + three_pta
            fg_pct = (fg_makes / fg_attempts * 100) if fg_attempts > 0 else 0
            ft_pct = (ftm / fta * 100) if fta > 0 else 0

            # Format strings (remove %)
            two_pt_str = f"{fmt(two_ptm)}-{fmt(two_pta)}"
            three_pt_str = f"{fmt(three_ptm)}-{fmt(three_pta)}"
            ft_str = f"{fmt(ftm)}-{fmt(fta)}"
            fg_str = f"{fmt(fg_makes)}-{fmt(fg_attempts)}"

            pts = (two_ptm * 2) + (three_ptm * 3) + ftm

            oreb = get_player_total_stat(player_name=p.name, stat="OREB") / scale
            dreb = get_player_total_stat(player_name=p.name, stat="DREB") / scale
            reb = oreb + dreb

            ordered_d = {
                "PLAYER": d.get("PLAYER", ""),
                "GAMES": fmt(1 if view_mode == "Per Game" else get_player_total_stat(player_name=p.name, stat="GAMES"),),
                "MIN": fmt(get_player_total_stat(player_name=p.name, stat="MIN") / scale),
                "PTS": fmt(pts),
                "AST": fmt(get_player_total_stat(player_name=p.name, stat="AST") / scale),
                "REB": fmt(reb),
                "OREB": fmt(oreb),
                "DREB": fmt(dreb),
                "TO": fmt(get_player_total_stat(player_name=p.name, stat="TO") / scale),
                "STL": fmt(get_player_total_stat(player_name=p.name, stat="STL") / scale),
                "BLK": fmt(get_player_total_stat(player_name=p.name, stat="BLK") / scale),
                "2PT": two_pt_str,
                "2FG%": fmt(two_pt_pct),
                "3PT": three_pt_str,
                "3FG%": fmt(three_pt_pct),
                "FG": fg_str,
                "FG%": fmt(fg_pct),
                "FT": ft_str,
                "FT%": fmt(ft_pct),
                "+/-": fmt(get_player_total_stat(player_name=p.name, stat="+/-") / scale),
                "PF": fmt(get_player_total_stat(player_name=p.name, stat="PF") / scale),
            }

            player_data.append(ordered_d)

        st.dataframe(
            player_data,
            use_container_width=True
        )

    else:
        st.info("No players yet. Add some on the 'Add Game' page.")

    


    # -------------------
    # Page 3: Box Scores
    # -------------------
elif page == "Box Scores":
    st.title("Box Scores")

    if st.session_state.games:
        for g in st.session_state.games:
            if not g.finished:
                continue  # only show finished games
            st.markdown(f"### 🏀 {g.name} (ID: {g.game_id})")

            # Build box-score rows using per-game player objects stored in game.players
            box_data = []
            for p in g.players:
                pts = (p.two_ptm * 2) + (p.three_ptm * 3) + p.ftm
                row = {
                    "PLAYER": p.name,
                    "GAMES": p.games,
                    "MIN": p.mins,
                    "PTS": pts,
                    "AST": p.assists,
                    "REB": p.oreb + p.dreb,
                    "OREB": p.oreb,
                    "DREB": p.dreb,
                    "TO": p.turnovers,
                    "STL": p.steals,
                    "BLK": p.blocks,
                    "2PT": f"{p.two_ptm}-{p.two_pta}",
                    "3PT": f"{p.three_ptm}-{p.three_pta}",
                    "FT": f"{p.ftm}-{p.fta}",
                    "+/-": p.plus_minus,
                    "PF": p.pf
                }
                box_data.append(row)

            df_box = pd.DataFrame(box_data)
            st.dataframe(df_box, use_container_width=True)
    else:
        st.info("No finished games yet.")
