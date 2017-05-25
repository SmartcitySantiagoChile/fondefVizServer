from django.conf.urls import url
from . import views
from datamanager.views import ShowDataManagerView, GetSourceFilesView

urlpatterns = [
	url(r'^show$', ShowDataManagerView.as_view(), name='datamanager'),
	url(r'^getSourceFiles$', GetSourceFilesView.as_view()),
]
