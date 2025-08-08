import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from users.models import User, Follow, UserProfile
from graphql_jwt.shortcuts import get_token
from django.contrib.auth import authenticate
from graphql import GraphQLError

class UserType(DjangoObjectType):
    """Represents a user and their profile information."""
    class Meta:
        model = User
        fields = ("id", "username","first_name", "last_name", "email", "created_at")
        description = "User profile data including social connections."

class UserProfileType(DjangoObjectType):
    """Represents a user profile information."""

    followers = graphene.List(lambda: UserType, description="List of users who follow this user.")
    following = graphene.List(lambda: UserType,  description="List of users this user is following.")
    is_following =  graphene.Boolean( description="Returns true if the current authenticated user is following this user.")

    followers_count = graphene.Int(description="Total number of users following this user.")
    following_count = graphene.Int( description="Total number of users this user is following.")
    class Meta:
        model = UserProfile
        fields = ("user", "bio", "profile_image")
        description = "User profile data including social connections."

    def resolve_followers(self, info):
        return [follow.follower for follow in self.followers.all()]

    def resolve_following(self, info):
        return [follow.following for follow in self.following.all()]

    def resolve_is_following(self, info):
        current_user = info.context.user
        return Follow.objects.filter(follower=current_user, following=self).exists()

    def resolve_followers_count(self, info):
        return self.followers.count()

    def resolve_following_count(self, info):
        return self.following.count()

class FollowType(DjangoObjectType):
    """Represents a follow relationship between users."""

    class Meta:
        model = Follow
        fields = ("id", "follower", "following", "created_at")

class AuthPayload(graphene.ObjectType):
    """Returned after a successful authentication or registration. """

    token = graphene.String(description="JWT token for authenticated access")
    user = graphene.Field(UserType,  description="Authenticated user's data")

class RegisterUser(graphene.Mutation):
    """
    Registers a new user and returns a token with user details.
    """

    class Arguments:
        username = graphene.String(required=True, description="Desired username")
        firstName = graphene.String(required=True)
        lastName = graphene.String(required=True)
        email = graphene.String(required=True, description="Valid user email")
        password = graphene.String(required=True,  description="Secure password")

    Output = AuthPayload

    def mutate(self, info, username, email, password, firstName, lastName):
        # Handles the actual logic of creating the user in Django.
        try:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password, first_name=firstName, last_name=lastName)
            # Create empty profile
            UserProfile.objects.create(user=user)

            token = get_token(user)
            return AuthPayload(token=token, user=user)
        except Exception as e:
            raise Exception(f"Failed to register user: {e}")

class LoginUser(graphene.Mutation):
    """
    Logs in an existing user and returns a JWT token with user info.
    """
    class Arguments:
        username = graphene.String(required=True, description="Username of the registered user")
        password = graphene.String(required=True, description="Password for the user")

    Output = AuthPayload

    def mutate(self, info, username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception("Invalid credentials!")
        
        token = get_token(user)
        return AuthPayload(token=token, user=user)

class UpdateProfile(graphene.Mutation):
    """
    Allows an authenticated user to update their profile.
    Only the provided fields will be updated.
    """
    class Arguments:
        username = graphene.String(description="New username (optional)")
        email = graphene.String(description="New email (optional)")
        firstName = graphene.String(description="New firstname (optional)")
        lastName = graphene.String(description="New lastname (optional)")
        bio = graphene.String(description="New bio (optional)")
        profile_image = graphene.String(description="New profile image URL (optional)")
        
    user = graphene.Field(UserType, description="Updated user information")
    profile = graphene.Field(UserProfileType, description="The updated user profile information")

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required to update profile.")
        
        user_fields = ['username', 'email', 'first_name', 'last_name']
        profile_fields = ['bio', 'profile_image']

        # Update user fields
        for key, value in kwargs.items():
            if key in user_fields and value is not None:
                setattr(user, key, value)
        user.save()

        # Update profile fields
        profile, created = UserProfile.objects.get_or_create(user=user)
        for key, value in kwargs.items():
            if key in profile_fields and value is not None:
                setattr(profile, key, value)
        profile.save()

        # Return the updated user and profile
        return UpdateProfile(user=user, profile=profile)

class FollowUser(graphene.Mutation):
    """
    Mutation to make one user follow another.
    """
    class Arguments:
        username = graphene.String(required=True,  description="The username of the user you want to follow.")

    success = graphene.Boolean(description="Indicates whether the follow operation was successful.")
    message = graphene.String(description="A message describing the result of the operation.")

    def mutate(root, info, username):
        current_user = info.context.user

        if current_user.is_anonymous:
            raise GraphQLError("Authentication required.")

        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist:
            raise GraphQLError("User not found")

        if user_to_follow == current_user:
            return FollowUser(success=False, message="You cannot folllow yourself!")

        Follow.objects.create(follower=current_user, following=user_to_follow)
        return FollowUser(success=True, message="Followed successfully!")

class UnfollowUser(graphene.Mutation):
    """
    Mutation that allows an authenticated user to unfollow another user by their username.
    """
    class Arguments:
        username = graphene.String(required=True,  description="The username of the user you want to unfollow.")

    success = graphene.Boolean(description="Indicates whether the unfollow operation was successful.")
    message = graphene.String(description="A message describing the result of the operation.")

    def mutate(root, info, username):
        follower = info.context.user

        try:
            user_to_unfollow = User.objects.get(username=username)
        except User.DoesNotExist:
            raise GraphQLError("User not found")
        
        Follow.objects.filter(follower=follower, following=user_to_unfollow).delete()
        return UnfollowUser(success=True, message="Unfollowed successfully.")
class Query(graphene.ObjectType):
    """
    Root Query type for fetching user data.
    """
    userProfile = graphene.Field(
        UserProfileType,
        username =graphene.String(),
        description="Returns the user profile by username or current user if no username is provided"
    )

    all_users =  graphene.List(UserType, description="Returns a list of all users in the system.")

    def resolve_all_users(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
        return User.objects.all()

    def resolve_user_profile(root, info, username):
        if username:
            try:
                return UserProfile.objects.get(user__username = username)
            except UserProfile.DoesNotExist:
                raise Exception("Profile not found")

        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required to view profile.")

        return UserProfile.objects.get(user=user)

class Mutation(graphene.ObjectType):
    """
    Root Mutation type for user-related actions
    """
    
    register_user = RegisterUser.Field(description="Register a new user and return a token.")
    login_user = LoginUser.Field(description="Login a user and return a token.")
    update_profile = UpdateProfile.Field(description="Update the authenticated user's profile.")
    follow_user = FollowUser.Field(description="Authenticated user follows another user.")
    unfollow_user = UnfollowUser.Field(description="Authenticated user unfollows a user.")

    token_auth = graphql_jwt.ObtainJSONWebToken.Field(description="Obtain JWT token for authentication.")
    verify_token = graphql_jwt.Verify.Field(description="Verify the validity of a JWT token.")
    refresh_token = graphql_jwt.Refresh.Field(description="Refresh an existing JWT token.")