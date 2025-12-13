from django.urls import path

from monobank.views import TokenView

urlpatterns = [
    path('token/', TokenView.as_view(), name='token'),
]