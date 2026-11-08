from datetime import datetime, timedelta


def estimate_crossing_eta(
    station_time,
    distance_km,
    speed_kmh,
    station_is_before_crossing
):
    """
    Estimate train arrival at crossing using station time,
    distance and assumed average speed.
    """

    travel_minutes = (distance_km / speed_kmh) * 60

    station_time = datetime.strptime(
        station_time, "%H:%M"
    )

    if station_is_before_crossing:
        crossing_time = station_time + timedelta(
            minutes=travel_minutes
        )
    else:
        crossing_time = station_time - timedelta(
            minutes=travel_minutes
        )

    return crossing_time.strftime("%H:%M")