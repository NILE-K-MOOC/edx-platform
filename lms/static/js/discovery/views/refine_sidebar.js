(function (define) {
    define([
        'jquery',
        'underscore',
        'backbone',
        'edx-ui-toolkit/js/utils/html-utils'
    ], function ($, _, Backbone, HtmlUtils) {
        'use strict';

        return Backbone.View.extend({

            el: '.search-facets',
            events: {
                // 'click li button': 'selectOption',
                // 'change .facet-list': 'selectOption1',
                'click #course-org-select-move': 'selectOption1',
                'click li button': 'selectOption2',
                'click .show-less': 'collapse',
                'click .show-more': 'expand'
            },

            initialize: function (options) {
                this.meanings = options.meanings || {};
                this.$container = this.$el.find('.search-facets-lists');
                this.facetTpl = HtmlUtils.template($('#facet-tpl').html());
                this.facetOptionTpl = HtmlUtils.template($('#facet_option-tpl').html());
            },

            facetName: function (key) {
                if (key == 'middle_classfy') {
                    return gettext("Sub classified by");
                } else if (key == 'course_period') {
                    return gettext("Period of Studing");
                } else {
                    return this.meanings[key] && this.meanings[key].name || key;
                }
            },

            termName: function (facetKey, termKey) {
                return this.meanings[facetKey] &&
                    this.meanings[facetKey].terms &&
                    this.meanings[facetKey].terms[termKey] || termKey;
            },

            renderOptions: function (options) {
                return HtmlUtils.joinHtml.apply(this, _.map(options, function (option) {
                    var data = _.clone(option.attributes);

                    console.debug("renderOptions check facet > " + data.facet + " : term > " + data.term);

                    if (data.facet == 'classfy' || data.facet == 'classfysub') {
                        switch (data.term) {
                            case 'hum':
                                data.name = this.termName(data.facet, gettext("Humanities"));
                                break;
                            case 'social':
                                data.name = this.termName(data.facet, gettext("Social"));
                                break;
                            case 'edu':
                                data.name = this.termName(data.facet, gettext("Education"));
                                break;
                            case 'eng':
                                data.name = this.termName(data.facet, gettext("Engineering"));
                                break;
                            case 'nat':
                                data.name = this.termName(data.facet, gettext("Natural Sciences"));
                                break;
                            case 'med':
                                data.name = this.termName(data.facet, gettext("Medical Sciences & Pharmacy"));
                                break;
                            case 'art':
                                data.name = this.termName(data.facet, gettext("Arts & Physical Education"));
                                break;
                            case 'intd':
                                data.name = this.termName(data.facet, gettext("Interdisciplinary"));
                                break;
                            default:
                                data.name = this.termName(data.facet, data.term);
                        }
                    } else if (data.facet == 'course_period') {
                        switch (data.term) {
                            case 'S':
                                data.name = this.termName(data.facet, gettext("Short(1~6 weeks)"));
                                break;
                            case 'M':
                                data.name = this.termName(data.facet, gettext("Middle(7~12 weeks)"));
                                break;
                            case 'L':
                                data.name = this.termName(data.facet, gettext("Long(over 13 weeks)"));
                                break;
                        }
                    } else if (data.facet == 'middle_classfy') {

                        var middle_text = {
                            "lang": "Linguistics & Literature",
                            "husc": "Human Sciences",
                            "busn": "Business Administration & Economics",
                            "law": "Law",
                            "scsc": "Social Sciences",
                            "enor": "General Education",
                            "ekid": "Early Childhood Education",
                            "espc": "Special Education",
                            "elmt": "Elementary Education",
                            "emdd": "Secondary Education",
                            "cons": "Architecture",
                            "civi": "Civil Construction & Urban Engineering",
                            "traf": "Transportation",
                            "mach": "Mechanical & Metallurgical Engineering",
                            "elec": "Electricity & Electronics",
                            "deta": "Precision & Energy",
                            "matr": "Materials",
                            "comp": "Computers & Communication",
                            "indu": "Industrial Engineering",
                            "cami": "Chemical Engineering",
                            "other": "Others",
                            "agri": "Agriculture & Fisheries",
                            "bio": "Biology, Chemistry & Environmental Science",
                            "life": "Living Science",
                            "math": "Mathematics, Physics, Astronomy & Geography",
                            "metr": "Medical Science",
                            "nurs": "Nursing",
                            "phar": "Pharmacy",
                            "heal": "Therapeutics & Public Health",
                            "dsgn": "Design",
                            "appl": "Applied Arts",
                            "danc": "Dancing & Physical Education",
                            "form": "FineArts & Formative Arts",
                            "play": "Drama & Cinema",
                            "musc": "Music",
                            "intd_m": "Interdisciplinary",
                        };
                        if (middle_text[data.term]) {
                            data.name = this.termName(data.facet, gettext(middle_text[data.term]));
                        } else {
                            data.name = this.termName(data.facet, data.term);
                        }
                    } else if (data.facet == 'home_course_yn') {
                        // 집콕강좌 옵션 추가
                        if (data.term.toUpperCase() == 'Y') {
                            data.name = this.termName('home_course_yn', gettext("home_course_y"));
                        }

                    } else if (data.facet == 'home_course_step') {
                        // 집콕강좌 옵션 추가
                        //console.log('data.term:' + data.term);

                        if (data.term == '1') {
                            data.name = this.termName('home_course_step', gettext("home_course_step_1"));
                        } else if (data.term == '2') {
                            data.name = this.termName('home_course_step', gettext("home_course_step_2"));
                        } else if (data.term == '3') {
                            data.name = this.termName('home_course_step', gettext("home_course_step_3"));

                        }


                    } else if (data.facet == 'fourth_industry_yn' || data.facet == 'job_edu_yn' || data.facet == 'ai_sec_yn' || data.facet == 'basic_science_sec_yn' || data.facet == 'linguistics_yn' || data.facet == 'liberal_arts_yn' || data.facet == 'career_readiness_competencies_yn' || data.facet == 'matchup_yn') {

                        if (data.facet == 'fourth_industry_yn' && data.term.toUpperCase() == 'Y') {
                            data.name = this.termName('fourth_industry_yn', gettext("fourth_industry_y"));
                        } else if (data.facet == 'job_edu_yn' && data.term.toUpperCase() == 'Y') {
                            data.name = this.termName('job_edu_yn', gettext("job_edu_y"));
                        } else if (data.facet == 'ai_sec_yn' && data.term.toUpperCase() == 'Y') {
                            data.name = this.termName('ai_sec_yn', gettext("ai_sec_y"));
                        } else if (data.facet == 'basic_science_sec_yn' && data.term.toUpperCase() == 'Y') {
                            data.name = this.termName('basic_science_sec_yn', gettext("basic_science_sec_y"));
                        } else if (data.facet == 'linguistics_yn' && data.term.toUpperCase() == 'Y') {
                            data.name = this.termName('linguistics_yn', gettext("linguistics_y"));
                        } else if (data.facet == 'liberal_arts_yn' && (data.term.toUpperCase() == 'Y' || data.term == 'liberal_arts_y')) {
                            data.name = this.termName('liberal_arts_yn', gettext("liberal_arts_y"));
                        } else if (data.facet == 'career_readiness_competencies_yn' && (data.term.toUpperCase() == 'Y' || data.term == 'career_readiness_competencies_y')) {
                            data.name = this.termName('career_readiness_competencies_yn', gettext("career_readiness_competencies_y"));
                        } else if (data.facet == 'matchup_yn' && (data.term.toUpperCase() == 'Y' || data.term == 'matchup_y')) {
                            data.name = this.termName('matchup_yn', gettext("matchup_y"));
                        } else {
                            data.name = this.termName(data.facet, data.term);
                        }

                    } else if (data.facet == 'org') {
                        data.name = this.termName(data.facet, data.name);
                    } else {
                        data.name = this.termName(data.facet, data.term);
                    }

                    return this.facetOptionTpl(data);
                }, this));
            },

            renderFacet: function (facetKey, options) {

                // console.log('facetKey ==> ' + facetKey);

                return this.facetTpl({
                    name: facetKey,
                    displayName: this.facetName(facetKey),
                    optionsHtml: this.renderOptions(options),
                    listIsHuge: (options.length > 9)
                });
            },

            render: function () {
                let e = this;
                var i = 0;
                this.collection.comparator = function (model) {
                    i = 0;
                    switch (model.get('facet')) {
                        case 'classfy':
                            model.set('odby1', 10);
                            break;
                        case 'middle_classfy':
                            model.set('odby1', 20);
                            break;
                        case 'fourth_industry_yn':
                            model.set('odby1', 30);
                            break;
                        case 'linguistics':
                            model.set('odby1', 40);
                            break;
                        case 'liberal_arts_yn':
                            model.set('odby1', 41);
                            break;
                        case 'career_readiness_competencies_yn':
                            model.set('odby1', 42);
                            break;
                        case 'course_period':
                            model.set('odby1', 50);
                            break;
                        case 'language':
                            model.set('odby1', 60);
                            break;
                        case 'course_level':
                            model.set('odby1', 70);
                            break;
                        case 'home_course_yn':
                            model.set('odby1', 80);
                            break;
                        case 'home_course_step':
                            model.set('odby1', 90);
                            break;
                        case 'ribbon_yn':
                            model.set('odby1', 91);
                            break;
                        case 'matchup_yn':
                            model.set('odby1', 92);
                            break;

                        default:
                            model.set('odby1', 99);
                    }

                    switch (model.get('term')) {
                        //classfy or classfysub
                        case 'hum':
                            model.set('odby2', 1);
                            break;
                        case 'social':
                            model.set('odby2', 2);
                            break;
                        case 'edu':
                            model.set('odby2', 3);
                            break;
                        case 'eng':
                            model.set('odby2', 4);
                            break;
                        case 'nat':
                            model.set('odby2', 5);
                            break;
                        case 'med':
                            model.set('odby2', 6);
                            break;
                        case 'art':
                            model.set('odby2', 7);
                            break;

                        //middle_classfy or middle_classfysub
                        case 'lang':
                            model.set('odby2', 1);
                            break;
                        case 'husc':
                            model.set('odby2', 2);
                            break;
                        case 'busn':
                            model.set('odby2', 3);
                            break;
                        case 'law' :
                            model.set('odby2', 4);
                            break;
                        case 'scsc':
                            model.set('odby2', 5);
                            break;
                        case 'enor':
                            model.set('odby2', 6);
                            break;
                        case 'ekid':
                            model.set('odby2', 7);
                            break;
                        case 'espc':
                            model.set('odby2', 8);
                            break;
                        case 'elmt':
                            model.set('odby2', 9);
                            break;
                        case 'emdd':
                            model.set('odby2', 10);
                            break;
                        case 'cons':
                            model.set('odby2', 11);
                            break;
                        case 'civi':
                            model.set('odby2', 12);
                            break;
                        case 'traf':
                            model.set('odby2', 13);
                            break;
                        case 'mach':
                            model.set('odby2', 14);
                            break;
                        case 'elec':
                            model.set('odby2', 15);
                            break;
                        case 'deta':
                            model.set('odby2', 16);
                            break;
                        case 'matr':
                            model.set('odby2', 17);
                            break;
                        case 'comp':
                            model.set('odby2', 18);
                            break;
                        case 'indu':
                            model.set('odby2', 19);
                            break;
                        case 'cami':
                            model.set('odby2', 20);
                            break;
                        case 'other':
                            model.set('odby2', 21);
                            break;
                        case 'agri':
                            model.set('odby2', 22);
                            break;
                        case 'bio':
                            model.set('odby2', 23);
                            break;
                        case 'life':
                            model.set('odby2', 24);
                            break;
                        case 'math':
                            model.set('odby2', 25);
                            break;
                        case 'metr':
                            model.set('odby2', 26);
                            break;
                        case 'nurs':
                            model.set('odby2', 27);
                            break;
                        case 'phar':
                            model.set('odby2', 28);
                            break;
                        case 'heal':
                            model.set('odby2', 29);
                            break;
                        case 'dsgn':
                            model.set('odby2', 30);
                            break;
                        case 'appl':
                            model.set('odby2', 31);
                            break;
                        case 'danc':
                            model.set('odby2', 32);
                            break;
                        case 'form':
                            model.set('odby2', 33);
                            break;
                        case 'play':
                            model.set('odby2', 34);
                            break;
                        case 'musc':
                            model.set('odby2', 35);
                            break;
                        case 'intd_m':
                            model.set('odby2', 36);
                            break;

                        //course_period
                        case 'S':
                            model.set('odby2', 1);
                            break;
                        case 'M':
                            model.set('odby2', 2);
                            break;
                        case 'L':
                            model.set('odby2', 3);
                            break;
                        //language
                        case 'ko':
                            model.set('odby2', 1);
                            break;
                        case 'en':
                            model.set('odby2', 2);
                            break;
                        case 'zh':
                            model.set('odby2', 3);
                            break;
                        // home_course_step
                        case '1':
                            model.set('odby2', 1);
                        case '2':
                            model.set('odby2', 2);
                        case '3':
                            model.set('odby2', 3);

                        default:
                            model.set('odby2', 99);
                    }
                    return [model.get('odby1'), model.get('odby2')];
                };

                this.collection.sort();

                var grouped = this.collection.groupBy('facet');
                var htmlSnippet = HtmlUtils.joinHtml.apply(
                    this, _.map(grouped, function (options, facetKey) {
                        if (facetKey == 'modes') {
                            return;
                        }

                        if (options.length > 0) {
                            if (facetKey === 'org') {
                                var org_names = [];
                                $.ajax({
                                    url: '/search_org',
                                    async: false,
                                }).done(function (data) {
                                    org_names = data.org_dict;
                                });
                                var options2 = [];
                                _.map(options, function (option) {
                                    option.attributes.name = gettext(option.attributes.term);
                                    for (var i = 0; i < org_names.length; i++) {
                                        if (org_names[i].hasOwnProperty(option.attributes.term)) {
                                            option.attributes.name = org_names[i][option.attributes.term];
                                        }
                                    }
                                    options2.push(option);
                                });
                                //기관명으로 정렬
                                options2.sort(function (a, b) {
                                    return a.attributes.name.localeCompare(b.attributes.name);
                                });

                                return this.renderFacet(facetKey, options2);
                            } else {
                                return this.renderFacet(facetKey, options);
                            }
                        }
                    }, this)
                );
                HtmlUtils.setHtml(this.$container, htmlSnippet);

                $("h3[data-name='fourth_industry_yn']").text(gettext('Category of interest'));

                let li_list1 = $("#ai_sec_yn li").clone();
                let li_list2 = $("#basic_science_sec_yn li").clone();
                let li_list3 = $("#job_edu_yn li").clone();
                let li_list4 = $("#linguistics_yn li").clone();
                let li_list5 = $("#liberal_arts_yn li").clone();
                let li_list6 = $("#career_readiness_competencies_yn li").clone();
                let li_list7 = $("#matchup_yn li").clone();

                $("#fourth_industry_yn").append(li_list1, li_list2, li_list3, li_list4, li_list5, li_list6, li_list7);

                $(".search-facets li").each(function () {
                    let v = $(this).find("button").data('value');

                    if (typeof v == 'number')
                        return true;

                    if (!v || ['n', 'ribbon_n', 'liberal_arts_n', 'career_readiness_competencies_n', 'none', 'matchup_n', 'null', 'all', ''].indexOf(v.toString().toLowerCase()) >= 0) {
                        $(this).remove();
                    }
                });

                // 교양강좌 종류의 표시 영문명 변경
                $("h3:contains('liberal_arts')").text('on TV');

                $("#job_edu_yn, #ai_sec_yn, #basic_science_sec_yn, #linguistics_yn, #liberal_arts_yn, #career_readiness_competencies_yn, #matchup_yn").remove();

                // 20220517 집콕강좌 사용안함으로 삭제처리
                $("h3[data-name='home_course_step']").remove();
                $("ul[data-facet='home_course_step']").remove();

                // main 태그에 data-param 이 있으면 데이터에 값을 추가하고 선택된 형태르 변경후 data-param을 삭제
                let k, v, t;
                $("#main input[name='default_term']").each(function () {
                    k = $(this).data('key');
                    v = $(this).data('value');
                    var obj = new Object();
                    obj[k] = v;

                    $(this).remove();

                    // 검색박스 표시
                    if (k && v) {
                        switch (k) {
                            case 'fourth_industry_yn':
                                k = 'fourth_industry_yn';
                                v = 'fourth_industry_y';
                                t = 'fourth_industry_y';
                                break;
                            case 'job_edu_yn':
                                k = 'job_edu_yn'
                                v = 'job_edu_y';
                                t = 'job_edu_y';
                                break;
                            case 'ai_sec_yn':
                                k = 'ai_sec_yn';
                                v = 'ai_sec_y';
                                t = 'ai_sec_y';
                                break;
                            case 'basic_science_sec_yn':
                                k = 'basic_science_sec_yn';
                                v = 'basic_science_y';
                                t = 'basic_science_y';
                                break;
                            case 'linguistics_yn':
                                k = 'linguistics_yn';
                                v = 'y';
                                t = 'linguistics_y';
                                break;
                            case 'liberal_arts_yn':
                                k = 'liberal_arts_yn';
                                v = 'liberal_arts_y';
                                t = 'liberal_arts_y';
                                break;
                            case 'career_readiness_competencies_yn':
                                k = 'career_readiness_competencies_yn';
                                v = 'career_readiness_competencies_y';
                                t = 'career_readiness_competencies_y';
                                break;
                            case 'matchup_yn':
                                k = 'matchup_yn';
                                v = 'matchup_y';
                                t = 'matchup_y';
                                break;

                            case 'home_course_yn':
                                k = 'home_course_yn';
                                v = 'Y';
                                t = 'home_course_y';
                                break;
                            case 'home_course_step':
                                k = 'home_course_step';
                                v = v;

                                if (v == '1') {
                                    t = 'home_course_step_1';
                                } else if (v == '2') {
                                    t = 'home_course_step_2';
                                } else if (v == '3') {
                                    t = 'home_course_step_3';
                                }
                                break;
                        }

                        if ($("button[data-facet='" + k + "'][data-value='" + v + "']").size() > 0) {
                            e.trigger(
                                'selectedOption',
                                k,
                                v,
                                gettext(t)
                            );
                        } else {
                            console.debug('선택된 검색어가 존재 하지 않습니다.' + k + " : " + v);
                        }
                    }
                    return this;
                });


            },

            collapse: function (event) {
                var $el = $(event.currentTarget),
                    $more = $el.siblings('.show-more'),
                    // $ul = $el.parent().siblings('ul');
                    $ul = $('#' + ($el).attr('id')).parent().prev();
                $ul.addClass('collapse');
                $el.addClass('hidden');
                $more.removeClass('hidden');
            },

            expand: function (event) {
                var $el = $(event.currentTarget),
                    // $ul = $el.parent('div').siblings('ul');
                    $ul = $('#' + ($el).attr('id')).parent('div').prev();
                $el.addClass('hidden');
                $ul.removeClass('collapse');
                $el.siblings('.show-less').removeClass('hidden');
            },

            selectOption: function (event) {
                $(".course-facets-select").focus();
                $(".search-facets-lists").focus();
                var $target = $(event.currentTarget);
                var select_val = $target.val();
                var select_index = select_val.split('+');

                this.trigger(
                    'selectOption',
                    $target.data('facet'),
                    select_index[0],
                    select_index[1]
                );

                console.debug('select_val: ' + select_val);

                $(".facet-list option[value=" + select_val + "]").attr("selected", "selected")
            },

            selectOption1: function (event) {

                $(".course-facets-select").focus();
                $(".search-facets-lists").focus();

                var $target = $(event.currentTarget);
                var select_val = $("#org_select").val();
                var select_index = select_val.split('+');

                this.trigger(
                    'selectOption',
                    $target.data('facet'),
                    select_index[0],
                    select_index[1]
                );

                console.debug('select_val1: ' + select_val);

                $(".facet-list option[value='" + select_val + "']").attr("selected", "selected")
            },

            selectOption2: function (event) {
                $(".course-facets-select").focus();
                var $target = $(event.currentTarget);

                let f, v, t;

                f = $target.data('facet');
                v = $target.data('value');
                t = $target.data('text');

                // console.log('selectOption2 check ---- s')
                // console.log(f);
                // console.log(v);
                // console.log(t);

                // 한글화 후 표시
                t = gettext(t);
                // console.log(t);
                // console.log('selectOption2 check ---- e')

                // console.debug('select_val2: ' + select_val);

                this.trigger(
                    'selectOption', f, v, t
                );
            }
        });
    });
}(define || RequireJS.define));
