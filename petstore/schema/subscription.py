import strawberry
from petstore.resolvers import subscriptions


@strawberry.type
class Subscription:
    subscribe_to_pet_by_id = strawberry.subscription(
        resolver=subscriptions.subscribe_to_pet_by_id,
    )
    subscribe_to_pets_by_id = strawberry.subscription(
        resolver=subscriptions.subscribe_to_pets_by_id,
    )
    subscribe_to_pets_list = strawberry.subscription(
        resolver=subscriptions.subscribe_to_pets_list,
    )
