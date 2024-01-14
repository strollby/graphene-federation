from graphql import GraphQLDirective

from .v1_0 import get_directives as get_directives_v1_0
from .v2_0 import get_directives as get_directives_v2_0
from .v2_1 import get_directives as get_directives_v2_1
from .v2_2 import get_directives as get_directives_v2_2
from .v2_3 import get_directives as get_directives_v2_3
from .v2_4 import get_directives as get_directives_v2_4
from .v2_5 import get_directives as get_directives_v2_5
from .v2_6 import get_directives as get_directives_v2_6
from .version import FederationVersion

LATEST_VERSION = FederationVersion.VERSION_2_6


def get_directives_based_on_version(
    federation_version: FederationVersion,
) -> dict[str, GraphQLDirective]:
    if federation_version == FederationVersion.VERSION_1_0:
        return get_directives_v1_0()
    if federation_version == FederationVersion.VERSION_2_0:
        return get_directives_v2_0()
    if federation_version == FederationVersion.VERSION_2_1:
        return get_directives_v2_1()
    if federation_version == FederationVersion.VERSION_2_2:
        return get_directives_v2_2()
    if federation_version == FederationVersion.VERSION_2_3:
        return get_directives_v2_3()
    if federation_version == FederationVersion.VERSION_2_4:
        return get_directives_v2_4()
    if federation_version == FederationVersion.VERSION_2_5:
        return get_directives_v2_5()
    if federation_version == FederationVersion.VERSION_2_6:
        return get_directives_v2_6()

    return get_directives_v2_6()


def get_directive_from_name(
    directive_name: str, federation_version: FederationVersion
) -> GraphQLDirective:
    directive = get_directives_based_on_version(federation_version).get(
        directive_name, None
    )
    if directive is None:
        raise ValueError(
            f"@{directive_name} not supported on federation version {federation_version}"
        )
    return directive
