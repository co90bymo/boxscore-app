import streamlit as st
import pandas as pd
import json
import os
from game_logic import run_game  # import the extracted function
from time_arithmetic import time_str_to_seconds, seconds_to_time_str, add_times

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
    def __init__(self, name: str, games=0, min=0, assists=0, dreb=0, oreb=0, turnovers=0, steals=0, blocks=0,
                 two_pta=0, two_ptm=0, three_pta=0, three_ptm=0, fta=0, ftm=0, plus_minus=0, pf=0):
        self.games = games
        self.name = name
        self.min = min
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
            "MIN": self.min,
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
                min=data.get("MIN", 0),
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

def fmt(val):
        """Formats numbers cleanly."""
        if isinstance(val, (int, float)):
            if val == int(val):
                return int(val)
            else:
                return round(val, 1)
        return val

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
                value = p.get(stat, 0)
                
                # Special handling for 'MIN' using time helper
                if stat == "MIN":
                    if isinstance(value, str):
                        value = time_str_to_seconds(value)  # convert "MM:SS" to seconds
                    elif isinstance(value, (int, float)):
                        value = value * 60  # convert minutes to seconds

                total += value      

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

    if st.session_state.players:
        player_data = []

        # Determine total games played (only finished games count)
        total_games_played = sum(1 for g in st.session_state.games if g.finished)
        if total_games_played == 0:
            total_games_played = 1  # prevent division by zero

        # Initialize team totals
        team_totals = {
            "MIN": 0, "PTS": 0, "AST": 0, "REB": 0, "OREB": 0, "DREB": 0,
            "TO": 0, "STL": 0, "BLK": 0, "2PTM": 0, "2PTA": 0,
            "3PTM": 0, "3PTA": 0, "FTM": 0, "FTA": 0, "+/-": 0, "PF": 0
        }

        # Precompute total team minutes for tPIE
        total_team_min = sum(get_player_total_stat(p.name, "MIN") for p in st.session_state.players)
        if total_team_min == 0:
            total_team_min = 1  # prevent division by zero

        for p in st.session_state.players:
            d = p.to_dict()
            games = get_player_total_stat(p.name, "GAMES")
            if games == 0:
                continue

            # Determine scale for this player
            scale = 1 if view_mode == "Total" else games

            # Shooting stats
            two_ptm = get_player_total_stat(p.name, "2PTM") / scale
            two_pta = get_player_total_stat(p.name, "2PTA") / scale
            three_ptm = get_player_total_stat(p.name, "3PTM") / scale
            three_pta = get_player_total_stat(p.name, "3PTA") / scale
            ftm = get_player_total_stat(p.name, "FTM") / scale
            fta = get_player_total_stat(p.name, "FTA") / scale

            # Derived stats
            pts = (two_ptm * 2) + (three_ptm * 3) + ftm
            oreb = get_player_total_stat(p.name, "OREB") / scale
            dreb = get_player_total_stat(p.name, "DREB") / scale
            reb = oreb + dreb

            # Percentages
            two_pt_pct = (two_ptm / two_pta * 100) if two_pta > 0 else 0
            three_pt_pct = (three_ptm / three_pta * 100) if three_pta > 0 else 0
            fg_makes = two_ptm + three_ptm
            fg_attempts = two_pta + three_pta
            fg_pct = (fg_makes / fg_attempts * 100) if fg_attempts > 0 else 0
            ft_pct = (ftm / fta * 100) if fta > 0 else 0

            # --- Handle MIN as MM:SS ---
            min_seconds = get_player_total_stat(p.name, "MIN")
            if view_mode == "Per Game":
                min_seconds = round(min_seconds / scale)
            min_display = seconds_to_time_str(int(min_seconds))

            # Player row
            ordered_d = {
                "PLAYER": d.get("PLAYER", ""),
                "GAMES": fmt(1 if view_mode == "Per Game" else games),
                "MIN": min_display,
                "PTS": fmt(pts),
                "AST": fmt(get_player_total_stat(p.name, "AST") / scale),
                "REB": fmt(reb),
                "OREB": fmt(oreb),
                "DREB": fmt(dreb),
                "TO": fmt(get_player_total_stat(p.name, "TO") / scale),
                "STL": fmt(get_player_total_stat(p.name, "STL") / scale),
                "BLK": fmt(get_player_total_stat(p.name, "BLK") / scale),
                "FG": f"{fmt(fg_makes)}-{fmt(fg_attempts)}",
                "FG%": fmt(fg_pct),
                "2PT": f"{fmt(two_ptm)}-{fmt(two_pta)}",
                "2FG%": fmt(two_pt_pct),
                "3PT": f"{fmt(three_ptm)}-{fmt(three_pta)}",
                "3FG%": fmt(three_pt_pct),
                "FT": f"{fmt(ftm)}-{fmt(fta)}",
                "FT%": fmt(ft_pct),
                "+/-": fmt(get_player_total_stat(p.name, "+/-") / scale),
                "PF": fmt(get_player_total_stat(p.name, "PF") / scale),
            }

            player_data.append(ordered_d)

            scale = 1 if view_mode == "Total" else total_games_played

            # --- Handle MIN as MM:SS ---
            min_seconds = get_player_total_stat(p.name, "MIN")
            if view_mode == "Per Game":
                min_seconds = round(min_seconds / total_games_played)
                print("scale:")
                print(scale)

            # Accumulate team totals (raw sums)
            team_totals["MIN"] += min_seconds
            team_totals["AST"] += get_player_total_stat(p.name, "AST")
            team_totals["OREB"] += get_player_total_stat(p.name, "OREB")
            team_totals["DREB"] += get_player_total_stat(p.name, "DREB")
            team_totals["TO"] += get_player_total_stat(p.name, "TO") 
            team_totals["STL"] += get_player_total_stat(p.name, "STL") 
            team_totals["BLK"] += get_player_total_stat(p.name, "BLK")
            team_totals["2PTM"] += get_player_total_stat(p.name, "2PTM")
            team_totals["2PTA"] += get_player_total_stat(p.name, "2PTA")
            team_totals["3PTM"] += get_player_total_stat(p.name, "3PTM")
            team_totals["3PTA"] += get_player_total_stat(p.name, "3PTA")
            team_totals["FTM"] += get_player_total_stat(p.name, "FTM")
            team_totals["FTA"] += get_player_total_stat(p.name, "FTA")
            team_totals["+/-"] += get_player_total_stat(p.name, "+/-") 
            team_totals["PF"] += get_player_total_stat(p.name, "PF")

        scale = 1 if view_mode == "Total" else total_games_played

        # --- Team totals row ---
        # Shooting stats
        two_ptm = team_totals["2PTM"] / scale
        two_pta = team_totals["2PTA"] / scale
        three_ptm = team_totals["3PTM"] / scale
        three_pta = team_totals["3PTA"] / scale
        ftm = team_totals["FTM"] / scale
        fta = team_totals["FTA"] / scale

        # Derived stats
        pts = (two_ptm * 2) + (three_ptm * 3) + ftm
        oreb = team_totals["OREB"] / scale
        dreb = team_totals["DREB"] / scale
        reb = oreb + dreb

        # Percentages
        two_pt_pct = (two_ptm / two_pta * 100) if two_pta > 0 else 0
        three_pt_pct = (three_ptm / three_pta * 100) if three_pta > 0 else 0
        fg_makes = two_ptm + three_ptm
        fg_attempts = two_pta + three_pta
        fg_pct = (fg_makes / fg_attempts * 100) if fg_attempts > 0 else 0
        ft_pct = (ftm / fta * 100) if fta > 0 else 0

        print((team_totals["MIN"]))
        team_row = {
            "PLAYER": "👥 TEAM TOTAL",
            "GAMES": fmt(1 if view_mode == "Per Game" else total_games_played),
            "MIN": fmt(seconds_to_time_str(team_totals["MIN"])),
            "PTS": fmt(pts),
            "AST": fmt(team_totals["AST"] / scale),
            "REB": fmt(reb),
            "OREB": fmt(oreb),
            "DREB": fmt(dreb),
            "TO": fmt(team_totals["TO"] / scale),
            "STL": fmt(team_totals["STL"] / scale),
            "BLK": fmt(team_totals["BLK"] / scale),
            "FG": f"{fmt(fg_makes)}-{fmt(fg_attempts)}",
            "FG%": fmt(fg_pct),
            "2PT": f"{fmt(two_ptm)}-{fmt(two_pta)}",
            "2FG%": fmt(two_pt_pct),
            "3PT": f"{fmt(three_ptm)}-{fmt(three_pta)}",
            "3FG%": fmt(three_pt_pct),
            "FT": f"{fmt(ftm)}-{fmt(fta)}",
            "FT%": fmt(ft_pct),
            "+/-": fmt(team_totals["+/-"] / scale),
            "PF": fmt(team_totals["PF"] / scale),
        }

        player_data.append(team_row)

        # --- tPIE calculation for each player ---
        for ordered_d in player_data:
            if ordered_d["PLAYER"] == "👥 TEAM TOTAL":
                continue  # skip team row

            # Extract numeric values from row
            pts = float(ordered_d["PTS"])
            fg_makes = float(ordered_d["2PT"].split("-")[0]) + float(ordered_d["3PT"].split("-")[0])
            ftm = float(ordered_d["FT"].split("-")[0])
            fta = float(ordered_d["FT"].split("-")[1])
            fg_attempts = float(ordered_d["2PT"].split("-")[1]) + float(ordered_d["3PT"].split("-")[1])
            dreb = float(ordered_d["DREB"])
            oreb = float(ordered_d["OREB"])
            ast = float(ordered_d["AST"])
            stl = float(ordered_d["STL"])
            blk = float(ordered_d["BLK"])
            pf = float(ordered_d["PF"])
            to = float(ordered_d["TO"])

            # player_minutes from MIN string (MM:SS)
            min_parts = ordered_d["MIN"].split(":")
            player_minutes = int(min_parts[0]) * 60 + int(min_parts[1])

            tpie_minutes = (player_minutes / team_totals["MIN"]) * 100

            player_total = pts + fg_makes + ftm - fg_attempts - fta + dreb + (0.5 * oreb) + ast + stl + (0.5 * blk) - pf - to
            team_total_points = team_totals["2PTM"]*2 + team_totals["3PTM"]*3 + team_totals["FTM"]
            team_test_total = (
                team_total_points + team_totals["2PTM"] + team_totals["3PTM"] + team_totals["FTM"]
                - team_totals["2PTA"] - team_totals["3PTA"] - team_totals["FTA"]
                + team_totals["DREB"] + (0.5 * team_totals["OREB"]) + team_totals["AST"] + team_totals["STL"]
                + (0.5 * team_totals["BLK"]) - team_totals["PF"] - team_totals["TO"]
            )
            tPIE = player_total / team_test_total
            print("player total and team total:")
            print(player_total)
            print(team_test_total)
            tPIE = tPIE * 100
            ordered_d["tPIE"] = fmt(tPIE)

        st.dataframe(player_data, use_container_width=True)

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

                # Percentages
                two_fg_pct = (p.two_ptm / p.two_pta * 100) if p.two_pta > 0 else 0
                three_fg_pct = (p.three_ptm / p.three_pta * 100) if p.three_pta > 0 else 0
                ft_pct = (p.ftm / p.fta * 100) if p.fta > 0 else 0

                # Combined FG stats
                fg_makes = p.two_ptm + p.three_ptm
                fg_attempts = p.two_pta + p.three_pta
                fg_pct = (fg_makes / fg_attempts * 100) if fg_attempts > 0 else 0

                row = {
                    "PLAYER": p.name,
                    "MIN": p.min,
                    "PTS": pts,
                    "AST": p.assists,
                    "REB": p.oreb + p.dreb,
                    "OREB": p.oreb,
                    "DREB": p.dreb,
                    "TO": p.turnovers,
                    "STL": p.steals,
                    "BLK": p.blocks,
                    "FG": f"{fg_makes}-{fg_attempts}",
                    "FG%": round(fg_pct, 1),
                    "2PT": f"{p.two_ptm}-{p.two_pta}",
                    "2FG%": round(two_fg_pct, 1),
                    "3PT": f"{p.three_ptm}-{p.three_pta}",
                    "3FG%": round(three_fg_pct, 1),
                    "FT": f"{p.ftm}-{p.fta}",
                    "FT%": round(ft_pct, 1),
                    "+/-": p.plus_minus,
                    "PF": p.pf
                }
                box_data.append(row)

            # --- Calculate team totals ---
            total_seconds = sum(time_str_to_seconds(p.min) for p in g.players)
            total_min = seconds_to_time_str(total_seconds)
            total_pts = sum((p.two_ptm * 2) + (p.three_ptm * 3) + p.ftm for p in g.players)
            total_ast = sum(p.assists for p in g.players)
            total_reb = sum(p.oreb + p.dreb for p in g.players)
            total_oreb = sum(p.oreb for p in g.players)
            total_dreb = sum(p.dreb for p in g.players)
            total_to = sum(p.turnovers for p in g.players)
            total_stl = sum(p.steals for p in g.players)
            total_blk = sum(p.blocks for p in g.players)
            total_pf = sum(p.pf for p in g.players)
            total_plus_minus = sum(p.plus_minus for p in g.players)

            total_two_ptm = sum(p.two_ptm for p in g.players)
            total_two_pta = sum(p.two_pta for p in g.players)
            total_three_ptm = sum(p.three_ptm for p in g.players)
            total_three_pta = sum(p.three_pta for p in g.players)
            total_ftm = sum(p.ftm for p in g.players)
            total_fta = sum(p.fta for p in g.players)
            total_fg_makes = total_two_ptm + total_three_ptm
            total_fg_attempts = total_two_pta + total_three_pta

            team_fg_pct = (total_fg_makes / total_fg_attempts * 100) if total_fg_attempts > 0 else 0
            team_2fg_pct = (total_two_ptm / total_two_pta * 100) if total_two_pta > 0 else 0
            team_3fg_pct = (total_three_ptm / total_three_pta * 100) if total_three_pta > 0 else 0
            team_ft_pct = (total_ftm / total_fta * 100) if total_fta > 0 else 0

            team_row = {
                "PLAYER": "👥 TEAM TOTAL",
                "MIN": total_min,
                "PTS": total_pts,
                "AST": total_ast,
                "REB": total_reb,
                "OREB": total_oreb,
                "DREB": total_dreb,
                "TO": total_to,
                "STL": total_stl,
                "BLK": total_blk,
                "FG": f"{total_fg_makes}-{total_fg_attempts}",
                "FG%": fmt(team_fg_pct),
                "2PT": f"{total_two_ptm}-{total_two_pta}",
                "2FG%": fmt(team_2fg_pct),
                "3PT": f"{total_three_ptm}-{total_three_pta}",
                "3FG%": fmt(team_3fg_pct),
                "FT": f"{total_ftm}-{total_fta}",
                "FT%": fmt(team_ft_pct),
                "+/-": total_plus_minus,
                "PF": total_pf
            }

            box_data.append(team_row) 
            # Display DataFrame 
            df_box = pd.DataFrame(box_data) 
            st.dataframe(df_box, use_container_width=True)
    else:
        st.info("No finished games yet.")
