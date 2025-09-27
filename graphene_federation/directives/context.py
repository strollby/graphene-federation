from typing import Any

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def context(
    name: str,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Any:
    """
    The @context directive defines a named context from which a field of the annotated type can be passed to a receiver
    of the context. The receiver must be a field annotated with the @fromContext directive.

    Reference:
    https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/directives#context

    https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/entities/use-contexts
    """
    directive = get_directive_from_name("context", federation_version)
    decorator = directive_decorator(directive)

    if "_" in name:
        raise ValueError(
            f"Invalid name for @context directive. Name must not contain '_' character."
        )

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None, name=name)(field_or_type)
        raise TypeError(
            "\n".join(
                [
                    f"\nInvalid Usage of {directive}.",
                    "Must be applied on a class of ObjectType|InterfaceType|UnionType",
                    "Example:",
                    f"{directive}",
                    "class Product(graphene.ObjectType)",
                    "\t...",
                ]
            )
        )

    return wrapper
