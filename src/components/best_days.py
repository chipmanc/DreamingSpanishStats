"""Best Days component."""

import streamlit as st

from src.model import AnalysisResult
from src.utils import get_best_days


def best_days(result: AnalysisResult) -> None:
    """Show best days.

    Args:
        result (AnalysisResult): Result of Data Analysis for the app

    """
    with st.container(border=True):
        st.subheader("Best Days")
        best_days = get_best_days(result, num_days=5)
        if not best_days:
            st.write("Not enough data to show top 5 days.")
        else:
            for day in best_days:
                hours, remainder = divmod(day["timeSeconds"], 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = (
                    f"{int(hours):02d} hours {int(minutes):02d} minutes "
                    f"{int(seconds):02d} seconds"
                )
                st.write(f"**{day['date']}**: {time_str}")
