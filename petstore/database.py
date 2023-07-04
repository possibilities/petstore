import asyncio
import uuid
from petstore import errors
from copy import deepcopy
from typing import Any, Dict, List, cast, AsyncGenerator


class Database:
    def __init__(self, cls: type) -> None:
        self.cls = cls
        self.store: Dict[str, Any] = {}
        self.subscribers: Dict[str, Any] = {}

    async def get_item(self, id: str) -> Dict[str, Any] | errors.NotFoundError:
        try:
            return deepcopy(self.store[self.cls.__name__][id])
        except KeyError:
            return errors.NotFoundError()

    async def get_items(
        self, ids: List[str]
    ) -> List[Dict[str, Any]] | errors.NotFoundError:
        item_dicts = [await self.get_item(id) for id in ids]
        if any(isinstance(item_dict, errors.NotFoundError) for item_dict in item_dicts):
            return errors.NotFoundError()
        return cast(List[Dict[str, Any]], item_dicts)

    async def create_item(
        self, item: Dict[str, Any]
    ) -> Dict[str, Any] | errors.BadRequestError:
        if "id" in item:
            return errors.BadRequestError()
        item["id"] = str(uuid.uuid4())
        self.store.setdefault(self.cls.__name__, {})[item["id"]] = item
        await self._emit(f"item{item['id']}", {"type": "create", "data": item})
        await self._emit(f"list/{self.cls.__name__}", {"type": "create", "data": item})
        return deepcopy(item)

    async def create_items(
        self, items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]] | errors.BadRequestError:
        for item in items:
            if "id" in item:
                return errors.BadRequestError()
        return cast(
            List[Dict[str, Any]],
            [await self.create_item(item) for item in items],
        )

    async def update_item(
        self, item: Dict[str, Any]
    ) -> Dict[str, Any] | errors.NotFoundError | errors.BadRequestError:
        if "id" not in item:
            return errors.BadRequestError()
        if (
            self.cls.__name__ not in self.store
            or item["id"] not in self.store[self.cls.__name__]
        ):
            return errors.NotFoundError()
        self.store[self.cls.__name__][item["id"]].update(item)
        item = deepcopy(self.store[self.cls.__name__][item["id"]])
        await self._emit(f"item/{item['id']}", {"type": "update", "data": item})
        return item

    async def update_items(
        self, items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]] | errors.NotFoundError | errors.BadRequestError:
        for item in items:
            if "id" not in item:
                return errors.BadRequestError()
            if (
                self.cls.__name__ not in self.store
                or item["id"] not in self.store[self.cls.__name__]
            ):
                return errors.NotFoundError()
        return cast(
            List[Dict[str, Any]],
            [await self.update_item(item) for item in items],
        )

    async def delete_item(
        self,
        id: str,
    ) -> Dict[str, str] | errors.NotFoundError:
        try:
            del self.store[self.cls.__name__][id]
        except KeyError:
            return errors.NotFoundError()
        await self._emit(f"item/{id}", {"type": "delete", "data": {"id": id}})
        await self._emit(
            f"list/{self.cls.__name__}", {"type": "delete", "data": {"id": id}}
        )

        return {"id": id}

    async def delete_items(
        self, ids: List[str]
    ) -> List[Dict[str, str]] | errors.NotFoundError:
        for id in ids:
            if (
                self.cls.__name__ not in self.store
                or id not in self.store[self.cls.__name__]
            ):
                return errors.NotFoundError()
        return cast(
            List[Dict[str, str]],
            [await self.delete_item(id) for id in ids],
        )

    async def patch_item(
        self, item: Dict[str, Any]
    ) -> Dict[str, Any] | errors.NotFoundError | errors.BadRequestError:
        if "id" not in item:
            return errors.BadRequestError()
        if (
            self.cls.__name__ not in self.store
            or item["id"] not in self.store[self.cls.__name__]
        ):
            return errors.NotFoundError()
        self.store[self.cls.__name__][item["id"]].update(
            {k: v for k, v in item.items() if v is not None}
        )
        await self._emit(f"item/{item['id']}", {"type": "update", "data": item})
        return deepcopy(self.store[self.cls.__name__][item["id"]])

    async def patch_items(
        self, items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]] | errors.NotFoundError | errors.BadRequestError:
        for item in items:
            if "id" not in item:
                return errors.BadRequestError()
            if (
                self.cls.__name__ not in self.store
                or item["id"] not in self.store[self.cls.__name__]
            ):
                return errors.NotFoundError()
        return cast(
            List[Dict[str, Any]],
            [await self.patch_item(item) for item in items],
        )

    async def list_items(self, page: int = 1, size: int = 20) -> Dict[str, Any]:
        start = (page - 1) * size
        end = start + size
        items = list(deepcopy(self.store.get(self.cls.__name__, {})).values())[
            start:end
        ]
        total_pages = -(-len(self.store.get(self.cls.__name__, {})) // size)
        return {"size": size, "page": page, "total_pages": total_pages, "items": items}

    async def count_items(self) -> int:
        return len(self.store.get(self.cls.__name__, {}))

    async def subscribe_to_item_by_id(self, item_id: str) -> AsyncGenerator[Any, None]:
        try:
            self.store[self.cls.__name__][item_id]
        except KeyError:
            raise errors.NotFoundError()

        item_key = f"item/{item_id}"

        if item_key not in self.subscribers:
            self.subscribers[item_key] = []

        queue: asyncio.Queue = asyncio.Queue()
        self.subscribers[item_key].append(queue)

        try:
            while True:
                data = await queue.get()
                yield data
        finally:
            self.subscribers[item_key].remove(queue)

    async def subscribe_to_items_by_id(
        self, item_ids: List[str]
    ) -> AsyncGenerator[Any, None]:
        for item_id in item_ids:
            try:
                self.store[self.cls.__name__][item_id]
            except KeyError:
                raise errors.NotFoundError()

        queue: asyncio.Queue = asyncio.Queue()

        item_keys = [f"item/{item_id}" for item_id in item_ids]

        for item_key in item_keys:
            if item_key not in self.subscribers:
                self.subscribers[item_key] = []
            self.subscribers[item_key].append(queue)

        try:
            while True:
                data = await queue.get()
                yield data
        finally:
            self.subscribers[item_key].remove(queue)

    async def subscribe_to_list(self) -> AsyncGenerator[Any, None]:
        queue: asyncio.Queue = asyncio.Queue()

        list_key = f"list/{self.cls.__name__}"
        if list_key not in self.subscribers:
            self.subscribers[list_key] = []
        self.subscribers[list_key].append(queue)

        try:
            while True:
                data = await queue.get()
                yield data
        finally:
            self.subscribers[list_key].remove(queue)

    async def _emit(self, key: str, data: Dict[str, Any]) -> None:
        if key in self.subscribers:
            for queue in self.subscribers[key]:
                await queue.put(data)
