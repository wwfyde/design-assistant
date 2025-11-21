# routers/websocket_router.py
from api.states import add_connection, remove_connection, sio


@sio.event
async def connect(sid, environ, auth):
    print(f"Client {sid} connected")

    user_info = auth or {}
    # print(f"{user_info=}")
    print(f"{user_info=}, {sid=}")
    add_connection(sid, user_info)

    await sio.emit("connected", {"status": "connected"}, room=sid)


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")
    remove_connection(sid)


@sio.event
async def ping(sid, data):
    print("ping")
    await sio.emit("pong", data, room=sid)
