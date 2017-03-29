import uuid
from boto3 import Session
from django.db import models
from django.contrib.auth.models import AbstractUser

from heartext import settings


class User(AbstractUser):
    pass


class Snippet(models.Model):
    session = Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='us-east-1',
    )
    s3_client = session.resource('s3')
    bucket = s3_client.Bucket('heartext')
    s3_base_url = "https://s3.amazonaws.com/heartext"

    title = models.CharField(max_length=200, null=True, blank=True)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The URL that the text was pulled from
    source_url = models.URLField(null=True, blank=True)
    # Original text gets populated from the source_url
    text = models.TextField()
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField('date created', auto_now_add=True)

    @property
    def s3_url(self):
        """The S3 URL where the audio is stored
        """
        return "%s/%s.mp3" % (self.s3_base_url, self.uuid)

    def upload_to_s3(self, filename):
        with open(filename, 'rb') as f:
            self.bucket.put_object(Key="%s.mp3" % str(self.uuid), Body=f)
