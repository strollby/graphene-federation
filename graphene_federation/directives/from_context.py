from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from graphene_federation.validators import (
    InternalNamespace,
    ast_to_str,
    build_ast,
    validate_from_context_field_str,
)
from .utils import is_non_field


def from_context(
    graphene_type,
    field: str,
    *,
    auto_case: bool = True,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    A `@fromContext` directive must be used as an argument on a field.
    Its field value—the `ContextFieldValue` scalar—must contain the name of a defined context and
    a selection of a field from the context's type.

    - The first element must be the name of a context defined by `@context` and prefixed with `$`.
      For example, `$myContext`. This is the only context that can be referenced by the annotated field.
    - The second element must be a selection set that resolves to a single field.
    - Top-level type conditions must not overlap with one another so that the field can be resolved to a single value.
    - All fields referenced in the ContextFieldValue must be expressed within the current subgraph.
      If the fields are referenced across multiple subgraphs, they must be annotated with @external.

    Reference: https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/directives#fromcontext
    """
    directive = get_directive_from_name("from_context", federation_version)
    decorator = directive_decorator(directive)

    field = validate_from_context_field_str(directive, field)

    if not auto_case:
        field = f"{InternalNamespace.NO_AUTO_CASE.value} {field}"

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            raise TypeError(
                "\n".join(
                    [
                        f"\nInvalid Usage of {directive}.",
                        "Must be applied on a field argument level",
                        "Example:",
                        "class Query(graphene.ObjectType)",
                        """\tproductQuery = graphene.Field(
                                            ProductType, 
                                            category=from_context(
                                                graphene.Argument(graphene.Int),
                                                field="$context1 { some_int_field }"
                                            ),
                                        )
                    """,
                    ]
                )
            )
        return decorator(field=field_or_type, args_via_dict={"field": field})

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
