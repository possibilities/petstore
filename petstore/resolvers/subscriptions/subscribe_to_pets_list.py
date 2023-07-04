from strawberry.types import Info
from petstore import types, responses


async def subscribe_to_pets_list(
    info: Info,
) -> responses.SubscribeToPetsListResponse:
    database = info.context["database"]
    async for message in database.pets.subscribe_to_list():
        if message["type"] == "create":
            yield types.PetCreateMessage(**message["data"])
        elif message["type"] == "delete":
            yield types.PetDeleteMessage(**message["data"])
