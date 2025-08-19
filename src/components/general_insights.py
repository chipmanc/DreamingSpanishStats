"""General Insights component."""

import streamlit as st
from pandas import DataFrame

from model import AnalysisResult


def general_insights(df: DataFrame, result: AnalysisResult) -> None:
    """Show general insights.

    Args:
        df (DataFrame): DataFrame containing language data from Dreaming Spanish
        result (AnalysisResult): Result of Data Analysis for the app

    """
    streak_lengths = df[df["streak"] == 1].groupby("streak_group").size()
    current_streak = df["current_streak"].iloc[-1] if df["streak"].iloc[-1] == 1 else 0

    current_goal_streak = result.current_goal_streak
    longest_goal_streak = result.longest_goal_streak

    with st.container(border=True):
        st.subheader("Insights")
        col1, col2, col3 = st.columns(3)

        with col1:
            # Best day stats
            longest_streak = streak_lengths.max() if not streak_lengths.empty else 0
            st.metric("Longest Streak", f"{longest_streak} days")
            # Add consistency metric
            days_watched = (df["seconds"] > 0).sum()
            consistency = (days_watched / len(df)) * 100
            st.metric(
                "Consistency",
                f"{consistency:.1f}%",
                f"{days_watched} of {len(df)} days",
            )

        with col2:
            # Streak information
            st.metric("Current Streak", f"{current_streak} days")

            st.metric(
                "Goal Streak",
                f"{current_goal_streak} days",
                f"Best: {longest_goal_streak} days",
            )

        with col3:
            # Achievement metrics
            avg_streak = streak_lengths.mean() if not streak_lengths.empty else 0
            st.metric(
                "Average Streak",
                f"{avg_streak:.1f} days",
                f"Best: {longest_streak} days",
            )

            goal_rate = (result.goals_reached / result.total_days) * 100
            st.metric(
                "Goal Achievement",
                f"{result.goals_reached} days",
                f"{goal_rate:.1f}% of days",
            )
