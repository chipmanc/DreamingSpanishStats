"""Streamlit dashboard app for tracking and visualizing Dreaming Spanish progress.

This application provides an interactive interface to:
- Load and display viewing data from the Dreaming Spanish API
- Visualize viewing patterns
- Track progress towards learning milestones (50, 150, 300, 600, 1000, 1500 hours)
- Generate predictions for future milestone achievements
- Display statistics like streaks, best days, and goal completion rates
- Export viewing data to CSV format
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import constants
from src.components import basic_stats, projected_growth
from src.utils import (
    get_best_days,
    get_initial_time,
    load_data,
)

# Set pandas option for future compatibility
pd.set_option("future.no_silent_downcasting", True)  # noqa: FBT003

st.set_page_config(page_title="Dreaming Spanish Time Tracker", layout="wide")

title = "Dreaming Spanish Stats"
subheader = "Analyze your viewing habits and predict your progress"

if st.context.url.startswith("https://ds-stats-dev."):
    title += " - :orange[Dev Build]"
elif not st.context.url.startswith("https://ds-stats."):
    title += " - :violet[Local Build]"

st.title(title)
st.subheader(subheader)

# Show warning for dev build
if st.context.url.startswith("https://ds-stats-dev."):
    st.warning(
        "You are viewing the development version of the application, meaning "
        "that it may not be fully functional, may contain bugs, or may be "
        "using experimental features.\n Resort to the production version if "
        "you encounter any issues.",
    )

button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
with button_col1:
    st.link_button(
        "☁️ Official Progress",
        "https://www.dreamingspanish.com/progress",
        use_container_width=True,
    )

with button_col2:
    st.link_button(
        "🪲 Report Issue",
        "http://github.com/HarryPeach/dreamingspanishstats/issues",
        use_container_width=True,
    )

with button_col3:
    st.link_button(
        "📖 Source Code",
        "http://github.com/HarryPeach/dreamingspanishstats",
        use_container_width=True,
    )

# Add token input and buttons in an aligned row
st.write("")  # Add some spacing
col1, col2 = st.columns([4, 1])
with col1:
    token = st.text_input(
        "Enter your bearer token:",
        type="password",
        key="token_input",
        label_visibility="collapsed",
    )
with col2:
    go_button = st.button("Go", type="primary", use_container_width=True)

if not token:
    st.warning("Please enter your bearer token above to fetch data")
    # Load and display README
    try:
        with Path("bearer_how_to.md").open() as file:
            readme_content = file.read()
            if readme_content:
                st.markdown(readme_content, unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    st.stop()

# Load data when token is provided and button is clicked
if "data" not in st.session_state or go_button:
    with st.spinner("Fetching data..."):
        data = load_data(token)
        if data is None:
            st.error(
                "Failed to fetch data from the DreamingSpanish API."
                "Please check your bearer token, ensuring it doesn't contain "
                "anything extra such as 'token:' at the beginning.",
            )
            st.stop()
        st.session_state.data = data

result = st.session_state.data
df = result.df
initial_time = get_initial_time(token) or 0
goals_reached = result.goals_reached
total_days = result.total_days
current_goal_streak = result.current_goal_streak
longest_goal_streak = result.longest_goal_streak

df = result.df.rename(columns={"timeSeconds": "seconds"})

# Calculate cumulative seconds and streak
df["cumulative_seconds"] = df["seconds"].cumsum() + initial_time
df["cumulative_minutes"] = df["cumulative_seconds"] / 60
df["cumulative_hours"] = df["cumulative_minutes"] / 60
df["streak"] = (df["seconds"] > 0).astype(int)

# Calculate current streak
df["streak_group"] = (df["streak"] != df["streak"].shift()).cumsum()
df["current_streak"] = df.groupby("streak_group")["streak"].cumsum()
current_streak = df["current_streak"].iloc[-1] if df["streak"].iloc[-1] == 1 else 0

# Calculate all-time longest streak
streak_lengths = df[df["streak"] == 1].groupby("streak_group").size()

# Calculate moving averages
df["7day_avg"] = df["seconds"].rolling(7, min_periods=1).mean()
df["30day_avg"] = df["seconds"].rolling(30, min_periods=1).mean()

current_7day_avg = df["7day_avg"].iloc[-1]
current_30day_avg = df["30day_avg"].iloc[-1]

avg_seconds_per_day = df["seconds"].mean()

basic_stats.basic_stats(df, initial_time)

projected_growth.projected_growth(df)

with st.container(border=True):
    st.subheader("Additional Graphs")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Moving Averages",
            "Daily Breakdown",
            "Monthly Breakdown",
            "Yearly Heatmap",
            "Days of Week",
        ],
    )

    with tab1:
        # Moving averages visualization
        moving_avg_fig = go.Figure()

        # Calculate cumulative average (running mean)
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

        moving_avg_fig.update_yaxes(dtick=15, title="Minutes Watched", ticklabelstep=2)

        st.plotly_chart(moving_avg_fig, use_container_width=True)

    with tab2:
        # Daily breakdown
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

    with tab3:
        # Monthly breakdown
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

    with tab4:
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
                hovertemplate="Date: %{customdata}<br>Minutes: %{z:.1f}<extra></extra>",
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

    with tab5:
        # Days of week breakdown
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
            labels={"day_of_week": "Day of Week", "minutes": "Average Minutes Watched"},
            color_discrete_sequence=[constants.COLOUR_PALETTE["primary"]],
        )

        days_of_week_fig.update_layout(xaxis_title="Day of Week", yaxis_title="Minutes")
        st.plotly_chart(days_of_week_fig, use_container_width=True)

with st.container(border=True):
    # Text predictions
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

                predicted_date = df["date"].iloc[-1] + timedelta(days=days_to_milestone)
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

general_insights, best_days = st.columns(2)
with general_insights:  # noqa: SIM117
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

            goal_rate = (goals_reached / total_days) * 100
            st.metric(
                "Goal Achievement",
                f"{goals_reached} days",
                f"{goal_rate:.1f}% of days",
            )

with best_days:  # noqa: SIM117
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
            previous_7_total = df.iloc[-14:-7]["seconds"].sum() if len(df) >= 14 else 0  # noqa: PLR2004
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
                df.iloc[-60:-30]["seconds"].sum() if len(df) >= 60 else 0
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

with st.container(border=True):
    st.subheader("Tools")
    result = st.session_state.data
    st.download_button(
        label="📥 Export Data to CSV",
        data=df.to_csv(index=False),
        file_name="dreaming_spanish_data.csv",
        mime="text/csv",
    )

st.caption(
    f"Data range: {df['date'].min().strftime('%Y-%m-%d')} to {
        df['date'].max().strftime('%Y-%m-%d')
    }",
)
