angular.module('frontend').controller('RepoFormCtrl', function($scope, $window) {
    $scope.repo = {};
    $scope.submit = function() {
        // TODO: client side validate repo url for pretty error report
        $window.alert($scope.repo.url);
        // issue a json request to the server
        // switch to status page on success, report error?
    };
});
