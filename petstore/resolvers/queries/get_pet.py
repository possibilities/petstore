import strawberry
from petstore import responses
from petstore import types, errors
from typing import Dict, Any, cast
from strawberry.types import Info


async def get_pet(id: strawberry.ID, info: Info) -> responses.GetPetResponse:
    database = info.context["database"]
    try:
        pet = await database.pets.get_item(id)
        if isinstance(pet, errors.NotFoundError):
            return types.NotFoundError()
        else:
            return types.Pet(**cast(Dict[str, Any], pet))
    except Exception:
        return types.UnexpectedError()
