from django.conf.urls import url
from . import views
from profile.views import LoadProfileByExpeditionView, GetLoadProfileByExpeditionData

urlpatterns = [
	url(r'^expedition$', LoadProfileByExpeditionView.as_view(), name='expedition'),
	url(r'^getExpeditionData$', GetLoadProfileByExpeditionData.as_view()),
]
