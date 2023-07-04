import strawberry
from petstore import responses
from petstore.resolvers import queries


@strawberry.type
class Query:
    get_pet: responses.GetPetResponse = strawberry.field(
        resolver=queries.get_pet,
    )
    get_pets: responses.GetPetsResponse = strawberry.field(
        resolver=queries.get_pets,
    )
    list_pets: responses.ListPetsResponse = strawberry.field(
        resolver=queries.list_pets,
    )
    count_pets: responses.PetsCountResponse = strawberry.field(
        resolver=queries.count_pets,
    )
