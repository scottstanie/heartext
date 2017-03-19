# HearText

A way to give some texty, and get back a robot-y MP3


### Dependencies:

- ffmpeg

Used for audio speedup: https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest

```bash
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
``

- boilerpipe

Extracts text from HTML pages

Installed from https://code.google.com/archive/p/boilerpipe/downloads

May have followed this: https://github.com/k-bx/boilerpipe/wiki/QuickStart
