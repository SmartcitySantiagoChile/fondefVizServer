from django.conf.urls import url
from .views import ShowDataManager, GetDataManagerData

urlpatterns = [
	url(r'^show$', ShowDataManager.as_view(), name='datamanager'),
	url(r'^getSourceFiles$', GetDataManagerData.as_view()),
]
