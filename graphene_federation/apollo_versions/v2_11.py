from graphql import GraphQLDirective

from .v2_10 import get_directives as get_directives_v2_10


# No Change
def get_directives() -> dict[str, GraphQLDirective]:
    return get_directives_v2_10()
