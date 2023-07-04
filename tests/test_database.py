import asyncio
import pytest
from typing import Dict, Any, List, cast
from petstore import errors
from petstore.database import Database


def cast_to_item(a: Any) -> Dict[str, Any]:
    return cast(Dict[str, Any], a)


def cast_to_items(a: Any) -> List[Dict[str, Any]]:
    return cast(List[Dict[str, Any]], a)


def cast_to_deleted_item(a: Any) -> Dict[str, str]:
    return cast(Dict[str, str], a)


def cast_to_page(a: Any) -> Dict[str, Any]:
    return cast(Dict[str, Any], a)


@pytest.mark.asyncio
async def test_creates_and_gets_pet(database: Database) -> None:
    created_pet = cast_to_item(await database.create_item({"name": "Max"}))
    fetched_pet = cast_to_item(await database.get_item(created_pet["id"]))
    assert fetched_pet["name"] == "Max"


@pytest.mark.asyncio
async def test_creating_pet_with_id_returns_bad_request_error(
    database: Database,
) -> None:
    bad_request_error = await database.create_item(
        {
            "name": "Max",
            "id": "non_existent_pet_id",
        },
    )
    assert isinstance(bad_request_error, errors.BadRequestError)


@pytest.mark.asyncio
async def test_getting_non_existent_pet_returns_not_found_error(
    database: Database,
) -> None:
    not_found_error = await database.get_item("non_existent_pet_id")
    assert isinstance(not_found_error, errors.NotFoundError)


@pytest.mark.asyncio
async def test_creates_and_gets_pets(database: Database) -> None:
    created_pets = cast_to_items(
        await database.create_items(
            [
                {"name": "Max 1"},
                {"name": "Max 2"},
            ],
        )
    )
    [fetched_pet_1, fetched_pet_2] = cast_to_items(
        await database.get_items([pet["id"] for pet in created_pets]),
    )
    assert fetched_pet_1["name"] == "Max 1"
    assert fetched_pet_2["name"] == "Max 2"


@pytest.mark.asyncio
async def test_creating_pets_with_ids_returns_bad_request_error(
    database: Database,
) -> None:
    bad_request_error = cast_to_items(
        await database.create_items(
            [
                {"name": "Max 1"},
                {"name": "Max 2", "id": "non_existent_pet_id"},
            ],
        )
    )
    assert isinstance(bad_request_error, errors.BadRequestError)


@pytest.mark.asyncio
async def test_getting_non_existent_pets_returns_not_found_error(
    database: Database,
) -> None:
    created_pet = cast_to_item(await database.create_item({"name": "Max"}))

    not_found_error = await database.get_items(
        [created_pet["id"], "non_existent_pet_id"]
    )

    assert isinstance(not_found_error, errors.NotFoundError)


@pytest.mark.asyncio
async def test_updates_pet(database: Database) -> None:
    created_pet = cast_to_item(await database.create_item({"name": "Max"}))
    fetched_pet = cast_to_item(await database.get_item(created_pet["id"]))
    updated_pet = cast_to_item(
        await database.update_item({**fetched_pet, "name": "Max 2"}),
    )
    refetched_pet = cast_to_item(await database.get_item(created_pet["id"]))

    assert fetched_pet["name"] == "Max"
    assert updated_pet["name"] == "Max 2"
    assert updated_pet == refetched_pet


@pytest.mark.asyncio
async def test_updating_non_existent_pet_returns_not_found_error(
    database: Database,
) -> None:
    not_found_error = cast_to_item(
        await database.update_item({"id": "non_existent_pet_id", "name": "Max 2"}),
    )
    assert isinstance(not_found_error, errors.NotFoundError)


@pytest.mark.asyncio
async def test_updating_pet_without_id_returns_bad_request_error(
    database: Database,
) -> None:
    created_pet = cast_to_item(await database.create_item({"name": "Max"}))

    del created_pet["id"]

    bad_request_error = cast_to_item(
        await database.update_item({**created_pet, "name": "Max 2"}),
    )
    assert isinstance(bad_request_error, errors.BadRequestError)


@pytest.mark.asyncio
async def test_updates_pets(database: Database) -> None:
    created_pet_1 = cast_to_item(await database.create_item({"name": "Max 1"}))
    created_pet_2 = cast_to_item(await database.create_item({"name": "Max 2"}))
    created_pet_3 = cast_to_item(await database.create_item({"name": "Max 3"}))

    [updated_pet_1, updated_pet_3] = cast_to_items(
        await database.update_items(
            [
                {**created_pet_1, "name": "Maximus 1"},
                {**created_pet_3, "name": "Maximus 3"},
            ],
        ),
    )

    fetched_pet_1 = cast_to_item(await database.get_item(created_pet_1["id"]))
    fetched_pet_2 = cast_to_item(await database.get_item(created_pet_2["id"]))
    fetched_pet_3 = cast_to_item(await database.get_item(created_pet_3["id"]))

    assert fetched_pet_1["name"] == "Maximus 1"
    assert fetched_pet_2["name"] == "Max 2"
    assert fetched_pet_3["name"] == "Maximus 3"

    assert fetched_pet_1 == updated_pet_1
    assert fetched_pet_2 == created_pet_2
    assert fetched_pet_3 == updated_pet_3


@pytest.mark.asyncio
async def test_updating_non_existent_pets_returns_not_found_error(
    database: Database,
) -> None:
    created_pet_1 = cast_to_item(await database.create_item({"name": "Max 1"}))
    created_pet_2 = cast_to_item(await database.create_item({"name": "Max 2"}))

    await database.delete_item(created_pet_2["id"])

    not_found_error = cast_to_items(
        await database.update_items(
            [
                {**created_pet_1, "name": "Maximus 1"},
                {**created_pet_2, "name": "Maximus 2"},
            ],
        ),
    )

    assert isinstance(not_found_error, errors.NotFoundError)


@pytest.mark.asyncio
async def test_updating_pets_without_ids_returns_bad_request_error(
    database: Database,
) -> None:
    created_pet_1 = cast_to_item(await database.create_item({"name": "Max 1"}))
    created_pet_2 = cast_to_item(await database.create_item({"name": "Max 2"}))

    del created_pet_2["id"]

    bad_request_error = cast_to_items(
        await database.update_items(
            [
                {**created_pet_1, "name": "Maximus 1"},
                {**created_pet_2, "name": "Maximus 2"},
            ],
        ),
    )

    assert isinstance(bad_request_error, errors.BadRequestError)


@pytest.mark.asyncio
async def test_patches_pet(database: Database) -> None:
    created_pet = cast_to_item(
        await database.create_item({"name": "Max", "category": "cat"}),
    )
    patched_pet = cast_to_item(
        await database.patch_item({"id": created_pet["id"], "category": "dog"}),
    )
    fetched_pet = cast_to_item(await database.get_item(created_pet["id"]))

    assert created_pet["category"] == "cat"
    assert patched_pet["category"] == "dog"
    assert patched_pet == fetched_pet


@pytest.mark.asyncio
async def test_patching_pet_without_id_returns_bad_request_error(
    database: Database,
) -> None:
    bad_request_error = await database.patch_item({"category": "dog"})
    assert isinstance(bad_request_error, errors.BadRequestError)


@pytest.mark.asyncio
async def test_patching_non_existent_pet_returns_not_found_error(
    database: Database,
) -> None:
    not_found_error = await database.patch_item(
        {"id": "non_existent_pet_id", "category": "dog"}
    )
    assert isinstance(not_found_error, errors.NotFoundError)


@pytest.mark.asyncio
async def test_patches_pets(database: Database) -> None:
    created_pet_1 = cast_to_item(
        await database.create_item({"name": "Max 3", "category": "cat"}),
    )
    created_pet_2 = cast_to_item(
        await database.create_item({"name": "Max 2", "category": "cat"}),
    )
    created_pet_3 = cast_to_item(
        await database.create_item({"name": "Max 3", "category": "cat"}),
    )
    [patched_pet_1, patched_pet_3] = cast_to_items(
        await database.patch_items(
            [
                {"id": created_pet_1["id"], "category": "dog"},
                {"id": created_pet_3["id"], "category": "snake"},
            ],
        ),
    )
    fetched_pet_1 = cast_to_item(await database.get_item(created_pet_1["id"]))
    fetched_pet_2 = cast_to_item(await database.get_item(created_pet_2["id"]))
    fetched_pet_3 = cast_to_item(await database.get_item(created_pet_3["id"]))

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
async def test_patching_pets_without_ids_returns_bad_request_error(
    database: Database,
) -> None:
    created_pet_1 = cast_to_item(
        await database.create_item({"name": "Max 3", "category": "cat"}),
    )
    await database.create_item({"name": "Max 2", "category": "cat"})

    bad_request_error = await database.patch_items(
        [
            {"id": created_pet_1["id"], "category": "dog"},
            {"category": "dog"},
        ],
    )

    assert isinstance(bad_request_error, errors.BadRequestError)


@pytest.mark.asyncio
async def test_patching_non_existent_pets_returns_not_found_error(
    database: Database,
) -> None:
    created_pet_1 = cast_to_item(
        await database.create_item({"name": "Max 3", "category": "cat"}),
    )

    not_found_error = await database.patch_items(
        [
            {"id": created_pet_1["id"], "category": "dog"},
            {"id": "non_existent_pet_id", "category": "dog"},
        ],
    )

    assert isinstance(not_found_error, errors.NotFoundError)


@pytest.mark.asyncio
async def test_deletes_pet(database: Database) -> None:
    created_pet = cast_to_item(await database.create_item({"name": "Max"}))

    deleted_pet = cast_to_deleted_item(await database.delete_item(created_pet["id"]))
    assert deleted_pet == {"id": created_pet["id"]}

    not_found_error = await database.get_item(created_pet["id"])
    assert isinstance(not_found_error, errors.NotFoundError)


@pytest.mark.asyncio
async def test_deleting_non_existent_pet_returns_not_found_error(
    database: Database,
) -> None:
    not_found_error = await database.delete_item("non_existent_pet_id")
    assert isinstance(not_found_error, errors.NotFoundError)


@pytest.mark.asyncio
async def test_deletes_pets(database: Database) -> None:
    created_pet_1 = cast_to_item(await database.create_item({"name": "Max"}))
    created_pet_2 = cast_to_item(await database.create_item({"name": "Max"}))
    created_pet_3 = cast_to_item(await database.create_item({"name": "Max"}))

    [deleted_pet_1, deleted_pet_3] = cast_to_deleted_item(
        await database.delete_items(
            [
                created_pet_1["id"],
                created_pet_3["id"],
            ],
        )
    )
    assert deleted_pet_1 == {"id": created_pet_1["id"]}
    assert deleted_pet_3 == {"id": created_pet_3["id"]}

    not_found_error_1 = await database.get_item(created_pet_1["id"])
    assert isinstance(not_found_error_1, errors.NotFoundError)

    not_found_error_2 = await database.get_item(created_pet_2["id"])
    assert not isinstance(not_found_error_2, errors.NotFoundError)

    not_found_error_3 = await database.get_item(created_pet_3["id"])
    assert isinstance(not_found_error_3, errors.NotFoundError)


@pytest.mark.asyncio
async def test_deleting_non_existent_pets_returns_not_found_error(
    database: Database,
) -> None:
    created_pet_1 = cast_to_item(await database.create_item({"name": "Max"}))
    created_pet_2 = cast_to_item(await database.create_item({"name": "Max"}))

    await database.delete_item(created_pet_2["id"])

    not_found_error = cast_to_deleted_item(
        await database.delete_items(
            [
                created_pet_1["id"],
                created_pet_2["id"],
            ],
        )
    )
    assert isinstance(not_found_error, errors.NotFoundError)


@pytest.mark.asyncio
async def test_lists_pets(database: Database) -> None:
    cast_to_item(await database.create_item({"name": "Max 1"}))
    cast_to_item(await database.create_item({"name": "Max 2"}))
    cast_to_item(await database.create_item({"name": "Max 3"}))
    cast_to_item(await database.create_item({"name": "Max 4"}))
    cast_to_item(await database.create_item({"name": "Max 5"}))

    pets_page_default = await database.list_items()

    assert pets_page_default["page"] == 1
    assert pets_page_default["size"] == 20
    assert pets_page_default["total_pages"] == 1
    assert len(pets_page_default["items"]) == 5
    assert pets_page_default["items"][0]["name"] == "Max 1"
    assert pets_page_default["items"][1]["name"] == "Max 2"
    assert pets_page_default["items"][2]["name"] == "Max 3"
    assert pets_page_default["items"][3]["name"] == "Max 4"
    assert pets_page_default["items"][4]["name"] == "Max 5"

    pets_page_1 = await database.list_items(size=3, page=1)

    assert pets_page_1["page"] == 1
    assert pets_page_1["size"] == 3
    assert pets_page_1["total_pages"] == 2
    assert len(pets_page_1["items"]) == 3
    assert pets_page_1["items"][0]["name"] == "Max 1"
    assert pets_page_1["items"][1]["name"] == "Max 2"
    assert pets_page_1["items"][2]["name"] == "Max 3"

    pets_page_2 = await database.list_items(size=3, page=2)

    assert pets_page_2["page"] == 2
    assert pets_page_2["size"] == 3
    assert pets_page_2["total_pages"] == 2
    assert len(pets_page_2["items"]) == 2
    assert pets_page_2["items"][0]["name"] == "Max 4"
    assert pets_page_2["items"][1]["name"] == "Max 5"


@pytest.mark.asyncio
async def test_counts_pets(database: Database) -> None:
    cast_to_item(await database.create_item({"name": "Max 1"}))
    cast_to_item(await database.create_item({"name": "Max 2"}))
    cast_to_item(await database.create_item({"name": "Max 3"}))
    cast_to_item(await database.create_item({"name": "Max 4"}))
    cast_to_item(await database.create_item({"name": "Max 5"}))

    count = await database.count_items()
    assert count == 5


@pytest.mark.asyncio
async def test_subscribes_to_pet_by_id_update_messages(database: Database) -> None:
    created_pet = cast_to_item(await database.create_item({"name": "Max"}))

    messages = []

    async def collect_messages(item_id: str) -> None:
        async for message in database.subscribe_to_item_by_id(item_id):
            messages.append(message)

    collecting_messages = asyncio.create_task(collect_messages(created_pet["id"]))

    await asyncio.sleep(0)
    updated_item_1 = await database.update_item({**created_pet, "name": "Max 2"})
    updated_item_2 = await database.update_item({**created_pet, "name": "Max 3"})
    await asyncio.sleep(0)

    collecting_messages.cancel()

    [update_message_1, update_message_2] = messages
    assert update_message_1["type"] == "update"
    assert update_message_1["data"] == updated_item_1
    assert update_message_2["type"] == "update"
    assert update_message_2["data"] == updated_item_2


@pytest.mark.asyncio
async def test_subscribes_to_pet_by_id_delete_messages(database: Database) -> None:
    created_pet = cast_to_item(await database.create_item({"name": "Max"}))

    messages = []

    async def collect_messages(item_id: str) -> None:
        async for message in database.subscribe_to_item_by_id(item_id):
            messages.append(message)

    collecting_messages = asyncio.create_task(collect_messages(created_pet["id"]))

    await asyncio.sleep(0)
    deleted_item_1 = await database.delete_item(created_pet["id"])
    await asyncio.sleep(0)

    collecting_messages.cancel()

    [delete_message] = messages
    assert delete_message["type"] == "delete"
    assert delete_message["data"] == deleted_item_1


@pytest.mark.asyncio
async def test_subscribing_to_non_existent_pet_by_id_returns_not_found_error(
    database: Database,
) -> None:
    with pytest.raises(Exception, match="Not found"):
        async for message in database.subscribe_to_item_by_id("non_existent_pet_id"):
            pass


@pytest.mark.asyncio
async def test_subscribes_to_pets_by_id_update_messages(
    database: Database,
) -> None:
    created_pet_1 = cast_to_item(await database.create_item({"name": "Max 1"}))
    created_pet_2 = cast_to_item(await database.create_item({"name": "Max 2"}))
    created_pet_3 = cast_to_item(await database.create_item({"name": "Max 3"}))

    messages = []

    async def collect_messages(item_ids: List[str]) -> None:
        async for message in database.subscribe_to_items_by_id(item_ids):
            messages.append(message)

    collecting_messages = asyncio.create_task(
        collect_messages([created_pet_1["id"], created_pet_2["id"]])
    )

    await asyncio.sleep(0)
    updated_item_1 = await database.update_item({**created_pet_1, "name": "Maximus 1"})
    updated_item_2 = await database.update_item({**created_pet_2, "name": "Maximus 2"})
    await database.update_item({**created_pet_3, "name": "Maximus 3"})
    await asyncio.sleep(0)

    collecting_messages.cancel()

    [update_message_1, update_message_2] = messages
    assert update_message_1["type"] == "update"
    assert update_message_1["data"] == updated_item_1
    assert update_message_2["type"] == "update"
    assert update_message_2["data"] == updated_item_2


@pytest.mark.asyncio
async def test_subscribes_to_pets_by_id_delete_messages(
    database: Database,
) -> None:
    created_pet_1 = cast_to_item(await database.create_item({"name": "Max 1"}))
    created_pet_2 = cast_to_item(await database.create_item({"name": "Max 2"}))
    created_pet_3 = cast_to_item(await database.create_item({"name": "Max 3"}))

    messages = []

    async def collect_messages(item_ids: List[str]) -> None:
        async for message in database.subscribe_to_items_by_id(item_ids):
            messages.append(message)

    collecting_messages = asyncio.create_task(
        collect_messages([created_pet_1["id"], created_pet_3["id"]])
    )

    await asyncio.sleep(0)
    deleted_item_1 = await database.delete_item(created_pet_1["id"])
    await database.delete_item(created_pet_2["id"])
    deleted_item_3 = await database.delete_item(created_pet_3["id"])
    await asyncio.sleep(0)

    collecting_messages.cancel()

    [update_message_1, update_message_2] = messages
    assert update_message_1["type"] == "delete"
    assert update_message_1["data"] == deleted_item_1
    assert update_message_2["type"] == "delete"
    assert update_message_2["data"] == deleted_item_3


@pytest.mark.asyncio
async def test_subscribing_to_non_existent_pets_by_id_returns_not_found_error(
    database: Database,
) -> None:
    with pytest.raises(Exception, match="Not found"):
        async for message in database.subscribe_to_items_by_id(["non_existent_pet_id"]):
            pass


@pytest.mark.asyncio
async def test_subscribes_to_pets_list_create_messages(
    database: Database,
) -> None:
    messages = []

    async def collect_messages() -> None:
        async for message in database.subscribe_to_list():
            messages.append(message)

    collecting_messages = asyncio.create_task(collect_messages())

    await asyncio.sleep(0)
    created_pet_1 = cast_to_item(await database.create_item({"name": "Max 1"}))
    created_pet_2 = cast_to_item(await database.create_item({"name": "Max 2"}))
    await asyncio.sleep(0)

    collecting_messages.cancel()

    [update_message_1, update_message_2] = messages
    assert update_message_1["type"] == "create"
    assert update_message_1["data"] == created_pet_1
    assert update_message_2["type"] == "create"
    assert update_message_2["data"] == created_pet_2


@pytest.mark.asyncio
async def test_subscribes_to_pets_list_delete_messages(
    database: Database,
) -> None:
    created_pet_1 = cast_to_item(await database.create_item({"name": "Max 1"}))
    created_pet_2 = cast_to_item(await database.create_item({"name": "Max 2"}))

    messages = []

    async def collect_messages() -> None:
        async for message in database.subscribe_to_list():
            messages.append(message)

    collecting_messages = asyncio.create_task(collect_messages())

    await asyncio.sleep(0)
    deleted_pet_1 = cast_to_item(await database.delete_item(created_pet_1["id"]))
    deleted_pet_2 = cast_to_item(await database.delete_item(created_pet_2["id"]))
    await asyncio.sleep(0)

    collecting_messages.cancel()

    [update_message_1, update_message_2] = messages
    assert update_message_1["type"] == "delete"
    assert update_message_1["data"] == deleted_pet_1
    assert update_message_2["type"] == "delete"
    assert update_message_2["data"] == deleted_pet_2
