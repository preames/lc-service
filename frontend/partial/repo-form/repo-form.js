angular.module('frontend').controller('RepoFormCtrl', function($scope, api) {
    $scope.repo = {};
    $scope.submit = function() {
        // TODO: client side validate repo url for pretty error report
        api.start($scope.repo.url).then(function(response) {
	    $scope.status = response;
	}, function(error) {
	    throw error;
	});
        // switch to status page on success, report error?
    };
});
