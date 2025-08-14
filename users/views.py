from django.shortcuts import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("""
        <h1>Welcome to My GraphQL API</h1>
        <p>This API uses GraphQL. You can explore it at <a href="/graphql/">/graphql/</a>.</p>
    """)