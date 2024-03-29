from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from consistencychecker.views import LoadConsistencyHTML, GetConsistencyData

app_name = 'consistencychecker'
urlpatterns = [
    url(r'^consistency/$', staff_member_required(LoadConsistencyHTML.as_view()), name='concistency'),
    url(r'^data/$', staff_member_required(GetConsistencyData.as_view()), name='getConsistencyData'),

]
