describe('RepoFormCtrl', function() {
    var $scope,
        $q,
        $interval,
        ctrl,
        api;

    beforeEach(module('frontend'));

    beforeEach(inject(function($rootScope, $controller, _$q_) {
        $scope = $rootScope.$new();
        $q = _$q_;
        $interval = jasmine.createSpy('$interval');
        api = jasmine.createSpyObj('api', ['start', 'status']);
        ctrl = $controller('RepoFormCtrl', {$scope: $scope, api: api});
    }));

    it('should start a job on form submission', function() {
        var url = 'https://github.com/LegalizeAdulthood/iterated-dynamics',
            deferred = $q.defer(),
            job_type = 'clang-tidy';
        $scope.repo.url = url;
        $scope.repo.job_type = job_type;
        deferred.resolve({"repo": "tainted_repo", "id": 123});
        api.start.andReturn(deferred.promise);
        api.status.andReturn($q.defer().promise);

        $scope.submit();
        $scope.$digest();

        expect(api.start).toHaveBeenCalledWith(url, job_type);
    });

    it('should query status after successful start', function() {
        var startPromise = $q.defer(),
            statusPromise = $q.defer();
        startPromise.resolve({ "repo": "tainted_repo", "id": 123 });
        var events = [ { "datetime": "timestamp", "action": "start"} ];
        statusPromise.resolve(events);
        api.start.andReturn(startPromise.promise);
        api.status.andReturn(statusPromise.promise);
        $scope.repo.url = 'fmeh://foo';
        $scope.repo.job_type = 'clang-tidy';

        $scope.submit();
        $scope.$digest();

        expect($scope.job.events).toBe(events);
    });
});
