from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('', KhojAndSearch.as_view(), name='khoj-the-search'),
    path('all-input-values/', AllInputValues.as_view(), name='all-input-values')
]