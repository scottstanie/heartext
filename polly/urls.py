from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'^download/$', views.song_download, name='song_download'),
]
