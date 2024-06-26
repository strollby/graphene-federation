from textwrap import dedent

import pytest

from graphql import graphql_sync

from graphene import ObjectType, ID, String, Field

from graphene_federation.entity import key
from graphene_federation.main import build_schema
from graphene_federation.utils import clean_schema


def test_multiple_keys():
    @key("identifier")
    @key("email")
    class User(ObjectType):
        identifier = ID()
        email = String()

    class Query(ObjectType):
        user = Field(User)

    schema = build_schema(query=Query)
    expected_result = dedent(
        """
    type Query {
      user: User
      _entities(representations: [_Any!]!): [_Entity]!
      _service: _Service!
    }
    
    type User {
      identifier: ID
      email: String
    }
    
    union _Entity = User
    
    scalar _Any
    
    type _Service {
      sdl: String
    }
    """
    )
    assert clean_schema(schema) == clean_schema(expected_result)
    # Check the federation service schema definition language
    query = """
    query {
        _service {
            sdl
        }
    }
    """
    result = graphql_sync(schema.graphql_schema, query)
    assert not result.errors
    expected_result = dedent(
        """
    type Query {
      user: User
    }
    
    type User @key(fields: "email") @key(fields: "identifier") {
      identifier: ID
      email: String
    }
    """
    )
    assert clean_schema(result.data["_service"]["sdl"]) == clean_schema(expected_result)


def test_key_non_existing_field_failure():
    """
    Test that using the key decorator and providing a field that does not exist fails.
    """
    with pytest.raises(AssertionError) as err:

        @key("potato")
        class A(ObjectType):
            id = ID()

    assert 'Field "potato" does not exist on type "A"' == str(err.value)
