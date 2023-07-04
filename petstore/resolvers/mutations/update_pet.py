from dataclasses import asdict
from typing import Dict, Any, cast
from petstore import inputs, responses, types, errors
from strawberry.types import Info


async def update_pet(
    input: inputs.UpdatePetInput, info: Info
) -> responses.UpdatePetResponse:
    database = info.context["database"]
    try:
        pet = await database.pets.update_item(asdict(input))
        if isinstance(pet, errors.NotFoundError):
            return types.NotFoundError()
        else:
            return types.Pet(**cast(Dict[str, Any], pet))
    except Exception:
        return types.UnexpectedError()
