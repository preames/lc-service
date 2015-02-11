describe('api', function() {
    var api,
        $http,
        url = 'https://github.com/LegalizeAdulthood/iterated-dynamics';

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
            "repository=" + encodeURIComponent(url),
            isFormDataContent);
    }

    it('should post repository URL to /api/start', function() {
        expectStart().respond(200, { status: true });

        api.start(url);
        $http.flush();
    });

    it('should resolve promise to status value when start succeeds', function() {
        var success = jasmine.createSpy('success'),
	    response = { "repo": "tainted_repo", "id": 666 };
        expectStart().respond(200, response);

        api.start(url).then(success);
        $http.flush();

        expect(success).toHaveBeenCalledWith(response);
    });

    it('should reject promise with object on http error', function() {
        var error = jasmine.createSpy('error');
        expectStart().respond(404);

        api.start(url).then(function() {}, error);
        $http.flush();

        expect(error).toHaveBeenCalledWith(jasmine.any(Object));
    });
});
