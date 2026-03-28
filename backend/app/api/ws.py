import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.workers.celery_app import celery_app

router = APIRouter(tags=["websocket"])


@router.websocket("/status/{task_id}")
async def task_status(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        while True:
            result = celery_app.AsyncResult(task_id)
            state = result.state
            payload: dict = {"task_id": task_id, "state": state}

            if state == "PROGRESS" and result.info:
                payload["progress"] = result.info

            if state in ("SUCCESS", "FAILURE"):
                if state == "SUCCESS":
                    payload["result"] = result.result
                else:
                    payload["error"] = str(result.info)
                await websocket.send_text(json.dumps(payload))
                break

            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
