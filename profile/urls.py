from django.conf.urls import url
from . import views
from profile.views import LoadProfileByExpedition, GetLoadProfileData

urlpatterns = [
	url(r'^expedition$', LoadProfileByExpedition.as_view(), name='expedition'),
	url(r'^getExpeditionData$', GetLoadProfileData.as_view()),
]
