from typing import Callable

from graphene_directives import directive_decorator

from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)
from .utils import is_non_field


def cost(
    graphene_type=None,
    *,
    weight: int,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    """
    The @cost directive defines a custom weight for a schema location.
    For GraphOS Router, it customizes the operation cost calculation of the demand control feature.

    If @cost is not specified for a field, a default value is used:
        - Scalars and enums have default cost of 0
        - Composite input and output types have default cost of 1

    Regardless of whether @cost is specified on a field, the field cost for that field also accounts for its arguments
    and selections.

    Reference: https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/directives#cost
    """
    directive = get_directive_from_name("cost", federation_version=federation_version)
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None, weight=weight)(field_or_type)
        return decorator(field=field_or_type, weight=weight)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
