import os
import asyncio
import pytest
import pytest_asyncio
import websockets
import re
import json
import uuid
from rich import print
from types import TracebackType
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from aiohttp.test_utils import TestServer
from petstore import types
from petstore.app import create_app, PetsDatabase
from petstore.database import Database
from typing import (
    Self,
    Optional,
    Coroutine,
    Type,
    Any,
    Dict,
    Callable,
    Awaitable,
    Generator,
    List,
    cast,
)


@pytest.fixture
def database() -> Generator[Database, None, None]:
    database = Database(types.Pet)
    yield database

    if os.environ.get("DEBUG"):
        print("\n\n" + json.dumps(database.store, indent=2))


@pytest_asyncio.fixture
async def server(
    aiohttp_server: Callable[..., Awaitable[TestServer]],
) -> TestServer:
    return await aiohttp_server(create_app(PetsDatabase(pets=Database(types.Pet))))


@pytest_asyncio.fixture
async def broken_server(
    aiohttp_server: Callable[..., Awaitable[TestServer]]
) -> TestServer:
    class BrokenDatabase:
        def __getattr__(self, name: str) -> None:
            raise AttributeError(f"Database.{name} is fucked, Have a great day!")

    broken_database = PetsDatabase(pets=cast(Database, BrokenDatabase()))
    return await aiohttp_server(create_app(broken_database))


@pytest_asyncio.fixture
async def client(
    server: TestServer,
) -> Callable:
    transport = AIOHTTPTransport(url=f"http://localhost:{server.port}/graphql")
    api_client = Client(transport=transport, fetch_schema_from_transport=True)

    async def run_api_query(
        raw_query: str, variable_values: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        response = await api_client.execute_async(
            gql(raw_query),
            variable_values=variable_values,
        )

        return next(iter(response.values()))

    return run_api_query


def _get_graphql_query_operation_name(query_string: str) -> str:
    match = re.search(r"(subscription)\s+(\w+)", query_string)
    if not match:
        raise Exception("Operation name couldn't be found for query: \n {query_string}")
    return match.group(2)


class SubscriptionMessagesListener:
    def __init__(self, subscription_coroutine: Coroutine) -> None:
        self._subscription: asyncio.Task = asyncio.create_task(subscription_coroutine)

    async def __aenter__(self: Self) -> Self:
        await asyncio.sleep(0.1)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        pass

    async def wait_for_messages(self: Self) -> List[Dict[str, Any]]:
        await asyncio.sleep(0.3)
        exception = self._subscription.exception()
        if exception:
            raise exception
        messages = self._subscription.result()
        self._subscription.cancel()
        return messages


@pytest_asyncio.fixture
async def subscription_messages() -> Callable:
    def collect_messages(
        subscription_coroutine: Coroutine,
    ) -> SubscriptionMessagesListener:
        return SubscriptionMessagesListener(subscription_coroutine)

    return collect_messages


@pytest.fixture
def subscription_client(
    server: TestServer,
) -> Callable:
    async def start_api_subscription(
        query: str,
        variable_values: Dict[str, Any] = {},
    ) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = []

        uri = f"ws://localhost:{server.port}/graphql"
        async with websockets.connect(  # type: ignore
            uri,
            subprotocols=["graphql-transport-ws"],
        ) as websocket:
            await websocket.send(json.dumps({"type": "connection_init", "payload": {}}))
            await websocket.recv()

            id = str(uuid.uuid4())
            subscription = {
                "id": id,
                "type": "subscribe",
                "payload": {
                    "query": query.strip(),
                    "variables": variable_values,
                    "operationName": _get_graphql_query_operation_name(query),
                },
            }
            await websocket.send(json.dumps(subscription))
            while True:
                message = None
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=0.2)
                except asyncio.TimeoutError:
                    break
                message = json.loads(message)
                if message["type"] == "complete":
                    break
                elif message["id"] == id:
                    if "payload" in message and "data" in message["payload"]:
                        messages.append(next(iter(message["payload"]["data"].values())))
                    else:
                        raise Exception("Error in subscription: " + str(message))

        return messages

    return start_api_subscription


@pytest_asyncio.fixture
async def broken_client(
    broken_server: TestServer,
) -> Callable:
    transport = AIOHTTPTransport(url=f"http://localhost:{broken_server.port}/graphql")
    api_client = Client(transport=transport, fetch_schema_from_transport=True)

    async def run_api_query(
        raw_query: str, variable_values: Dict[str, Any] | None = {}
    ) -> Dict[str, Any]:
        query = gql(raw_query)
        response = await api_client.execute_async(
            query,
            variable_values=variable_values,
        )

        return next(iter(response.values()))

    return run_api_query
