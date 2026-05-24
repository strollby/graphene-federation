from graphql import GraphQLDirective

from .v2_13 import get_directives as get_directives_v2_13


def get_directives() -> dict[str, GraphQLDirective]:
    return get_directives_v2_13()
