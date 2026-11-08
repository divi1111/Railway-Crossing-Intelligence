
from railway_api.train_service import (
    get_live_train_status,
    get_station_from_route
)

candidate_trains = [
    "51907",
    "54356",
    "64620",
    "51908",
    "64621",
    "55333",
    "55334",
    "64622",
    "64619",
    "51909",
    "51910"
]

verified_trains = []

print("\nBICHPURI TRAIN ROUTE VERIFICATION")
print("=" * 45)

for train_number in candidate_trains:

    print(f"\nChecking train: {train_number}")

    try:
        result = get_live_train_status(train_number)

        if not result.get("success"):
            print("API status: Could not fetch")
            continue

        train = result["data"]

        bichpuri = get_station_from_route(train, "BCP")

        if bichpuri:

            print("Result: BICHPURI FOUND")

            print(
                "Train Name:",
                train.get("trainName", "Unknown")
            )

            print(
                "Scheduled Arrival:",
                bichpuri.get("scheduledArrival", "Unknown")
            )

            print(
                "Scheduled Departure:",
                bichpuri.get("scheduledDeparture", "Unknown")
            )

            verified_trains.append(train_number)

        else:
            print("Result: Bichpuri not found in route")

    except Exception as error:
        print("Error:", error)

print("\n" + "=" * 45)
print("VERIFICATION SUMMARY")

print("Verified trains:", verified_trains)
print("Total verified:", len(verified_trains))
