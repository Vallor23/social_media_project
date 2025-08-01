import graphene
from users.schema import Mutation as UsersMutation, Query as usersQuery

class Query(usersQuery):
    pass

class Mutation(UsersMutation):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)