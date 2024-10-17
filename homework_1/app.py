import json
from typing import Any, Callable, Dict

from .factorial import factorial
from .fibonacci import fibonacci
from .mean import mean

from urllib.parse import parse_qs

from .utils import send_error, sent_response

from http import HTTPStatus


async def app(scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
    if scope["type"] != "http":
        return

    path = scope["path"]
    method = scope["method"]

    if path.startswith("/factorial") and method == "GET":
        qs = parse_qs(scope["query_string"].decode())
        query = qs.get("n", None)
        if query is None or query[0] == "":
            await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            return
        try:
            n = int(query[0])
        except ValueError:
            await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            return
        if n < 0:
            await send_error(send, HTTPStatus.BAD_REQUEST)
            return
        result = {"result": factorial(n)}
        await sent_response(send, result)
        return
    elif path.startswith("/fibonacci") and method == "GET":
        try:
            query = scope["path"].split("/")[-1]
            n = int(query)
        except ValueError:
            await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            return
        if n < 0:
            await send_error(send, HTTPStatus.BAD_REQUEST)
            return
        result = {"result": fibonacci(n)}
        await sent_response(send, result)
        return
    elif path.startswith("/mean") and method == "GET":
        body = await receive()
        try:
            values = json.loads(body["body"].decode())
        except ValueError:
            await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            return
        if values is None:
            await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            return
        if len(values) == 0:
            await send_error(send, HTTPStatus.BAD_REQUEST)
            return
        result = {"result": mean(values)}
        await sent_response(send, result)
        return
    await send_error(send, HTTPStatus.NOT_FOUND)

