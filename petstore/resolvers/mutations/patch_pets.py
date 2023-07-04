from dataclasses import asdict
from typing import List, Dict, Any, cast
from petstore import inputs, responses, types, errors
from strawberry.types import Info


async def patch_pets(
    input: inputs.PatchPetsInput, info: Info
) -> responses.PatchPetsResponse:
    database = info.context["database"]
    try:
        pets = await database.pets.patch_items(asdict(input)["pets"])
        if isinstance(pets, errors.NotFoundError):
            return types.NotFoundError()
        else:
            pets = [types.Pet(**pet) for pet in cast(List[Dict[str, Any]], pets)]
            return types.Pets(pets=pets)
    except Exception:
        return types.UnexpectedError()
