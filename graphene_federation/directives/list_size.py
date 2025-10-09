from typing import Callable, Optional

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def list_size(
    graphene_type,
    assumed_size: Optional[int] = None,
    slicing_arguments: Optional[list[str]] = None,
    sized_fields: Optional[list[str]] = None,
    require_one_slicing_argument: Optional[bool] = None,
    *,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    The @listSize directive is used to customize the cost calculation of the demand control feature of GraphOS Router.

    Reference: https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/directives#listField
    """
    directive = get_directive_from_name(
        "listSize", federation_version=federation_version
    )
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            raise TypeError(
                "\n".join(
                    [
                        f"\nInvalid Usage of {directive}.",
                        "Must be applied on a field level",
                        "Example:",
                        "class Query(graphene.ObjectType)",
                        "\tproductsQuery = list_field(graphene.List(ProductType), assumed_size=10)",
                    ]
                )
            )
        return decorator(
            field=field_or_type,
            **{
                "assumed_size": assumed_size,
                "slicing_arguments": slicing_arguments,
                "sized_fields": sized_fields,
                "require_one_slicing_argument": require_one_slicing_argument,
            },
        )

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
