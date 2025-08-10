import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from utils.storage import StorageManager
from users.schema import UserType
from .models import Comment, Like, Post

class PostType(DjangoObjectType):
    likes_count = graphene.Int(description='Total number of likes for this post')
    comments_count = graphene.Int(description='Total number of comments for this post')
    is_liked = graphene.Boolean(description='Whether the current user has liked this post')
    author = graphene.Field(UserType, description='post author details')
    class Meta:
        model = Post
        fields = ["id", "user", "image", "content", "created_at"]

    def resolve_likes_count(self, info):
        self.likes.count()

    def resolve_likes_count(self, info):
        self.comments.count()

    def resolve_is_liked(self, info):
        user = info.context.user
        if user.is_anonymous:
            return False
        return Like.objects.filter(user=user, post=self).exists()
class CreatePost(graphene.Mutation):
        """Mutation for creating a new post"""
        class Arguments:
            image = graphene.String(description='Base64 encoded image')
            content = graphene.String(description='Content of the post')

        post = graphene.Field(PostType, description='The created post')
        success = graphene.Boolean(description='Whether the post was created successfully')
        message = graphene.String(description='Success/Error message')

        def mutate(self, info, content=None, image=None):
            user = info.context.user
            if user.is_anonymous:
                raise GraphQLError('You must be logged in to create a post')
            
            if not image and not content:
                raise GraphQLError('Post must have atleast an image or text')

            try:
                # Handle image upload if provided
                image_url = None
                if image:
                    image_url = StorageManager.upload_post_image(image, str(user.id))
                
                # Create post with image URL
                post = Post.objects.create(user=user, content=content, image=image_url)
                return CreatePost(success=True, post=post, message='Post created successfully')
            except Exception as e:
                return CreatePost(success=False, Post=None, message=f'Failed to create post: {str(e)}')
class DeletePost(graphene.Mutation):
        """Mutation for deleting a post"""
        class Arguments:
            post_id = graphene.ID(description='ID of the post to delete')

        success = graphene.Boolean(description='Whether the post was deleted successfully')
        message = graphene.String(description='Success/Error message')

        def mutate(self, info, post_id):
            user = info.context.user
            if user.is_anonymous:
                raise GraphQLError('You must be logged in to delete a post')

            try:
                post = Post.objects.filter(user=user,id=post_id ).delete()
                return DeletePost(success=True, message='Post deleted successfully')
            except Post.DoesNotExist:
                return DeletePost(success=False, message='Post not found or you do not have the permission to delete it')
            except Exception as e:
                return DeletePost(success=False, message=f'Failed to delete post: {str(e)}')
class EditPost(graphene.Mutation):
    """Mutation for editing a  user's post"""
    class Arguments:
        post_id = graphene.ID(description='ID of the post to edit')
        content = graphene.String(description='New content post')

    post = graphene.Field(PostType, description='The edited post')
    success = graphene.Boolean(description='Whether the post was edited successfully')
    message = graphene.String(description='Success/Error message')
    
    def mutate(self, info, post_id, content):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in to edit a post')

        if not content or not content.strip():
            raise GraphQLError('Content cannot be empty')

        try:
            post = Post.objects.get(user=user,id=post_id)
            post.content = content
            post.save()
            return EditPost(success=True, post=post, message='Post updated successfully')
        except Post.DoesNotExist:
            return EditPost(success=False, post=None, message='Post not found or you dont have the  permission to edit it')
        except Exception as e:
            return EditPost(success=False,post=None, message=f'Failed to edit post: {str(e)}')

class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]

class LikePost(graphene.Mutation):
    """Mutation for liking a post"""
    class Arguments:
        post_id = graphene.ID(description='ID of the post to be liked')
    
    success=graphene.Boolean(description='Whether the post was liked successfully')
    message=graphene.String(description='Success/Error message')

    def mutate(self, info, post_id):
        user =  info.context.user

        if user.is_anonymous:
            raise GraphQLError('You must be logged in to like a post')
         
        try:
            post= Post.objects.get(id=post_id)

            #   check if user already liked the post
            if Like.objects.filter(user=user, post=post).exists():
                return LikePost(success=False, message='You have already liiked this post')

            # otherwise create the like
            Like.objects.create(post=post, user=user)
            return LikePost(success=True, message='Post liked successfully')

        except Post.DoesNotExist:
            return LikePost(success=False, message='Post not found')

        except Exception as e:
            return LikePost(success=False, message=f'Failed to like post: {str(e)}')

class UnlikePost(graphene.Mutation):
    """Mutation for unliking a post"""
    class Arguments:
        post_id = graphene.ID(description='ID of the post to be unliked')
    
    success=graphene.Boolean(description='Whether the post was unliked successfully')
    message=graphene.String(description='Success/Error message')

    def mutate(self, info, post_id):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('You must be logged in to unlike post')
        
        try:
            post = Post.objects.get(id=post_id)
            Like.objects.filter(user=user, post=post).delete()
            return UnlikePost(success=True, message='unliked post successfully')
        except Post.DoesNotExist:
            return UnlikePost(success=False, message='Post not found')
        except Exception as e:
            return LikePost(success=False, message=f'Failed to like post: {str(e)}')

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ["post", "user", "content", "created_at"]
        
class CreateComment(graphene.Mutation):
    """Mutation for commenting on a post"""
    class Arguments:
        post_id = graphene.ID(required=True, description='ID of post that is to be commented on')
        content = graphene.String(required=True, description='Body of the comment, cannot be empty')
    
    success=graphene.Boolean(description='Whether the post was unliked successfully')
    message=graphene.String(description='Success/Error message')
    comment = graphene.Field(CommentType, description='The comment made')

    def mutate(self, info, post_id, content):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('You must be logged in to comment on a post')

        if not content or not content.strip():
            raise GraphQLError('Comment content cannot be empty')

        if len(content) > 1000:
            raise GraphQLError('Comment too long(max 1000 characters)')

        try:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.create(user=user, post=post, content=content.strip())
            return CreateComment(success=True, comment=comment, message='comment made successfully')
        except Post.DoesNotExist:
            return CreateComment(success=False, comment=None, message='Post not found')
        except Exception as e:
            return CreateComment(success=False, comment=None, message=f'Failed to create comment: {str(e)}')

class DeleteComment(graphene.Mutation):
    """"Mutation for deleting a comment"""
    class Arguments:
        comment_id = graphene.ID(description='ID of the comment to be deleted')
    
    success=graphene.Boolean(description='Whether the comment was deleted successfully')
    message=graphene.String(description='Success/Error message')

    def mutate(self, info, comment_id ):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('You must be logged in to delete on a comment')
        
        try:
            Comment.objects.filter(user=user, id=comment_id ).delete()
            return CreateComment(success=True, message='Comment deleted successfully')
        except Post.DoesNotExist:
            return CreateComment(success=False, comment=None, message='Post not found')
        except Exception as e:
            return CreateComment(success=False, comment=None, message=f'Failed to delete comment: {str(e)}')

class EditComment(graphene.Mutation):
    """"Mutation for deleting a comment"""
    class Arguments:
        comment_id = graphene.ID(description='ID of the edited comment')
        content = graphene.String(required=True, description='Content of the new comment')

    success=graphene.Boolean(description='Whether the post was edited successfully')
    message=graphene.String(description='Success/Error message')
    comment = graphene.Field(CommentType, description='The new comment made')

    def mutate(self, info, comment_id, content):
        user = info.context.user

        if user.is_anonymous:
            raise GraphQLError('You must be logged in to edit this comment')

        if not content or not content.strip():
            raise GraphQLError('Comment content cannot be empty')

        try:
            comment = Comment.objects.get(user=user, id=comment_id)
            comment.content = content
            comment.save()
            return EditComment(success=True, comment=comment, message='comment made successfully')
        except Post.DoesNotExist:
            return EditComment(success=False, comment=None, message='Post not found')
        except Exception as e:
            return EditComment(success=False, comment=None, message=f'Failed to edit comment: {str(e)}')

class Query():
    user_posts = graphene.List(PostType, username=graphene.String(required=True), description='Get posts for this specific user')

    def resolve_user_posts(self, info, username):
        # Get posts for specific user
        return Post.objects.filter(user__username=username).order_by('-created_at')

    post_comments =  graphene.List(CommentType, post_id=graphene.ID(required=True), description='Get comments for a specific post')
    def resolve_post_comments(self, info, post_id):
        # Get comments
        return Comment.objects.filter(post_id=post_id).select_related('user').order_by('-created_at')
     
    feed = graphene.List(PostType, description='Get feed of posts from followed users')
    
    def resolve_feed(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("Authentication required")
        
        # Get IDs of user being followed
        following_ids = user.following.values_list('following_id', flat=True)

        # Get posts from followed users
        return Post.objects.filter(user_id__in=following_ids).order_by('-created_at')
class Mutation(graphene.ObjectType):
    create_comment = CreateComment.Field(description='Comment on a post')
    delete_comment = DeleteComment.Field(description='Delete a comment on a post')
    edit_comment =  EditComment.Field(description='Edit a comment on a post')
    create_post =  CreatePost.Field(description='Create a post')
    delete_post = DeletePost.Field(description='Delete a post')
    edit_post = EditPost.Field(description='Edit a text post')
    like_post = LikePost.Field(description='Like a post')
    unlike_post = UnlikePost.Field(description='Unlike a post')