;(function (define) {

    define([
        'underscore',
        'backbone',
        'js/discovery/models/course_card',
        'js/discovery/models/facet_option',
    ], function (_, Backbone, CourseCard, FacetOption) {
        'use strict';
        var facet_row_temp = {};
        var facet_row_temp_set = {};
        var facet_row_set = {};


        return Backbone.Model.extend({
            url: '/search/course_discovery/',
            jqhxr: null,

            defaults: {
                totalCount: 0,
                latestCount: 0
            },

            initialize: function () {
                this.courseCards = new Backbone.Collection([], {model: CourseCard});
                this.facetOptions = new Backbone.Collection([], {model: FacetOption});
            },

            parse: function (response) {
                var courses = response.results || [];
                var facets = response.facets || {};
                this.courseCards.add(_.pluck(courses, 'data'));

                this.set({
                    totalCount: response.total,
                    latestCount: courses.length
                });

                var options = this.facetOptions;

                var cnt = 0;

                facet_row_temp = {};
                facet_row_temp_set = {};
                facet_row_set = {};

                _(facets).each(function (obj, key) {

                    //console.log("parse --------" + "obj:" + obj + ", key:" + key);

                    if (key == 'org') {

                        var count2 = 0;
                        var count3 = 0;
                        var term2 = "sum_test";

                        // skp, smu hard coding
                        //console.log("_(obj.terms) ==>"+_(obj.terms));

                        _(obj.terms).each(function (count, term) {

                            //console.log("1 _(obj.terms).each --------" + "term:" + term + ", count:" + count);

                            if (term.match(/^SKP.*/)) {
                                count2 += count;
                                return true;
                            }
                            if (term === 'SMUk' || term === 'SMUCk') {
                                count3 += count;
                                return true;
                            }
                            options.add({
                                facet: key,
                                term: term,
                                count: count
                            }, {merge: true});
                        });

                        // skp, smu hard coding
                        if (count2 > 0) {
                            options.add({
                                facet: key,
                                term: 'SKP',
                                count: count2
                            }, {merge: true});
                        }
                        if (count3 > 0) {
                            options.add({
                                facet: key,
                                term: 'SMUk',
                                count: count3
                            }, {merge: true});
                        }
                    } else {
                        _(obj.terms).each(function (count, term) {
                            //classfy and middle_classfy count
                            //console.log("2 _(obj.terms).each --------" + "term:" + term + ", count:" + count);

                            //facet_row_temp[key] = term;
                            //facet_row_temp_set[term] = count;
                            facet_row_temp[key] = {facet: key, term: term, count: count};
                            facet_row_temp_set[cnt++] = facet_row_temp[key];

                            //options.add({
                            //    facet: key,
                            //    term: term,
                            //    count: count
                            //}, {merge: true});
                        });
                    }
                });

                //for(var key in facet_row_temp) {
                //    console.log("facet_row_temp["+key+"] : " + facet_row_temp[key]);
                //    for(var subkey in facet_row_temp[key]) {
                //        console.log("facet_row_temp["+key+"]["+subkey+"] : " + facet_row_temp[key][subkey]);
                //    }
                //}

                facet_row_set = facet_row_temp_set;
                var v1 = 0;
                var v2 = 0;
                var v3 = 0;
                for(var key in facet_row_set) {
                    //console.log("facet_row_set[" + key + "][facet] : " + facet_row_set[key]['facet'] + ":" + facet_row_set[key]['term'] + facet_row_set[key]['count']);
                    //look for the same name
                    if (facet_row_set[key]['facet'] == 'classfysub') {
                        for(var key1 in facet_row_set) {
                            if (facet_row_set[key1]['facet'] == 'classfy') {
                                if (facet_row_set[key]['term'] == facet_row_set[key1]['term']){
                                    v1 = v2 = v3 = 0;
                                    v1 = parseInt(facet_row_set[key]['count']);
                                    v2 = parseInt(facet_row_set[key1]['count']);
                                    v3 = v1+v2;
                                    facet_row_set[key1]['count'] = v3;     // count plus
                                }
                            }
                        }
                    } else if (facet_row_set[key]['facet'] == 'middle_classfysub') {
                        for (var key1 in facet_row_set) {
                            if (facet_row_set[key1]['facet'] == 'middle_classfy') {
                                if (facet_row_set[key]['term'] == facet_row_set[key1]['term']) {
                                    v1 = v2 = v3 = 0;
                                    v1 = parseInt(facet_row_set[key]['count']);
                                    v2 = parseInt(facet_row_set[key1]['count']);
                                    v3 = v1+v2;
                                    facet_row_set[key1]['count'] = v3;     // count plus
                                }
                            }
                        }
                    }
                }

                // if it does not exist, add it.
                var exist_flag = false;
                var exist_in_flag = false;
                for(var key in facet_row_set) {
                    exist_flag = false;
                    exist_in_flag = true;
                    if (facet_row_set[key]['facet'] == 'classfysub') {
                        for(var key1 in facet_row_set) {
                            if (facet_row_set[key1]['facet'] == 'classfy') {
                                if (facet_row_set[key]['term'] == facet_row_set[key1]['term']){
                                    exist_flag = true;
                                }
                                if (facet_row_set[key]['term'] == 'null' || facet_row_set[key]['term'] == 'all' || facet_row_set[key]['term'] == ''){
                                    exist_in_flag = false;
                                }
                            }
                        }
                        if (exist_flag == false && exist_in_flag == true) {
                            facet_row_set[key]['facet'] = 'classfy'
                        }
                    } else if (facet_row_set[key]['facet'] == 'middle_classfysub') {
                        for (var key1 in facet_row_set) {
                            if (facet_row_set[key1]['facet'] == 'middle_classfy') {
                                if (facet_row_set[key]['term'] == facet_row_set[key1]['term']){
                                    exist_flag = true;
                                }
                                if (facet_row_set[key]['term'] == 'null' || facet_row_set[key]['term'] == 'all' || facet_row_set[key]['term'] == ''){
                                    exist_in_flag = false;
                                }
                            }
                        }
                        if (exist_flag == false && exist_in_flag == true) {
                            facet_row_set[key]['facet'] = 'middle_classfy'
                        }
                    }
                }

                //debug data display
                //for(var key in facet_row_temp_set) {
                //    for(var subkey in facet_row_temp_set[key]) {
                //        console.log("facet_row_temp_set[" + key + "][" + subkey + "] : " + facet_row_temp_set[key][subkey]);
                //    }
                //}

                for(var key in facet_row_set) {
                    for(var subkey in facet_row_set[key]) {
                        //console.log("facet_row_set[" + key + "][" + subkey + "] : " + facet_row_set[key][subkey]);
                        if (facet_row_set[key]['facet'] == 'classfysub') {
                            //look for the same name
                        } else if (facet_row_set[key]['facet'] == 'middle_classfysub') {
                            //look for the same name and count plus
                        } else {
                            options.add({
                                facet: facet_row_set[key]['facet'],
                                term: facet_row_set[key]['term'],
                                count: facet_row_set[key]['count']
                            }, {merge: true});
                        }
                    }
                }
            },

            reset: function () {
                this.set({
                    totalCount: 0,
                    latestCount: 0
                });
                this.courseCards.reset();
                this.facetOptions.reset();
            },

            latest: function () {
                return this.courseCards.last(this.get('latestCount'));
            }

        });

    });


})(define || RequireJS.define);
