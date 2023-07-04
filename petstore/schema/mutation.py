import strawberry
from petstore import responses
from petstore.resolvers import mutations


@strawberry.type
class Mutation:
    create_pet: responses.CreatePetResponse = strawberry.mutation(
        resolver=mutations.create_pet,
    )
    create_pets: responses.CreatePetsResponse = strawberry.mutation(
        resolver=mutations.create_pets,
    )
    update_pet: responses.UpdatePetResponse = strawberry.mutation(
        resolver=mutations.update_pet,
    )
    update_pets: responses.UpdatePetsResponse = strawberry.mutation(
        resolver=mutations.update_pets,
    )
    patch_pet: responses.PatchPetResponse = strawberry.mutation(
        resolver=mutations.patch_pet,
    )
    patch_pets: responses.PatchPetsResponse = strawberry.mutation(
        resolver=mutations.patch_pets,
    )
    delete_pet: responses.DeletePetResponse = strawberry.mutation(
        resolver=mutations.delete_pet,
    )
    delete_pets: responses.DeletePetsResponse = strawberry.mutation(
        resolver=mutations.delete_pets,
    )
