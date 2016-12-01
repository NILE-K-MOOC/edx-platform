;(function (define) {

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
            'click li button': 'selectOption',
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
            if(key == 'classfy'){
                return gettext("Classified by");
            }
            else if(key == 'middle_classfy'){
                return gettext("Sub classified by");
            }
            else if(key == 'linguistics'){
                return gettext("Linguistics by");
            }
            else if(key == 'course_period'){
                return gettext("Period of Studing");
            }
            else {
                return this.meanings[key] && this.meanings[key].name || key;
            }

        },

        termName: function (facetKey, termKey) {
            return this.meanings[facetKey] &&
                this.meanings[facetKey].terms  &&
                this.meanings[facetKey].terms[termKey] || termKey;
        },

        renderOptions: function (options) {
            return HtmlUtils.joinHtml.apply(this, _.map(options, function(option) {
                var data = _.clone(option.attributes);

                if(data.facet == 'classfy'){
                    switch (data.term){
                        case 'hum':
                            data.name = this.termName(data.facet, gettext("Humanities"));break;
                        case 'social':
                            data.name = this.termName(data.facet, gettext("Social Sciences"));break;
                        case 'edu':
                            data.name = this.termName(data.facet, gettext("Education"));break;
                        case 'eng':
                            data.name = this.termName(data.facet, gettext("Engineering"));break;
                        case 'nat':
                            data.name = this.termName(data.facet, gettext("Natural Sciences"));break;
                        case 'med':
                            data.name = this.termName(data.facet, gettext("Medical Sciences & Pharmacy"));break;
                        case 'art':
                            data.name = this.termName(data.facet, gettext("Arts & Physical Education"));break;
                        default:
                            data.name = this.termName(data.facet, data.term);
                    }
                }else if(data.facet == 'course_period'){
                    switch (data.term){
                        case 'S':
                            data.name = this.termName(data.facet, gettext("Short(1~6 weeks)"));break;
                        case 'M':
                            data.name = this.termName(data.facet, gettext("Middle(7~12 weeks)"));break;
                        case 'L':
                            data.name = this.termName(data.facet, gettext("Long(over 13 weeks)"));break;
                    }
                }
                else if(data.facet == 'middle_classfy'){

                    var middle_text = {
                        "lang": "Linguistics & Literature","husc":"Humanities",
                        "busn":"Business Administration & Economics", "law":"Law", "scsc": "Social Sciences",
                        "enor":"General Education", "ekid":"Early Childhood Education", "espc":"Special Education", "elmt":"Elementary Education", "emdd":"Secondary Education",
                        "cons":"Architecture", "civi":"Civil Construction & Urban Engineering", "traf":"Transportation", "mach":"Mechanical & Metallurgical Engineering", "elec":"Electricity & Electronics", "deta":"Precision & Energy", "matr":"Materials", "comp":"Computers & Communication", "indu":"Industrial Engineering", "cami":"Chemical Engineering", "other":"Others",
                        "agri":"Agriculture & Fisheries", "bio":"Biology, Chemistry & Environmental Science", "life": "Living Science", "math": "Mathematics, Physics, Astronomy & Geography",
                        "metr":"Medical Science", "nurs":"Nursing", "phar": "Pharmacy", "heal": "Therapeutics & Public Health",
                        "dsgn":"Design", "appl":"Applied Arts", "danc": "Dancing & Physical Education", "form": "FineArts & Formative Arts", "play": "Drama & Cinema", "musc": "Music"

                    };
                    if(middle_text[data.term]){
                        data.name = this.termName(data.facet, gettext(middle_text[data.term]));
                    }else{
                        data.name = this.termName(data.facet, data.term);
                    }
                }else if(data.facet == 'linguistics'){
                    if(data.term == 'Y'){
                        data.name = this.termName(data.facet, gettext("Koreanology"));
                    }else{
                        data.name = this.termName(data.facet, gettext("Others"));
                    }
                }
                else{
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
            var grouped = this.collection.groupBy('facet');

            var dict = {"org": [], "classfy": [], "middle_classfy": [], "linguistics": [],"course_period": [], "language": [], "modes": []};





            var htmlSnippet = HtmlUtils.joinHtml.apply(
                this, _.map(grouped, function(options, facetKey) {
                    if (options.length > 0) {
                        return this.renderFacet(facetKey, options);
                    }
                }, this)
            );

            HtmlUtils.setHtml(this.$container, htmlSnippet);
            return this;
        },
        collapse: function (event) {
            var $el = $(event.currentTarget),
                $more = $el.siblings('.show-more'),
                $ul = $el.parent().siblings('ul');

            $ul.addClass('collapse');
            $el.addClass('hidden');
            $more.removeClass('hidden');
        },

        expand: function (event) {
            var $el = $(event.currentTarget),
                $ul = $el.parent('div').siblings('ul');

            $el.addClass('hidden');
            $ul.removeClass('collapse');
            $el.siblings('.show-less').removeClass('hidden');
        },

        selectOption: function (event) {
            var $target = $(event.currentTarget);
            this.trigger(
                'selectOption',
                $target.data('facet'),
                $target.data('value'),
                $target.data('text')
            );
        }

    });

});

})(define || RequireJS.define);
