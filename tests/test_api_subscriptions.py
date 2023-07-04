import pytest
from typing import Callable


@pytest.mark.asyncio
async def test_subscribes_to_pet_by_id_update_messages(
    client: Callable,
    subscription_client: Callable,
    subscription_messages: Callable,
) -> None:
    create_pet = """
    mutation CreatePet($input: CreatePetInput!) {
        createPet(input: $input) { ... on Pet { id name category } }
    }
    """
    created_pet_1 = await client(
        create_pet, {"input": {"name": "Max 1", "category": "cat"}}
    )
    created_pet_2 = await client(
        create_pet, {"input": {"name": "Max 2", "category": "cat"}}
    )
    subscription = subscription_client(
        """
        subscription SubscribeToPetById($id: ID!) {
            subscribeToPetById(id: $id) {
                __typename
                ... on PetDeleteMessage { id }
                ... on PetUpdateMessage { id name category }
            }
        }
        """,
        variable_values={"id": created_pet_1["id"]},
    )
    async with subscription_messages(subscription) as messages:
        update_pet = """
        mutation UpdatePet($input: UpdatePetInput!) {
            updatePet(input: $input) { ... on Pet { id name category } }
        }
        """
        pet_1_update_1 = await client(
            update_pet, {"input": {**created_pet_1, "name": "Maximus 1"}}
        )
        pet_1_update_2 = await client(
            update_pet, {"input": {**created_pet_1, "name": "Moxy 1"}}
        )
        pet_2_update_1_causes_no_subscription_message = await client(  # noqa
            update_pet, {"input": {**created_pet_2, "name": "Maximus 1"}}
        )
        [update_message_1, update_message_2] = await messages.wait_for_messages()
        assert update_message_1 == {**pet_1_update_1, "__typename": "PetUpdateMessage"}
        assert update_message_2 == {**pet_1_update_2, "__typename": "PetUpdateMessage"}


@pytest.mark.asyncio
async def test_subscribes_to_pet_by_id_delete_messages(
    client: Callable,
    subscription_client: Callable,
    subscription_messages: Callable,
) -> None:
    delete_pet = """
    mutation CreatePet($input: CreatePetInput!) {
        createPet(input: $input) { ... on Pet { id name category } }
    }
    """
    created_pet_1 = await client(
        delete_pet, {"input": {"name": "Max 1", "category": "cat"}}
    )

    created_pet_2 = await client(
        delete_pet, {"input": {"name": "Max 2", "category": "cat"}}
    )
    subscription = subscription_client(
        """
        subscription SubscribeToPetById($id: ID!) {
            subscribeToPetById(id: $id) {
                __typename
                ... on PetDeleteMessage { id }
                ... on PetUpdateMessage { id name category }
            }
        }
        """,
        variable_values={"id": created_pet_1["id"]},
    )
    async with subscription_messages(subscription) as messages:
        delete_pet = """
        mutation DeletePet($id: ID!) {
            deletePet(id: $id) { ... on DeletedPet { id } }
        }
        """
        deleted_pet_1 = await client(delete_pet, {"id": created_pet_1["id"]})
        deleted_pet_2_causes_no_subscription_message = await client(  # noqa
            delete_pet, {"id": created_pet_2["id"]}
        )
        [delete_message_1] = await messages.wait_for_messages()
        assert delete_message_1 == {**deleted_pet_1, "__typename": "PetDeleteMessage"}


@pytest.mark.asyncio
async def test_subscribing_to_non_existent_pet_by_id_returns_not_found_error(
    client: Callable,
    subscription_client: Callable,
    subscription_messages: Callable,
) -> None:
    subscription = subscription_client(
        """
        subscription SubscribeToPetById($id: ID!) {
            subscribeToPetById(id: $id)
        }
        """,
        variable_values={"id": "non_existent_pet_id"},
    )
    with pytest.raises(Exception, match="Not found"):
        async with subscription_messages(subscription) as messages:
            await messages.wait_for_messages()


@pytest.mark.asyncio
async def test_subscribes_to_pets_by_id_update_messages(
    client: Callable,
    subscription_client: Callable,
    subscription_messages: Callable,
) -> None:
    create_pet = """
    mutation CreatePet($input: CreatePetInput!) {
        createPet(input: $input) { ... on Pet { id name category } }
    }
    """
    created_pet_1 = await client(
        create_pet, {"input": {"name": "Max 1", "category": "cat"}}
    )
    created_pet_2 = await client(
        create_pet, {"input": {"name": "Max 2", "category": "cat"}}
    )
    created_pet_3 = await client(
        create_pet, {"input": {"name": "Max 3", "category": "cat"}}
    )
    subscription = subscription_client(
        """
        subscription SubscribeToPetById($ids: [ID!]!) {
            subscribeToPetsById(ids: $ids) {
                __typename
                ... on PetDeleteMessage { id }
                ... on PetUpdateMessage { id name category }
            }
        }
        """,
        variable_values={"ids": [created_pet_1["id"], created_pet_2["id"]]},
    )
    async with subscription_messages(subscription) as messages:
        update_pet = """
        mutation UpdatePet($input: UpdatePetInput!) {
            updatePet(input: $input) { ... on Pet { id name category } }
        }
        """
        pet_1_update_1 = await client(
            update_pet, {"input": {**created_pet_1, "name": "Maximus 1"}}
        )

        pet_1_update_2 = await client(
            update_pet, {"input": {**created_pet_1, "name": "Moxy 1"}}
        )

        pet_2_update_1 = await client(
            update_pet, {"input": {**created_pet_2, "name": "Maximus 1"}}
        )

        pet_3_update_1_causes_no_subscription_message = await client(  # noqa
            update_pet, {"input": {**created_pet_3, "name": "Maximus 3"}}
        )
        [
            update_message_1,
            update_message_2,
            update_message_3,
        ] = await messages.wait_for_messages()
        assert update_message_1 == {**pet_1_update_1, "__typename": "PetUpdateMessage"}
        assert update_message_2 == {**pet_1_update_2, "__typename": "PetUpdateMessage"}
        assert update_message_3 == {**pet_2_update_1, "__typename": "PetUpdateMessage"}


@pytest.mark.asyncio
async def test_subscribes_to_pets_by_id_delete_messages(
    client: Callable,
    subscription_client: Callable,
    subscription_messages: Callable,
) -> None:
    create_pet = """
    mutation CreatePet($input: CreatePetInput!) {
        createPet(input: $input) { ... on Pet { id name category } }
    }
    """
    created_pet_1 = await client(
        create_pet, {"input": {"name": "Max 1", "category": "cat"}}
    )
    created_pet_2 = await client(
        create_pet, {"input": {"name": "Max 2", "category": "cat"}}
    )
    created_pet_3 = await client(
        create_pet, {"input": {"name": "Max 3", "category": "cat"}}
    )
    subscription = subscription_client(
        """
        subscription SubscribeToPetsById($ids: [ID!]!) {
            subscribeToPetsById(ids: $ids) {
                __typename
                ... on PetDeleteMessage { id }
                ... on PetUpdateMessage { id name category }
            }
        }
        """,
        variable_values={"ids": [created_pet_1["id"], created_pet_2["id"]]},
    )
    async with subscription_messages(subscription) as messages:
        delete_pet = """
        mutation DeletePet($id: ID!) { deletePet(id: $id) { ... on DeletedPet { id } } }
        """
        deleted_pet_1 = await client(delete_pet, {"id": created_pet_1["id"]})
        deleted_pet_2 = await client(delete_pet, {"id": created_pet_2["id"]})
        deleted_pet_3_causes_no_subscription_message = await client(  # noqa
            delete_pet, {"id": created_pet_3["id"]}
        )
        [delete_message_1, delete_message_2] = await messages.wait_for_messages()
        assert delete_message_1 == {**deleted_pet_1, "__typename": "PetDeleteMessage"}
        assert delete_message_2 == {**deleted_pet_2, "__typename": "PetDeleteMessage"}


@pytest.mark.asyncio
async def test_subscribing_to_non_existent_pets_by_id_returns_not_found_error(
    client: Callable,
    subscription_client: Callable,
    subscription_messages: Callable,
) -> None:
    subscription = subscription_client(
        """
        subscription SubscribeToPetsById($ids: [ID!]!) {
            subscribeToPetsById(ids: $ids)
        }
        """,
        variable_values={"ids": ["non_existent_pet_id"]},
    )
    with pytest.raises(Exception, match="Not found"):
        async with subscription_messages(subscription) as messages:
            await messages.wait_for_messages()


@pytest.mark.asyncio
async def test_subscribes_to_pets_list_create_messages(
    client: Callable,
    subscription_client: Callable,
    subscription_messages: Callable,
) -> None:
    subscription = subscription_client(
        """
        subscription SubscribeToPetsList {
            subscribeToPetsList {
                __typename
                ... on PetDeleteMessage { id }
                ... on PetCreateMessage { id name category }
            }
        }
        """,
    )
    async with subscription_messages(subscription) as messages:
        create_pet = """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """
        created_pet_1 = await client(
            create_pet, {"input": {"name": "Max 1", "category": "cat"}}
        )
        created_pet_2 = await client(
            create_pet, {"input": {"name": "Max 2", "category": "cat"}}
        )
        [create_message_1, create_message_2] = await messages.wait_for_messages()
        assert create_message_1 == {**created_pet_1, "__typename": "PetCreateMessage"}
        assert create_message_2 == {**created_pet_2, "__typename": "PetCreateMessage"}


@pytest.mark.asyncio
async def test_subscribes_to_pets_list_delete_messages(
    client: Callable,
    subscription_client: Callable,
    subscription_messages: Callable,
) -> None:
    create_mutation = """
    mutation CreatePet($input: CreatePetInput!) {
        createPet(input: $input) { ... on Pet { id name category } }
    }
    """
    created_pet_1 = await client(
        create_mutation, {"input": {"name": "Max 1", "category": "cat"}}
    )
    created_pet_2 = await client(
        create_mutation, {"input": {"name": "Max 2", "category": "cat"}}
    )
    subscription = subscription_client(
        """
        subscription SubscribeToPetsList {
            subscribeToPetsList {
                __typename
                ... on PetDeleteMessage { id }
                ... on PetCreateMessage { id name category }
            }
        }
        """,
    )
    async with subscription_messages(subscription) as messages:
        delete_query = """
        mutation DeletePet($id: ID!) { deletePet(id: $id) { ... on DeletedPet { id } } }
        """
        deleted_pet_1 = await client(delete_query, {"id": created_pet_1["id"]})
        deleted_pet_2 = await client(delete_query, {"id": created_pet_2["id"]})
        [delete_message_1, delete_message_2] = await messages.wait_for_messages()
        assert delete_message_1 == {**deleted_pet_1, "__typename": "PetDeleteMessage"}
        assert delete_message_2 == {**deleted_pet_2, "__typename": "PetDeleteMessage"}
