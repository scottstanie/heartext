from django.conf.urls import url
import views

urlpatterns = [
    url(r'^convert/?$', views.convert, name="convert"),
    url(r'^download/$', views.song_download, name='song_download'),
    url(r'^progress/?$', views.progress, name="progress"),
]
