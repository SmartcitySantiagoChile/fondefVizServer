# -*- coding: utf-8 -*-


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View

from webuser.messages import PasswordUpdatedSuccessfully, FormError


class PasswordChangeView(View):

    def get(self, request):
        template = "webuser/password_change.html"
        context = dict(form=PasswordChangeForm(request.user))

        return render(request, template, context)

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)

        response = dict()

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messenger = PasswordUpdatedSuccessfully()
        else:
            messenger = FormError(form.error_messages)

        response['status'] = messenger.get_status_response()

        return JsonResponse(response)
