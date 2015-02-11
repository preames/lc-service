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
        if response.getcode() == 200:
            return [response.getcode(), json.loads(raw_data)]
        else:
            return [response.getcode(), raw_data]

    def start(self, args):
        return self.request('http://127.0.0.1:8000/api/start', args)
    def status(self, args):
        return self.request('http://127.0.0.1:8000/api/status', args)
    def stop(self, args):
        return self.request('http://127.0.0.1:8000/api/stop', args)

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

def test_basic():
    [retcode, json] = API().start({'repository' : 'foo', 
                                   'job_type' : 'clang-tidy' })
    print [retcode, json]
    request_id = json['id']
    [retcode, json] = API().status({'id' : request_id})
    # TODO: validate job_start found
    print [retcode, json]
    [retcode, json] = API().stop({'id' : request_id})
    print [retcode, json]

def test_stop():
    [retcode, json] = API().start({'repository' : 'foo', 
                                   'job_type' : 'clang-tidy' })
    print [retcode, json]
    request_id = json['id']
    [retcode, json] = API().stop({'id' : request_id})
    print [retcode, json]
    [retcode, json] = API().status({'id' : request_id})
    print [retcode, json]
    # Note: The job may have run, can't test for job_stop


test_basic()
test_stop()
test_start()

