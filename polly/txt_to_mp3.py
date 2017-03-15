#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module containiner functions to parse input text and convert to speech


"""
from __future__ import unicode_literals

import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from boto3 import Session
from botocore.exceptions import ClientError
import nltk.data

session = Session(profile_name="personal")
polly = session.client("polly")


class InputHandler(object):
    """Takes in raw text and produces a list of sentences

    Handles the splitting and SSML tags to ready for speech conversion"""

    request_limit = 1450  # AWS refuses anything bigger than 1500, add padding
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

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

    def _check_length(self, lines):
        good_lines = []
        for line in lines:
            if len(line) < self.request_limit:
                good_lines.append(line)
            else:
                good_lines.extend(self.split_into_sentences(line))

        return good_lines

    def split_into_sentences(self, text):
        return self.tokenizer.tokenize(text)

    def format_lines(self, raw_text):
        """Takes the raw text and produces SSML formatted list of lines

        Runs the _check_length function on the raw line split in order to
        break up lines longer than the AWS limit
        """
        lines = [self._surround(line) for line in self._check_length(raw_text.splitlines())]
        return [self._start()] + lines + [self._end()]


class Converter(object):
    """Goes through each snippet of text and converts to mp3

    TODO: speedup sound?
    """
    concurrency = 8

    def __init__(self, lines, debug=True, path='.', output_name='tmp.mp3'):
        self.lines = lines
        self.debug = debug
        # TODO: make sure path gets final slash stripped
        # TODO: use the os library better
        self.path = path
        self.temp_file_format = '{}/tmpoutput_'.format(path)

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
            print "Error making _synth_speech call:"
            print e
            print 'Input text length: ', len(line)
            print line

        return response['AudioStream']

    def write_text_chunk(self, line, idx):
        if self.debug:
            print line
            print '-----' * 10

        response_stream = self.convert_text(line)

        with open(self.temp_file_format + idx, 'w') as f:
            f.write(response_stream.read())

    def run(self):
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_chunk_num = {
                executor.submit(self.write_text_chunk, chunk, index): index
                for index, chunk in enumerate(self.lines)
            }
            for future in as_completed(future_to_chunk_num):
                index = future_to_chunk_num[future]
                future.result()
                print "Completed %s" % index


class OutputHandler(object):
    """Takes the temporary files and processes into final output

    Handles the cleanup of temporary files, may have several options
    of where to store or send final mp3 data
    """
    def __init__(self, temp_file_format, path='.', output_name='tmp.mp3'):
        self.temp_file_format = temp_file_format
        self.output_name = '%s/%s' % (path, output_name)

    def combine_outputs(self):
        """List the output files in numerical order, and combine them into one"""
        print 'Output file:', self.output_name
        cat_command = 'cat $(ls %s* | sort -n -t "_" -k 2) > "%s"' % \
            (self.temp_file_format, self.output_name.replace("'", ''))
        subprocess.check_call(cat_command, shell=True)

    def cleanup_dir(self):
        """Cleanup the tmp files"""
        rm_command = 'rm -f %s/tmpoutput_*' % self.path
        subprocess.check_call(rm_command, shell=True)

    def run(self):
        self.combine_outputs()
        self.cleanup_dir()



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
    oh = OutputHandler(temp_file_format=converter.temp_file_format)
