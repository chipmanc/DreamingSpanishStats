"""Additional Graphs component."""

from datetime import UTC, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pandas import DataFrame

from src import constants

__all__ = ["additional_graphs"]


def additional_graphs(df: DataFrame) -> None:
    """Show additional graphs.

    Args:
        df (DataFrame): DataFrame containing language data from Dreaming Spanish

    """
    with st.container(border=True):
        st.subheader("Additional Graphs")
        (
            tab_moving_averages,
            tab_daily_breakdown,
            tab_monthly_breakdown,
            tab_yearly_heatmap,
            tab_days_of_week,
        ) = st.tabs(
            [
                "Moving Averages",
                "Daily Breakdown",
                "Monthly Breakdown",
                "Yearly Heatmap",
                "Days of Week",
            ],
        )

        with tab_moving_averages:
            _moving_averages(df)

        with tab_daily_breakdown:
            _daily_breakdown(df)

        with tab_monthly_breakdown:
            _monthly_breakdown(df)

        with tab_yearly_heatmap:
            _yearly_heatmap(df)

        with tab_days_of_week:
            _days_of_week(df)


def _moving_averages(df: DataFrame) -> None:
    moving_avg_fig = go.Figure()

    df["cumulative_avg"] = df["seconds"].expanding().mean()

    moving_avg_fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["seconds"] / 60,
            name="Daily Minutes",
            mode="markers",
            marker={"size": 6},
        ),
    )

    moving_avg_fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["7day_avg"] / 60,
            name="7-day Average",
            line={"color": constants.COLOUR_PALETTE["7day_avg"]},
        ),
    )

    moving_avg_fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["30day_avg"] / 60,
            name="30-day Average",
            line={"color": constants.COLOUR_PALETTE["30day_avg"]},
        ),
    )

    moving_avg_fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["cumulative_avg"] / 60,
            name="Overall Average",
            line={"color": constants.COLOUR_PALETTE["primary"], "dash": "dash"},
        ),
    )

    moving_avg_fig.update_layout(
        title="Daily Minutes with Moving Averages",
        xaxis_title="Date",
        yaxis_title="Minutes",
        height=400,
    )

    moving_avg_fig.update_yaxes(
        dtick=15,
        title="Minutes Watched",
        ticklabelstep=2,
    )

    st.plotly_chart(moving_avg_fig, use_container_width=True)


def _daily_breakdown(df: DataFrame) -> None:
    avg_seconds_per_day = df["seconds"].mean()
    daily_fig = go.Figure()

    daily_fig.add_trace(
        go.Bar(
            x=df["date"],
            y=df["seconds"] / 60,  # Convert to minutes
            name="Daily Minutes",
        ),
    )

    daily_fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=[avg_seconds_per_day / 60] * len(df),  # Convert to minutes
            name="Overall Average",
            line={"color": constants.COLOUR_PALETTE["primary"], "dash": "dash"},
        ),
    )

    daily_fig.update_layout(
        title="Daily Minutes Watched",
        xaxis_title="Date",
        yaxis_title="Minutes",
    )

    daily_fig.update_yaxes(dtick=15, title="Minutes Watched", ticklabelstep=2)
    st.plotly_chart(daily_fig, use_container_width=True)


def _monthly_breakdown(df: DataFrame) -> None:
    df["month_year"] = df["date"].dt.to_period("M")

    last_12_months = sorted(df["month_year"].unique(), reverse=True)[:12][::-1]

    monthly_data = []
    today = datetime.now(tz=UTC).date()

    for month_period in last_12_months:
        month_df = df[df["month_year"] == month_period]

        days_practiced = month_df[month_df["seconds"] > 0]["date"].nunique()
        days_target_met = month_df["goalReached"].sum()

        if month_period.year == today.year and month_period.month == today.month:
            days_in_month = month_df["date"].nunique()
        else:
            days_in_month = month_period.days_in_month

        monthly_data.append(
            {
                "month": month_period.strftime("%Y-%m"),
                "days_practiced": days_practiced,
                "days_target_met": days_target_met,
                "days_in_month": days_in_month,
            },
        )

    monthly_df = pd.DataFrame(monthly_data)

    # Create grouped bar chart
    monthly_fig = go.Figure()

    monthly_fig.add_trace(
        go.Bar(
            x=monthly_df["month"],
            y=monthly_df["days_target_met"],
            name="Days Target Met",
            marker_color=constants.COLOUR_PALETTE["7day_avg"],
        ),
    )

    monthly_fig.add_trace(
        go.Bar(
            x=monthly_df["month"],
            y=monthly_df["days_practiced"],
            name="Days Practiced (> 0 mins)",
            marker_color=constants.COLOUR_PALETTE["primary"],
        ),
    )

    monthly_fig.add_trace(
        go.Bar(
            x=monthly_df["month"],
            y=monthly_df["days_in_month"],
            name="Tracked Days in Month",
            marker_color=constants.COLOUR_PALETTE["30day_avg"],
        ),
    )

    monthly_fig.update_layout(
        barmode="group",
        title="Monthly Breakdown of Practice and Goals",
        xaxis_title="Month",
        yaxis_title="Number of Days",
        height=500,
        legend_title="Metric",
    )

    st.plotly_chart(monthly_fig, use_container_width=True)


def _yearly_heatmap(df: DataFrame) -> None:
    # Create a complete year date range
    today = pd.Timestamp.now()
    year_start = pd.Timestamp(today.year, 1, 1)
    year_end = pd.Timestamp(today.year, 12, 31)
    all_dates = pd.date_range(year_start, year_end, freq="D")

    # Create a DataFrame with all dates
    full_year_df = pd.DataFrame({"date": all_dates})
    full_year_df["seconds"] = 0

    full_year_df = full_year_df.merge(
        df[["date", "seconds"]],
        on="date",
        how="left",
    )
    full_year_df["seconds"] = full_year_df["seconds_y"].fillna(0)

    # Calculate week and weekday using isocalendar
    isocalendar_df = full_year_df["date"].dt.isocalendar()
    full_year_df["weekday"] = isocalendar_df["day"]

    # Handle week numbers correctly
    full_year_df["week"] = isocalendar_df["week"]
    # Adjust week numbers for consistency
    mask = (full_year_df["date"].dt.month == 12) & (full_year_df["week"] <= 1)  # noqa: PLR2004
    full_year_df.loc[mask, "week"] = full_year_df.loc[mask, "week"] + 52
    mask = (full_year_df["date"].dt.month == 1) & (full_year_df["week"] >= 52)  # noqa: PLR2004
    full_year_df.loc[mask, "week"] = full_year_df.loc[mask, "week"] - 52

    # Rest of the heatmap code remains the same
    heatmap_fig = go.Figure()

    heatmap_fig.add_trace(
        go.Heatmap(
            x=full_year_df["week"],
            y=full_year_df["weekday"],
            z=full_year_df["seconds"] / 60,  # Convert to minutes
            colorscale=[
                [0, "rgba(227,224,227,.5)"],  # Grey for zeros/future
                [0.001, "rgb(243,231,154)"],
                [0.5, "rgb(246,90,109)"],
                [1, "rgb(126,29,103)"],
            ],
            showscale=True,
            colorbar={"title": "Minutes"},
            hoverongaps=False,
            hovertemplate="Date: %{customdata}<br>Minutes:%{z:.1f}<extra></extra>",
            customdata=full_year_df["date"].dt.strftime("%Y-%m-%d"),
            xgap=3,  # Add 3 pixels gap between columns
            ygap=3,  # Add 3 pixels gap between rows
        ),
    )

    # Update layout for GitHub-style appearance
    heatmap_fig.update_layout(
        title="Yearly Activity Heatmap",
        xaxis_title="Week",
        yaxis_title="Day of Week",
        height=300,
        yaxis={
            "ticktext": ["", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "tickvals": [0, 1, 2, 3, 4, 5, 6, 7],
            "showgrid": False,
            "autorange": "reversed",  # This ensures Mon-Sun order
        },
        xaxis={
            "showgrid": False,
            "dtick": 1,  # Show all week numbers
            "range": [0.5, 53.5],  # Fix the range to show all weeks
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(heatmap_fig, use_container_width=True)


def _days_of_week(df: DataFrame) -> None:
    df["day_of_week"] = df["date"].dt.day_name()
    daily_avg_df = (
        df.groupby("day_of_week")["seconds"]
        .mean()
        .reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
        )
        .reset_index()
    )
    daily_avg_df["minutes"] = daily_avg_df["seconds"] / 60

    days_of_week_fig = px.bar(
        daily_avg_df,
        x="day_of_week",
        y="minutes",
        title="Average Minutes Watched per Day of Week",
        labels={
            "day_of_week": "Day of Week",
            "minutes": "Average Minutes Watched",
        },
        color_discrete_sequence=[constants.COLOUR_PALETTE["primary"]],
    )

    days_of_week_fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Minutes",
    )
    st.plotly_chart(days_of_week_fig, use_container_width=True)
