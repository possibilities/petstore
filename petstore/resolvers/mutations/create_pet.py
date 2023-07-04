from dataclasses import asdict
from typing import Dict, Any, cast
from petstore import inputs, responses, types
from strawberry.types import Info


async def create_pet(
    input: inputs.CreatePetInput, info: Info
) -> responses.CreatePetResponse:
    database = info.context["database"]
    try:
        pet = await database.pets.create_item(asdict(input))
        return types.Pet(**cast(Dict[str, Any], pet))
    except Exception:
        return types.UnexpectedError()
