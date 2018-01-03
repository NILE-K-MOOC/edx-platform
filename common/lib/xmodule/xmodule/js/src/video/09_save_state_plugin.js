(function(define) {
<<<<<<< HEAD
        'use strict';
        define('video/09_save_state_plugin.js', [], function() {
                /**
                * Save state module.
                * @exports video/09_save_state_plugin.js
                * @constructor
                * @param {Object} state The object containing the state of the video
                * @param {Object} i18n The object containing strings with translations.
                * @param {Object} options
                * @return {jquery Promise}
                */
                var SaveStatePlugin = function(state, i18n, options) {
                        if (!(this instanceof SaveStatePlugin)) {
                                return new SaveStatePlugin(state, i18n, options);
                        }

                        _.bindAll(this, 'onSpeedChange', 'saveStateHandler', 'bindUnloadHandler', 'onUnload', 'onYoutubeAvailability',
                        'onLanguageChange', 'destroy');
                        this.state = state;
                        this.options = _.extend({events: []}, options);
                        this.state.videoSaveStatePlugin = this;
                        this.i18n = i18n;
                        this.initialize();

                        return $.Deferred().resolve().promise();
                };


                SaveStatePlugin.moduleName = 'SaveStatePlugin';
                SaveStatePlugin.prototype = {
                        destroy: function() {
                                this.state.el.off(this.events).off('destroy', this.destroy);
                                $(window).off('unload', this.onUnload);
                                delete this.state.videoSaveStatePlugin;
                        },

                        initialize: function() {
                                this.events = {
                                        'speedchange': this.onSpeedChange,
                                        'play': this.bindUnloadHandler,
                                        'pause destroy': this.saveStateHandler,
                                        'language_menu:change': this.onLanguageChange,
                                        'youtube_availability': this.onYoutubeAvailability
                                };
                                this.bindHandlers();
                        },

                        bindHandlers: function() {
                                if (this.options.events.length) {
                                        _.each(this.options.events, function(eventName) {
                                                var callback;
                                                if (_.has(this.events, eventName)) {
                                                        callback = this.events[eventName];
                                                        this.state.el.on(eventName, callback);
                                                }
                                        }, this);
                                } else {
                                        this.state.el.on(this.events);
                                }
                                this.state.el.on('destroy', this.destroy);
                        },

                        bindUnloadHandler: _.once(function() {
                                $(window).on('unload.video', this.onUnload);
                        }),

                        onSpeedChange: function(event, newSpeed) {
                                this.saveState(true, {speed: newSpeed});
                                this.state.storage.setItem('speed', newSpeed, true);
                                this.state.storage.setItem('general_speed', newSpeed);
                        },

                        saveStateHandler: function() {
                                this.saveState(true);
                        },

                        onUnload: function() {
                                this.saveState();
                        },

                        onLanguageChange: function(event, langCode) {
                                this.state.storage.setItem('language', langCode);
                        },

                        onYoutubeAvailability: function(event, youtubeIsAvailable) {
                                // Compare what the client-side code has determined Youtube
                                // availability to be (true/false) vs. what the LMS recorded for
                                // this user. The LMS will assume YouTube is available by default.
                                if (youtubeIsAvailable !== this.state.config.recordedYoutubeIsAvailable) {
                                        this.saveState(true, {youtube_is_available: youtubeIsAvailable});
                                }
                        },







                        saveState: function(async, data) {
                                if (!($.isPlainObject(data))) {
                                        data = {
                                                saved_video_position: this.state.videoPlayer.currentTime
                                        };
                                }

                                if (data.speed) {
                                        this.state.storage.setItem('speed', data.speed, true);
                                }

                                if (_.has(data, 'saved_video_position')) {
                                        this.state.storage.setItem('savedVideoPosition', data.saved_video_position, true);
                                        data.saved_video_position = Time.formatFull(data.saved_video_position);

                                        // chali5124@gmail.com
                                        // 2016.11.30 비디오 컨텐츠 이벤트에 대한 이용자정보 수집부분 추가
                                        var cookie = JSON.parse($.cookie('edx-user-info').replace(/\\054/g, ",").replace(/\\"/g, "'").replace(/\"/g, "").replace(/\'/g, "\""));
                                        // var url = this.state.config.element.baseURI;
                                        var url = document.location.href;
                                        var re = /^((https?):\/\/(.*))\/courses\/(.*)\/courseware\/(.*)\/(.*)\/(.*)$/i;
                                        var match = url.match(re);
                                        var nedx_data = {
                                                "course_id":(typeof match[4] !== 'undefined' ? match[4] : ''),
                                                "course_key":(typeof match[5] !== 'undefined' ? match[5] : ''),
                                                "total_duration":this.state.videoPlayer.duration(),
                                                "duration":this.state.videoPlayer.currentTime,
                                                "section":(typeof match[6] !== 'undefined' ? match[6] : ''),
                                                "units":this.state.id,
                                                "user_id":cookie.email,
                                                "cookie":document.cookie,
                                                "mov_url": this.state.config.sources,
                                                "baseUrl" : this.state.config.element.baseURI
                                        };
                                        // console.log("NEDX---------------", nedx_data);
                                        $.ajax({
                                                url: "http://mme.kmooc.kr/mov_handle",
                                                type: 'GET',
                                                // async: true,
                                                dataType: 'jsonp',
                                                data: nedx_data
                                        });
                                }

                                $.ajax({
                                        url: this.state.config.saveStateUrl,
                                        type: 'POST',
                                        async: async ? true : false,
                                        dataType: 'json',
                                        data: data
                                });
                        }
                };

                return SaveStatePlugin;
        });
=======
    'use strict';
    define('video/09_save_state_plugin.js', [], function() {
    /**
     * Save state module.
     * @exports video/09_save_state_plugin.js
     * @constructor
     * @param {Object} state The object containing the state of the video
     * @param {Object} i18n The object containing strings with translations.
     * @param {Object} options
     * @return {jquery Promise}
     */
        var SaveStatePlugin = function(state, i18n, options) {
            if (!(this instanceof SaveStatePlugin)) {
                return new SaveStatePlugin(state, i18n, options);
            }

            _.bindAll(this, 'onSpeedChange', 'saveStateHandler', 'bindUnloadHandler', 'onUnload', 'onYoutubeAvailability',
            'onLanguageChange', 'destroy');
            this.state = state;
            this.options = _.extend({events: []}, options);
            this.state.videoSaveStatePlugin = this;
            this.i18n = i18n;
            this.initialize();

            return $.Deferred().resolve().promise();
        };


        SaveStatePlugin.moduleName = 'SaveStatePlugin';
        SaveStatePlugin.prototype = {
            destroy: function() {
                this.state.el.off(this.events).off('destroy', this.destroy);
                $(window).off('unload', this.onUnload);
                delete this.state.videoSaveStatePlugin;
            },

            initialize: function() {
                this.events = {
                    'speedchange': this.onSpeedChange,
                    'play': this.bindUnloadHandler,
                    'pause destroy': this.saveStateHandler,
                    'language_menu:change': this.onLanguageChange,
                    'youtube_availability': this.onYoutubeAvailability
                };
                this.bindHandlers();
            },

            bindHandlers: function() {
                if (this.options.events.length) {
                    _.each(this.options.events, function(eventName) {
                        var callback;
                        if (_.has(this.events, eventName)) {
                            callback = this.events[eventName];
                            this.state.el.on(eventName, callback);
                        }
                    }, this);
                } else {
                    this.state.el.on(this.events);
                }
                this.state.el.on('destroy', this.destroy);
            },

            bindUnloadHandler: _.once(function() {
                $(window).on('unload.video', this.onUnload);
            }),

            onSpeedChange: function(event, newSpeed) {
                this.saveState(true, {speed: newSpeed});
                this.state.storage.setItem('speed', newSpeed, true);
                this.state.storage.setItem('general_speed', newSpeed);
            },

            saveStateHandler: function() {
                this.saveState(true);
            },

            onUnload: function() {
                this.saveState();
            },

            onLanguageChange: function(event, langCode) {
                this.state.storage.setItem('language', langCode);
            },

            onYoutubeAvailability: function(event, youtubeIsAvailable) {
            // Compare what the client-side code has determined Youtube
            // availability to be (true/false) vs. what the LMS recorded for
            // this user. The LMS will assume YouTube is available by default.
                if (youtubeIsAvailable !== this.state.config.recordedYoutubeIsAvailable) {
                    this.saveState(true, {youtube_is_available: youtubeIsAvailable});
                }
            },

            saveState: function(async, data) {
                if (!($.isPlainObject(data))) {
                    data = {
                        saved_video_position: this.state.videoPlayer.currentTime
                    };
                }

                if (data.speed) {
                    this.state.storage.setItem('speed', data.speed, true);
                }

                if (_.has(data, 'saved_video_position')) {
                    this.state.storage.setItem('savedVideoPosition', data.saved_video_position, true);
                    data.saved_video_position = Time.formatFull(data.saved_video_position);
                }

                $.ajax({
                    url: this.state.config.saveStateUrl,
                    type: 'POST',
                    async: async ? true : false,
                    dataType: 'json',
                    data: data
                });
            }
        };

        return SaveStatePlugin;
    });
>>>>>>> origin
}(RequireJS.define));
