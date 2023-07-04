from dataclasses import asdict
from typing import Dict, Any, cast
from petstore import inputs, responses, types, errors
from strawberry.types import Info


async def patch_pet(
    input: inputs.PatchPetInput, info: Info
) -> responses.PatchPetResponse:
    database = info.context["database"]
    try:
        pet = await database.pets.patch_item(asdict(input))
        if isinstance(pet, errors.NotFoundError):
            return types.NotFoundError()
        else:
            return types.Pet(**cast(Dict[str, Any], pet))
    except Exception:
        return types.UnexpectedError()
