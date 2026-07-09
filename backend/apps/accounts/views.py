from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import MeSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/ — open registration; new users get Member role."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        out = UserSerializer(user).data
        return Response(out, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/auth/me/ — current authenticated user profile."""

    serializer_class = MeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


__all__ = [
    "RegisterView",
    "MeView",
    "TokenObtainPairView",
    "TokenRefreshView",
]
