"""takeit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.contrib import admin
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from . import views
urlpatterns = [
url(r'^admin/', admin.site.urls),
url(r'^$', views.button),
url(r'^button', views.button),
url(r'^vow', views.vow),
url(r'^el', views.el),
url(r'^gen', views.gen),
url(r'^ttll', views.ttll ),
url(r'^upload', views.upload ),
url(r'^external', views.external),
url(r'^wavForm', views.wavForm),
url(r'^deleteMedia', views.deleteMedia),
url(r'^getData', views.getData),
url(r'^SaveAudio', views.SaveAudio),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

