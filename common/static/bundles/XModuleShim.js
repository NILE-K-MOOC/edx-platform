(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([34,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74],{

/***/ "./common/lib/xmodule/xmodule/js/src/xmodule.js":
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function(_, $) {/*** IMPORTS FROM imports-loader ***/
(function () {

    (function () {
        'use strict';

        var XModule = {};

        XModule.Descriptor = function () {
            /*
             * Bind the module to an element. This may be called multiple times,
             * if the element content has changed and so the module needs to be rebound
             *
             * @method: constructor
             * @param {html element} the .xmodule_edit section containing all of the descriptor content
             */
            var Descriptor = function Descriptor(element) {
                this.element = element;
                this.update = _.bind(this.update, this);
            };

            /*
             * Register a callback method to be called when the state of this
             * descriptor is updated. The callback will be passed the results
             * of calling the save method on this descriptor.
             */
            Descriptor.prototype.onUpdate = function (callback) {
                if (!this.callbacks) {
                    this.callbacks = [];
                }

                this.callbacks.push(callback);
            };

            /*
             * Notify registered callbacks that the state of this descriptor has changed
             */
            Descriptor.prototype.update = function () {
                var data, callbacks, i, length;

                data = this.save();
                callbacks = this.callbacks;
                length = callbacks.length;

                $.each(callbacks, function (index, callback) {
                    callback(data);
                });
            };

            /*
             * Return the current state of the descriptor (to be written to the module store)
             *
             * @method: save
             * @returns {object} An object containing children and data attributes (both optional).
             *                   The contents of the attributes will be saved to the server
             */
            Descriptor.prototype.save = function () {
                return {};
            };

            return Descriptor;
        }();

        this.XBlockToXModuleShim = function (runtime, element, initArgs) {
            /*
             * Load a single module (either an edit module or a display module)
             * from the supplied element, which should have a data-type attribute
             * specifying the class to load
             */
            var moduleType, module;

            if (initArgs) {
                moduleType = initArgs['xmodule-type'];
            }
            if (!moduleType) {
                moduleType = $(element).data('type');
            }

            if (moduleType === 'None') {
                return;
            }

            try {
                module = new window[moduleType](element);

                if ($(element).hasClass('xmodule_edit')) {
                    $(document).trigger('XModule.loaded.edit', [element, module]);
                }

                if ($(element).hasClass('xmodule_display')) {
                    $(document).trigger('XModule.loaded.display', [element, module]);
                }

                return module;
            } catch (error) {
                console.error('Unable to load ' + moduleType + ': ' + error.message);
            }
        };

        // Export this module. We do it at the end when everything is ready
        // because some RequireJS scripts require this module. If
        // `window.XModule` appears as defined before this file has a chance
        // to execute fully, then there is a chance that RequireJS will execute
        // some script prematurely.
        this.XModule = XModule;
    }).call(this);
}).call(window);

/*** EXPORTS FROM exports-loader ***/
module.exports = window.XModule;
/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(1), __webpack_require__(0)))

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ }),

/***/ 1:
/***/ (function(module, exports) {

(function() { module.exports = window["_"]; }());

/***/ })

},["./common/lib/xmodule/xmodule/js/src/xmodule.js"])));
//# sourceMappingURL=XModuleShim.js.map