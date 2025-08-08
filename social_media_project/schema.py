import graphene
from users.schema import Mutation as UsersMutation, Query as usersQuery
from posts.schema import Mutation as postsMutation, Query as postsQuery

class Query(usersQuery, postsQuery):
    pass

class Mutation(UsersMutation, postsMutation):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)