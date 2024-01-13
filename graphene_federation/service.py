from graphene import Field, ObjectType, String
from graphene_directives.schema import Schema
from graphql.utilities.print_schema import print_scalar

from .scalars import FieldSet, _FieldSet


def get_sdl(schema) -> str:
    """
    Add all needed decorators to the string representation of the schema.
    """

    string_schema = str(schema)
    # Remove All Scalar definitions
    for scalar in [_FieldSet, FieldSet]:
        string_schema = string_schema.replace(print_scalar(scalar), "")

    return string_schema.strip()


def get_service_query(schema: Schema):
    sdl_str = get_sdl(schema)

    class _Service(ObjectType):
        sdl = String()

        def resolve_sdl(self, _) -> str:  # noqa
            return sdl_str

    class ServiceQuery(ObjectType):
        _service = Field(_Service, name="_service", required=True)

        def resolve__service(self, info) -> _Service:  # noqa
            return _Service()

    return ServiceQuery
