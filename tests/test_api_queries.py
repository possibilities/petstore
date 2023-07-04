import pytest
from .conftest import Callable


@pytest.mark.asyncio
async def test_gets_pet(client: Callable) -> None:
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
async def test_getting_non_existent_pet_returns_not_found_error(
    client: Callable,
) -> None:
    not_found_error = await client(
        """
        query GetPet($id: ID!) {
            getPet(id: $id) { ... on NotFoundError { message status } }
        }
        """,
        {"id": "non_existent_pet_id"},
    )
    assert not_found_error["status"] == 404
    assert not_found_error["message"] == "Not found"


@pytest.mark.asyncio
async def test_getting_pet_returns_unexpected_error_when_api_broken(
    client: Callable, broken_client: Callable
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
        query GetPet($id: ID!) {
            getPet(id: $id) { ... on UnexpectedError { message status } }
        }
        """,
        {"id": created_pet["id"]},
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"


@pytest.mark.asyncio
async def test_gets_pets(client: Callable) -> None:
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
async def test_getting_pets_returns_unexpected_error_when_api_broken(
    client: Callable,
    broken_client: Callable,
) -> None:
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
    unexpected_error = await broken_client(
        """
        query GetPets($ids: [ID!]!) {
            getPets(ids: $ids) { ... on UnexpectedError { message status } }
        }
        """,
        {"ids": [pet["id"] for pet in created_pets["pets"]]},
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"


@pytest.mark.asyncio
async def test_getting_pets_returns_not_found_error(client: Callable) -> None:
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
        query GetPets($ids: [ID!]!) {
            getPets(ids: $ids) { ... on NotFoundError { message status } }
        }
        """,
        {"ids": [created_pet["id"], "non_existent_pet_id"]},
    )
    assert not_found_error["status"] == 404
    assert not_found_error["message"] == "Not found"


@pytest.mark.asyncio
async def test_lists_pets(client: Callable) -> None:
    create_pet = """
    mutation CreatePet($input: CreatePetInput!) {
        createPet(input: $input) { ... on Pet { id name category } }
    }
    """
    await client(create_pet, {"input": {"name": "Max 1", "category": "cat"}})
    await client(create_pet, {"input": {"name": "Max 2", "category": "cat"}})
    await client(create_pet, {"input": {"name": "Max 3", "category": "cat"}})
    await client(create_pet, {"input": {"name": "Max 4", "category": "cat"}})
    await client(create_pet, {"input": {"name": "Max 5", "category": "cat"}})
    pets_page_default = await client(
        """
        query ListPets($input: ListPetsInput!) {
            listPets(input: $input) {
                ... on PetPage {
                    page
                    size
                    totalPages
                    items { id name category }
                }
            }
        }
        """,
        {"input": {}},
    )
    assert pets_page_default["page"] == 1
    assert pets_page_default["size"] == 20
    assert pets_page_default["totalPages"] == 1
    assert len(pets_page_default["items"]) == 5
    assert pets_page_default["items"][0]["name"] == "Max 1"
    assert pets_page_default["items"][1]["name"] == "Max 2"
    assert pets_page_default["items"][2]["name"] == "Max 3"
    assert pets_page_default["items"][3]["name"] == "Max 4"
    assert pets_page_default["items"][4]["name"] == "Max 5"
    pets_page_1 = await client(
        """
        query ListPets($input: ListPetsInput!) {
            listPets(input: $input) {
                ... on PetPage {
                    page
                    size
                    totalPages
                    items { id name category }
                }
            }
        }
        """,
        {"input": {"size": 3, "page": 1}},
    )
    assert pets_page_1["page"] == 1
    assert pets_page_1["size"] == 3
    assert pets_page_1["totalPages"] == 2
    assert len(pets_page_1["items"]) == 3
    assert pets_page_1["items"][0]["name"] == "Max 1"
    assert pets_page_1["items"][1]["name"] == "Max 2"
    assert pets_page_1["items"][2]["name"] == "Max 3"
    pets_page_2 = await client(
        """
        query ListPets($input: ListPetsInput!) {
            listPets(input: $input) {
                ... on PetPage {
                    page
                    size
                    totalPages
                    items { id name category }
                }
            }
        }
        """,
        {"input": {"size": 3, "page": 2}},
    )
    assert pets_page_2["page"] == 2
    assert pets_page_2["size"] == 3
    assert pets_page_2["totalPages"] == 2
    assert len(pets_page_2["items"]) == 2
    assert pets_page_2["items"][0]["name"] == "Max 4"
    assert pets_page_2["items"][1]["name"] == "Max 5"


@pytest.mark.asyncio
async def test_listing_pets_pages_returns_unexpected_error_when_api_broken(
    broken_client: Callable,
) -> None:
    unexpected_error = await broken_client(
        """
        query ListPets($input: ListPetsInput!) {
            listPets(input: $input) {
                ... on UnexpectedError { message status }
            }
        }
        """,
        {"input": {}},
    )
    assert unexpected_error["message"] == "Unexpected error"
    assert unexpected_error["status"] == 500


@pytest.mark.asyncio
async def test_counts_pets(client: Callable) -> None:
    create_pet = """
    mutation CreatePet($input: CreatePetInput!) {
        createPet(input: $input) { ... on Pet { id name category } }
    }
    """
    await client(create_pet, {"input": {"name": "Max 1", "category": "cat"}})
    await client(create_pet, {"input": {"name": "Max 2", "category": "cat"}})
    await client(create_pet, {"input": {"name": "Max 3", "category": "cat"}})
    await client(create_pet, {"input": {"name": "Max 4", "category": "cat"}})
    await client(create_pet, {"input": {"name": "Max 5", "category": "cat"}})
    count = await client("query PetsCount { countPets { ... on PetsCount { count } } }")
    assert count == {"count": 5}


@pytest.mark.asyncio
async def test_counting_pets_returns_unexpected_error_when_api_broken(
    broken_client: Callable,
) -> None:
    unexpected_error = await broken_client(
        "query PetsCount { countPets { ... on UnexpectedError { message status } } }"
    )
    assert unexpected_error["status"] == 500
    assert unexpected_error["message"] == "Unexpected error"
