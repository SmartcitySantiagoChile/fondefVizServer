# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.shortcuts import reverse


class PasswordChangeView(View):

    def get(self, request):
        template = "webuser/password_change.html"
        title = "Cambiar contraseña"
        context = dict(form = PasswordChangeForm(request.user), title=title)

        return render(request, template, context)

    def post(self, request):
        template = "webuser/password_change.html"
        form = PasswordChangeForm(request.user, request.POST)
        title = "Cambiar contraseña"

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect(reverse('webuser:change_password'))
        else:
            messages.error(request, 'Please correct the error below.')

        context = dict(form=form, title=title)

        return render(request, template, context)