angular.module('frontend', ['ui.bootstrap','ui.utils','ngRoute','ngAnimate']);

angular.module('frontend').config(function($routeProvider) {
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