"""Best Days component."""

import pandas as pd
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
        best_days_list = get_best_days(result)
        if not best_days_list:
            st.write("Not enough data to show top 5 days.")
        else:
            df = pd.DataFrame(best_days_list)
            df["time_spent"] = df["timeSeconds"].apply(
                lambda x: (f"{int(x // 3600):02d} hours {int((x % 3600) // 60):02d} "
                           f"minutes {int(x % 60):02d} seconds"),
            )
            df["Time in Minutes"] = (df["timeSeconds"] / 60).round(2)
            df = df.rename(columns={"date": "Day", "time_spent": "Time Spent"})
            df = df[["Day", "Time Spent", "Time in Minutes"]]
            st.dataframe(df, hide_index=True)
