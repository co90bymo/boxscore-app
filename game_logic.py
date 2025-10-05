import streamlit as st
import pandas as pd

def run_game(current_game, save_games_func):
    """
    Handles the in-game UI and stat tracking for the given game.
    Updates player stats in st.session_state when the game ends.
    """
    st.info(f"Game '{current_game.name}' is currently running.")

    # Columns for stats
    columns = ["PLAYER", "2PT MAKE", "2PT MISS", "3PT MAKE", "3PT MISS",
               "FT MAKE", "FT MISS", "OREB", "DREB", "AST", "TO",
               "STL", "BLK", "+/-", "PF", "MIN"]

    # Initialize session state for stats table
    if "stats_state" not in st.session_state:
        st.session_state.stats_state = {
            p.name: {col: 0 for col in columns if col != "PLAYER"} for p in current_game.players
        }

    if "selected_stat" not in st.session_state:
        st.session_state.selected_stat = None

    # Buttons for selecting which stat to edit (grid layout)
    st.markdown("### Select a stat to edit:")
    stat_cols = columns[1:]  # exclude PLAYER column
    buttons_per_row = 5  # adjust based on space

    for i in range(0, len(stat_cols), buttons_per_row):
        cols = st.columns(buttons_per_row)
        for j, stat in enumerate(stat_cols[i:i+buttons_per_row]):
            if cols[j].button(stat):
                st.session_state.selected_stat = stat

    # Display per-player controls if a stat is selected
    if st.session_state.selected_stat:
        st.markdown(f"### Adjust {st.session_state.selected_stat}:")
        for p in current_game.players:
            # For +/- , PF, and MIN: use number_input
            if st.session_state.selected_stat in ["+/-", "PF", "MIN"]:
                st.session_state.stats_state[p.name][st.session_state.selected_stat] = st.number_input(
                    f"{p.name} {st.session_state.selected_stat}",
                    min_value=0,
                    value=st.session_state.stats_state[p.name][st.session_state.selected_stat],
                    key=f"{p.name}_{st.session_state.selected_stat}_input"
                )
            else:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"{p.name} +", key=f"{p.name}_{st.session_state.selected_stat}_plus"):
                        st.session_state.stats_state[p.name][st.session_state.selected_stat] += 1
                with col2:
                    if st.button(f"{p.name} -", key=f"{p.name}_{st.session_state.selected_stat}_minus"):
                        st.session_state.stats_state[p.name][st.session_state.selected_stat] = max(
                            0, st.session_state.stats_state[p.name][st.session_state.selected_stat] - 1
                        )

    # Prepare data for display using the latest stats_state
    data = []
    for p in current_game.players:
        row = [p.name] + [st.session_state.stats_state[p.name][col] for col in columns[1:]]
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    st.markdown("### Players in this game:")
    st.dataframe(df, use_container_width=True)

    # End Game with confirmation
    if not st.session_state.confirm_end_game:
        if st.button("End Game"):
            st.session_state.confirm_end_game = True
    else:
        st.warning("Are you sure you want to end this game?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, End Game"):
                # Apply stats to Player objects
                for p in current_game.players:
                    stats = st.session_state.stats_state[p.name]
                    p.two_ptm += stats["2PT MAKE"]
                    p.two_pta += stats["2PT MAKE"] + stats["2PT MISS"]
                    p.three_ptm += stats["3PT MAKE"]
                    p.three_pta += stats["3PT MAKE"] + stats["3PT MISS"]
                    p.ftm += stats["FT MAKE"]
                    p.fta += stats["FT MAKE"] + stats["FT MISS"]
                    p.oreb += stats["OREB"]
                    p.dreb += stats["DREB"]
                    p.assists += stats["AST"]
                    p.turnovers += stats["TO"]
                    p.steals += stats["STL"]
                    p.blocks += stats["BLK"]
                    p.plus_minus += stats["+/-"]
                    p.pf += stats["PF"]
                    p.mins += stats["MIN"]
                    p.games += 1

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
