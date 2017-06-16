from django.shortcuts import render


def time(request):
    return render(request, "indicators/byTravelTime.html", {})
