import pandas as pd
from pathlib import Path
from datetime import datetime
import os
import requests
from dotenv import load_dotenv


DATA_FILE = Path("data/train_schedule.csv")


def load_train_schedule():
    """Load the Bichpuri train timetable."""

    if not DATA_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        return df

    df["arrival_time"] = pd.to_datetime(
        df["arrival_time"],
        format="%H:%M",
        errors="coerce"
    ).dt.time

    df["departure_time"] = pd.to_datetime(
        df["departure_time"],
        format="%H:%M",
        errors="coerce"
    ).dt.time

    return df


def get_upcoming_trains():
    """Return trains scheduled to arrive later today."""

    trains = load_train_schedule()

    if trains.empty:
        return trains

    current_time = datetime.now().time()

    upcoming = trains[
        (trains["arrival_time"].notna()) &
        (trains["arrival_time"] >= current_time)
    ].copy()

    return upcoming.sort_values("arrival_time")




load_dotenv()

API_KEY = os.getenv("RAILRADAR_API_KEY")

BASE_URL = "https://api.railradar.in/v1"


def get_live_train_status(train_number):

    if not API_KEY:
        return {
            "success": False,
            "message": "API key not found in .env file"
        }

    url = f"{BASE_URL}/trains/{train_number}/live"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("success"):
            return {
                "success": False,
                "message": result.get("error", {}).get(
                    "message", "API request failed"
                )
            }

        return {
            "success": True,
            "data": result.get("data", {})
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "message": str(error)
        }


def get_station_from_route(train_data, station_code="BCP"):
    """
    Find a particular station in a train's route.
    Default station is Bichpuri (BCP).
    """

    route = train_data.get("route", [])

    for station in route:

        if station.get("stationCode") == station_code:
            return station

    return None    