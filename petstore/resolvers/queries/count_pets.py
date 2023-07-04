from petstore import types
from petstore import responses
from strawberry.types import Info


async def count_pets(info: Info) -> responses.PetsCountResponse:
    database = info.context["database"]
    try:
        count = await database.pets.count_items()
        return types.PetsCount(count=count)

    except Exception:
        return types.UnexpectedError()
