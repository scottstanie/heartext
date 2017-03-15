#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import subprocess
from boto3 import Session
from botocore.exceptions import ClientError
import nltk.data

session = Session(profile_name="personal")
polly = session.client("polly")


def split_into_sentences(text):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)


class InputHandler(object):
    """Takes in raw text and produces a list of sentences

    Handles the splitting and SSML tags to ready for speech conversion"""
    def __init__(self, text, debug=True):
        self.text = text
        self.debug = debug
        self.lines = self.format_lines(text)

    def _surround(self, line, tag='p'):
        return "<speak><{tag}>{line}</{tag}></speak>".format(line=line, tag=tag)

    def _silence(self, seconds):
        """Add a short silence, used to avoid abrupt start or end
        """
        return self._surround('<break time="{}s"/>'.format(seconds))

    def _start(self):
        """Short silence at end of text for smoothness
        """
        return self._silence(0.5)

    def _end(self):
        """Final silence at end of text to not break abruptly
        """
        return self._silence(2)

    def format_lines(self, raw_text):
        """Takes the raw text and produces SSML formatted list of lines
        """
        lines = [self._surround(line) for line in raw_text.splitlines()]
        return [self._start()] + lines + [self._end()]


class Converter(object):
    """Goes through each snippet of text and converts to mp3

    TODO: speedup sound?
    """
    def __init__(self, lines, debug=True, path='.', output_name='tmp.mp3'):
        self.lines = lines
        self.debug = debug
        # TODO: make sure path gets final slash stripped
        # TODO: use the os library better
        self.path = path
        self.output_name = '%s/%s' % (path, output_name)

    def _synth_speech(self, input_text):
        return polly.synthesize_speech(
            OutputFormat='mp3',
            # SampleRate='string',
            Text=input_text,
            TextType='ssml',
            VoiceId='Joanna'
        )

    def _divide_input(input_text):
        return input_text.split('.')

    def convert_text(self, line):
        """Takes input_text, returns object with audio stream
        https://boto3.readthedocs.io/en/latest/reference/services/polly.html#synthesize_speech

        returns:
            AudioStream (StreamingBody)
        """
        try:
            response = self._synth_speech(line)
        except ClientError as e:
            print e
            print 'Input text length: ', len(line)
            print line
            # TODO: handle split and combine correctly
            # print 'Trying to split...'
            # sentences = _divide_input(input_text)
            # for sentence in sentences:
            #     response = _synth_speech

        return response['AudioStream']

    def write_text(self, line, idx):
        if self.debug:
            print line
            print '-----' * 10

        response_stream = self.convert_text(line)

        with open('tmpoutput_%s' % idx, 'w') as f:
            f.write(response_stream.read())

    def run(self):

        current_conversion_text = ''
        idx = 0
        while True:
            try:
                next_text = self.lines[idx]
            except IndexError:
                print 'Done!'
                break

            if len(current_conversion_text) + len(next_text) > 1500:
                # If the combination would be too big, write first,
                # then have the next iteration start with next_text
                self.write_text(current_conversion_text, idx)
                current_conversion_text = next_text
            else:
                # If the addition is small enough, synth them in one request
                current_conversion_text += next_text
                self.write_text(current_conversion_text, idx)
                current_conversion_text = ''

            idx += 1

        # Don't forget the final leftovers
        if current_conversion_text:
            self.write_text(current_conversion_text, idx)

        self.combine_outputs()
        self.cleanup_dir()

    def combine_outputs(self):
        """List the output files in numerical order,
        and combine them into one using cat"""
        print 'Output file:', self.output_name
        cat_command = 'cat $(ls %s/tmpoutput_* | sort -n -t "_" -k 2) > "%s"' % \
            (self.path, self.output_name.replace("'", ''))
        subprocess.check_call(cat_command, shell=True)

    def cleanup_dir(self):
        # Cleanup the tmp files
        rm_command = 'rm -f %s/tmpoutput_*' % self.path
        subprocess.check_call(rm_command, shell=True)


if __name__ == '__main__':
    sample_text = """
Sam Altman
The FCC has announced plans to roll back policies on net neutrality,  and its new head has indicated he has no plan to stop soon .
The internet is a public good, and I believe access should be a basic right.  We've seen such great innovation in software because the internet has been a level playing field.  People have been able to succeed by merit, not the regulatory weight of incumbency.
It seems best to keep it regulated like a common carrier. [1] Doing this allows the government to ensure a level playing field, impose privacy regulations, and subsidize access for people who can't afford it.
But this idea is under attack, and I'm surprised the tech community isn't speaking out more forcefully.  Although many leading tech companies are now the incumbents, I hope we'll all remember that openness helped them achieve their great success.  It could be disastrous for future startups if this were to change--openness is what made the recent wave of innovation happen.
We need to make our voices heard.  We won this fight once before, and we can win it again.  I really hope an activist or tech leader will step up and organize this fight (and I'm happy to help!).  It's important for our future.
[1] There's an argument that Internet Service Providers should be able to charge a metered rate based on usage.  I'm not sure whether I agree with this, but in principle it seems ok.  That's how we pay for public utilities.
What's clearly not OK is taking it further--charging different services different rates based on their relationships with ISPs.  You wouldn't accept your electric company charging you different rates depending on the manufacturer of each of your appliances."""

    ih = InputHandler(sample_text)
    converter = Converter(lines=ih.lines, debug=True)
    converter.run()
