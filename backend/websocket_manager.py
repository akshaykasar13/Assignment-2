from typing import Set
from fastapi import WebSocket
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, event: dict):
        message = json.dumps(event, default=str)
        dead = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead.add(connection)
        for d in dead:
            self.active_connections.discard(d)
