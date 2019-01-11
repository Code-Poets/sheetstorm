from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from users.common.fields import Action
from users.common.strings import ConfirmationMessages
from users.models import CustomUser
from users.permissions import AuthenticatedAdmin
from users.permissions import AuthenticatedAdminOrUser
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
    permission_classes = (AuthenticatedAdmin,)

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
    permission_classes = (AuthenticatedAdminOrUser,)

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

    @classmethod
    def get(cls, request):
        serializer = CustomRegisterSerializer(context={'request': request})
        return Response({'serializer': serializer})

    @classmethod
    def post(cls, request):
        serializer = CustomRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            try:
                serializer.errors['non_field_errors']
            except:
                return Response({
                    'serializer': serializer,
                    'errors': serializer.errors,
                    'non_field_errors': None,
                })
            return Response({
                'serializer': serializer,
                'errors': serializer.errors,
                'non_field_errors': serializer.errors['non_field_errors'],
            })
        serializer.save(request)
        return redirect('login')


class UserCreate(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'user_create.html'

    @classmethod
    def get(cls, request):
        serializer = UserCreateSerializer(context={'request': request})
        return Response({'serializer': serializer})

    @classmethod
    def post(cls, request):
        serializer = UserCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'serializer': serializer,
                'errors': serializer.errors,
            })
        email = serializer.validated_data.get('email')
        serializer.save()
        user = CustomUser.objects.get(email=email)
        user.set_password('passwduser')
        user.full_clean()
        user.save()
        return redirect('custom-users-list')


class UserUpdate(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'user_update.html'

    @classmethod
    def get(cls, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if request.user.user_type == CustomUser.UserType.ADMIN.name:
            serializer = UserDetailSerializer(user, context={'request': request})
        else:
            serializer = UserUpdateSerializer(user, context={'request': request})
        return Response({'serializer': serializer, 'user': user})

    @classmethod
    def post(cls, request, pk):
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
        messages.success(request, ConfirmationMessages.SUCCESSFUL_UPDATE_USER_MESSAGE)
        return redirect('custom-user-update', pk=pk)


class UserDetail(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'users_detail.html'

    @classmethod
    def get(cls, request, pk):
        user_detail = get_object_or_404(CustomUser, pk=pk)
        serializer = UserDetailSerializer(user_detail, context={'request': request})
        return Response({'serializer': serializer, 'user_detail': user_detail})

    @classmethod
    def post(cls, request, pk):
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
        messages.success(request, ConfirmationMessages.SUCCESSFUL_UPDATE_USER_MESSAGE)
        return redirect('custom-users-detail', pk=pk)


def delete_account(request, pk):
    if str(request.user.pk) == pk:
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return redirect('logout')
    else:
        return redirect('home')


def delete_user(request, pk):
    if request.user.user_type == CustomUser.UserType.ADMIN.name:
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return redirect('custom-users-list')
    else:
        return redirect('home')


class UserList(APIView):
    serializer_class = UserListSerializer
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'users_list.html'
    permission_classes = (
        permissions.IsAuthenticated,
    )

    @classmethod
    def get_queryset(cls):
        return CustomUser.objects.order_by('id')

    @classmethod
    def get(cls, request):
        users_queryset = cls.get_queryset()
        users_serializer = UserListSerializer(context={'request': request})
        return Response({
            'serializer': users_serializer,
            'users_list': users_queryset,
        })
