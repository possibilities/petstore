from dataclasses import asdict
from petstore import responses
from petstore import types, inputs
from typing import List, Dict, Any, cast
from strawberry.types import Info


async def list_pets(
    input: inputs.ListPetsInput, info: Info
) -> responses.ListPetsResponse:
    database = info.context["database"]
    try:
        pets = await database.pets.list_items(**cast(Dict[str, Any], asdict(input)))
        return types.PetPage(
            page=pets["page"],
            size=pets["size"],
            total_pages=pets["total_pages"],
            items=[
                types.Pet(**pet) for pet in cast(List[Dict[str, Any]], pets["items"])
            ],
        )

    except Exception:
        return types.UnexpectedError()
