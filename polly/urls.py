from django.conf.urls import url
import views

urlpatterns = [
    url(r'^convert/?$', views.convert, name="convert"),
    url(r'^download/$', views.song_download, name='song_download'),
    url(r'^progress/?$', views.progress, name="progress"),
    url(r'^download_playlist/?$', views.download_playlist, name="download_playlist"),
    url(r'^download_zip/(?P<playlist_id>[\d]+)/$', views.download_zip, name='download_zip'),
]
