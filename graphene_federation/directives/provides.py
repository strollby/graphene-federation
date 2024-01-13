from typing import Any, Callable, Union

from graphene_directives import directive_decorator

from ..appolo_versions import FederationVersion, LATEST_VERSION, get_directive_from_name


def provides(
    field: Any,
    fields: Union[str, list[str]],
    federation_version: FederationVersion = LATEST_VERSION,
) -> Callable:
    directive = get_directive_from_name(
        "provides", federation_version=federation_version
    )
    return directive_decorator(directive)(
        field=field, fields=fields if isinstance(fields, str) else " ".join(fields)
    )
