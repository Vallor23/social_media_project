import graphene
from graphene_django import DjangoObjectType

from .models import Comment, Like, Post

class CommentType(DjangoObjectType):
    pass
class CreateComment(graphene.Mutation):
    pass
class DeleteComment(graphene.Mutation):
    pass
class EditComment(graphene.Mutation):
    pass
class LikePost(graphene.Mutation):
    pass
class UnlikePost(graphene.Mutation):
    pass
class CreatePost(graphene.Mutation):
    pass
class DeletePost(graphene.Mutation):
    pass
class EditPost(graphene.Mutation):
    pass

