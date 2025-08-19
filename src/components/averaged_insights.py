"""Averaged Insights component."""

import streamlit as st
from pandas import DataFrame

from src import constants


def averaged_insights(df: DataFrame) -> None:
    """Show averaged insights.

    Args:
        df (DataFrame): DataFrame containing language data from Dreaming Spanish

    """
    avg_seconds_per_day = df["seconds"].mean()

    with st.container(border=True):
        st.subheader("Averaged Insights")

        tab_7days, tab_30days, tab_all_time = st.tabs(
            [
                "7 days",
                "30 days",
                "All Time",
            ],
        )

        with tab_7days:
            col1, col2 = st.columns(2)

            with col1:
                # Time comparisons
                last_7_total = df.tail(7)["seconds"].sum()
                previous_7_total = (
                    df.iloc[-14:-7]["seconds"].sum() if len(df) >= 14 else 0  # noqa: PLR2004
                )
                week_change = last_7_total - previous_7_total
                st.metric(
                    "Last 7 Days Total",
                    f"{(last_7_total / 60):.0f} min",
                    f"{(week_change / 60):+.0f} min vs previous week",
                )

            with col2:
                weekly_avg = df.tail(7)["seconds"].mean()
                st.metric(
                    "7-Day Average",
                    f"{(weekly_avg / 60):.1f} min/day",
                    f"{((weekly_avg - avg_seconds_per_day) / 60):+.1f} vs overall",
                )

        with tab_30days:
            col1, col2 = st.columns(2)

            with col1:
                # Time comparisons
                last_30_total = df.tail(30)["seconds"].sum()
                previous_30_total = (
                    df.iloc[-60:-30]["seconds"].sum() if len(df) >= 60 else 0  # noqa: PLR2004
                )
                month_change = last_30_total - previous_30_total
                st.metric(
                    "Last 30 Days Total",
                    f"{(last_30_total / 60):.0f} min",
                    f"{(month_change / 60):+.0f} min vs previous 30 days",
                )

            with col2:
                monthly_avg = df.tail(30)["seconds"].mean()
                st.metric(
                    "30-Day Average",
                    f"{(monthly_avg / 60):.1f} min/day",
                    f"{((monthly_avg - avg_seconds_per_day) / 60):+.1f} vs overall",
                )

        with tab_all_time:
            col1, col2 = st.columns(2)

            with col1:
                # Time comparisons
                all_time_total = df["seconds"].sum()
                milestone_count = sum(
                    m <= df["cumulative_hours"].iloc[-1] for m in constants.MILESTONES
                )
                st.metric(
                    "All Time Total",
                    f"{(all_time_total / 60):.0f} min",
                    f"{milestone_count} milestones reached",
                    delta_color="off",
                )

            with col2:
                all_time_avg = df["seconds"].mean()
                st.metric(
                    "All Time Average",
                    f"{(all_time_avg / 60):.1f} min/day",
                )
