"""Constants used throughout the application."""

# The maximum amount of future milestones to show at any one point
UPCOMING_MILESTONES_CAP = 3

# The milestones to track (taken from Dreaming Spanish website)
MILESTONES = [50, 150, 300, 600, 1000, 1500]

# Colours used in the graphs and charts
COLOUR_PALETTE = {
    "primary": "#2E86C1",  # Primary blue
    "7day_avg": "#FFA500",  # Orange
    "30day_avg": "#2ECC71",  # Green
    # Milestone colors - using an accessible and distinguishable gradient
    "50": "#FF6B6B",  # Coral red
    "150": "#4ECDC4",  # Turquoise
    "300": "#9B59B6",  # Purple
    "600": "#F1C40F",  # Yellow
    "1000": "#E67E22",  # Orange
    "1500": "#2ECC71",  # Green
}
