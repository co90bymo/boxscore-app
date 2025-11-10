import streamlit as st
import pandas as pd

def run_game(current_game, save_games_func, save_players):
    """
    Handles in-game stat tracking.
    Stats are stored per game; player totals are calculated from games.json.
    """
    st.info(f"Game '{current_game.name}' is currently running.")

    columns = ["PLAYER", "2PT MAKE", "2PT MISS", "3PT MAKE", "3PT MISS",
               "FT MAKE", "FT MISS", "OREB", "DREB", "AST", "TO",
               "STL", "BLK", "+/-", "PF", "MIN"]

    player_names = [p.name for p in current_game.players]

    # Initialize session state for stats table
    if "stats_state" not in st.session_state or set(st.session_state.stats_state.keys()) != set(player_names):
        st.session_state.stats_state = {p.name: {col: 0 for col in columns if col != "PLAYER"} for p in current_game.players}

    if "selected_stat" not in st.session_state:
        st.session_state.selected_stat = None

    # Buttons to select stat
    st.markdown("### Select a stat to edit:")
    stat_cols = columns[1:]
    buttons_per_row = 5
    for i in range(0, len(stat_cols), buttons_per_row):
        cols = st.columns(buttons_per_row)
        for j, stat in enumerate(stat_cols[i:i+buttons_per_row]):
            if cols[j].button(stat):
                st.session_state.selected_stat = stat

    # Increment/decrement buttons for stats
    if st.session_state.selected_stat and st.session_state.selected_stat not in ["+/-", "PF", "MIN"]:
        st.markdown(f"### Adjust {st.session_state.selected_stat}:")
        for p in current_game.players:
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button(f"{p.name} +", key=f"{p.name}_{st.session_state.selected_stat}_plus"):
                    st.session_state.stats_state[p.name][st.session_state.selected_stat] += 1
            with col2:
                if st.button(f"{p.name} -", key=f"{p.name}_{st.session_state.selected_stat}_minus"):
                    st.session_state.stats_state[p.name][st.session_state.selected_stat] -= 1

    # Input fields for +/- , PF, MIN
    st.markdown("### Input values for +/- , PF, MIN:")
    for p in current_game.players:
        col_player, col_pm, col_pf, col_min = st.columns([2,1,1,1])
        col_player.write(f"👤 {p.name}")
        st.session_state.stats_state[p.name]["+/-"] = col_pm.number_input("+/-", value=st.session_state.stats_state[p.name]["+/-"], step=1, key=f"{p.name}_plusminus")
        st.session_state.stats_state[p.name]["PF"] = col_pf.number_input("PF", value=st.session_state.stats_state[p.name]["PF"], step=1, key=f"{p.name}_pf")
        st.session_state.stats_state[p.name]["MIN"] = col_min.number_input("MIN", value=st.session_state.stats_state[p.name]["MIN"], step=1, key=f"{p.name}_min")

    # Display live table
    data = []
    for p in current_game.players:
        row = [p.name] + [st.session_state.stats_state[p.name][col] for col in columns[1:]]
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    st.markdown("### Players in this game:")
    st.dataframe(df, use_container_width=True)

    # Confirm end game
    if "confirm_end_game" not in st.session_state:
        st.session_state.confirm_end_game = False

    if not st.session_state.confirm_end_game:
        if st.button("End Game"):
            st.session_state.confirm_end_game = True
    else:
        st.warning("Are you sure you want to end this game?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, End Game"):
                # Save game stats (per game only)
                for p in current_game.players:
                    stats = st.session_state.stats_state[p.name]
                    p.min = stats["MIN"]
                    p.assists = stats["AST"]
                    p.oreb = stats["OREB"]
                    p.dreb = stats["DREB"]
                    p.turnovers = stats["TO"]
                    p.steals = stats["STL"]
                    p.blocks = stats["BLK"]
                    p.two_ptm = stats["2PT MAKE"]
                    p.two_pta = stats["2PT MAKE"] + stats["2PT MISS"]
                    p.three_ptm = stats["3PT MAKE"]
                    p.three_pta = stats["3PT MAKE"] + stats["3PT MISS"]
                    p.ftm = stats["FT MAKE"]
                    p.fta = stats["FT MAKE"] + stats["FT MISS"]
                    p.plus_minus = stats["+/-"]
                    p.pf = stats["PF"]
                    p.games = 1  # per-game record

                current_game.finished = True
                st.session_state.games.append(current_game)
                save_games_func(st.session_state.games)

                # Clear session state
                st.session_state.current_game = None
                st.session_state.stats_state = {}
                st.session_state.selected_stat = None
                st.session_state.confirm_end_game = False

                st.success("Game ended and stats saved!")
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_end_game = False
