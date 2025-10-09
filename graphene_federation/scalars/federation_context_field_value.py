from graphql import GraphQLScalarType

# Reference:
# https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/directives#fromcontext
# https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/entities/use-contexts
ContextFieldValue = GraphQLScalarType(
    name="federation__ContextFieldValue",
    description=" ".join(
        (
            "Contains the name of a defined context and a selection of a field from the context's type",
        )
    ),
)
