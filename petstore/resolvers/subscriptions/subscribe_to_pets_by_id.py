import strawberry
from strawberry.types import Info
from typing import List, cast
from petstore import types, responses


async def subscribe_to_pets_by_id(
    ids: List[strawberry.ID], info: Info
) -> responses.SubscribeToPetsByIdResponse:
    database = info.context["database"]
    async for message in database.pets.subscribe_to_items_by_id(cast(List[str], ids)):
        if message["type"] == "update":
            yield types.PetUpdateMessage(**message["data"])
        elif message["type"] == "delete":
            yield types.PetDeleteMessage(**message["data"])
