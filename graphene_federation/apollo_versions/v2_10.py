from graphql import GraphQLDirective

from .v2_9 import get_directives as get_directives_v2_9


# No Change
def get_directives() -> dict[str, GraphQLDirective]:
    return get_directives_v2_9()
