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
        context = dict(form = PasswordChangeForm(request.user))

        return render(request, template, context)

    def post(self, request):
        template = "webuser/password_change.html"
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente!')
            return redirect(reverse('webuser:password_change'))
        else:
            messages.error(request, 'Por favor corrige los errores mostrados abajo!')

        context = dict(form=form)

        return render(request, template, context)