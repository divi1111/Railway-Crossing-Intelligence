from datetime import datetime, timedelta


def predict_gate_timing(
    crossing_arrival,
    closing_lead_minutes=8,
    reopening_delay_minutes=4
):
    arrival = datetime.strptime(
        crossing_arrival, "%H:%M"
    )

    closing_time = arrival - timedelta(
        minutes=closing_lead_minutes
    )

    reopening_time = arrival + timedelta(
        minutes=reopening_delay_minutes
    )

    return {
        "gate_closing": closing_time.strftime("%H:%M"),
        "train_arrival": arrival.strftime("%H:%M"),
        "gate_reopening": reopening_time.strftime("%H:%M"),
        "waiting_minutes": (
            closing_lead_minutes + reopening_delay_minutes
        )
    }




def predict_gate_timing_from_api(
    station_arrival,
    closing_lead_minutes=8,
    reopening_delay_minutes=4,
    crossing_offset_minutes=0
):
    """
    Predict gate timings using the train's
    predicted arrival at Bichpuri station.

    crossing_offset_minutes:
    Estimated time between Bichpuri station
    and the actual railway crossing.
    """

    arrival = datetime.fromisoformat(station_arrival)

    # Estimate train arrival at the crossing
    crossing_arrival = arrival + timedelta(
        minutes=crossing_offset_minutes
    )

    gate_closing = crossing_arrival - timedelta(
        minutes=closing_lead_minutes
    )

    gate_reopening = crossing_arrival + timedelta(
        minutes=reopening_delay_minutes
    )

    return {
        "crossing_arrival": crossing_arrival.strftime(
            "%d-%m-%Y %I:%M %p"
        ),
        "gate_closing": gate_closing.strftime(
            "%d-%m-%Y %I:%M %p"
        ),
        "gate_reopening": gate_reopening.strftime(
            "%d-%m-%Y %I:%M %p"
        ),
        "waiting_minutes": (
            closing_lead_minutes + reopening_delay_minutes
        )
    }