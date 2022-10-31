import graphene

from graphene_federation import inaccessible, external, provides, key, override

from graphene_federation import build_schema


@key(fields="x")
class Position(graphene.ObjectType):
    x = graphene.Int(required=True)
    y = external(graphene.Int(required=True))
    z = inaccessible(graphene.Int(required=True))
    a = provides(graphene.Int(), fields="x")
    b = override(graphene.Int(required=True), from_="h")


class Query(graphene.ObjectType):
    position = graphene.Field(Position)


schema = build_schema(Query, enable_federation_2=True)

query = '''
    query getSDL {
      _service {
         sdl
      }
    }
'''
result = schema.execute(query)
print(result.data)
# OrderedDict([('_service', OrderedDict([('sdl', '   extend type Message @key(fields: "id") {   id: Int! @external }  type Query {   message: Message } ')]))])
