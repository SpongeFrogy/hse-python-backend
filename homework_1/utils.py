import json
from typing import Any, Awaitable, Callable

async def send_error(send: Callable[[dict[str, Any]], Awaitable[None]], status_code: int) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"text/plain"),
            ],
        }
    )
    await send({"type": "http.response.body", "body": f"Error: {status_code}".encode("utf-8")})

async def sent_response(send: Callable, body: Any, status_code: int = 200) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"text/plain"),
            ],
        }
    )
    await send({"type": "http.response.body", "body": json.dumps(body).encode("utf-8")})
