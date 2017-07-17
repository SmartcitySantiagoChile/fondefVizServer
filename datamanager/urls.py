from django.conf.urls import url
from .views import ShowDataManager, GetDataManagerData

app_name = "datamanager"
urlpatterns = [
	#url(r'^users$', LoadFileView.as_view(), name="loadFiles"),
	#url(r'^loadFile$', LoadFileView.as_view(), name="loadFiles"),
	#url(r'^getSourceFiles$', GetDataManagerData.as_view(), name="getLoadFiles"),
]
