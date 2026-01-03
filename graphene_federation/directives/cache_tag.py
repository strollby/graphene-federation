from typing import Any

from graphene_directives import directive_decorator
from graphene_federation.apollo_versions import (
    FederationVersion,
    LATEST_VERSION,
    get_directive_from_name,
)

from .utils import is_non_field


def cache_tag(
    graphene_type=None,
    *,
    format: str,
    federation_version: FederationVersion = LATEST_VERSION,
) -> Any:
    """
    Assigns cache tags to cached data in the Apollo Router for active cache invalidation.
    Use cache tags to remove specific cached entries on demand when data changes,
    instead of waiting for time-to-live (TTL) expiration.

    Reference:
    https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/directives#cachetag
    https://www.apollographql.com/docs/graphos/routing/performance/caching/response-caching/overview
    """
    directive = get_directive_from_name("cacheTag", federation_version)
    decorator = directive_decorator(directive)

    def wrapper(field_or_type):
        if is_non_field(field_or_type):
            return decorator(field=None, format=format)(field_or_type)
        return decorator(field=field_or_type, format=format)

    if graphene_type:
        return wrapper(graphene_type)

    return wrapper
