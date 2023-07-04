from dataclasses import asdict
from typing import List, Dict, Any, cast
from petstore import inputs, responses, types
from strawberry.types import Info


async def create_pets(
    input: inputs.CreatePetsInput, info: Info
) -> responses.CreatePetsResponse:
    database = info.context["database"]
    try:
        pets = await database.pets.create_items(asdict(input)["pets"])
        return types.Pets(
            pets=[types.Pet(**pet) for pet in cast(List[Dict[str, Any]], pets)]
        )
    except Exception:
        return types.UnexpectedError()
