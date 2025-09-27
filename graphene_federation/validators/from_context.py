from graphql import GraphQLDirective

from .utils import ast_to_str, build_ast


def validate_from_context_field_str(directive: GraphQLDirective, field: str) -> str:
    """
    Used to validate the context field str

    Raises:
        ValueError

    Returns validated and parsed context field str
    """
    ast_node = build_ast(
        fields=field if isinstance(field, str) else " ".join(field),
        directive_name=str(directive),
        additional_valid_special_characters={"$"},
    )

    errors = []
    found_context = False
    context_has_underscore = False
    for token in ast_node:
        if token.startswith("$"):
            found_context = True
            if "_" in token:
                context_has_underscore = True
            break

    if not found_context:
        errors.append("One context must be specified")
    if context_has_underscore:
        errors.append('Context name cannot contain "_"')

    if errors:
        raise ValueError("\n".join(errors))

    return ast_to_str(ast_node)
