import strawberry
from typing import Dict, cast
from petstore import responses, types, errors
from strawberry.types import Info


async def delete_pet(id: strawberry.ID, info: Info) -> responses.DeletePetResponse:
    database = info.context["database"]
    try:
        deleted_pet = await database.pets.delete_item(id)
        if isinstance(deleted_pet, errors.NotFoundError):
            return types.NotFoundError()
        else:
            return types.DeletedPet(**cast(Dict[str, strawberry.ID], deleted_pet))
    except Exception:
        return types.UnexpectedError()
