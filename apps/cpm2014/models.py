from django.db import models
from django.utils.functional import cached_property
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from hvad.models import TranslatableModel, TranslatedFields

from constants import YESNO, YESNOMAYBE, COUNTRIES, LANGUAGES,\
     SECTIONS, BACKLINKS, TRANSLATION_LANGUAGES

class Submission(models.Model):
    title = models.CharField(verbose_name=_('Original title'), max_length=1000)
    title_en = models.CharField(verbose_name=_('English title'),
                                max_length=1000)
    country = models.CharField(verbose_name=_('Country of production'),
                                max_length=2, choices=COUNTRIES)
    language = models.CharField(verbose_name=_('Language of original version'),
                                max_length=10, choices=LANGUAGES)
    genre = models.CharField(verbose_name=_('Genre'),
                             max_length=1000, blank=True, null=True)
    section = models.IntegerField(verbose_name=_('Section'),
                                  choices=SECTIONS)
    synopsis = models.TextField(verbose_name=_('Synopsis'))
    length = models.IntegerField(verbose_name=_('Runtime (in minutes)'))
    aspect_ratio = models.CharField(verbose_name=_('Aspect ratio'),
                                    max_length=1000)
    year = models.IntegerField(verbose_name=_('Year of production'))
    premiere = models.IntegerField(verbose_name=_('Premiere'), choices=YESNO) ##
    film_awards = models.TextField(verbose_name=_('Film awards'), blank=True)
    director_awards = models.TextField(
        verbose_name=_('Director awards'), blank=True)
    budget = models.CharField(verbose_name=_('Film budget'), max_length=1000)
    film_link = models.CharField(
        verbose_name=_('Link to download the film (optional)'),
        max_length=1000, blank=True
    )

    attend = models.IntegerField(
        verbose_name=_('I intend to visit final part of festival'),
        choices=YESNOMAYBE, default=0)
    backlink = models.IntegerField(
        verbose_name=_('The source of information about '\
                       'Cinema Perpetuum Mobile'),
        choices=BACKLINKS
    )##

    director = models.CharField(verbose_name=_('Name'),
                                max_length=1000)
    director_address = models.TextField(verbose_name=_('Address'))
    director_email = models.CharField(verbose_name=_('Email'),
                                      max_length=1000)
    director_site = models.CharField(verbose_name=_('Website'),
                                      max_length=1000, blank=True)
    director_phone = models.CharField(
        verbose_name=_('Tel.'),
        max_length=1000, blank=True)

    producer = models.CharField(verbose_name=_('Name'),
                                max_length=1000, blank=True)
    producer_address = models.TextField(verbose_name=_('Address'), blank=True)
    producer_email = models.CharField(
        verbose_name=_('Email'), max_length=1000, blank=True)
    producer_site = models.CharField(
        verbose_name=_('Website'), max_length=1000, blank=True)
    producer_phone = models.CharField(
        verbose_name=_('Tel.'),
        max_length=1000, blank=True)

    screenwriter = models.CharField(verbose_name=_('Script writer'),
                                    max_length=1000, blank=True)
    editor = models.CharField(verbose_name=_('Editor'),
                                 max_length=1000, blank=True)
    music = models.CharField(verbose_name=_('Music composer'),
                                max_length=1000, blank=True)
    director_photography = models.CharField(
        verbose_name=_('Director of photography'),
        max_length=1000, blank=True)
    other_credits = models.TextField(verbose_name=_('Other credits'), blank=True)


    allow_tv = models.IntegerField(
        verbose_name=_('Authorization to use excerpts of the film for promotion (max 10% of the total length) in television'),
        choices=YESNO, default=1)
    allow_noncommercial = models.IntegerField(
        verbose_name=_('Authorization to include the film in the festival video collection for non-commercial screenings'),
        choices=YESNO, default=1)
    allow_network = models.IntegerField(
        verbose_name=_('Authorization to screen the film at film festivals from Cinema Perpetuum Mobile partner network'),
        choices=YESNO, default=1)

    applicant = models.CharField(verbose_name=_('Name'),
                                max_length=1000)
    applicant_address = models.TextField(verbose_name=_('Address'))
    applicant_email = models.CharField(verbose_name=_('Email'),
                                      max_length=1000)
    applicant_site = models.CharField(verbose_name=_('Website'),
                                      max_length=1000, blank=True)
    applicant_phone = models.CharField(
        verbose_name=_('Tel.'),
        max_length=1000, blank=True)

    submission_language = models.CharField(
        verbose_name=_('Submission language'),
        max_length=2, choices=settings.LANGUAGES,
        default=settings.LANGUAGES[0][0])

    extra_data = models.TextField(
        verbose_name=_('Structured data'), null=True, blank=True)
    comment = models.TextField(
        verbose_name=_('Comment'), null=True, blank=True)
    comment_email_sent = models.BooleanField(
        verbose_name=_('E-mail was sent'), default=False)
    comment_film_received = models.BooleanField(
        verbose_name=_('Film is received'), default=False)
    comment_papers_received = models.BooleanField(
        verbose_name=_('Papers were received'), default=False)
    comment_vob_received = models.BooleanField(
        verbose_name=_('Vob received'), default=False)

    submitted_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Submitted at'))
    email_sent_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('E-mail sent at'))
    film_received_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('Film received at'))
    papers_received_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('Papers received at'))
    vob_received_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('Vob received at'))

    preview = models.FloatField(
        null=True, blank=True, verbose_name=_('Preview result'))
    preview_average = models.FloatField(
        null=True, blank=True, verbose_name=_('Preview average result'))
    previewers = models.IntegerField(
        null=True, blank=True, verbose_name=_('Previewers count'))

    def __unicode__(self):
        return 'Film %s' % (self.title)

    def __repr__(self):
        return '<Film %s>' % (self.title)


    def get_absolute_url(self):
        submission_hash = md5('%s%s' % (settings.SECRET_KEY, self.id))

        return reverse('cpm2013:submission_info', args=[
            str(self.id), submission_hash.hexdigest()
        ])

    @cached_property
    def translation(self):
        from django.utils import translation
        current_language = translation.get_language()

        return next(
            (
                trans for trans in self.submissiontranslation_set.all()
                if trans.language == current_language
            ),
            None
        )


class Prescreening(models.Model):
    datetime = models.DateTimeField(verbose_name=_('Date and time'))
    submissions = models.ManyToManyField(Submission)

    def __unicode__(self):
        return 'Prescreening %s' % (self.datetime.strftime('%Y-%m-%d %H:%M'),)


class NewsEntry(TranslatableModel):
    added_at = models.DateTimeField(auto_now_add=True)

    translations = TranslatedFields(
        title = models.CharField(verbose_name=_('Title'), max_length=100),
        short_text = models.TextField(verbose_name=_('Short text'), max_length=1000),
        text = models.TextField(verbose_name=_('Text'), max_length=1000),
    )

    __unicode__ = lambda self: self.title


class SubmissionTranslation(models.Model):
    submission = models.ForeignKey(Submission)
    language = models.CharField(max_length=2, choices=TRANSLATION_LANGUAGES)

    title = models.CharField(verbose_name=_('Title'),
                             max_length=1000, default='')
    genre = models.CharField(verbose_name=_('Genre'),
                             max_length=1000, default='')
    synopsis = models.TextField(verbose_name=_('Synopsis'), default='')
    synopsis_short = models.TextField(verbose_name=_('Synopsis (short)'), default='')
    director = models.CharField(verbose_name=_('Director'),
                                max_length=1000, default='')

    class Meta:
        unique_together = [('submission', 'language')]


class Program(models.Model):
    code = models.SlugField(
        unique=True, verbose_name=_(u'Code'),
        help_text=_(u'Unique technical code, e.g. regional_mogilev')
    )
    section = models.IntegerField(choices=SECTIONS, verbose_name=_(u'Section'))
    __unicode__ = lambda self: self.code

    @cached_property
    def translation(self):
        try:
            return ProgramTranslation.objects.get(
                program=self, language=translation.get_language()
            )
        except ProgramTranslation.DoesNotExist:
            return None


class ProgramTranslation(models.Model):
    program = models.ForeignKey(Program)
    language = models.CharField(max_length=2, choices=TRANSLATION_LANGUAGES)
    name = models.CharField(verbose_name=_(u'Name'), max_length=1000)
    description = models.CharField(verbose_name=_(u'Description'),
                                   max_length=1000)

    class Meta:
        unique_together = [('language', 'program')]


class SubmissionScreening(models.Model):
    num = models.IntegerField()
    submission = models.ForeignKey(Submission)
    program = models.ForeignKey(Program)

    class Meta:
        unique_together = [('submission', 'program')]


class City(TranslatableModel):
    code = models.CharField(verbose_name=_(u'Code'), max_length=1000)
    priority = models.IntegerField(verbose_name=_(u'Priority'))

    translations = TranslatedFields(
        name = models.CharField(verbose_name=_(u'Name'), max_length=1000)
    )

    __unicode__ = lambda self: self.code

    class Meta:
        verbose_name_plural = 'Cities'


class Place(TranslatableModel):
    code = models.CharField(verbose_name=_(u'Code'), max_length=1000)
    city = models.ForeignKey(City)

    translations = TranslatedFields(
        name = models.CharField(verbose_name=_(u'Name'), max_length=1000),
        address = models.CharField(verbose_name=_(u'Address'), max_length=1000)
    )

    __unicode__ = lambda self: self.code


class Event(TranslatableModel):
    code = models.CharField(verbose_name=_(u'Code'), max_length=1000)
    starts_at = models.DateTimeField(verbose_name=_('Starts at'), db_index=True)
    place = models.ForeignKey(Place)
    program = models.ForeignKey(Program, null=True, blank=True)

    translations = TranslatedFields(
        name = models.CharField(verbose_name=_(u'Name'), max_length=1000),
        description = models.TextField(verbose_name=_('Description'),
                                       blank=True, null=True)
    )

    __unicode__ = lambda self: self.code
