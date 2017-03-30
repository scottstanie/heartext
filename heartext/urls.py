"""heartext URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from registration.backends.simple.views import RegistrationView

from heartext.forms import CustomUserForm
import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^polly/', include('polly.urls', namespace="polly")),
    url(r'^$', views.index, name="index"),
    url(r'^parse/?$', views.parse, name="parse"),
    url(r'^upload/?$', views.upload, name="upload"),
    url(r'^profile/?$', views.profile, name="profile"),
    # login / account views
    url(r'^register/$',
        RegistrationView.as_view(form_class=CustomUserForm),
        name='registration_register'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('registration.backends.simple.urls')),

    # Generic playlist views
    url(r'^playlists/$', views.PlaylistList.as_view(), name='playlist-list'),
    url(r'^playlists/create/$', views.PlaylistCreate.as_view(), name='playlist-create'),
    url(r'^playlists/(?P<pk>[\d]+)/update/$', views.PlaylistUpdate.as_view(), name='playlist-update'),
    url(r'^playlists/(?P<pk>[\d]+)/delete/?$', views.PlaylistDelete.as_view(), name='playlist-delete'),
    url(r'^playlists/(?P<pk>[\d]+)/?$', views.PlaylistDetail.as_view(), name='playlist-detail'),

    # Generic snippet views
    url(r'^snippets/(?P<uuid>[^/]+)/update/?$', views.SnippetUpdate.as_view(), name='snippet-update'),
    url(r'^snippets/(?P<uuid>[^/]+)/delete/?$', views.SnippetDelete.as_view(), name='snippet-delete'),
    url(r'^snippets/(?P<uuid>[^/]+)/?$', views.SnippetDetail.as_view(), name='snippet-detail'),
]
