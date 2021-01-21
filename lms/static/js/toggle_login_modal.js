(function ($) {
    $.fn.extend({
        /*
         * leanModal prepares an element to be a modal dialog.  Call it once on the
         * element that launches the dialog, when the page is ready.  This function
         * will add a .click() handler that properly opens the dialog.
         *
         * The launching element must:
         *   - be an <a> element, not a button,
         *   - have an href= attribute identifying the id of the dialog element,
         *   - have rel='leanModal'.
         */

        course_preview: function (options) {

            var defaults = {
                top: 100,
                overlay: 0.5,
                closeButton: null,
                position: 'fixed'
            };

            if ($('#lean_overlay').length == 0) {
                var $overlay = $("<div id='lean_overlay'></div>");
                $('body').append($overlay);
            }
            options = $.extend(defaults, options);

            return this.each(function () {
                var o = options;

                $(this).click(function (e) {

                    var modal_id = $(this).attr('href');

                    $.ajax({
                        url: "/courses/video_check",
                        type: "POST",
                        data: {
                            video_url: $('video', modal_id).data('src')
                        },
                        success: function (data) {
                            if (data.is_error == 'true') {
                                alert('해당 강좌는 미리보기 영상을 제공하지 않습니다.');
                                return;
                            } else {
                                $('.modal, .js-modal').hide();

                                if ($(modal_id).hasClass('video-modal')) {
                                    // Video modals need to be cloned before being presented as a modal
                                    // This is because actions on the video get recorded in the history.
                                    // Deleting the video (clone) prevents the odd back button behavior.
                                    var modal_clone = $(modal_id).clone(true, true);
                                    modal_clone.attr('id', 'modal_clone');
                                    $(modal_id).after(modal_clone);
                                    modal_id = '#modal_clone';
                                }

                                $('#lean_overlay').click(function (e) {
                                    close_modal(modal_id, e);
                                });

                                $(o.closeButton).click(function (e) {
                                    close_modal(modal_id, e);
                                });

                                // To enable closing of email modal when copy button hit
                                $(o.copyEmailButton).click(function (e) {
                                    close_modal(modal_id, e);
                                });

                                var modal_height = $(modal_id).outerHeight();
                                var modal_width = $(modal_id).outerWidth();

                                $('#lean_overlay').css({display: 'block', opacity: 0});
                                $('#lean_overlay').fadeTo(200, o.overlay);

                                $('video', modal_id).attr('src', $('video', modal_id).data('src'));
                                if ($(modal_id).hasClass('email-modal')) {
                                    $(modal_id).css({
                                        width: 80 + '%',
                                        height: 80 + '%',
                                        position: o.position,
                                        opacity: 0,
                                        'z-index': 11000,
                                        left: 10 + '%',
                                        top: 10 + '%'
                                    });
                                } else {
                                    $(modal_id).css({
                                        position: o.position,
                                        opacity: 0,
                                        'z-index': 11000,
                                        left: 50 + '%',
                                        'margin-left': -(modal_width / 2) + 'px',
                                        top: o.top + 'px'
                                    });
                                }

                                $(modal_id).show().fadeTo(200, 1);
                                $(modal_id).find('.notice').hide().html('');
                                window.scrollTo(0, 0);
                                e.preventDefault();
                            }
                        }
                    })
                })
            });

            function close_modal(modal_id, e) {
                $('#lean_overlay').fadeOut(200);
                $('iframe', modal_id).attr('src', '');
                $(modal_id).css({display: 'none'});
                if (modal_id == '#modal_clone') {
                    $(modal_id).remove();
                }
                e.preventDefault();
            }
        }
        ,
        leanModal: function (options) {

            var defaults = {
                top: 100,
                overlay: 0.5,
                closeButton: null,
                position: 'fixed'
            };

            if ($('#lean_overlay').length == 0) {
                var $overlay = $("<div id='lean_overlay'></div>");
                $('body').append($overlay);
            }

            options = $.extend(defaults, options);

            return this.each(function () {
                var o = options;

                $(this).click(function (e) {

                    $('.modal, .js-modal').hide();

                    var modal_id = $(this).attr('href');

                    if ($(modal_id).hasClass('video-modal')) {
                        // Video modals need to be cloned before being presented as a modal
                        // This is because actions on the video get recorded in the history.
                        // Deleting the video (clone) prevents the odd back button behavior.
                        var modal_clone = $(modal_id).clone(true, true);
                        modal_clone.attr('id', 'modal_clone');
                        $(modal_id).after(modal_clone);
                        modal_id = '#modal_clone';
                    }

                    $('#lean_overlay').click(function (e) {
                        close_modal(modal_id, e);
                    });

                    $(o.closeButton).click(function (e) {
                        close_modal(modal_id, e);
                    });

                    // To enable closing of email modal when copy button hit
                    $(o.copyEmailButton).click(function (e) {
                        close_modal(modal_id, e);
                    });

                    var modal_height = $(modal_id).outerHeight();
                    var modal_width = $(modal_id).outerWidth();

                    $('#lean_overlay').css({display: 'block', opacity: 0});
                    $('#lean_overlay').fadeTo(200, o.overlay);

                    $('iframe', modal_id).attr('src', $('iframe', modal_id).data('src'));
                    if ($(modal_id).hasClass('email-modal')) {
                        $(modal_id).css({
                            width: 80 + '%',
                            height: 80 + '%',
                            position: o.position,
                            opacity: 0,
                            'z-index': 11000,
                            left: 10 + '%',
                            top: 10 + '%'
                        });
                    } else {
                        $(modal_id).css({
                            position: o.position,
                            opacity: 0,
                            'z-index': 11000,
                            left: 50 + '%',
                            'margin-left': -(modal_width / 2) + 'px',
                            top: o.top + 'px'
                        });
                    }

                    $(modal_id).show().fadeTo(200, 1);
                    $(modal_id).find('.notice').hide().html('');

                    window.scrollTo(0, 0);
                    e.preventDefault();
                });
            });

            function close_modal(modal_id, e) {
                $('#lean_overlay').fadeOut(200);
                $('iframe', modal_id).attr('src', '');
                $(modal_id).css({display: 'none'});
                if (modal_id == '#modal_clone') {
                    $(modal_id).remove();
                }
                e.preventDefault();
            }
        }
    });

    $(document).ready(function ($) {

        $('.preview_video_id').on('timeupdate', function (event) {

            if ($(this)[0].currentTime == '0') {
                $(this)[0].play();
            }

            let honor_check = $(".register")[0]
            let title = ''

            if ($(this)[0].duration > 300) {
                if ($(this)[0].currentTime > '300') {
                    $(this)[0].pause();
                    $("#modal_clone").hide()
                    $('#lean_overlay').fadeOut(200);

                    if(honor_check){
                        title += "강좌를 등록하시겠습니까?"
                    }else{
                        title += "강좌를 청강하시겠습니까?"
                    }

                    swal({
                        title: title,
                        icon: "info",
                        buttons: true,
                        dangerMode: false,
                    }).then(function (value) {
                        if(value) {
                            if (honor_check) {
                                $(".register").click();
                            } else if (value) {
                                $("#audit_mode").click();
                            }
                        }
                    })
                }
            } else {
                $('.preview_video_id').on('ended', function () {
                    $("#modal_clone").hide()
                    $('#lean_overlay').fadeOut(200);

                    if(honor_check){
                        title += "강좌를 등록하시겠습니까?"
                    }else{
                        title += "강좌를 청강하시겠습니까?"
                    }

                    swal({
                        title: title,
                        icon: "info",
                        buttons: true,
                        dangerMode: false,
                    }).then(function (value) {
                        if(value) {
                            if (honor_check) {
                                $(".register").click();
                            } else if (value) {
                                $("#audit_mode").click();
                            }
                        }
                    })
                })
            }
        });

        $('a[rel*=course_preview]').each(function () {

            var $link = $(this),
                closeButton = $link.data('modalCloseButtonSelector') || '.close-modal',
                embed;

            embed = $($link.attr('href')).find('video');

            $link.course_preview({top: 120, overlay: 1, closeButton: closeButton, position: 'absolute'});

            if (embed.length > 0 && embed.attr('src')) {
                var sep = (embed.attr('src').indexOf('?') > 0) ? '&' : '?';
                embed.data('src', embed.attr('src') + sep);
                embed.attr('src', '');
            }
        });

        $('a[rel*=leanModal]').each(function () {
            var $link = $(this),
                closeButton = $link.data('modalCloseButtonSelector') || '.close-modal',
                embed;

            $link.leanModal({top: 120, overlay: 1, closeButton: closeButton, position: 'absolute'});
            embed = $($link.attr('href')).find('iframe');

            if (embed.length > 0 && embed.attr('src')) {
                var sep = (embed.attr('src').indexOf('?') > 0) ? '&' : '?';
                embed.data('src', embed.attr('src') + sep);
                embed.attr('src', '');
            }
        });
    });
}(jQuery));
