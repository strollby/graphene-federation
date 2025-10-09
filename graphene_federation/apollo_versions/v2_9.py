from graphene_directives import CustomDirective, DirectiveLocation
from graphql import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLDirective,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLString,
)

from .v2_8 import get_directives as get_directives_v2_8

list_size_directive = CustomDirective(
    name="listSize",
    locations=[
        DirectiveLocation.FIELD_DEFINITION,
    ],
    args={
        "assumed_size": GraphQLArgument(GraphQLInt),
        "slicing_arguments": GraphQLArgument(
            GraphQLList(GraphQLNonNull(GraphQLString))
        ),
        "sized_fields": GraphQLArgument(GraphQLList(GraphQLNonNull(GraphQLString))),
        "require_one_slicing_argument": GraphQLArgument(GraphQLBoolean),
    },
    description="Federation @listSize directive",
    add_definition_to_schema=False,
)

requires_scope_directive = CustomDirective(
    name="cost",
    locations=[
        DirectiveLocation.ARGUMENT_DEFINITION,
        DirectiveLocation.FIELD_DEFINITION,
        DirectiveLocation.INPUT_FIELD_DEFINITION,
        DirectiveLocation.OBJECT,
        DirectiveLocation.SCALAR,
        DirectiveLocation.ENUM,
    ],
    args={
        "weight": GraphQLArgument(GraphQLNonNull(GraphQLInt)),
    },
    description="Federation @cost directive",
    add_definition_to_schema=False,
)


# Added @listSize, @cost
def get_directives() -> dict[str, GraphQLDirective]:
    directives = get_directives_v2_8()
    directives.update(
        {
            directive.name: directive
            for directive in [list_size_directive, requires_scope_directive]
        }
    )
    return directives
