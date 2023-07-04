import strawberry
from aiohttp import web
from dataclasses import dataclass
from strawberry.aiohttp.views import GraphQLView

from petstore import types
from petstore.database import Database

from petstore.schema.query import Query
from petstore.schema.mutation import Mutation
from petstore.schema.subscription import Subscription


@dataclass
class PetsDatabase:
    pets: Database


class GraphQLViewWithContext(GraphQLView):
    def __init__(self, database: PetsDatabase):
        super().__init__(
            schema=strawberry.Schema(
                query=Query,
                mutation=Mutation,
                subscription=Subscription,
            )
        )
        self._database = database

    async def get_context(self, *args, **kwargs):
        return {"database": self._database}


def create_app(
    database: PetsDatabase = PetsDatabase(pets=Database(types.Pet)),
) -> web.Application:
    app = web.Application()

    app.router.add_route(
        "*",
        "/graphql",
        handler=GraphQLViewWithContext(database=database),
    )

    return app
