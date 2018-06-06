import logging
import os
import time

import audiotools
from PIL import Image
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

log = logging.getLogger(__name__)


class Note(models.Model):
    """
    Model for card notes
    """
    FILE_TYPES = Choices(
        ("image", "IMAGE", "image"),
        ("audio", "AUDIO", "audio"),
        ("other", "OTHER", "other"),
    )

    def get_file_path(self, filename):
        """
        Makes path for uploading files
        """
        if self.card_id:
            path = u'notes/card/%s' % self.card_id
        else:
            path = u'notes/card/undefined'
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, path)):
            os.makedirs(os.path.join(settings.MEDIA_ROOT, path))
        return os.path.join(path, filename)

    card = models.ForeignKey('nc_workflow.Card', verbose_name=u'Карточка')
    text = models.TextField(_("Text"), null=True, blank=True, default='')
    audio = models.FileField(_("Audio file"), upload_to=get_file_path, null=True, blank=True, default='')
    file = models.FileField(_("File"), upload_to=get_file_path, null=True, blank=True, default='')
    image = models.ImageField(_("Image file"), upload_to=get_file_path, null=True, blank=True, default='')
    audio_duration = models.PositiveSmallIntegerField(_("Audio file duration"), null=True, blank=True, default=0)
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta(object):
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def __str__(self):
        return "Note of card '{}' (created {})".format(self.card, self.created.ctime())

    def create_thumbnail(self):
        """
        Makes thumbnails when uploads the image files in description items
        """
        if not self.image:
            return
        file_name, file_extension = os.path.splitext(self.image.name)

        # TODO: Move to settings
        THUMBNAIL_SIZE = (300, 300)

        image = Image.open(self.image)
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        full_path = self.get_file_path(file_name)
        thumb_path = os.path.join(settings.MEDIA_ROOT, '%s_thumbnail%s' % (full_path, file_extension))
        image.save(thumb_path)
        return image

    def delete_thumbnail(self):
        """
        Deletes thumbnails when deletes Description items or changes image files
        """
        file_name, file_extension = os.path.splitext(self.image.name)
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, file_name))
        except Exception as e:
            log.error('Delete thumbnail error: %s' % e)
            return False
        return True

    def save(self, *args, **kwargs):
        if self.file:
            content_type = self.file.file.content_type
        elif self.image:
            content_type = self.image.file.content_type
        else:
            content_type = None

        if content_type in ('application/octet-stream', 'audio/x-wav', 'audio/mpeg', 'audio/mp3', 'audio/wav'):
            file_extension = os.path.splitext(self.file.name)[-1]
            if file_extension in ('.aiff', '.m4a', '.flac', '.mp2', '.mp3', '.ogg', '.opus', '.au', '.wav', '.wv'):
                self.audio, self.file = self.file, None
                filename = self.audio.path
                audio_class = audiotools.file_type(open(filename))
                if audio_class:
                    audio_file = audio_class(filename)
                    self.audio_duration = int(audio_file.seconds_length())
        elif content_type in ('image/jpeg', 'image/png', 'image/gif'):
            self.image, self.file = self.file, None
            if self.id:
                old_note = Note.objects.get(id=self.id)
                old_note.delete_thumbnail()
            self.image.name = ("_%s" % time.time()).join(os.path.splitext(self.image.name))
            self.create_thumbnail()
        super(Note, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            self.delete_thumbnail()
        super(Note, self).delete(*args, **kwargs)
