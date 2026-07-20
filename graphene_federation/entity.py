from __future__ import annotations

from typing import Any
from typing import Dict, Type

from graphene import Enum, Field, List, NonNull, ObjectType, Scalar, Union
from graphene.types.definitions import GrapheneInterfaceType
from graphene.types.enum import EnumMeta
from graphene.types.objecttype import ObjectTypeMeta
from graphene.types.schema import TypeMap
from graphene_directives import Schema
from graphene_directives.utils import has_non_field_attribute

from .apollo_versions import LATEST_VERSION, get_directive_from_name
from .scalars import _Any


def get_entities(schema: Schema) -> Dict[str, Any]:
    """
    Find all the entities from the type map.
    They can be easily distinguished from the other type as
    the `@key` and `@extend` decorators adds a `_sdl` attribute to them.
    """
    type_map: TypeMap = schema.graphql_schema.type_map
    entities = {}
    key_directive = get_directive_from_name("key", LATEST_VERSION)
    extends_directive = get_directive_from_name("extends", LATEST_VERSION)
    for type_name, type_ in type_map.items():
        if not hasattr(type_, "graphene_type"):
            continue

        graphene_type = type_.graphene_type
        is_entity = any(
            [
                has_non_field_attribute(graphene_type, key_directive),
                has_non_field_attribute(graphene_type, extends_directive),
            ]
        ) and not isinstance(type_, GrapheneInterfaceType)
        if is_entity:
            entities[type_name] = graphene_type
    return entities


def get_entity_cls(entities: Dict[str, Any]) -> Type[Union]:
    """
    Create _Entity type which is a union of all the entity types.
    """

    class _Entity(Union):
        class Meta:
            types = tuple(entities.values())

    return _Entity


def get_base_type_of_list(field: List) -> Type[ObjectType | Union | Scalar]:
    while hasattr(field, "of_type"):
        field = field.of_type
    return field


def get_base_type_of_field(field: Field) -> Type[ObjectType | Union | Scalar]:
    type = field.type
    while hasattr(type, "of_type"):
        type = type.of_type
    return type


def get_entity_query(schema: Schema):
    """
    Create Entity query.
    """
    entities_dict = get_entities(schema)
    if not entities_dict:
        return

    entity_type = get_entity_cls(entities_dict)

    class EntityQuery:
        entities = List(
            entity_type,
            name="_entities",
            representations=NonNull(List(NonNull(_Any))),
            required=True,
        )

        def resolve_entities(self, info, representations, sub_field_resolution=False):
            entities = []
            for representation in representations:
                type_ = schema.graphql_schema.get_type(representation["__typename"])

                # @interfaceObject subgraphs never learn concrete types, so the router may ask this
                # interface's own subgraph to resolve a representation keyed by the interface name
                # itself. `type_.graphene_type` is then the raw Interface class, which can't be
                # instantiated - dispatch to a `_resolve_reference` on the interface instead.
                if isinstance(type_, GrapheneInterfaceType):
                    graphene_type = type_.graphene_type
                    resolver = getattr(graphene_type, "_resolve_reference", None)
                    if resolver is None:
                        raise TypeError(
                            f"Entity interface {graphene_type.__name__!r} has no "
                            "_resolve_reference to dispatch a representation keyed by the "
                            "interface's own typename (this happens when another subgraph "
                            "only knows the interface via @interfaceObject). Add a "
                            "`_resolve_reference` staticmethod to it, the same way concrete "
                            "entities do."
                        )
                    representation_fields = {
                        k: v for k, v in representation.items() if k != "__typename"
                    }
                    representation_proxy = type(
                        "InterfaceRepresentationProxy", (), representation_fields
                    )
                    entities.append(resolver(representation_proxy, info))
                    continue

                model = type_.graphene_type
                model_arguments = representation.copy()
                model_arguments.pop("__typename")
                if schema.auto_camelcase:
                    get_model_attr = schema.field_name_to_type_attribute(model)
                    model_arguments = {
                        get_model_attr(k): v for k, v in model_arguments.items()
                    }

                # convert subfields of models from dict to a corresponding graphql type,
                # This will be useful when @requires is used
                for model_field, value in model_arguments.items():
                    if not hasattr(model, model_field):
                        continue

                    field = getattr(model, model_field)
                    if (
                        isinstance(field, Field)
                        and (base_type := get_base_type_of_field(field))
                        and isinstance(base_type, ObjectTypeMeta)
                        and isinstance(value, dict)
                    ):
                        if value.get("__typename") is None:
                            value["__typename"] = base_type._meta.name  # noqa
                        model_arguments[model_field] = EntityQuery.resolve_entities(
                            self,
                            info,
                            representations=[value],
                            sub_field_resolution=True,
                        ).pop()
                    elif (
                        isinstance(field, List)
                        and isinstance(value, list)
                        and any(
                            [
                                issubclass(get_base_type_of_list(field), ObjectType),
                                issubclass(get_base_type_of_list(field), Union),
                            ]
                        )
                    ):
                        for sub_value in value:
                            if sub_value.get("__typename") is None:
                                sub_value["__typename"] = (
                                    field.of_type._meta.name
                                )  # noqa
                        model_arguments[model_field] = EntityQuery.resolve_entities(
                            self, info, representations=value, sub_field_resolution=True
                        )
                    elif isinstance(field, Scalar) and getattr(
                        field, "parse_value", None
                    ):
                        model_arguments[model_field] = type(field).parse_value(value)
                    elif isinstance(field, Enum):
                        model_arguments[model_field] = (
                            field._meta.enum[value] if value else None
                        )
                    elif (
                        isinstance(field, Field)
                        and (base_type := get_base_type_of_field(field))
                        and isinstance(base_type, EnumMeta)
                    ):
                        model_arguments[model_field] = (
                            base_type._meta.enum[value] if value else None
                        )

                model_instance = model(**model_arguments)

                resolver = getattr(
                    model, "_%s__resolve_reference" % model.__name__, None
                ) or getattr(model, "_resolve_reference", None)

                if resolver and not sub_field_resolution:
                    model_instance = resolver(model_instance, info)

                entities.append(model_instance)

            return entities

    return EntityQuery
