from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from postproducts.views import TransfersHTML, TripsBetweenZonesHTML, BoardingAndAlightingByZoneHTML

app_name = 'postproducts'
urlpatterns = [
    # html
    url(r'^transfers/$', login_required(TransfersHTML.as_view()), name='transfers'),
    url(r'^tripsBetweenZones/$', login_required(TripsBetweenZonesHTML.as_view()), name='tripsBetweenZones'),
    url(r'^boardingAndAlightingByZone/$', login_required(BoardingAndAlightingByZoneHTML.as_view()),
        name='boardingAndAlightingByZone'),

]
