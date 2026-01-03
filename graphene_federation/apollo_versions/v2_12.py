from graphene_directives import CustomDirective, DirectiveLocation
from graphql import GraphQLArgument, GraphQLDirective, GraphQLNonNull, GraphQLString

from .v2_11 import get_directives as get_directives_v2_11

cache_tag_directive = CustomDirective(
    name="cacheTag",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.OBJECT,
    ],
    args={
        "format": GraphQLArgument(GraphQLNonNull(GraphQLString)),
    },
    description="Federation @cacheTag directive",
    add_definition_to_schema=False,
    is_repeatable=True,
)


def get_directives() -> dict[str, GraphQLDirective]:
    directives = get_directives_v2_11()
    directives.update(
        {directive.name: directive for directive in [cache_tag_directive]}
    )
    return directives
