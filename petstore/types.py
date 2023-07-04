import strawberry
from typing import List


@strawberry.type
class Pet:
    id: strawberry.ID
    name: str
    category: str


@strawberry.type
class DeletedPet:
    id: strawberry.ID


@strawberry.type
class PetPage:
    items: List[Pet]
    page: int
    size: int
    total_pages: int


@strawberry.type
class PetsCount:
    count: int


@strawberry.type
class DeletedPets:
    pets: List[DeletedPet]


@strawberry.type
class Pets:
    pets: List[Pet]


@strawberry.type
class PetCreateMessage(Pet):
    pass


@strawberry.type
class PetUpdateMessage(Pet):
    pass


@strawberry.type
class PetDeleteMessage(DeletedPet):
    pass


@strawberry.type
class UnexpectedError:
    message: str = "Unexpected error"
    status: int = 500


@strawberry.type
class NotFoundError:
    message: str = "Not found"
    status: int = 404


@strawberry.type
class BadRequestError:
    message: str = "Bad request"
    status: int = 400
