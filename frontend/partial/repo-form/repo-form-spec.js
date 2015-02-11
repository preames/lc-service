describe('RepoFormCtrl', function() {
    beforeEach(module('frontend'));

    var $scope,
	$q,
        ctrl,
        api;
    beforeEach(inject(function($rootScope, $controller, _$q_) {
	$q = _$q_;
        $scope = $rootScope.$new();
        api = jasmine.createSpyObj('api', [ 'start' ]);
        ctrl = $controller('RepoFormCtrl', { $scope: $scope, api: api});
    }));

    it('should start a job on form submission', inject(function() {
        var url = 'https://github.com/LegalizeAdulthood/iterated-dynamics',
	    deferred = $q.defer();
        $scope.repo.url = url;
	deferred.resolve({"repo": "tainted_repo", "id": 123});
	api.start.andReturn(deferred.promise);

        $scope.submit();
	$scope.$digest();

        expect(api.start).toHaveBeenCalledWith(url);
    }));
});
