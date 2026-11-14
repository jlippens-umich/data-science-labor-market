import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="The Data Science Labor Market in America",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    state = pd.read_csv("dashboard_state.csv")
    occupation = pd.read_csv("dashboard_occupation.csv")
    time_series = pd.read_csv("dashboard_time_series.csv")

    return state, occupation, time_series


state, occupation, time_series = load_data()

# --------------------------------------------------
# DATA PREPARATION
# --------------------------------------------------

families = [
    "Data Science",
    "AI/ML Engineering",
    "Statistics",
    "Business Analytics",
    "Computer Science/Data Engineering"
]

state["YEAR"] = pd.to_numeric(state["YEAR"], errors="coerce")

for col in [
    "FAMILY_EMPLOYMENT",
    "FAMILY_MEAN_ANNUAL_WAGE",
    "FAMILY_LQ",
    "EMPLOYMENT_COVERAGE"
]:
    state[col] = pd.to_numeric(state[col], errors="coerce")

occupation["A_MEDIAN"] = pd.to_numeric(
    occupation["A_MEDIAN"], errors="coerce"
)

time_series["YEAR"] = pd.to_numeric(
    time_series["YEAR"], errors="coerce"
)

# State abbreviations for the Plotly US map
state_abbreviations = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}

# --------------------------------------------------
# DASHBOARD TITLE AND INTRODUCTION
# --------------------------------------------------

st.title("The Data Science Labor Market in America")

st.markdown(
    """
    **Mapping employment, wages, and occupational concentration
    across the United States.**

    How does the data science labor market vary across states?
    Explore where employment is concentrated, how wages compare,
    and how these patterns have changed over time.
    """
)

st.divider()

# --------------------------------------------------
# GLOBAL FILTERS
# --------------------------------------------------

st.subheader("Explore the labor market")

filter1, filter2 = st.columns(2)

years = sorted(
    state["YEAR"].dropna().astype(int).unique().tolist()
)

with filter1:
    selected_year = st.selectbox(
        "Select year",
        years,
        index=len(years) - 1
    )

with filter2:
    selected_family = st.selectbox(
        "Select occupational family",
        families,
        index=0
    )

# The same family and year selections feed multiple charts.
selected_state_data = state[
    (state["YEAR"] == selected_year) &
    (state["JOB_FAMILY"] == selected_family)
].copy()

selected_occupation_data = occupation[
    occupation["JOB_FAMILY"] == selected_family
].copy()

# --------------------------------------------------
# VISUALIZATION 1: CHOROPLETH MAP
# --------------------------------------------------

st.divider()
st.header("1. Geographic concentration")

st.markdown(
    f"**{selected_family} — {selected_year}**  \n"
    "Location Quotient (LQ) shows whether a state's share of "
    "employment in this occupational family is above or below "
    "the national share."
)

map_data = selected_state_data.copy()

map_data["STATE_ABBREV"] = map_data["AREA_TITLE"].map(
    state_abbreviations
)

map_data = map_data[
    (map_data["STATE_ABBREV"].notna()) &
    (map_data["STATE_ABBREV"] != "DC") &
    (map_data["FAMILY_LQ"].notna())
]

fig_map = px.choropleth(
    map_data,
    locations="STATE_ABBREV",
    locationmode="USA-states",
    color="FAMILY_LQ",
    scope="usa",
    color_continuous_scale="Blues",
    range_color=(0, 2),
    hover_name="AREA_TITLE",
    hover_data={
        "STATE_ABBREV": False,
        "FAMILY_LQ": ":.2f",
        "FAMILY_EMPLOYMENT": ":,.0f",
        "EMPLOYMENT_COVERAGE": ":.0%"
    },
    labels={
        "FAMILY_LQ": "Location Quotient",
        "FAMILY_EMPLOYMENT": "Estimated Employment",
        "EMPLOYMENT_COVERAGE": "Employment Coverage"
    }
)

fig_map.update_layout(
    height=550,
    margin=dict(l=0, r=0, t=20, b=0),
    coloraxis_colorbar_title="LQ"
)

st.plotly_chart(fig_map, use_container_width=True)

st.caption(
    "DC is excluded from the map because the map displays state "
    "polygons. DC remains included in the ranked bar chart. "
    "An LQ above 1.0 indicates greater employment concentration "
    "than the national average."
)

# --------------------------------------------------
# VISUALIZATION 2: RANKED BAR CHART
# --------------------------------------------------

st.divider()
st.header("2. State rankings")

st.markdown(
    "Which states have the highest occupational concentration?"
)

bar_data = selected_state_data[
    selected_state_data["FAMILY_LQ"].notna()
].sort_values("FAMILY_LQ", ascending=True)

fig_bar = px.bar(
    bar_data,
    x="FAMILY_LQ",
    y="AREA_TITLE",
    orientation="h",
    text="FAMILY_LQ",
    hover_data={
        "FAMILY_EMPLOYMENT": ":,.0f",
        "EMPLOYMENT_COVERAGE": ":.0%",
        "FAMILY_LQ": ":.2f"
    },
    labels={
        "AREA_TITLE": "State",
        "FAMILY_LQ": "Location Quotient",
        "FAMILY_EMPLOYMENT": "Estimated Employment",
        "EMPLOYMENT_COVERAGE": "Employment Coverage"
    }
)

fig_bar.update_traces(
    texttemplate="%{x:.2f}",
    textposition="outside",
    cliponaxis=False
)

fig_bar.add_vline(
    x=1,
    line_dash="dash",
    line_color="red",
    annotation_text="National average (LQ = 1.0)"
)

fig_bar.update_layout(
    height=850,
    margin=dict(l=10, r=65, t=35, b=30),
    yaxis_title="",
    xaxis_title="Location Quotient",
    showlegend=False
)

st.plotly_chart(fig_bar, use_container_width=True)

# --------------------------------------------------
# VISUALIZATION 3: SCATTERPLOT
# --------------------------------------------------

st.divider()
st.header("3. Employment versus wages")

st.markdown(
    "How do employment size, wages, and occupational concentration "
    "relate to one another?"
)

scatter_data = selected_state_data.dropna(
    subset=[
        "FAMILY_EMPLOYMENT",
        "FAMILY_MEAN_ANNUAL_WAGE",
        "FAMILY_LQ"
    ]
).copy()

scatter_data = scatter_data[
    (scatter_data["FAMILY_EMPLOYMENT"] > 0) &
    (scatter_data["FAMILY_MEAN_ANNUAL_WAGE"] > 0)
]

fig_scatter = px.scatter(
    scatter_data,
    x="FAMILY_EMPLOYMENT",
    y="FAMILY_MEAN_ANNUAL_WAGE",
    color="FAMILY_LQ",
    hover_name="AREA_TITLE",
    color_continuous_scale="Viridis",
    range_color=(0, 2),
    hover_data={
        "FAMILY_EMPLOYMENT": ":,.0f",
        "FAMILY_MEAN_ANNUAL_WAGE": ":$,.0f",
        "FAMILY_LQ": ":.2f",
        "EMPLOYMENT_COVERAGE": ":.0%"
    },
    labels={
        "FAMILY_EMPLOYMENT": "Estimated Employment",
        "FAMILY_MEAN_ANNUAL_WAGE": "Weighted Mean Annual Wage",
        "FAMILY_LQ": "Location Quotient"
    }
)

fig_scatter.update_xaxes(
    type="log",
    title="Estimated Employment (log scale)"
)

fig_scatter.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=25, b=20)
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.caption(
    "The weighted family wage is an analytical estimate based on "
    "available occupation-level employment and wage data. "
    "It is not an official BLS occupational-family wage."
)

# --------------------------------------------------
# VISUALIZATION 4: BEESWARM
# --------------------------------------------------

st.divider()
st.header("4. Occupational wage distribution")

st.markdown(
    "**Beeswarm — 2025 state-level occupation median wages**  \n"
    "Each dot represents an occupation in a state. Horizontal "
    "position separates nearby observations to make the distribution "
    "easier to see."
)

# The uploaded occupation CSV contains 2025 observations.
beeswarm_data = selected_occupation_data.dropna(
    subset=["A_MEDIAN"]
).copy()

if not beeswarm_data.empty:

    beeswarm_data = beeswarm_data[
        beeswarm_data["A_MEDIAN"] > 0
    ].copy()

    values = beeswarm_data["A_MEDIAN"].to_numpy()
    y_span = max(values.max() - values.min(), 1)
    min_vertical_gap = y_span * 0.025
    lane_step = 0.12

    offsets = np.zeros(len(beeswarm_data))
    assigned = []

    # Assign horizontal lanes to reduce overlap.
    order = np.argsort(values)

    for idx in order:
        candidate_lanes = [0]

        for lane in range(1, 15):
            candidate_lanes.extend([lane, -lane])

        for lane in candidate_lanes:
            x_candidate = lane * lane_step

            collision = False

            for previous_idx, previous_lane in assigned:
                x_previous = previous_lane * lane_step

                dx = x_candidate - x_previous
                dy = (
                    values[idx] - values[previous_idx]
                ) / y_span

                distance = np.sqrt(
                    dx ** 2 + (dy * 10) ** 2
                )

                if distance < 0.13:
                    collision = True
                    break

            if not collision:
                offsets[idx] = x_candidate
                assigned.append((idx, lane))
                break

    beeswarm_data["SWARM_X"] = offsets

    fig_beeswarm = go.Figure()

    fig_beeswarm.add_trace(
        go.Scatter(
            x=beeswarm_data["SWARM_X"],
            y=beeswarm_data["A_MEDIAN"],
            mode="markers",
            marker=dict(
                size=9,
                color=beeswarm_data["A_MEDIAN"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Annual<br>Median Wage"),
                opacity=0.8
            ),
            customdata=beeswarm_data[
                ["AREA_TITLE", "OCC_TITLE", "OCC_CODE"]
            ].to_numpy(),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Occupation: %{customdata[1]}<br>"
                "SOC: %{customdata[2]}<br>"
                "Annual Median Wage: $%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    fig_beeswarm.update_layout(
        height=550,
        xaxis=dict(
            title="Individual state/occupation observations",
            showticklabels=False,
            zeroline=False,
            showgrid=False
        ),
        yaxis_title="Annual Median Wage ($)",
        margin=dict(l=20, r=20, t=25, b=30),
        showlegend=False
    )

    st.plotly_chart(
        fig_beeswarm,
        use_container_width=True
    )

else:
    st.warning(
        "No available occupation-level median wage observations "
        "for this selection."
    )

st.caption(
    "The beeswarm uses 2025 data regardless of the year selector. "
    "Each dot is an occupation-state observation, not an individual "
    "worker. Some occupations intentionally appear in more than "
    "one analytical job family."
)

# --------------------------------------------------
# VISUALIZATION 5: NATIONAL TIME SERIES
# --------------------------------------------------

st.divider()
st.header("5. National trends over time")

st.markdown(
    "How have employment and wages changed across all five "
    "occupational families since 2021?"
)

fig_trends = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "Employment Index (2021 = 100)",
        "Wage Index (2021 = 100)"
    ),
    horizontal_spacing=0.12
)

colors = px.colors.qualitative.Plotly

for i, family in enumerate(families):

    family_data = time_series[
        time_series["JOB_FAMILY"] == family
    ].sort_values("YEAR")

    if family_data.empty:
        continue

    employment_hover = (
        family_data["EMPLOYMENT_YOY_PCT"]
        if "EMPLOYMENT_YOY_PCT" in family_data.columns
        else pd.Series(np.nan, index=family_data.index)
    )

    wage_hover = (
        family_data["WAGE_YOY_PCT"]
        if "WAGE_YOY_PCT" in family_data.columns
        else pd.Series(np.nan, index=family_data.index)
    )

    fig_trends.add_trace(
        go.Scatter(
            x=family_data["YEAR"],
            y=family_data["EMPLOYMENT_INDEX"],
            mode="lines+markers",
            name=family,
            legendgroup=family,
            showlegend=True,
            line=dict(color=colors[i % len(colors)], width=2),
            customdata=employment_hover.to_numpy(),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Year: %{x}<br>"
                "Employment Index: %{y:.1f}<br>"
                "Year-over-year change: %{customdata:.1f}%"
                "<extra></extra>"
            )
        ),
        row=1,
        col=1
    )

    fig_trends.add_trace(
        go.Scatter(
            x=family_data["YEAR"],
            y=family_data["WAGE_INDEX"],
            mode="lines+markers",
            name=family,
            legendgroup=family,
            showlegend=False,
            line=dict(color=colors[i % len(colors)], width=2),
            customdata=wage_hover.to_numpy(),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Year: %{x}<br>"
                "Wage Index: %{y:.1f}<br>"
                "Year-over-year change: %{customdata:.1f}%"
                "<extra></extra>"
            )
        ),
        row=1,
        col=2
    )

fig_trends.add_hline(
    y=100,
    line_dash="dash",
    line_color="gray",
    row=1,
    col=1
)

fig_trends.add_hline(
    y=100,
    line_dash="dash",
    line_color="gray",
    row=1,
    col=2
)

fig_trends.update_xaxes(
    title_text="Year",
    tickmode="linear",
    dtick=1
)

fig_trends.update_yaxes(
    title_text="Index (2021 = 100)"
)

fig_trends.update_layout(
    height=600,
    hovermode="x unified",
    legend_title="Occupational Family",
    margin=dict(l=20, r=20, t=65, b=30)
)

st.plotly_chart(
    fig_trends,
    use_container_width=True
)

# --------------------------------------------------
# METHODOLOGY AND DATA NOTES
# --------------------------------------------------

st.divider()

with st.expander("About the data and methodology"):

    st.markdown(
        """
        **Source:** U.S. Bureau of Labor Statistics,
        Occupational Employment and Wage Statistics (OEWS),
        May 2021–2025.

        **Geographic coverage:** United States, 50 states,
        and the District of Columbia.

        **Occupational families:** These are analytical groupings
        constructed from selected Standard Occupational
        Classification (SOC) codes. They are not official BLS
        occupational categories.

        **Location Quotient:** An LQ above 1.0 means the area's
        share of employment in the selected family is higher
        than the corresponding national share.

        **Employment estimates:** BLS employment estimates are
        rounded and exclude self-employed workers.

        **Missing data:** Suppressed or unavailable estimates
        are treated as missing, not zero. Employment coverage
        indicates the share of expected occupations with
        available employment estimates.

        **Overlapping families:** Some occupations are included
        in more than one analytical family. Family totals should
        not be added together as unique workforce totals.

        **Wages:** Family-level weighted wages are analytical
        estimates, not official BLS family wage statistics.

        **Time series:** Employment and wage indices use 2021
        as the baseline (100). Hover over the lines to see
        year-over-year percentage changes.
        """
    )

st.caption(
    "Data source: U.S. Bureau of Labor Statistics, "
    "Occupational Employment and Wage Statistics. "
    "Analysis and occupational groupings are the author's."
)
