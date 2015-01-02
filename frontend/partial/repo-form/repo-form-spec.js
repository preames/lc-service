describe('RepoFormCtrl', function() {
    beforeEach(module('frontend'));

    var $scope,
        ctrl,
        api;
    beforeEach(inject(function($rootScope, $controller) {
        $scope = $rootScope.$new();
        api = jasmine.createSpyObj('api', [ 'start' ]);
        ctrl = $controller('RepoFormCtrl', { $scope: $scope, api: api});
    }));

    it('should start a job on form submission', inject(function() {
        var url = 'https://github.com/LegalizeAdulthood/iterated-dynamics';
        $scope.repo.url = url;

        $scope.submit();

        expect(api.start).toHaveBeenCalledWith(url);
    }));
});