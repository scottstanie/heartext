# HearText

A way to give some texty, and get back a robot-y MP3


## Local setup

    psql -c 'CREATE DATABASE heartext'


    mkvirtualenv heartext
    brew install ffmpeg
    brew install redis
    pip install -r requirements.txt
    ./manage.py migrate

#### Running locally with redis for celery background jobs

In one window, run:

    redis-server

Then in a separate tab, run

    heroku local


### Dependencies:

- ffmpeg

Used for audio speedup: https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest

```bash
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```

- boilerpipe

Extracts text from HTML pages

Installed from https://code.google.com/archive/p/boilerpipe/downloads

May have followed this: https://github.com/k-bx/boilerpipe/wiki/QuickStart

- redis

Used for celery task queue and result backend

#### New bucket policy to public-read:

```python
s3 = boto3.session.resource('s3')
client = boto3.session.client('s3')
s3.create_bucket(Bucket='bucketname', ACL='public-read')
client.put_bucket_policy(Bucket='bucketname', Policy="""{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AddPerm",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::heartext/*"
        }
    ]
}""")
```
