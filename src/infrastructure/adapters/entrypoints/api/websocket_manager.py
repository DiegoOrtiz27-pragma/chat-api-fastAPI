"""
Manages active WebSocket connections for real-time updates.
"""
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts a new WebSocket connection and adds it to the list."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Removes a WebSocket connection from the list."""
        self.active_connections.remove(websocket)

    async def broadcast(self, data: str):
        """Sends a JSON message to all active WebSocket connections."""
        for connection in self.active_connections:
            await connection.send_text(data)

# (Singleton)
manager = ConnectionManager()