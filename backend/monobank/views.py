from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from monobank.models import MonobankUser
from monobank.serializers import TokenSerializer


# Create your views here.

class TokenView(generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = TokenSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(MonobankUser, user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
