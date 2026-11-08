
import streamlit as st
import pandas as pd

from datetime import datetime

from railway_api.train_service import (
    load_train_schedule,
    get_upcoming_trains,
    get_live_train_status,
    get_station_from_route
)

from prediction.gate_predictor import (
    predict_gate_timing,
    predict_gate_timing_from_api
)


# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="Railway Crossing Intelligence",
    page_icon="🚆",
    layout="wide"
)


# -----------------------------------------
# API CACHING
# -----------------------------------------

@st.cache_data(ttl=300)
def get_cached_train_status(train_number):

    result = get_live_train_status(train_number)

    return result


# -----------------------------------------
# DATE AND TIME FORMATTING
# -----------------------------------------

def format_train_datetime(timestamp):

    if not timestamp or timestamp == "Not Available":
        return "Not Available"

    try:
        date_time = datetime.fromisoformat(timestamp)

        return date_time.strftime("%d %b %Y, %I:%M %p")

    except (ValueError, TypeError):
        return "Not Available"


# -----------------------------------------
# ARRIVAL COUNTDOWN FUNCTION
# -----------------------------------------

def get_arrival_countdown(arrival):

    if not arrival or arrival == "Not Available":
        return "Not Available"

    try:

        arrival_time = datetime.fromisoformat(arrival)

        if arrival_time.tzinfo:
            current_time = datetime.now(arrival_time.tzinfo)
        else:
            current_time = datetime.now()

        remaining_seconds = (
            arrival_time - current_time
        ).total_seconds()

        if remaining_seconds <= 0:
            return "Due / possibly passed"

        remaining_minutes = int(remaining_seconds // 60)

        hours = remaining_minutes // 60
        minutes = remaining_minutes % 60

        if hours > 0:
            return f"{hours} hr {minutes} min"

        return f"{minutes} minutes"

    except (ValueError, TypeError):
        return "Not Available"


# -----------------------------------------
# MULTIPLE TRAIN FETCHING FUNCTION
# -----------------------------------------

def fetch_bichpuri_trains():

    # Read train numbers from CSV
    schedule = pd.read_csv(
        "data/train_schedule.csv",
        dtype={"train_number": str}
    )

    if schedule.empty:
        return pd.DataFrame()

    train_results = []

    # Check every train in the CSV
    for _, row in schedule.iterrows():

        train_number = row["train_number"]

        if pd.isna(train_number) or not str(train_number).strip():
            continue

        try:

            # Fetch cached live train information
            result = get_cached_train_status(train_number)

            if not result.get("success"):
                continue

            train = result["data"]

            # Check whether Bichpuri exists in this train's route
            bichpuri = get_station_from_route(train, "BCP")

            if not bichpuri:
                continue

            # Get predicted Bichpuri arrival
            arrival = bichpuri.get("actualArrival")

            # Calculate gate timings
            if arrival:

                prediction = predict_gate_timing_from_api(
                    station_arrival=arrival,
                    closing_lead_minutes=8,
                    reopening_delay_minutes=4,
                    crossing_offset_minutes=0
                )

                gate_closing = prediction["gate_closing"]
                gate_reopening = prediction["gate_reopening"]
                waiting_time = prediction["waiting_minutes"]

            else:

                gate_closing = "Not Available"
                gate_reopening = "Not Available"
                waiting_time = "Not Available"

            # Store train information
            train_results.append({

                "Train Number": train_number,

                "Train Name": train.get(
                    "trainName",
                    row["train_name"]
                ),

                "Status": train.get("status", "Unknown"),

                "Delay (Minutes)": train.get(
                    "delayMinutes",
                    0
                ),

                "Scheduled Arrival": format_train_datetime(
                    bichpuri.get("scheduledArrival")
                ),

                "Predicted Arrival": format_train_datetime(arrival),

                "Gate Closing": gate_closing,

                "Gate Reopening": gate_reopening,

                "Waiting Time (Minutes)": waiting_time

            })

        except Exception as error:

            print(
                f"Error fetching train {train_number}: {error}"
            )

    # Convert collected information into DataFrame
    train_df = pd.DataFrame(train_results)

    if not train_df.empty:

        # Calculate arrival countdown
        train_df["Arrival Countdown"] = (
            train_df["Predicted Arrival"].apply(
                get_arrival_countdown
            )
        )

        # Sort trains by predicted Bichpuri arrival time
        train_df["_sort_arrival"] = pd.to_datetime(
            train_df["Predicted Arrival"],
            format="%d %b %Y, %I:%M %p",
            errors="coerce"
        )

        train_df = train_df.sort_values(
            by="_sort_arrival",
            ascending=True,
            na_position="last"
        )

        # Remove temporary sorting column
        train_df = train_df.drop(
            columns=["_sort_arrival"]
        )

        # Reset table index
        train_df = train_df.reset_index(drop=True)

    return train_df


# =========================================
# MAIN DASHBOARD
# =========================================

st.title("🚆 Railway Crossing Intelligence System")

st.subheader("Bichpuri Railway Crossing, Agra")

st.info(
    "This application estimates train arrival and "
    "railway gate timings. Predictions are not official "
    "railway gate-status information."
)

st.divider()


# =========================================
# TRAIN TIMETABLE
# =========================================

st.header("🚆 Bichpuri Train Information")

all_trains = load_train_schedule()
upcoming_trains = get_upcoming_trains()

if all_trains.empty:

    st.warning(
        "No verified train timetable has been added yet. "
        "Please update data/train_schedule.csv."
    )

else:

    st.metric(
        "Total trains in timetable",
        len(all_trains)
    )

    st.subheader("Upcoming Trains")

    if upcoming_trains.empty:

        st.info("No more scheduled trains for today.")

    else:

        st.dataframe(
            upcoming_trains,
            use_container_width=True,
            hide_index=True
        )


# Display complete train schedule

try:

    trains = pd.read_csv("data/train_schedule.csv")

    if trains.empty:

        st.warning("Train schedule is not available yet.")

    else:

        st.subheader("Train Schedule")

        st.dataframe(
            trains,
            use_container_width=True
        )

except Exception as error:

    st.error(
        f"Unable to load train schedule: {error}"
    )


st.divider()


# =========================================
# SINGLE TRAIN LIVE TRACKING
# =========================================

st.header("🚆 Live Train Running Status")

train_number = st.text_input(
    "Enter Train Number",
    value="54355"
)

if st.button("Fetch Live Train Status"):

    with st.spinner("Fetching live train information..."):

        result = get_cached_train_status(train_number)

    if result.get("success"):

        train = result["data"]

        st.success(
            "Live train information fetched successfully!"
        )

        st.subheader("🚆 Live Train Information")

        st.write(
            "Train Name:",
            train.get("trainName", "Not Available")
        )

        st.write(
            "Train Number:",
            train.get("trainNumber", "Not Available")
        )

        st.write(
            "Current Status:",
            train.get("status", "Not Available")
        )

        delay = train.get("delayMinutes", 0)

        st.write(
            "Current Delay:",
            f"{delay} minutes"
        )

        # Bichpuri station information

        st.divider()

        st.subheader("🚉 Bichpuri Station Information")

        bichpuri = get_station_from_route(
            train,
            "BCP"
        )

        if bichpuri:

            st.write(
                "Station Name:",
                bichpuri.get("stationName", "Bichpuri")
            )

            st.write(
                "Station Code:",
                bichpuri.get("stationCode", "BCP")
            )

            scheduled_arrival = bichpuri.get("scheduledArrival")

            st.write(   
                "Scheduled Arrival:",
                format_train_datetime(scheduled_arrival)
            )

            arrival = bichpuri.get("actualArrival")

            if arrival:

                st.write(
                    "Predicted Arrival:",
                    format_train_datetime(arrival)
                )

                # Gate timing prediction

                st.divider()

                st.subheader(
                    "🚦 Bichpuri Gate Time Prediction"
                )

                prediction = predict_gate_timing_from_api(
                    station_arrival=arrival,
                    closing_lead_minutes=8,
                    reopening_delay_minutes=4,
                    crossing_offset_minutes=0
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Predicted Gate Closing",
                    prediction["gate_closing"]
                )

                col2.metric(
                    "Estimated Train Arrival",
                    prediction["crossing_arrival"]
                )

                col3.metric(
                    "Predicted Gate Reopening",
                    prediction["gate_reopening"]
                )

                st.info(
                    f"Estimated waiting time: "
                    f"{prediction['waiting_minutes']} minutes"
                )

                st.caption(
                    "This is an estimated prediction based on train "
                    "arrival information and assumed gate timings "
                    "(8 minutes before arrival and 4 minutes after "
                    "arrival). It does not show the actual railway "
                    "gate status."
                )

            else:

                st.warning(
                    "Predicted arrival is not available for Bichpuri."
                )

        else:

            st.warning(
                "This train does not have Bichpuri station in its route."
            )

    

    else:
        st.error("Unable to fetch live train information.")
        
        st.write("Actual API response:")
        
        st.json(result)


st.divider()


# =========================================
# AUTOMATIC MULTIPLE TRAIN TRACKING
# =========================================

@st.fragment(run_every="5m")
def multiple_train_dashboard():

    st.header(
        "🚆 Multiple Trains Passing Through Bichpuri"
    )

    st.caption(
        "Live train information refreshes automatically "
        "every 60 seconds."
    )

    with st.spinner("Fetching train information..."):

        train_df = fetch_bichpuri_trains()

    if not train_df.empty:

        st.success(
            f"Found {len(train_df)} train(s) passing through Bichpuri!"
        )

        # Find the next approaching train

        # Find the next approaching train
        arrival_times = pd.to_datetime(
            train_df["Predicted Arrival"],
            format="%d %b %Y, %I:%M %p",
            errors="coerce"
        )

        current_time = pd.Timestamp.now()

        upcoming_trains = train_df[
            arrival_times > current_time
        ].copy()
        
        if not upcoming_trains.empty:

            next_train = upcoming_trains.iloc[0]

            st.divider()

            st.subheader("⭐ Next Approaching Train")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Train Number",
                next_train["Train Number"]
            )

            col2.metric(
                "Train Name",
                next_train["Train Name"]
            )

            col3.metric(
                "Arrival Countdown",
                next_train["Arrival Countdown"]
            )

            st.info(
                f"Expected Bichpuri arrival: "
                f"{next_train['Predicted Arrival']}"
            )

        else:

            st.info(
                "No upcoming train with a future predicted arrival."
            )

        st.divider()

        st.subheader(
            "All Trains Passing Through Bichpuri"
        )

        st.dataframe(
            train_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No trains passing through Bichpuri were found. "
            "Check your train numbers or API response."
        )


# Display automatic tracking dashboard

multiple_train_dashboard()


# =========================================
# MANUAL GATE TIMING CALCULATOR
# =========================================

st.divider()

st.subheader("🚦 Gate Timing Prediction")

train_arrival = st.time_input(
    "Enter estimated train arrival time",
    value=pd.to_datetime("10:30").time()
)

closing_lead = st.number_input(
    "Minutes before train arrival to close gate",
    min_value=1,
    max_value=30,
    value=8
)

reopening_delay = st.number_input(
    "Minutes after train passage to reopen gate",
    min_value=1,
    max_value=30,
    value=4
)

if st.button("Predict Gate Timing"):

    arrival = train_arrival.strftime("%H:%M")

    prediction = predict_gate_timing(
        arrival,
        closing_lead,
        reopening_delay
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Predicted Gate Closing",
        prediction["gate_closing"]
    )

    col2.metric(
        "Estimated Train Arrival",
        prediction["train_arrival"]
    )

    col3.metric(
        "Predicted Gate Reopening",
        prediction["gate_reopening"]
    )

    st.success(
        f"Estimated waiting time: "
        f"{prediction['waiting_minutes']} minutes"
    )

    st.caption(
        "Demo calculation based on manually supplied "
        "assumptions. Not a confirmed gate schedule."
    )
