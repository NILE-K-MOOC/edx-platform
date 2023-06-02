(function (define) {
    define([
        'underscore',
        'backbone',
        'js/discovery/models/course_discovery',
        'js/discovery/collections/filters'
    ], function (_, Backbone, CourseDiscovery, Filters) {
        'use strict';


        return Backbone.Model.extend({

            page: 0,
            pageSize: 20,
            searchTerm: '',
            sort: "start:desc",
            terms: {},
            jqhxr: null,

            initialize: function () {
                this.discovery = new CourseDiscovery();
                this.listenTo(this.discovery, 'sync', this.onSync, this);
                this.listenTo(this.discovery, 'error', this.onError, this);
            },
            performSearch: function (searchTerm, otherTerms) {
                // main 태그에 data-param 이 있으면 데이터에 값을 추가하고 선택된 형태르 변경후 data-param을 삭제

                //console.log("searchTerm:::::" + searchTerm);

                let k, v, t;
                $("#main input[name='default_term']").each(function () {
                    k = $(this).data('key');
                    v = $(this).data('value');
                    var obj = new Object();
                    obj[k] = v;

                    _.extend(otherTerms, obj);
                });

                this.reset();
                this.searchTerm = searchTerm;
                if (otherTerms) {
                    this.terms = otherTerms;
                }
                this.sendQuery(this.buildQuery(0));
            },

            refineSearch: function (terms) {
                this.reset();
                this.terms = terms;
                this.sendQuery(this.buildQuery(0));
            },

            loadNextPage: function () {
                if (this.hasNextPage()) {
                    this.sendQuery(this.buildQuery(this.page + 1));
                }
            },

            // private

            hasNextPage: function () {
                var total = this.discovery.get('totalCount');
                return total - ((this.page + 1) * this.pageSize) > 0;
            },

            sendQuery: function (data) {
                this.jqhxr && this.jqhxr.abort();
                this.jqhxr = this.discovery.fetch({
                    type: 'POST',
                    data: data
                });

                return this.jqhxr;
            },

            getTermParameter: function (sParam) {
                var sPageURL = decodeURIComponent(window.location.search.substring(1)),
                    sURLVariables = sPageURL.split('&'),
                    sParameterName,
                    i;

                for (i = 0; i < sURLVariables.length; i++) {
                    sParameterName = sURLVariables[i].split('=');

                    if (sParameterName[0] === sParam) {
                        return sParameterName[1] === undefined ? true : sParameterName[1];
                    }
                }
            },
            buildQuery: function (pageIndex) {
                var data = {
                    search_string: this.searchTerm,
                    page_size: this.pageSize,
                    page_index: pageIndex,
                    sort: this.sort
                };
                // console.log('buildQuery --- s');
                // console.log("this terms:"+ this.terms);
                // console.log('buildQuery --- e');
                _.extend(data, this.terms);

                /* 대분류 검사 */
                var get_term = this.getTermParameter('term');
                if (get_term) {
                    _.extend(data, {"classfy": get_term});
                }
                /* 중분류 검사 */
                var get_mterm = this.getTermParameter('mterm')
                if (get_mterm) {
                    _.extend(data, {"middle_classfy": get_mterm});
                }

                /* 언어학 부분 검사 */
                var linguistics = this.getTermParameter('linguistics');
                if (linguistics) {
                    _.extend(data, {"linguistics": linguistics});


                }

                /* 강의기간 분류류 */
                var course_period = this.getTermParameter('course_period');
                if (course_period) {
                    _.extend(data, {"course_period": course_period});
                }

                /**
                 * 강의 종류 검색
                 * range=e : 종료된 강의
                 * range=i : 진행중 강의
                 * range=t : 진행예정 강의
                 */
                var range = this.getTermParameter('range');

                if (range) {
                    _.extend(data, {'range': range});
                }

                return data;
            },

            reset: function () {
                this.discovery.reset();
                this.page = 0;
                this.errorMessage = '';
            },

            onError: function (collection, response, options) {
                if (response.statusText !== 'abort') {
                    this.errorMessage = response.responseJSON.error;
                    this.trigger('error');
                }
            },

            onSync: function (collection, response, options) {

                var total = this.discovery.get('totalCount');
                var originalSearchTerm = this.searchTerm;
                if (options.data.page_index === 0) {
                    if (total === 0) {
                        // list all courses
                        this.cachedDiscovery().done(function (cached) {
                            this.discovery.courseCards.reset(cached.courseCards.toJSON());
                            this.discovery.facetOptions.reset(cached.facetOptions.toJSON());
                            this.discovery.set('latestCount', cached.get('latestCount'));
                            this.trigger('search', originalSearchTerm, total);
                        });
                        this.searchTerm = '';
                        this.terms = {};
                    } else {
                        _.each(this.terms, function (term, facet) {
                            if (facet !== 'search_query') {
                                var option = this.discovery.facetOptions.findWhere({
                                    facet: facet,
                                    term: term
                                });
                                if (option) {
                                    option.set('selected', true);
                                }
                            }
                        }, this);

                        //alert('this.searchTerm:' + this.searchTerm);

                        this.trigger('search', this.searchTerm, total);
                    }
                } else {
                    this.page = options.data.page_index;
                    this.trigger('next');
                }
            },

            // lazy load
            cachedDiscovery: function () {

                var deferred = $.Deferred();
                var self = this;


                if (this.cached) {
                    deferred.resolveWith(this, [this.cached]);
                } else {
                    this.cached = new CourseDiscovery();
                    this.cached.fetch({
                        type: 'POST',
                        data: {
                            search_string: '',
                            page_size: this.pageSize,
                            page_index: 0,
                            sort: this.sort
                        },
                        success: function (model, response, options) {
                            deferred.resolveWith(self, [model]);
                        }
                    });
                }
                return deferred.promise();
            }

        });
    });
}(define || RequireJS.define));
