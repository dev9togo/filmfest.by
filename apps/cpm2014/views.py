
# -*- coding: utf-8 -*-
import io
import json
import os.path
from collections import defaultdict

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView
from django.conf import settings

from rest_framework import viewsets

from apps.cpm2014.constants import APP_ROOT
from apps.cpm2014.models import Submission, NewsEntry, SubmissionTranslation
from apps.cpm2014.forms import SubmissionForm, SubmissionTranslationForm
from apps.cpm2014.serializers import SubmissionSerializer
from apps.cpm2014.tasks import SendSubmissionEmail


class IndexView(RedirectView):
    url = '/'
    permanent = False
index = IndexView.as_view()

def submit(request):
    form = SubmissionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        submission = form.save(commit=False)
        submission.submission_language = translation.get_language()
        submission.save()

        SendSubmissionEmail().apply_async(args=[submission])

        return render_to_response(
            'cpm2014/submit_done.html',
            {'email': submission.applicant_email},
            context_instance=RequestContext(request),
        )

    return render_to_response(
        'cpm2014/submit.html',
        {'form': form},
        context_instance=RequestContext(request),
    )


class Rules:
    LANGUAGES = {
        'be': 'rules_ru.md',
        'ru': 'rules_ru.md',
        'en': 'rules_en.md',

    }
    RTL = set(('ar',))

    PATH = os.path.join(APP_ROOT, 'docs')

    @classmethod
    def translation(cls, lang):
        if lang is None:
            lang = translation.get_language()

        lang = lang.lower()
        if lang not in cls.LANGUAGES:
            lang = 'en'

        rules = os.path.join(cls.PATH, cls.LANGUAGES[lang])
        rtl = lang in cls.RTL

        return lang, rules, rtl

    def __call__(self, request, lang=None):
        lang, rules_filename, rtl = self.translation(lang)
        rules = io.open(
            rules_filename,
            'r', encoding='utf-8'
        ).read()
        return render_to_response(
            'cpm2014/rules.html',
            {
                'rules': rules,
                'rtl': rtl,
                'current_lang': lang,
                'languages': sorted(self.LANGUAGES.iterkeys()),
            },
            context_instance=RequestContext(request),
        )
rules = Rules()

def partners(request):
    img_dir = '/static/cpm2014/banners/'
    main_banners = [
        (
            img_dir + 'where450.png',
            'http://www.spn.ru/publishing/whereminsk/',
            'Where Minsk'
        ),
        (
            img_dir + 'relax450.png',
            'http://relax.by/',
            'relax.by - развлечения в Минске, развлекательные центры столицы'
        ),

    ]
    banners = [
        (
            img_dir + 'lamora.png',
            'http://la-mora.info/',
            'Арт-пространство ДК «La мора»'
        ),
        (
            img_dir + 'bvc.png',
            'http://www.belvc.by/',
            'Белорусский видеоцентр'
        ),
        (
            img_dir + 'minsk24dok.png',
            'http://mtis.tv/',
            'Минск 24 ДОК'
        ),
        (
            img_dir + 'paramonak.png',
            'http://paramonak.by/',
            'Креативное агенство Парамонак'
        ),
        (
            img_dir + 'kinolife.png',
            'http://kinolife.eu/',
            'Film & TV Online Platform'
        ),
        (
            img_dir + 'iysff.png',
            'http://www.makesilentfilm.com/',
            'International Youth Silent Film Festival'
        ),
        (
            img_dir + 'luma.png',
            'http://luma.net.my/',
            'LUMA – a creative hub for the media arts'
        ),
        (
            img_dir + 'euroradio.png',
            'http://euroradio.fm/',
            'Последние новости политики и культуры Беларуси - Euroradio'
        ),
        (
            img_dir + 'bolshoi.png',
            'http://bolshoi.by/',
            'Журнал "Большой"'
        ),
        (
            img_dir + 'minchanka.png',
            'http://www.minchanka.by/',
            'Минчанка: быть женщиной - это интересно!'
        ),
        (
            img_dir + 'open.png',
            'http://open.by/',
            'Интернет-портал OPEN.BY'
        ),
        (
            img_dir + 'mart.png',
            'http://mart.by/',
            'Современное белорусское искусство'
        ),
        (
            img_dir + 'vgomele.png',
            'http://vgomele.by/',
            'vGomele.by - гомельский информационно-развлекательный портал'
        ),
        (
            img_dir + 'belarusdigest.png',
            'http://belarusdigest.com/',
            'Беларусы за мяжой'
        ),
        (
            img_dir + 'ky.png',
            'http://kyky.org/',
            'KYKY.ORG - Культурный портал'
        ),
        (
            img_dir + 'nomadic.png',
            'http://vagrant.kinaklub.org/',
            'Nomadic Film Club'
        ),
    ]
    return render_to_response(
        'cpm2014/partners.html',
        {'main_banners': main_banners, 'banners': banners},
        context_instance=RequestContext(request),
    )


def press_kit(request):
    return render_to_response(
        'cpm2014/press_kit.html', {},
        context_instance=RequestContext(request),
    )



class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows submissions to be viewed or edited.
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    @csrf_exempt
    def create(self, request, *args, **kwargs):
        return super(SubmissionViewSet, self).create(request, *args, **kwargs)

    @csrf_exempt
    def update(self, request, *args, **kwargs):
        return super(SubmissionViewSet, self).update(request, *args, **kwargs)

    get_paginate_by = lambda self: None


@staff_member_required
def translation_details(request, submission_id, lang):
    submission = get_object_or_404(Submission, id=submission_id)
    translation, created = SubmissionTranslation.objects.get_or_create(
        submission=submission, language=lang
    )

    data = [
        (_(u'Title'), submission.title, translation.title),
        (_(u'Director'), submission.director, translation.director),
        (_(u'Genre'), submission.genre, translation.genre),
        (_(u'Synopsis'), submission.synopsis, translation.synopsis),
        (_(u'Synopsis (short)'), '', translation.synopsis_short),
    ]
    context = {'submission': submission, 'data': data, 'lang': lang}
    return render_to_response('cpm2014/translation_details.html', context,
                              context_instance=RequestContext(request))


@staff_member_required
def translation_edit(request, submission_id, lang):
    submission = get_object_or_404(Submission, id=submission_id)
    translation, created = SubmissionTranslation.objects.get_or_create(
        submission=submission, language=lang
    )
    form = SubmissionTranslationForm(
        request.POST or None, instance=translation
    )

    if form.is_valid():
        form.save()
        return redirect('cpm2014:translation_details', submission_id, lang)

    context = {
        'submission': submission,
        'translation': translation,
        'form': form,
        'lang': lang
    }
    return render_to_response('cpm2014/translation_edit.html', context,
                              context_instance=RequestContext(request))


@staff_member_required
def translations_all_json(request):
    response_dict = defaultdict(dict)

    for t in SubmissionTranslation.objects.all():
        response_dict[t.submission_id][t.language] = {
            'title': t.title,
            'genre': t.genre,
            'synopsis': t.synopsis,
            'synopsis_short': t.synopsis_short,
            'director': t.director,
        }

    return HttpResponse(
        json.dumps(response_dict, indent=2),
        content_type="application/json"
    )
