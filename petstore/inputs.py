import strawberry
from typing import List, Optional


@strawberry.input
class CreatePetInput:
    name: str
    category: str


@strawberry.input
class CreatePetsInput:
    pets: List[CreatePetInput]


@strawberry.input
class UpdatePetInput:
    id: strawberry.ID
    name: str
    category: str


@strawberry.input
class ListPetsInput:
    page: Optional[int] = 1
    size: Optional[int] = 20


@strawberry.input
class DeletePetInput:
    id: strawberry.ID


@strawberry.input
class DeletePetsInput:
    pets: List[DeletePetInput]


@strawberry.input
class UpdatePetsInput:
    pets: List[UpdatePetInput]


@strawberry.input
class PatchPetInput:
    id: strawberry.ID
    name: Optional[str] = None
    category: Optional[str] = None


@strawberry.input
class PatchPetsInput:
    pets: List[PatchPetInput]
