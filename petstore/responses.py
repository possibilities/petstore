from typing import Union, AsyncGenerator
from petstore import types

CreatePetResponse = Union[
    types.Pet,
    types.UnexpectedError,
]

CreatePetsResponse = Union[
    types.Pets,
    types.UnexpectedError,
]

GetPetResponse = Union[
    types.Pet,
    types.UnexpectedError,
    types.NotFoundError,
]

GetPetsResponse = Union[
    types.Pets,
    types.UnexpectedError,
    types.NotFoundError,
]

UpdatePetResponse = Union[
    types.Pet,
    types.UnexpectedError,
    types.NotFoundError,
]

UpdatePetsResponse = Union[
    types.Pets,
    types.UnexpectedError,
    types.NotFoundError,
]

PatchPetResponse = Union[
    types.Pet,
    types.UnexpectedError,
    types.NotFoundError,
]

PatchPetsResponse = Union[
    types.Pets,
    types.UnexpectedError,
    types.NotFoundError,
]

DeletePetResponse = Union[
    types.DeletedPet,
    types.UnexpectedError,
    types.NotFoundError,
]

DeletePetsResponse = Union[
    types.DeletedPets,
    types.UnexpectedError,
    types.NotFoundError,
]

ListPetsResponse = Union[
    types.PetPage,
    types.UnexpectedError,
]

PetsCountResponse = Union[
    types.PetsCount,
    types.UnexpectedError,
]

SubscribeToPetByIdResponse = AsyncGenerator[
    types.PetUpdateMessage | types.PetDeleteMessage,
    None,
]

SubscribeToPetsByIdResponse = AsyncGenerator[
    types.PetUpdateMessage | types.PetDeleteMessage,
    None,
]

SubscribeToPetsListResponse = AsyncGenerator[
    types.PetCreateMessage | types.PetDeleteMessage,
    None,
]
