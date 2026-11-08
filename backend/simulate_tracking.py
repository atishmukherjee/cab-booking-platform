import asyncio
import socketio

async def run_simulation():
    rider_sio = socketio.AsyncClient()
    driver_sio = socketio.AsyncClient()

    test_ride_id = "test-ride-room-101"

    @rider_sio.on("rider_location_feed")
    def on_location_received(data):
        print(f"\n[RIDER SCREEN UPDATE] -> Driver Moving! New GPS: Lat {data['lat']}, Lon {data['lon']}")

    @rider_sio.on("room_notification")
    def on_notification(data):
        print(f"[RIDER NOTIFICATION] -> {data['message']}")

    await rider_sio.connect("http://localhost:8000", socketio_path="/socket.io")
    await driver_sio.connect("http://localhost:8000", socketio_path="/socket.io")

    await rider_sio.emit("join_ride_room", {"ride_id": test_ride_id})
    await driver_sio.emit("join_ride_room", {"ride_id": test_ride_id})
    await asyncio.sleep(1)

    route_points = [
        {"lat": 21.2550, "lon": 81.6350},
        {"lat": 21.2538, "lon": 81.6332},
        {"lat": 21.2520, "lon": 81.6305},
    ]

    print("\n--- Driver Ride Start Kar Raha Hai ---")
    for pt in route_points:
        payload = {"ride_id": test_ride_id, "lat": pt["lat"], "lon": pt["lon"]}
        print(f"[DRIVER GPS TRANSMIT] -> Sending coordinates: {payload['lat']}, {payload['lon']}")
        await driver_sio.emit("driver_location_update", payload)
        await asyncio.sleep(1.5)

    await rider_sio.disconnect()
    await driver_sio.disconnect()
    print("\nSimulation complete!")

if __name__ == "__main__":
    asyncio.run(run_simulation())
