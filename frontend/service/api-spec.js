describe('api', function() {
    var api,
        $http,
        url = 'https://github.com/LegalizeAdulthood/iterated-dynamics',
	job_type = 'clang-tidy';

    beforeEach(module('frontend'));

    beforeEach(inject(function(_api_, $httpBackend) {
        api = _api_;
        $http = $httpBackend;
    }));

    afterEach(function() {
        $http.verifyNoOutstandingExpectation();
        $http.verifyNoOutstandingRequest();
    });

    function isFormDataContent(header) {
        return header['Content-Type'] === 'application/x-www-form-urlencoded';
    }

    function expectStart() {
        return $http.expectPOST('/api/start',
            "repository=" + encodeURIComponent(url) + "&job_type=" + encodeURIComponent(job_type),
            isFormDataContent);
    }

    it('should post repository URL to /api/start', function() {
        expectStart().respond(200, { status: true });

        api.start(url, job_type);
        $http.flush();
    });

    it('should resolve promise to status value when start succeeds', function() {
        var success = jasmine.createSpy('success'),
	    response = { "repo": "tainted_repo", "job_type": "clang-tidy", "id": 666 };
        expectStart().respond(200, response);

        api.start(url, job_type).then(success);
        $http.flush();

        expect(success).toHaveBeenCalledWith(response);
    });

    it('should reject promise with object on http error', function() {
        var error = jasmine.createSpy('error');
        expectStart().respond(404);

        api.start(url, job_type).then(function() {}, error);
        $http.flush();

        expect(error).toHaveBeenCalledWith(jasmine.any(Object));
    });

    it('should post to /api/status to get job status', function() {
        var success = jasmine.createSpy('success'),
            response = { "timestamp": "event" };
        $http.expectPOST('/api/status').respond(200, response);

        api.status(555).then(success);
        $http.flush();

        expect(success).toHaveBeenCalledWith(response);
    });
});
