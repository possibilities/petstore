import strawberry
from petstore import responses
from petstore import types, errors
from typing import List, Dict, Any, cast
from strawberry.types import Info


async def get_pets(ids: List[strawberry.ID], info: Info) -> responses.GetPetsResponse:
    database = info.context["database"]
    try:
        pets = await database.pets.get_items(cast(List[str], ids))
        if isinstance(pets, errors.NotFoundError):
            return types.NotFoundError()
        else:
            return types.Pets(
                pets=[types.Pet(**pet) for pet in cast(List[Dict[str, Any]], pets)]
            )

    except Exception:
        return types.UnexpectedError()
