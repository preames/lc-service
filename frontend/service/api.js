angular.module('frontend').factory('api', function($http, $q) {
    var api = {
        start: function(url) {
            var deferred = $q.defer();
            $http.post('/api/start', 'repository=' + encodeURIComponent(url),
                {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }).then(function(response) {
                deferred.resolve(response.data.status);
            }, function(response) {
                deferred.reject(response);
            });
            return deferred.promise;
        }
    };

    return api;
});