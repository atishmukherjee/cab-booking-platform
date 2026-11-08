import socketio
from app.core.config import settings

# Redis pub/sub manager
mgr = socketio.AsyncRedisManager(settings.REDIS_URL)

sio = socketio.AsyncServer(
    async_mode="asgi",
    client_manager=mgr,
    cors_allowed_origins="*"
)

@sio.event
async def connect(sid, environ):
    print(f"[Socket Connected]: {sid}")

@sio.event
async def disconnect(sid):
    print(f"[Socket Disconnected]: {sid}")

@sio.event
async def join_ride_room(sid, data):
    ride_id = data.get("ride_id")
    if ride_id:
        await sio.enter_room(sid, str(ride_id))
        print(f"[Room Joined]: Client {sid} joined room {ride_id}")
        await sio.emit("room_notification", {"message": f"Client joined room {ride_id}"}, room=str(ride_id))

@sio.event
async def driver_location_update(sid, data):
    ride_id = data.get("ride_id")
    if ride_id:
        await sio.emit("rider_location_feed", data, room=str(ride_id), skip_sid=sid)
