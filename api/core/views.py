from rest_framework import viewsets
from .serializers import PostSerializer, TagSerializer, ContactSerailizer, RegisterSerializer, UserSerializer, CommentSerializer
from .models import Post, Comment
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import pagination
from rest_framework import generics
from rest_framework import filters
from rest_framework.views import APIView
from django.core.mail import send_mail
from taggit.models import Tag


class PageNumberSetPagination(pagination.PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    ordering = 'created_at'

class TagDetailView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = PageNumberSetPagination
    permission_classes = [permissions.AllowAny]


    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug'].lower()
        tag = Tag.objects.get(slug=tag_slug) # type: ignore
        return Post.objects.filter(tags=tag) # type: ignore

class PostViewSet(viewsets.ModelViewSet):
    search_fields = ['h1', 'content']
    filter_backends = (filters.SearchFilter,)
    serializer_class = PostSerializer
    queryset = Post.objects.all() # type: ignore
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    pagination_class = PageNumberSetPagination

class TagView(generics.ListAPIView):
    queryset = Tag.objects.all() # type: ignore
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

class AsideView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-id')[:5] # type: ignore
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

class FeedBackView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ContactSerailizer

    def post(self, request, *args, **kwargs):
        serializer_class = ContactSerailizer(data=request.data)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            name = data.get('name') # type: ignore
            from_email = data.get('email') # type: ignore
            subject = data.get('subject') # type: ignore
            message = data.get('message') # type: ignore
            send_mail(
                f'От {name} | {subject}',
                'E-mail: '+str(from_email)+'\n\n'+str(message),
                from_email,
                ['django.ppp@gmail.com']
            )
            return Response({"success": "Sent"})

class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Пользователь успешно создан",
        })

class ProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args,  **kwargs):
        return Response({
            "user": UserSerializer(request.user, context=self.get_serializer_context()).data,
        })

class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()# type: ignore
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_slug = self.kwargs['post_slug'].lower()
        post = Post.objects.get(slug=post_slug)# type: ignore
        return Comment.objects.filter(post=post)# type: ignore

