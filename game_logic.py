import streamlit as st

def run_game(current_game, save_games_func):
    """
    Handles the in-game UI and stat tracking for the given game.
    Updates player stats in st.session_state when the game ends.
    """
    st.info(f"Game '{st.session_state.current_game.name}' is currently running.")
    st.markdown("### Players in this game:")
    for p in st.session_state.current_game.players:
        st.write(f"👤 {p.name}")

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
                st.session_state.current_game.finished = True
                st.session_state.games.append(st.session_state.current_game)
                save_games_func(st.session_state.games)
                st.session_state.current_game = None
                st.session_state.confirm_end_game = False
                st.success("Game ended.")
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_end_game = False
                st.rerun()
