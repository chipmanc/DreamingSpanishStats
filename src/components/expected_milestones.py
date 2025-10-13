"""Expected Milestones component."""

from datetime import timedelta

import streamlit as st
from pandas import DataFrame

from src import constants


def expected_milestones(df: DataFrame) -> None:
    """Show expected milestones.

    Args:
        df (DataFrame): DataFrame containing language data from Dreaming Spanish

    """
    avg_seconds_per_day = df["seconds"].mean()
    current_7day_avg = df["7day_avg"].iloc[-1]
    current_30day_avg = df["30day_avg"].iloc[-1]

    with st.container(border=True):
        current_hours = df["cumulative_hours"].iloc[-1]
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Expected Milestone Dates")

            header_cols = st.columns([2, 3, 3, 3])
            with header_cols[0]:
                st.write("**Milestone**")
            with header_cols[1]:
                st.write("**Overall avg**")
            with header_cols[2]:
                st.write("**7-day avg**")
            with header_cols[3]:
                st.write("**30-day avg**")

            for milestone in constants.MILESTONES:
                if current_hours < milestone:
                    days_to_milestone = (
                        (milestone - current_hours) * 3600
                    ) / avg_seconds_per_day
                    days_to_milestone_7day = (
                        ((milestone - current_hours) * 3600) / current_7day_avg
                        if current_7day_avg > 0
                        else float("inf")
                    )
                    days_to_milestone_30day = (
                        ((milestone - current_hours) * 3600) / current_30day_avg
                        if current_30day_avg > 0
                        else float("inf")
                    )

                    predicted_date = df["date"].iloc[-1] + timedelta(
                        days=days_to_milestone,
                    )
                    predicted_date_7day = df["date"].iloc[-1] + timedelta(
                        days=days_to_milestone_7day,
                    )
                    predicted_date_30day = df["date"].iloc[-1] + timedelta(
                        days=days_to_milestone_30day,
                    )

                    cols = st.columns([2, 3, 3, 3])
                    with cols[0]:
                        st.write(f"🗓️ {milestone}h")
                    with cols[1]:
                        st.write(
                            f"{predicted_date.strftime('%Y-%m-%d')} "
                            f"({days_to_milestone:.0f}d)",
                        )
                    with cols[2]:
                        st.write(
                            f"{predicted_date_7day.strftime('%Y-%m-%d')} "
                            f"({days_to_milestone_7day:.0f}d)",
                        )
                    with cols[3]:
                        st.write(
                            f"{predicted_date_30day.strftime('%Y-%m-%d')} "
                            f"({days_to_milestone_30day:.0f}d)",
                        )
                else:
                    cols = st.columns([2, 9])
                    with cols[0]:
                        st.write(f"🗓️ {milestone}h")
                    with cols[1]:
                        st.write("✅ Already achieved!")

        with col2:
            st.subheader("Progress Overview")
            for milestone in constants.MILESTONES:
                if current_hours < milestone:
                    percentage = (current_hours / milestone) * 100
                    st.write(f"Progress to {milestone} hours: {percentage:.1f}%")
                    st.progress(percentage / 100)
