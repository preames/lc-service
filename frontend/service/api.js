angular.module('frontend').factory('api', function($http, $q) {
    var api = {
        start: function(url, job_type) {
            var deferred = $q.defer();
            $http.post('/api/start',
	        'repository=' + encodeURIComponent(url) + '&job_type=' + encodeURIComponent(job_type),
                {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }).then(function(response) {
                deferred.resolve(response.data);
            }, function(response) {
                deferred.reject(response);
            });
            return deferred.promise;
        },
        status: function(id) {
            var deferred = $q.defer();
            $http.post('/api/status', 'id=' + encodeURIComponent(id),
                {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }).then(function(response) {
                    deferred.resolve(response.data);
                }, function(response) {
                    deferred.reject(response);
                });
            return deferred.promise;
        }
    };

    return api;
});
