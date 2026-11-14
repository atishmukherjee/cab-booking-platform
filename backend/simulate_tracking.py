import asyncio
import socketio

async def run_simulation():
    driver_sio = socketio.AsyncClient()
    test_ride_id = "test-ride-room-101"

    await driver_sio.connect("http://127.0.0.1:8001", socketio_path="/socket.io")
    await driver_sio.emit("join_ride_room", {"ride_id": test_ride_id})
    await asyncio.sleep(1)

    route_points = [
        {"lat": 21.2514, "lon": 81.6296},
        {"lat": 21.2535, "lon": 81.6320},
        {"lat": 21.2556, "lon": 81.6345},
        {"lat": 21.2578, "lon": 81.6370},
        {"lat": 21.2600, "lon": 81.6395},
        {"lat": 21.2622, "lon": 81.6420},
        {"lat": 21.2645, "lon": 81.6445},
        {"lat": 21.2665, "lon": 81.6465},
        {"lat": 21.2682, "lon": 81.6482},
        {"lat": 21.2700, "lon": 81.6500},
    ]

    print("\n--- Driver Live GPS Broadcast Start ---")
    for pt in route_points:
        payload = {"ride_id": test_ride_id, "lat": pt["lat"], "lon": pt["lon"]}
        print(f"[DRIVER GPS] -> Lat: {payload['lat']}, Lon: {payload['lon']}")
        await driver_sio.emit("driver_location_update", payload)
        await asyncio.sleep(1.5)

    await driver_sio.disconnect()
    print("\n--- Destination Reached! ---")

if __name__ == "__main__":
    asyncio.run(run_simulation())
