import streamlit as st

def run_game(current_game):
    """
    Handles the in-game UI and stat tracking for the given game.
    Updates player stats in st.session_state when the game ends.
    """
    st.info(f"Game '{current_game.name}' is currently running.")
    st.markdown("### Players in this game:")

    # Display players
    for p in current_game.players:
        st.write(f"👤 {p.name}")

    # Initialize in-game stats if not already
    if "game_stats" not in st.session_state:
        st.session_state.game_stats = {
            p.name: {
                "2PTM": 0, "2PTA": 0,
                "3PTM": 0, "3PTA": 0,
                "FTM": 0, "FTA": 0,
                "AST": 0, "OREB": 0, "DREB": 0,
                "TO": 0, "STL": 0, "BLK": 0,
                "MIN": 0, "PF": 0, "+/-": 0
            } for p in current_game.players
        }

    st.markdown("### Record Stats")
    for p in current_game.players:
        st.markdown(f"**{p.name}**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("2PT Made", key=f"2ptm_{p.name}"):
                st.session_state.game_stats[p.name]["2PTM"] += 1
                st.session_state.game_stats[p.name]["2PTA"] += 1
                st.rerun()
            if st.button("2PT Attempt", key=f"2pta_{p.name}"):
                st.session_state.game_stats[p.name]["2PTA"] += 1
                st.rerun()
        with col2:
            if st.button("3PT Made", key=f"3ptm_{p.name}"):
                st.session_state.game_stats[p.name]["3PTM"] += 1
                st.session_state.game_stats[p.name]["3PTA"] += 1
                st.rerun()
            if st.button("3PT Attempt", key=f"3pta_{p.name}"):
                st.session_state.game_stats[p.name]["3PTA"] += 1
                st.rerun()
        with col3:
            if st.button("FT Made", key=f"ftm_{p.name}"):
                st.session_state.game_stats[p.name]["FTM"] += 1
                st.session_state.game_stats[p.name]["FTA"] += 1
                st.rerun()
            if st.button("FT Attempt", key=f"fta_{p.name}"):
                st.session_state.game_stats[p.name]["FTA"] += 1
                st.rerun()
        with col4:
            if st.button("AST", key=f"ast_{p.name}"):
                st.session_state.game_stats[p.name]["AST"] += 1
                st.rerun()
            if st.button("TO", key=f"to_{p.name}"):
                st.session_state.game_stats[p.name]["TO"] += 1
                st.rerun()

    # End Game with confirmation
    if not st.session_state.confirm_end_game:
        if st.button("End Game"):
            st.session_state.confirm_end_game = True
            st.rerun()
    else:
        st.warning("Are you sure you want to end this game?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, End Game"):
                # Apply stats to player objects
                for p in current_game.players:
                    stats = st.session_state.game_stats[p.name]
                    p.two_ptm += stats["2PTM"]
                    p.two_pta += stats["2PTA"]
                    p.three_ptm += stats["3PTM"]
                    p.three_pta += stats["3PTA"]
                    p.ftm += stats["FTM"]
                    p.fta += stats["FTA"]
                    p.assists += stats["AST"]
                    p.oreb += stats["OREB"]
                    p.dreb += stats["DREB"]
                    p.turnovers += stats["TO"]
                    p.steals += stats["STL"]
                    p.blocks += stats["BLK"]
                    p.mins += stats["MIN"]
                    p.pf += stats["PF"]
                    p.plus_minus += stats["+/-"]
                    p.games += 1

                st.session_state.games.append(current_game)
                from main import save_games, save_players  # import here to avoid circular import
                save_games(st.session_state.games)
                save_players(st.session_state.players)
                st.session_state.current_game = None
                st.session_state.confirm_end_game = False
                st.session_state.game_stats = {}
                st.success("Game ended and stats recorded.")
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_end_game = False
                st.rerun()
