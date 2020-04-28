from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from users.serializers.ecommerces import RegisterSerializer, SigninSerializer


class AuthViewSet(viewsets.ViewSet):
    @action(methods=['POST'], detail=False)
    def register(self, request, pk=None):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        email = serializer.data.get('email')
        password = serializer.data.get('password')

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # Create token
        token = Token.objects.create(user=user)

        # Set payload
        payload = {
            'username': user.username,
            'email': user.email,
            'user_id': user.id,
            'token': f'Token {token.key}'
        }

        return Response(payload, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def signin(self, request, pk=None):
        serializer = SigninSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        password = serializer.data.get('password')

        try:
            user = User.objects.get(username=username)
            valid_password = user.check_password(password)
            if not user.is_active:
                raise AuthenticationFailed('User need actiavted account')

            if not valid_password:
                raise AuthenticationFailed('Invalid password')

            token = Token.objects.get(user=user)

            payload = {
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
                'token': f'Token {token.key}'
            }

            return Response(payload, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise AuthenticationFailed('User does not exist')

        except Token.DoesNotExist:
            raise AuthenticationFailed('User not have a token')

