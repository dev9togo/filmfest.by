def get_urls():
    from django.conf.urls import patterns, include, url
    from django.views.generic.simple import direct_to_template

    from rest_framework import routers

    from apps.cpm2014 import constants
    from apps.cpm2014 import views

    LANGS = '|'.join(c for c, n in constants.TRANSLATION_LANGUAGES)

    router = routers.DefaultRouter()
    router.register(r'submissions', views.SubmissionViewSet)

    return patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^rules/(?P<lang>\w{2})', views.rules, name='rules_lang'),
        url(r'^rules', views.rules, name='rules'),
        url(r'^submit', views.submit, name='submit'),
        url(r'^partners', views.partners, name='partners'),
        url(r'^contacts', direct_to_template,
            {'template': 'cpm2014/contacts.html'},
            name='contacts'),
        url(r'^presskit', views.press_kit, name='press_kit'),
        url(r'^api/', include(router.urls)),
        url(r'^angular/', 'cpm.views.angular'),

        url(r'^submission/(?P<submission_id>\d+)/'
            r'translation/(?P<lang>%s)$' % LANGS,
            views.translation_details, name='translation_details'),
        url(r'^submission/(?P<submission_id>\d+)/'
            r'translation/(?P<lang>%s)/edit$' % LANGS,
            views.translation_edit, name='translation_edit'),
        url(r'^translations/$',
            views.translations_all_json, name='translations_all_json'),

        url(r'^program/list/$',
            views.program_list, name='program_list'),
        url(r'^program/add/$',
            views.program_edit, name='program_add'),
        url(r'^program/(?P<program_id>\d+)/$',
            views.program_details, name='program_details'),
        url(r'^program/(?P<program_id>\d+)/edit/$',
            views.program_edit, name='program_edit'),
        url(r'^event/(?P<event_id>\d+)/$',
            views.event_details, name='event_details'),
    )

urls = (get_urls(), 'cpm2014', 'cpm2014')
