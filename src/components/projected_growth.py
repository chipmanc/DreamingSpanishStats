"""Projected Growth Component."""

import plotly.graph_objects as go
import streamlit as st
from pandas import DataFrame

from src import constants
from src.utils import generate_future_predictions


def projected_growth(df: DataFrame) -> None:
    """Show a graph of projected growth over time.

    Args:
        df (DataFrame): DataFrame containing language data from Dreaming Spanish

    """
    avg_seconds_per_day = df["seconds"].mean()
    with st.container(border=True):
        st.subheader("Projected Growth")

        # Calculate target milestone
        current_hours = df["cumulative_hours"].iloc[-1]
        upcoming_milestones = [m for m in constants.MILESTONES if m > current_hours][:3]
        target_milestone = (
            upcoming_milestones[2]
            if len(upcoming_milestones) >= constants.UPCOMING_MILESTONES_CAP
            else constants.MILESTONES[-1]
        )

        # Calculate current moving averages for predictions
        current_7day_avg = df["7day_avg"].iloc[-1]
        current_30day_avg = df["30day_avg"].iloc[-1]

        # Generate predictions up to target milestone
        predicted_df = generate_future_predictions(
            df,
            avg_seconds_per_day,
            target_milestone,
        )
        predicted_df_7day = generate_future_predictions(
            df,
            current_7day_avg,
            target_milestone,
        )
        predicted_df_30day = generate_future_predictions(
            df,
            current_30day_avg,
            target_milestone,
        )

        # Create milestone prediction visualization
        fig_prediction = go.Figure()

        # Add historical data
        fig_prediction.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["cumulative_hours"],
                name="Historical Data",
                line={"color": constants.COLOUR_PALETTE["primary"]},
                mode="lines+markers",
            ),
        )

        # Add predicted data - Overall Average
        fig_prediction.add_trace(
            go.Scatter(
                x=predicted_df["date"],
                y=predicted_df["cumulative_hours"],
                name="Predicted (Overall Avg)",
                line={
                    "color": f"{constants.COLOUR_PALETTE['primary']}",
                    "dash": "dash",
                },
                mode="lines",
                opacity=0.5,
            ),
        )

        # Add predicted data - 7-Day Average
        fig_prediction.add_trace(
            go.Scatter(
                x=predicted_df_7day["date"],
                y=predicted_df_7day["cumulative_hours"],
                name="Predicted (7-Day Avg)",
                line={"color": constants.COLOUR_PALETTE["7day_avg"], "dash": "dot"},
                mode="lines",
                opacity=0.5,
            ),
        )

        # Add predicted data - 30-Day Average
        fig_prediction.add_trace(
            go.Scatter(
                x=predicted_df_30day["date"],
                y=predicted_df_30day["cumulative_hours"],
                name="Predicted (30-Day Avg)",
                line={"color": constants.COLOUR_PALETTE["30day_avg"], "dash": "dot"},
                mode="lines",
                opacity=0.5,
            ),
        )

        for milestone in constants.MILESTONES:
            color = constants.COLOUR_PALETTE[str(milestone)]
            if milestone <= df["cumulative_hours"].max():
                milestone_date = df[df["cumulative_hours"] >= milestone]["date"].iloc[0]
            elif milestone <= predicted_df["cumulative_hours"].max():
                milestone_date = predicted_df[
                    predicted_df["cumulative_hours"] >= milestone
                ]["date"].iloc[0]
            else:
                continue

            fig_prediction.add_shape(
                type="line",
                x0=df["date"].min(),
                x1=milestone_date,
                y0=milestone,
                y1=milestone,
                line={"color": color, "dash": "dash", "width": 1},
            )

            fig_prediction.add_annotation(
                x=df["date"].min(),
                y=milestone,
                text=f"{milestone} Hours",
                showarrow=False,
                xshift=-5,
                xanchor="right",
                font={"color": color},
            )

            fig_prediction.add_annotation(
                x=milestone_date,
                y=milestone,
                text=milestone_date.strftime("%Y-%m-%d"),
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowcolor=color,
                font={"color": color, "size": 10},
                xanchor="left",
                yanchor="bottom",
            )

        # Find the next 3 upcoming milestones and their dates
        current_hours = df["cumulative_hours"].iloc[-1]
        upcoming_milestones = [m for m in constants.MILESTONES if m > current_hours][:3]

        # Get the date for the third upcoming milestone (or last if < 3 remain)
        target_milestone = upcoming_milestones[min(2, len(upcoming_milestones) - 1)]

        fig_prediction.update_layout(
            xaxis_title="Date",
            yaxis_title="Cumulative Hours",
            showlegend=True,
            height=600,
            margin={"l": 20, "r": 20, "t": 10, "b": 0},
            yaxis={
                "autorange": True,
            },
            xaxis={
                "autorange": True,
            },
        )

        st.plotly_chart(fig_prediction, use_container_width=True)
