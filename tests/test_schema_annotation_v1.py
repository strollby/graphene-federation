from pathlib import Path

from graphene import Field, ID, ObjectType, String
from graphene import NonNull
from graphql import graphql_sync

from graphene_federation import build_schema, key
from graphene_federation import extends, external
from tests.util import file_handlers, sdl_query

save_file, open_file = file_handlers(Path(__file__))

# ------------------------
# User service
# ------------------------
users = [
    {"user_id": "1", "name": "Jane", "email": "jane@mail.com"},
    {"user_id": "2", "name": "Jack", "email": "jack@mail.com"},
    {"user_id": "3", "name": "Mary", "email": "mary@mail.com"},
]


@key("user_id")
@key("email")
class User(ObjectType):
    user_id = ID(required=True)
    email = String(required=True)
    name = String()

    def __resolve_reference(self, info, *args, **kwargs):
        if self.id:
            user = next(filter(lambda x: x["id"] == self.id, users))
        elif self.email:
            user = next(filter(lambda x: x["email"] == self.email, users))
        return User(**user)


class UserQuery(ObjectType):
    user = Field(User, user_id=ID(required=True))

    def resolve_user(self, info, user_id, *args, **kwargs):
        return User(**next(filter(lambda x: x["user_id"] == user_id, users)))


user_schema = build_schema(query=UserQuery)

# ------------------------
# Chat service
# ------------------------
chat_messages = [
    {"id": "1", "user_id": "1", "text": "Hi"},
    {"id": "2", "user_id": "1", "text": "How is the weather?"},
    {"id": "3", "user_id": "2", "text": "Who are you"},
    {"id": "4", "user_id": "3", "text": "Don't be rude Jack"},
    {"id": "5", "user_id": "3", "text": "Hi Jane"},
    {"id": "6", "user_id": "2", "text": "Sorry but weather sucks so I am upset"},
]


@key("user_id")
@extends
class ChatUser(ObjectType):
    user_id = external(ID(required=True))


class ChatMessage(ObjectType):
    id = ID(required=True)
    text = String()
    user_id = ID()
    user = NonNull(ChatUser)

    def resolve_user(self, info, *args, **kwargs):
        return ChatUser(user_id=self.user_id)


class ChatQuery(ObjectType):
    message = Field(ChatMessage, id=ID(required=True))

    def resolve_message(self, info, id, *args, **kwargs):
        return ChatMessage(**next(filter(lambda x: x["id"] == id, chat_messages)))


chat_schema = build_schema(query=ChatQuery)

# ------------------------
# Tests
# ------------------------


def test_user_schema():
    """
    Check that the user schema has been annotated correctly
    and that a request to retrieve a user works.
    """
    assert open_file("1") == str(user_schema)
    assert open_file("2") == sdl_query(user_schema)

    query = """
    query {
        user(userId: "2") {
            name
        }
    }
    """

    result = graphql_sync(user_schema.graphql_schema, query)
    assert not result.errors
    assert result.data == {"user": {"name": "Jack"}}


def test_chat_schema():
    """
    Check that the chat schema has been annotated correctly
    and that a request to retrieve a chat message works.
    """
    assert open_file("1") == str(chat_schema)
    assert open_file("2") == sdl_query(chat_schema)

    # Query the message field
    query = """
    query {
        message(id: "4") {
            text
            userId
        }
    }
    """
    result = graphql_sync(chat_schema.graphql_schema, query)
    assert not result.errors
    assert result.data == {"message": {"text": "Don't be rude Jack", "userId": "3"}}