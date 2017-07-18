from django.conf.urls import url
from .views import LoadManager, getLoadFileData

app_name = "datamanager"
urlpatterns = [
	url(r'^loadManager$', LoadManager.as_view(), name="loadmanager"),
	url(r'^loadManager/data$', getLoadFileData.as_view(), name="getloadfiledata"),
	#url(r'^getSourceFiles$', GetDataManagerData.as_view(), name="getLoadFiles"),
]
