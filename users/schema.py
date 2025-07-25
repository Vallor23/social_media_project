import graphene
from graphene_django import DjangoObjectType
from users.models import User, Follow

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "profile_image", "created_at")
    
class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = ("id", "follower", "followed", "created_at")

class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    all_follows = graphene.List(FollowType)

    def resolve_all_users(root, info):
        return User.objects.prefetch_related("followers", "following").all()

    def resolve_all_follows(root, info):
        return User.objects.select_related("followers", "followed").all()

class FollowUser(graphene.Mutation):
    class Arguments:
        followed_id = graphene.ID(required=True)

        success = graphene.Boolean()
        message = graphene.String()

        def mutate(root, info, followed_id):
            follower = info.context.user
            followed = User.objects.get(id=followed_id)
            Follow.objects.create(follower=follower, followed=followed)
            return FollowUser(success=True, message="Followed successfully!")

class Mutation(graphene.ObjectType):
    follow_user = FollowUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)