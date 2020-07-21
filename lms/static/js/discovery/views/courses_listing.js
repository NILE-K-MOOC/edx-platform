(function(define) {
    define([
        'jquery',
        'underscore',
        'backbone',
        'gettext',
        'js/discovery/views/course_card'
    ], function($, _, Backbone, gettext, CourseCardView) {
        'use strict';
        let ribbon_list = []
        return Backbone.View.extend({

            el: 'div.courses',
            $window: $(window),
            $document: $(document),

            initialize: function () {
                this.$list = this.$el.find('.courses-listing');
                this.attachScrollHandler();
                $.ajax({
                    url: '/blue_ribbon_year',
                    type: "POST",
                    data: {
                        csrfmiddlewaretoken: $.cookie('csrftoken')
                    }
                }).done(function (data) {
                    ribbon_list = data
                    // console.log(ribbon_list)
                })
            },

            render: function() {
                this.$list.empty();
                this.renderItems();
                return this;
            },

            renderNext: function() {
                this.renderItems();
                this.isLoading = false;
            },

            renderItems: function () {
                /* eslint no-param-reassign: [2, { "props": true }] */
                var latest = this.model.latest();
                var items = latest.map(function (result) {

                    // if (result.attributes.id == 'course-v1:KMOOC+SNIS+939') {
                    //     result.attributes.ribbon_yn = 'Y';
                    //     result.attributes.ribbon_year = '2020';
                    // };
                    // console.log(ribbon_list)
                    if (result.attributes.id in ribbon_list){
                        // console.log('----------',result.attributes.id)
                        // console.log('==========',ribbon_list[result.attributes.id])
                        result.attributes.ribbon_year = ribbon_list[result.attributes.id]
                    }
                    // for(let key in ribbon_list){
                    //     console.log(key)
                    // };

                    // for(let i=0; i<ribbon_list.length; i++){
                    //     console.log('-------',ribbon_list[i])
                    //     if(result.attributes.id == ribbon_list.keys()){
                    //         result.attributes.ribbon_year = ribbon_list[i][result.attributes.id];
                    //     };
                    // };
                    // console.log('resultresultresult', result.attributes.ribbon_yn);
                    result.userPreferences = this.model.userPreferences;
                    var item = new CourseCardView({model: result});
                    // console.log('itemitem', item);
                    return item.render().el;
                }, this);
                this.$list.append(items);
                /* eslint no-param-reassign: [2, { "props": false }] */
            },

            attachScrollHandler: function() {
                this.$window.on('scroll', _.throttle(this.scrollHandler.bind(this), 400));
            },

            scrollHandler: function() {
                if (this.isNearBottom() && !this.isLoading) {
                    this.trigger('next');
                    this.isLoading = true;
                }
            },

            isNearBottom: function() {
                var scrollBottom = this.$window.scrollTop() + this.$window.height();
                var threshold = this.$document.height() - 200;
                return scrollBottom >= threshold;
            }

        });
    });
}(define || RequireJS.define));
