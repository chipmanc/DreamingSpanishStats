"""Basic Stats Component."""

from datetime import UTC, datetime

import streamlit as st
from pandas import DataFrame


def basic_stats(df: DataFrame, initial_time: int) -> None:
    """Show basic statistics.

    Args:
        df (DataFrame): DataFrame containing language data from Dreaming Spanish
        initial_time (int): The initial amount of time that the user has watched before
                            DS

    """
    current_streak = df["current_streak"].iloc[-1] if df["streak"].iloc[-1] == 1 else 0
    avg_seconds_per_day = df["seconds"].mean()

    with st.container(border=True):
        st.subheader("Basic Stats")

        # Current stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            today = datetime.now(tz=UTC).date()
            today_df = df[df["date"].dt.date == today]
            minutes_watched_today = today_df["seconds"].sum() / 60
            st.metric("Minutes Watched Today", f"{minutes_watched_today:.1f}")
        with col2:
            st.metric("Current Streak", f"{current_streak} days")
        with col3:
            if initial_time > 0:
                st.metric(
                    "Total Hours Watched",
                    f"{df['cumulative_hours'].iloc[-1]:.1f}",
                    f"including {initial_time / 60:.0f} min initial time",
                )
            else:
                st.metric(
                    "Total Hours Watched",
                    f"{df['cumulative_hours'].iloc[-1]:.1f}",
                )
        with col4:
            st.metric("Average Minutes/Day", f"{(avg_seconds_per_day / 60):.1f}")
