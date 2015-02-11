# This file contains external tests which excercise basic features of the 
# API.  These are dliberately written to test the external API.  Additional
# tests can be added as Django view tests, but we should make sure basic
# functionality works.

import json
from urllib import *

class API:
    def request(self, url, args):
        url = url + "?" +  urlencode(args)
        response = urlopen(url)
        raw_data = response.read().decode('utf-8')
        return [response.getcode(), raw_data]
        #return json.loads(raw_data)

    def start(self, args):
        return self.request('http://127.0.0.1:8000/api/start', args)

def expect_error(response):
    print response[0]
    assert response[0] != 200

def test_start():
    # required argument
    print API().start({'repository' : 'foo' })
    # optional argument
    print API().start({'repository' : 'foo', 
                       'job_type' : 'clang-tidy' })

    # extra arguments (dsiallowed)
    expect_error( API().start({'repository' : 'foo',
                               'garbage' : ''}) )

    # repo string validation
    expect_error( API().start({'repository' : '',
                               'job_type' : 'clang-tidy'}) )

    # job type validation
    print API().start({'repository' : 'foo',
                       'job_type' : 'clang-tidy'})
    print API().start({'repository' : 'foo',
                       'job_type' : 'clang-format'})
    print API().start({'repository' : 'foo',
                       'job_type' : 'clang-modernize'})
    expect_error(API().start({'repository' : 'foo',
                              'job_type' : 'garbage'}))

test_start()

