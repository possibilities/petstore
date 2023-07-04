import pytest
from typing import Callable


@pytest.mark.asyncio
async def test_creates_pet(client: Callable) -> None:
    created_pet = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max", "category": "cat"}},
    )
    fetched_pet = await client(
        """
        query GetPet($id: ID!) { getPet(id: $id) { ... on Pet { name } } }
        """,
        {"id": created_pet["id"]},
    )
    assert fetched_pet["name"] == "Max"


@pytest.mark.asyncio
async def test_creating_pet_returns_unexpected_error_when_api_broken(
    broken_client: Callable,
) -> None:
    unexpected_error = await broken_client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on UnexpectedError { message status } }
        }
        """,
        {"input": {"name": "Max", "category": "cat"}},
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"


@pytest.mark.asyncio
async def test_creates_pets(client: Callable) -> None:
    created_pets = await client(
        """
        mutation CreatePets($input: CreatePetsInput!) {
            createPets(input: $input) { ... on Pets { pets { id name category } } }
        }
        """,
        {
            "input": {
                "pets": [
                    {"name": "Max 1", "category": "cat"},
                    {"name": "Max 2", "category": "cat"},
                ]
            }
        },
    )
    fetched_pets = await client(
        """
        query GetPets($ids: [ID!]!) {
            getPets(ids: $ids) { ... on Pets { pets { name } } }
        }
        """,
        {"ids": [pet["id"] for pet in created_pets["pets"]]},
    )
    assert fetched_pets["pets"] == [{"name": "Max 1"}, {"name": "Max 2"}]


@pytest.mark.asyncio
async def test_creating_pets_returns_unexpected_error_when_api_broken(
    broken_client: Callable,
) -> None:
    unexpected_error = await broken_client(
        """
        mutation CreatePets($input: CreatePetsInput!) {
            createPets(input: $input) { ... on UnexpectedError { message status } }
        }
        """,
        {
            "input": {
                "pets": [
                    {"name": "Max 1", "category": "cat"},
                    {"name": "Max 2", "category": "cat"},
                ]
            }
        },
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"


@pytest.mark.asyncio
async def test_updates_pet(client: Callable) -> None:
    created_pet = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max", "category": "cat"}},
    )
    fetched_pet = await client(
        """
        query GetPet($id: ID!) {
            getPet(id: $id) { ... on Pet { id name category } }
        }
        """,
        {"id": created_pet["id"]},
    )
    updated_pet = await client(
        """
        mutation UpdatePet($input: UpdatePetInput!) {
            updatePet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {**fetched_pet, "name": "Max 2"}},
    )
    refetched_pet = await client(
        """
        query GetPet($id: ID!) {
            getPet(id: $id) { ... on Pet { id name category } }
        }
        """,
        {"id": created_pet["id"]},
    )
    assert fetched_pet["name"] == "Max"
    assert updated_pet["name"] == "Max 2"
    assert updated_pet == refetched_pet


@pytest.mark.asyncio
async def test_updating_pet_returns_not_found_error(client: Callable) -> None:
    not_found_error = await client(
        """
        mutation UpdatePet($input: UpdatePetInput!) {
            updatePet(input: $input) {
                ... on NotFoundError { message status }
            }
        }
        """,
        {
            "input": {
                "id": "non_existent_pet_id",
                "name": "Max 2",
                "category": "cat",
            }
        },
    )
    assert not_found_error["status"] == 404
    assert not_found_error["message"] == "Not found"


@pytest.mark.asyncio
async def test_updating_pet_returns_unexpected_error_when_api_broken(
    client: Callable,
    broken_client: Callable,
) -> None:
    created_pet = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max", "category": "cat"}},
    )
    unexpected_error = await broken_client(
        """
        mutation UpdatePet($input: UpdatePetInput!) {
            updatePet(input: $input) {
                ... on UnexpectedError { message status }
            }
        }
        """,
        {"input": {**created_pet, "name": "Max 2"}},
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"


@pytest.mark.asyncio
async def test_updates_pets(client: Callable) -> None:
    created_pet_1 = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max 1", "category": "cat"}},
    )
    created_pet_2 = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max 2", "category": "cat"}},
    )
    created_pet_3 = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max 3", "category": "cat"}},
    )
    updated_pets = await client(
        """
        mutation UpdatePets($input: UpdatePetsInput!) {
            updatePets(input: $input) { ... on Pets { pets { id name category } } }
        }
        """,
        {
            "input": {
                "pets": [
                    {**created_pet_1, "name": "Maximus 1"},
                    {**created_pet_3, "name": "Maximus 3"},
                ]
            }
        },
    )
    [updated_pet_1, updated_pet_3] = updated_pets["pets"]
    fetched_pet_1 = await client(
        """
        query GetPet($id: ID!) {
            getPet(id: $id) { ... on Pet { id name category } }
        }
        """,
        {"id": created_pet_1["id"]},
    )
    fetched_pet_2 = await client(
        """
        query GetPet($id: ID!) {
            getPet(id: $id) { ... on Pet { id name category } }
        }
        """,
        {"id": created_pet_2["id"]},
    )
    fetched_pet_3 = await client(
        """
        query GetPet($id: ID!) {
            getPet(id: $id) { ... on Pet { id name category } }
        }
        """,
        {"id": created_pet_3["id"]},
    )
    assert fetched_pet_1["name"] == "Maximus 1"
    assert fetched_pet_2["name"] == "Max 2"
    assert fetched_pet_3["name"] == "Maximus 3"
    assert fetched_pet_1 == updated_pet_1
    assert fetched_pet_2 == created_pet_2
    assert fetched_pet_3 == updated_pet_3


@pytest.mark.asyncio
async def test_updating_non_existent_pets_returns_not_found_error(
    client: Callable,
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
    await client(
        """
        mutation DeletePet($id: ID!) {
            deletePet(id: $id) { ... on DeletedPet { id } }
        }
        """,
        {"id": created_pet_2["id"]},
    )
    not_found_error = await client(
        """
        mutation UpdatePets($input: UpdatePetsInput!) {
            updatePets(input: $input) {
                ... on NotFoundError { message status }
            }
        }
        """,
        {
            "input": {
                "pets": [
                    {**created_pet_1, "name": "Maximus 1"},
                    {**created_pet_2, "name": "Maximus 3"},
                ]
            }
        },
    )
    assert not_found_error["status"] == 404
    assert not_found_error["message"] == "Not found"


@pytest.mark.asyncio
async def test_updating_pets_returns_unexpected_error_when_api_broken(
    client: Callable,
    broken_client: Callable,
) -> None:
    created_pet_1 = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max 1", "category": "cat"}},
    )
    created_pet_2 = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max 2", "category": "cat"}},
    )
    unexpected_error = await broken_client(
        """
        mutation UpdatePets($input: UpdatePetsInput!) {
            updatePets(input: $input) {
                ... on UnexpectedError { message status }
            }
        }
        """,
        {
            "input": {
                "pets": [
                    {**created_pet_1, "name": "Maximus 1"},
                    {**created_pet_2, "name": "Maximus 3"},
                ]
            }
        },
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"


@pytest.mark.asyncio
async def test_patches_pet(client: Callable) -> None:
    created_pet = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max", "category": "cat"}},
    )
    patched_pet = await client(
        """
        mutation PatchPet($input: PatchPetInput!) {
            patchPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"id": created_pet["id"], "category": "dog"}},
    )
    fetched_pet = await client(
        """
        query GetPet($id: ID!) {
            getPet(id: $id) { ... on Pet { id name category } }
        }
        """,
        {"id": created_pet["id"]},
    )
    assert created_pet["category"] == "cat"
    assert patched_pet["category"] == "dog"
    assert patched_pet == fetched_pet


@pytest.mark.asyncio
async def test_patching_pet_returns_not_found_error(client: Callable) -> None:
    not_found_error = await client(
        """
        mutation PatchPet($input: PatchPetInput!) {
            patchPet(input: $input) { ... on NotFoundError { message status } }
        }
        """,
        {"input": {"id": "non_existent_pet_id", "category": "dog"}},
    )
    assert not_found_error["status"] == 404
    assert not_found_error["message"] == "Not found"


@pytest.mark.asyncio
async def test_patching_pet_returns_unexpected_error_when_api_broken(
    client: Callable,
    broken_client: Callable,
) -> None:
    created_pet = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max", "category": "cat"}},
    )
    unexpected_error = await broken_client(
        """
        mutation PatchPet($input: PatchPetInput!) {
            patchPet(input: $input) {
                ... on UnexpectedError { message status }
            }
        }
        """,
        {"input": {"id": created_pet["id"], "category": "dog"}},
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"


@pytest.mark.asyncio
async def test_patches_pets(client: Callable) -> None:
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
    patched_pets = await client(
        """
        mutation PatchPets($input: PatchPetsInput!) {
            patchPets(input: $input) {
                ... on Pets { pets { id name category } }
            }
        }
        """,
        {
            "input": {
                "pets": [
                    {"id": created_pet_1["id"], "category": "dog"},
                    {"id": created_pet_3["id"], "category": "snake"},
                ]
            }
        },
    )
    [patched_pet_1, patched_pet_3] = patched_pets["pets"]
    get_pet = """
    query GetPet($id: ID!) {
        getPet(id: $id) { ... on Pet { id name category } }
    }
    """
    fetched_pet_1 = await client(get_pet, {"id": created_pet_1["id"]})
    fetched_pet_2 = await client(get_pet, {"id": created_pet_2["id"]})
    fetched_pet_3 = await client(get_pet, {"id": created_pet_3["id"]})
    assert created_pet_1["category"] == "cat"
    assert patched_pet_1["category"] == "dog"
    assert patched_pet_1 == fetched_pet_1
    assert created_pet_2["category"] == "cat"
    assert fetched_pet_2 == created_pet_2
    assert created_pet_2 == fetched_pet_2
    assert created_pet_3["category"] == "cat"
    assert patched_pet_3["category"] == "snake"
    assert patched_pet_3 == fetched_pet_3


@pytest.mark.asyncio
async def test_patching_non_existent_pets_returns_not_found_error(
    client: Callable,
) -> None:
    created_pet = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max", "category": "cat"}},
    )
    not_found_error = await client(
        """
        mutation PatchPets($input: PatchPetsInput!) {
            patchPets(input: $input) {
                ... on NotFoundError { message status }
            }
        }
        """,
        {
            "input": {
                "pets": [
                    {"id": created_pet["id"], "category": "dog"},
                    {"id": "non_existent_pet_id", "category": "snake"},
                ]
            }
        },
    )
    assert not_found_error["status"] == 404
    assert not_found_error["message"] == "Not found"


@pytest.mark.asyncio
async def test_patching_pets_returns_unexpected_error_when_api_broken(
    client: Callable,
    broken_client: Callable,
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
    unexpected_error_error = await broken_client(
        """
        mutation PatchPets($input: PatchPetsInput!) {
            patchPets(input: $input) {
                ... on UnexpectedError { message status }
            }
        }
        """,
        {
            "input": {
                "pets": [
                    {"id": created_pet_1["id"], "category": "dog"},
                    {"id": created_pet_2["id"], "category": "snake"},
                ]
            }
        },
    )

    assert unexpected_error_error["status"] == 500
    assert unexpected_error_error["message"] == "Unexpected error"


@pytest.mark.asyncio
async def test_deletes_pet(client: Callable) -> None:
    created_pet = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max", "category": "cat"}},
    )
    deleted_pet = await client(
        """
        mutation DeletePet($id: ID!) {
            deletePet(id: $id) { ... on DeletedPet { id } }
        }
        """,
        {"id": created_pet["id"]},
    )
    assert deleted_pet == {"id": created_pet["id"]}
    not_found_error = await client(
        """
        query GetPet($id: ID!) {
            getPet(id: $id) { ... on NotFoundError { message status } }
        }
        """,
        {"id": created_pet["id"]},
    )
    assert not_found_error["status"] == 404
    assert not_found_error["message"] == "Not found"


@pytest.mark.asyncio
async def test_deleting_non_existent_pet_returns_not_found_error(
    client: Callable,
) -> None:
    not_found_error = await client(
        """
        mutation DeletePet($id: ID!) {
            deletePet(id: $id) { ... on NotFoundError { message status } }
        }
        """,
        {"id": "non_existent_pet_id"},
    )
    assert not_found_error["status"] == 404
    assert not_found_error["message"] == "Not found"


@pytest.mark.asyncio
async def test_deleting_pet_returns_unexpected_error_when_api_broken(
    client: Callable,
    broken_client: Callable,
) -> None:
    created_pet = await client(
        """
        mutation CreatePet($input: CreatePetInput!) {
            createPet(input: $input) { ... on Pet { id name category } }
        }
        """,
        {"input": {"name": "Max", "category": "cat"}},
    )
    unexpected_error = await broken_client(
        """
        mutation DeletePet($id: ID!) {
            deletePet(id: $id) { ... on UnexpectedError { message status } }
        }
        """,
        {"id": created_pet["id"]},
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"


@pytest.mark.asyncio
async def test_deletes_pets(client: Callable) -> None:
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
    deleted_pets = await client(
        """
        mutation DeletePets($ids: [ID!]!) {
            deletePets(ids: $ids) { ... on DeletedPets { pets { id } } }
        }
        """,
        {"ids": [created_pet_1["id"], created_pet_3["id"]]},
    )
    [deleted_pet_1, deleted_pet_3] = deleted_pets["pets"]
    assert deleted_pet_1 == {"id": created_pet_1["id"]}
    assert deleted_pet_3 == {"id": created_pet_3["id"]}
    get_pet_not_found_error = """
    query GetPet($id: ID!) {
        getPet(id: $id) { ... on NotFoundError { message status } }
    }
    """
    not_found_error_1 = await client(
        get_pet_not_found_error, {"id": created_pet_1["id"]}
    )
    assert not_found_error_1["status"] == 404
    assert not_found_error_1["message"] == "Not found"
    not_found_error_2 = await client(
        get_pet_not_found_error,
        {"id": created_pet_2["id"]},
    )
    assert "status" not in not_found_error_2
    assert "message" not in not_found_error_2
    not_found_error_3 = await client(
        get_pet_not_found_error, {"id": created_pet_1["id"]}
    )
    assert not_found_error_3["status"] == 404
    assert not_found_error_3["message"] == "Not found"


@pytest.mark.asyncio
async def test_deleting_non_existent_pets_returns_not_found_error(
    client: Callable,
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
    await client(
        """
        mutation DeletePet($id: ID!) {
            deletePet(id: $id) { ... on DeletedPet { id } }
        }
        """,
        {"id": created_pet_2["id"]},
    )
    not_found_error = await client(
        """
        mutation DeletePets($ids: [ID!]!) {
            deletePets(ids: $ids) { ... on NotFoundError { message status } }
        }
        """,
        {"ids": [created_pet_1["id"], created_pet_2["id"]]},
    )
    assert not_found_error["status"] == 404
    assert not_found_error["message"] == "Not found"


@pytest.mark.asyncio
async def test_deleting_pets_returns_unexpected_error_when_api_broken(
    client: Callable,
    broken_client: Callable,
) -> None:
    create_pet = """
    mutation CreatePet($input: CreatePetInput!) {
        createPet(input: $input) { ... on Pet { id name category } }
    }
    """
    created_pet_1 = await client(
        create_pet, {"input": {"name": "Max", "category": "cat"}}
    )
    created_pet_2 = await client(
        create_pet, {"input": {"name": "Max", "category": "cat"}}
    )
    unexpected_error = await broken_client(
        """
        mutation DeletePets($ids: [ID!]!) {
            deletePets(ids: $ids) { ... on UnexpectedError { message status } }
        }
        """,
        {"ids": [created_pet_1["id"], created_pet_2["id"]]},
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"
