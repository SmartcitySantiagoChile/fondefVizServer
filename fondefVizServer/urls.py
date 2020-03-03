"""fondefVizServer URL Configuration

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
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView

from localinfo.views import FaqImgUploader, FaqHTML, CustomRouteCsvUploader

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='profile/expedition', permanent=True), name="index"),
    url(r'^admin/datamanager/', include('datamanager.urls')),
    url(r'^admin/django-rq/', include('django_rq.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^paymentfactor/', include('paymentfactor.urls')),
    url(r'^profile/', include('profile.urls')),
    url(r'^backup/', include('awsbackup.urls')),
    url(r'^shape/', include('shape.urls')),
    url(r'^speed/', include('speed.urls')),
    url(r'^trip/', include('trip.urls')),
    url(r'^globalstat/', include('globalstat.urls')),
    url(r'^esapi/', include('esapi.urls')),
    url(r'^user/', include('webuser.urls')),
    url(r'^user/login/$', auth_views.login, name='login'),
    url(r'^user/logout/$', auth_views.logout, name='logout'),
    url(r'^bip/', include('bip.urls')),
    url(r'^faqUpload/$', login_required(FaqImgUploader.as_view()), name='faqUpload'),
    url(r'^faq/$', FaqHTML.as_view(), name='faq'),
    url(r'^customRouteCsvUpload/$', login_required(CustomRouteCsvUploader.as_view()), name='customRouteCsvUpload'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
