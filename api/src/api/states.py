from typing import Dict

import socketio

# 配置 Socket.IO 服务器，允许所有来源并启用日志
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode="asgi",
    logger=True,
    engineio_logger=True,
)

active_connections: Dict[str, dict] = {}


def add_connection(socket_id: str, user_info: dict = None):
    active_connections[socket_id] = user_info or {}
    print("激活的连接: ", active_connections)

    print(
        f"New connection added: {socket_id}, total connections: {len(active_connections)}"
    )


def remove_connection(socket_id: str):
    if socket_id in active_connections:
        del active_connections[socket_id]
        print(
            f"Connection removed: {socket_id}, total connections: {len(active_connections)}"
        )


def get_all_socket_ids():
    return list(active_connections.keys())


def get_connection_count():
    return len(active_connections)
