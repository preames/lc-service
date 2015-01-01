describe('RepoFormCtrl', function() {
    beforeEach(module('frontend'));

    var $scope,
        ctrl,
        window;
    beforeEach(inject(function($rootScope, $controller) {
        $scope = $rootScope.$new();
        window = jasmine.createSpyObj('window', [ 'alert' ]);
        ctrl = $controller('RepoFormCtrl', { $scope: $scope, $window: window });
    }));

    it('should display an alert on form submission', inject(function() {
        var url = 'https://github.com/LegalizeAdulthood/iterated-dynamics';
        $scope.repo.url = url;

        $scope.submit();

        expect(window.alert).toHaveBeenCalledWith(url);
    }));
});