from railway_api.train_service import (
    get_live_train_status,
    get_station_from_route
)

train_number = "54355"

result = get_live_train_status(train_number)

if result["success"]:

    train = result["data"]

    print("\nLIVE TRAIN INFORMATION")
    print("Train:", train.get("trainName"))
    print("Delay:", train.get("delayMinutes"), "minutes")

    # Find Bichpuri in the route
    bichpuri = get_station_from_route(train)

    print("\nBICHPURI STATION INFORMATION")

    if bichpuri:

        print("Station:", bichpuri.get("stationName"))
        print("Station Code:", bichpuri.get("stationCode"))

        print("Scheduled Arrival:",
              bichpuri.get("scheduledArrival"))

        print("Scheduled Departure:",
              bichpuri.get("scheduledDeparture"))

        print("Predicted Arrival:",
              bichpuri.get("actualArrival"))

        print("Predicted Departure:",
              bichpuri.get("actualDeparture"))

        print("Arrival Delay:",
              bichpuri.get("delayArrival"), "minutes")

        print("Data Source:",
              bichpuri.get("provenance"))

    else:

        print("This train does not have Bichpuri in its route.")

else:

    print("API ERROR:", result["message"])