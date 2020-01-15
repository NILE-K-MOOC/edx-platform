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
                'change .facet-list': 'selectOption',
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
                if (key == 'classfy') {
                    return gettext("Classified by");
                }
                else if (key == 'middle_classfy') {
                    return gettext("Sub classified by");
                }
                else if (key == 'course_period') {
                    return gettext("Period of Studing");
                }
                else {
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
                    }
                    else if (data.facet == 'middle_classfy') {

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
                    }
                    else if (data.facet == 'fourth_industry_yn' || data.facet == 'linguistics' || data.facet == 'job_edu_yn') {

                        if (data.facet == 'fourth_industry_yn' && data.term.toUpperCase() == 'Y') {
                            data.name = this.termName('fourth_industry_yn', gettext("fourth_industry_y"));
                        } else if (data.facet == 'job_edu_yn' && data.term.toUpperCase() == 'Y') {
                            data.name = this.termName('job_edu_yn', gettext("job_edu_y"));
                        } else if (data.facet == 'linguistics' && data.term.toUpperCase() == 'Y') {
                            data.name = this.termName('linguistics', gettext("linguistics_y"));
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
                return this.facetTpl({
                    name: facetKey,
                    displayName: this.facetName(facetKey),
                    optionsHtml: this.renderOptions(options),
                    listIsHuge: (options.length > 9)
                });
            },

            render: function () {
                var i = 0;
                this.collection.comparator = function (model) {

                    i = 0;
                    switch (model.get('facet')) {
                        case 'classfy':
                            model.set('odby1', 1);
                            break;
                        case 'middle_classfy':
                            model.set('odby1', 2);
                            break;
                        case 'fourth_industry_yn':
                            model.set('odby1', 3);
                            break;
                        case 'course_period':
                            model.set('odby1', 4);
                            break;
                        case 'language':
                            model.set('odby1', 5);
                            break;
                        case 'course_level':
                            model.set('odby1', 6);
                            break;

                        default:
                            model.set('odby1', 7);
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
                                }).done(function(data){
                                    org_names = data.org_dict;
                                });
                                var options2 = [];
                                _.map(options, function (option) {
                                    option.attributes.name = gettext(option.attributes.term);
                                    for(var i=0; i<org_names.length; i++) {
                                        if(org_names[i].hasOwnProperty(option.attributes.term)){
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

                // 20200115 임시 비활성화
                $("h3[data-name='fourth_industry_yn']").hide();
                $("#fourth_industry_yn").hide();

                $("h3[data-name='fourth_industry_yn']").text(gettext('etc'));

                let lis1 = $("#linguistics li").clone();
                let lis2 = $("#job_edu_yn li").clone();

                $("#fourth_industry_yn").append(lis1, lis2);

                $("#fourth_industry_yn li").each(function () {
                    let v = $(this).find("button").data('value');

                    if (v.toUpperCase() == 'N') {
                        $(this).remove();
                        console.log('remove..');
                    }
                });

                $("#linguistics, #job_edu_yn").remove();

                // 20200115 임시 비활성화
                $("h3[data-name='fourth_industry_yn']").hide();
                $("#fourth_industry_yn").hide();



                // main 태그에 data-param 이 있으면 데이터에 값을 추가하고 선택된 형태르 변경후 data-param을 삭제
                let k, v, t;
                $("#main input[name='default_term']").each(function () {
                    k = $(this).data('key');
                    v = $(this).data('value');
                    var obj = new Object();
                    obj[k] = v;

                    $(this).remove();
                });

                // 검색박스 표시
                if (k && v) {
                    let e = this;
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
                        case 'linguistics':
                            k = 'linguistics';
                            v = 'Y';
                            t = 'linguistics_y';
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

                $(".facet-list option[value=" + select_val + "]").attr("selected", "selected")
            },
            selectOption2: function (event) {
                $(".course-facets-select").focus();
                var $target = $(event.currentTarget);

                let f, v, t;

                f = $target.data('facet');
                v = $target.data('value');
                t = $target.data('text');

                console.log('selectOption2 check ---- s')
                console.log(f);
                console.log(v);
                console.log(t);

                // 한글화 후 표시
                t = gettext(t);
                console.log(t);
                console.log('selectOption2 check ---- e')

                this.trigger(
                    'selectOption', f, v, t
                );
            }
        });
    });
}(define || RequireJS.define));
