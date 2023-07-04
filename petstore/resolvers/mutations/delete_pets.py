import strawberry
from typing import List, Dict, cast
from petstore import responses, types, errors
from strawberry.types import Info


async def delete_pets(
    ids: List[strawberry.ID], info: Info
) -> responses.DeletePetsResponse:
    database = info.context["database"]
    try:
        deleted_pets = await database.pets.delete_items(cast(List[str], ids))
        if isinstance(deleted_pets, errors.NotFoundError):
            return types.NotFoundError()
        else:
            return types.DeletedPets(
                pets=[
                    types.DeletedPet(**deleted_pet)
                    for deleted_pet in cast(
                        List[Dict[str, strawberry.ID]], deleted_pets
                    )
                ]
            )
    except Exception:
        return types.UnexpectedError()
