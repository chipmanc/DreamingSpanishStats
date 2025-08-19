"""Progress Bar component."""

from datetime import UTC, datetime

import streamlit as st
from pandas import DataFrame

from src.model import UserInfo


def progress_bar(df: DataFrame, user_info: UserInfo) -> None:
    """Show daily goal progress.

    Args:
        df (DataFrame): DataFrame containing language data from Dreaming Spanish
        user_info (UserInfo): User information taken from the API

    """
    with st.container(border=True):
        st.subheader("Daily Goal Progress")

        today = datetime.now(tz=UTC).date()
        today_df = df[df["date"].dt.date == today]
        seconds_watched_today = today_df["seconds"].sum()

        progress_val = seconds_watched_today / user_info.daily_goal_seconds
        status_text = (
            f"{(seconds_watched_today // 60):.0f}"
            f" / {(user_info.daily_goal_seconds // 60):.0f} mins"
            f" ({(progress_val * 100):.2f}%)"
        )

        st.progress(
            min(progress_val, 1.0),
            text=status_text,
        )
