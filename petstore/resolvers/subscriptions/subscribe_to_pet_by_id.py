import strawberry
from petstore import types, responses
from strawberry.types import Info


async def subscribe_to_pet_by_id(
    id: strawberry.ID, info: Info
) -> responses.SubscribeToPetByIdResponse:
    database = info.context["database"]
    async for message in database.pets.subscribe_to_item_by_id(id):
        if message["type"] == "update":
            yield types.PetUpdateMessage(**message["data"])
        elif message["type"] == "delete":
            yield types.PetDeleteMessage(**message["data"])
