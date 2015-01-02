angular.module('frontend', ['ui.bootstrap','ui.utils','ngRoute','ngAnimate']);

angular.module('frontend').constant('CSRF_COOKIE_NAME', 'csrftoken');
angular.module('frontend').constant('CSRF_HEADER_NAME', 'X-CSRFToken');

angular.module('frontend').config(function($routeProvider, $httpProvider, CSRF_COOKIE_NAME, CSRF_HEADER_NAME) {
    // for compatibility with Django CSRF mechanisms
    $httpProvider.defaults.xsrfCookieName = CSRF_COOKIE_NAME;
    $httpProvider.defaults.xsrfHeaderName = CSRF_HEADER_NAME;

    $routeProvider.when('/home', {
        templateUrl: 'partial/repo-form/repo-form.html',
        controller: 'RepoFormCtrl'
    });
    /* Add New Routes Above */
    $routeProvider.otherwise({redirectTo:'/home'});
});

angular.module('frontend').run(function($rootScope) {
    $rootScope.safeApply = function(fn) {
        var phase = $rootScope.$$phase;
        if (phase === '$apply' || phase === '$digest') {
            if (fn && (typeof(fn) === 'function')) {
                fn();
            }
        } else {
            this.$apply(fn);
        }
    };
});
