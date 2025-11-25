"""WebSocket manager for real-time updates."""
from __future__ import annotations

import json
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections for live monitoring."""
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, interview_id: int) -> None:
        """Accept a WebSocket connection for an interview."""
        await websocket.accept()
        if interview_id not in self.active_connections:
            self.active_connections[interview_id] = []
        self.active_connections[interview_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, interview_id: int) -> None:
        """Remove a WebSocket connection."""
        if interview_id in self.active_connections:
            self.active_connections[interview_id].remove(websocket)
            if not self.active_connections[interview_id]:
                del self.active_connections[interview_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Send a message to a specific WebSocket."""
        await websocket.send_text(message)
    
    async def broadcast_to_interview(
        self, message: dict, interview_id: int
    ) -> None:
        """Broadcast a message to all connections for an interview."""
        if interview_id in self.active_connections:
            message_str = json.dumps(message)
            for connection in self.active_connections[interview_id]:
                try:
                    await connection.send_text(message_str)
                except Exception:
                    # Connection might be closed
                    pass
    
    async def send_whisper_suggestion(
        self, interview_id: int, suggestion: str, context: str
    ) -> None:
        """Send a whisper suggestion to recruiters monitoring an interview."""
        message = {
            "type": "whisper",
            "suggestion": suggestion,
            "context": context,
            "timestamp": str(json.dumps({"type": "timestamp"})),
        }
        await self.broadcast_to_interview(message, interview_id)
    
    async def send_transcript_update(
        self, interview_id: int, speaker: str, text: str
    ) -> None:
        """Send a transcript update."""
        message = {
            "type": "transcript",
            "speaker": speaker,
            "text": text,
            "timestamp": str(json.dumps({"type": "timestamp"})),
        }
        await self.broadcast_to_interview(message, interview_id)
    
    async def send_status_update(
        self, interview_id: int, status: str, details: dict | None = None
    ) -> None:
        """Send an interview status update."""
        message = {
            "type": "status",
            "status": status,
            "details": details or {},
            "timestamp": str(json.dumps({"type": "timestamp"})),
        }
        await self.broadcast_to_interview(message, interview_id)


manager = ConnectionManager()
