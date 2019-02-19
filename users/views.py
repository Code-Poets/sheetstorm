from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from users.common.fields import Action
from users.models import CustomUser
from users.permissions import IsAdminUser
from users.permissions import IsOwnerOrAdmin
from users.serializers import CustomRegisterSerializer
from users.serializers import UserCreateSerializer
from users.serializers import UserDetailSerializer
from users.serializers import UserListSerializer
from users.serializers import UserSerializer
from users.serializers import UserUpdateSerializer


@api_view()
def api_root(request, format=None):
    if request.user.is_authenticated and request.user.user_type == CustomUser.UserType.ADMIN.name:
        return Response({
            'users': reverse(
                'users-list',
                request=request,
                format=format,
            ),
            'account': reverse(
                'user-account-detail',
                args=(request.user.pk,),
                request=request,
                format=format,
            ),
        })
    elif request.user.is_authenticated:
        return Response({
            'account': reverse(
                'user-account-detail',
                args=(request.user.pk,),
                request=request,
                format=format,
            ),
        })
    else:
        return Response({
            'registration': reverse(
                'rest_register',
                request=request,
                format=format,
            ),
        })


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == Action.LIST.value:
            return UserListSerializer
        if self.action == Action.RETRIEVE.value:
            return UserDetailSerializer
        if self.action == Action.CREATE.value:
            return UserCreateSerializer
        if self.action == Action.UPDATE.value:
            return UserCreateSerializer
        return UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsOwnerOrAdmin,)

    def get_serializer_class(self):
        if self.action == Action.RETRIEVE.value:
            return UserDetailSerializer
        if self.action == Action.UPDATE.value:
            return UserUpdateSerializer
        return UserSerializer


@login_required
def index(request):
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'home.html',
        context={
            'num_visits': num_visits
        },
    )


class SignUp(APIView):
    serializer_class = CustomRegisterSerializer
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'signup.html'

    def get(self, request):
        serializer = CustomRegisterSerializer(context={'request': request})
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = CustomRegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'serializer': serializer,
                'errors': serializer.errors,
            })
        serializer.save(request)
        return redirect('login')


class UserUpdate(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'user_update.html'

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if request.user.user_type == CustomUser.UserType.ADMIN.name:
            serializer = UserDetailSerializer(user, context={'request': request})
        else:
            serializer = UserUpdateSerializer(user, context={'request': request})
        return Response({'serializer': serializer, 'user': user})

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if request.user.user_type == CustomUser.UserType.ADMIN.name:
            serializer = UserDetailSerializer(
                user,
                data=request.data,
                context={'request': request},
            )
        else:
            serializer = UserUpdateSerializer(
                user,
                data=request.data,
                context={'request': request},
            )
        if not serializer.is_valid():
            return Response({
                'serializer': serializer,
                'user': user,
                'errors': serializer.errors,
            })
        serializer.save()
        return redirect('custom-user-update', pk=pk)


class UserDetail(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'users_detail.html'

    def get(self, request, pk):
        user_detail = get_object_or_404(CustomUser, pk=pk)
        serializer = UserDetailSerializer(user_detail, context={'request': request})
        return Response({'serializer': serializer, 'user_detail': user_detail})

    def post(self, request, pk):
        user_detail = get_object_or_404(CustomUser, pk=pk)
        serializer = UserDetailSerializer(
            user_detail,
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'serializer': serializer,
                'user_detail': user_detail,
                'errors': serializer.errors,
            })
        serializer.save()
        return redirect('custom-users-list')


def delete_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user.delete()
    return redirect('custom-users-list')


class UserList(APIView):
    serializer_class = UserListSerializer
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'users_list.html'
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        return CustomUser.objects.order_by('id')

    def get(self, request):
        users_queryset = self.get_queryset()
        users_serializer = UserListSerializer(context={'request': request})
        return Response({
            'serializer': users_serializer,
            'users_list': users_queryset,
        })
