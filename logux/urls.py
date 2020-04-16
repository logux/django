from django.urls import path

from logux.views import dispatch

urlpatterns = [
    path(r'', dispatch, name='logux-dispatch'),
]
