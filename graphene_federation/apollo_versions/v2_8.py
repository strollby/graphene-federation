from graphene_directives import CustomDirective, DirectiveLocation
from graphql import GraphQLArgument, GraphQLDirective, GraphQLNonNull, GraphQLString

from graphene_federation.scalars import ContextFieldValue
from graphene_federation.transform import context_field_set_case_transform
from .v2_7 import get_directives as get_directives_v2_7

context_directive = CustomDirective(
    name="context",
    locations=[
        DirectiveLocation.OBJECT,
        DirectiveLocation.INTERFACE,
        DirectiveLocation.UNION,
    ],
    args={
        "name": GraphQLArgument(GraphQLNonNull(GraphQLString)),
    },
    description="Federation @context directive",
    add_definition_to_schema=False,
    is_repeatable=True,
)

from_context_directive = CustomDirective(
    name="from_context",
    locations=[
        DirectiveLocation.ARGUMENT_DEFINITION,
    ],
    args={
        "field": GraphQLArgument(ContextFieldValue),
    },
    description="Federation @fromContext directive",
    add_definition_to_schema=False,
    input_transform=context_field_set_case_transform,
)


# Added directives @context, @from_context
def get_directives() -> dict[str, GraphQLDirective]:
    directives = get_directives_v2_7()
    directives.update(
        {
            directive.name: directive
            for directive in [context_directive, from_context_directive]
        }
    )
    return directives
