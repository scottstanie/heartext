import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

from polly.txt_to_mp3 import session


class User(AbstractUser):
    pass


class Snippet(models.Model):
    s3_client = session.resource('s3')
    bucket = s3_client.Bucket('heartext')

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The URL that the text was pulled from
    source_url = models.URLField(blank=True)
    # Original text gets populated from the source_url
    text = models.TextField()
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField('date created', auto_now_add=True)
    # The S3 URL where the audio is stored
    audio_url = models.URLField(blank=True)

    def upload_to_s3(self, filename):
        with open(filename, 'rb') as f:
            self.bucket.put_object(Key='%s.mp3' % self.uuid, Body=f)
