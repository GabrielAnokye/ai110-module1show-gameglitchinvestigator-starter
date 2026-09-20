import random
import streamlit as st

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")


def render_history(panel):
    """Draw the running session log into the given sidebar container.

    Called from every exit path so the table always reflects the guess that
    was just submitted, rather than lagging one rerun behind.
    """
    with panel:
        st.subheader("📊 Game History")

        if not st.session_state.history:
            st.caption("No guesses yet.")
            return

        # "Guess" holds an int for a parsed guess and the raw text for an
        # unparseable one. Arrow rejects that mix, so stringify for display
        # only — st.session_state.history keeps the original values.
        rows = [dict(row, Guess=str(row["Guess"])) for row in st.session_state.history]
        st.dataframe(rows, hide_index=True)

        st.caption(f"Score: {st.session_state.score}")


st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# Reserved here so the log sits under the settings, but filled in later by
# render_history() — after this run's guess has been scored.
history_panel = st.sidebar.container()

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

st.info(
    f"Guess a number between 1 and 100. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(1, 100)
    st.session_state.history = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    render_history(history_panel)
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(
            {
                "Attempt": st.session_state.attempts,
                "Guess": raw_guess,
                "Result": "Invalid",
                "Score": st.session_state.score,
            }
        )
        st.error(err)
    else:
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            # Hot/Cold colour coding. The message text and the outcome itself
            # are untouched — only the Streamlit callout style changes.
            if outcome == "Too High":
                st.error("🔥 " + message)
            elif outcome == "Too Low":
                st.info("❄️ " + message)
            else:
                st.success(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        # Appended after scoring so "Score" is the running total as it stood
        # at the end of this attempt.
        st.session_state.history.append(
            {
                "Attempt": st.session_state.attempts,
                "Guess": guess_int,
                "Result": outcome,
                "Score": st.session_state.score,
            }
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

render_history(history_panel)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
