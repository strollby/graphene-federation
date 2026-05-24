from graphql import GraphQLDirective

from .v2_12 import get_directives as get_directives_v2_12


def get_directives() -> dict[str, GraphQLDirective]:
    return get_directives_v2_12()
