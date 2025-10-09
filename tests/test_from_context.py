from pathlib import Path

import graphene
from graphene import Field, ID, ObjectType, String
from graphene import Int
import pytest

from graphene_federation import LATEST_VERSION, build_schema
from graphene_federation.directives import from_context
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))


def test_from_context_with_wrong_input():
    """
    Test checking that the issue https://github.com/preply/graphene-federation/pull/47 is resolved.
    """

    # Context cannot contain _
    with pytest.raises(ValueError) as err:

        class Acme(ObjectType):
            id = ID(required=True)
            age = Int()
            foo = Field(
                String,
                someInput=from_context(
                    graphene.Argument(String),
                    field="$con_text1{ someField }",
                    auto_case=False,
                ),
            )

        class Query(ObjectType):
            acme = Field(Acme)

        build_schema(query=Query, federation_version=LATEST_VERSION)

    assert str(err.value) == 'Context name cannot contain "_"'

    # No Context
    with pytest.raises(ValueError) as err:

        class Acme(ObjectType):
            id = ID(required=True)
            age = Int()
            foo = Field(
                String,
                someInput=from_context(
                    graphene.Argument(String),
                    field="abc { someField }",
                    auto_case=False,
                ),
            )

        class Query(ObjectType):
            acme = Field(Acme)

        build_schema(query=Query, federation_version=LATEST_VERSION)

    assert str(err.value) == "One context must be specified"


def test_from_context_with_input():
    """
    Test checking that the issue https://github.com/preply/graphene-federation/pull/47 is resolved.
    """

    class Acme(ObjectType):
        id = ID(required=True)
        age = Int()
        foo = Field(
            String,
            someInput=from_context(
                graphene.Argument(String),
                field="$context1 ... on A { someField } ... on B { someField } ... on C { someOtherField  }",
            ),
        )

    class Query(ObjectType):
        acme = Field(Acme)

    schema = build_schema(query=Query, federation_version=LATEST_VERSION)

    # save_file(str(schema), "1")
    # save_file(sdl_query(schema), "2")

    assert open_file("1") == str(schema)
    assert open_file("2") == sdl_query(schema)
