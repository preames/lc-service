angular.module('frontend').controller('RepoFormCtrl', function($scope, api, $interval) {
    $scope.repo = { job_type: "clang-tidy" };
    $scope.submit = function() {
        var timerId;
        // TODO: client side validate repo url for pretty error report
        api.start($scope.repo.url, $scope.repo.job_type).then(function(response) {
            function getEvents() {
                api.status(response.id).then(function(status) {
                    $scope.job.events = status;
                    if (status.length > 0 && status[status.length-1].action === 'job_finished') {
                        if (timerId) {
                            $interval.cancel(timerId);
                        }
                    } else if (!timerId) {
                        timerId = $interval(getEvents, 1000);
                    }
                }, function(error) {
                    throw error;
                });
            }

            $scope.job = response;
            getEvents();
        }, function(error) {
            throw error;
        });
        // switch to status page on success, report error?
    };
});
