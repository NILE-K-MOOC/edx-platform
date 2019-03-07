(function(e, a) { for(var i in a) e[i] = a[i]; }(window, webpackJsonp([26,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74],{

/***/ "./common/static/xmodule/descriptors/js/001-d7842ab69993e5eb58e8d4a4e80c23a2.js":
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function($) {/*** IMPORTS FROM imports-loader ***/
(function () {

  // Once generated by CoffeeScript 1.9.3, but now lives as pure JS
  /* eslint-disable */
  (function () {
    var bind = function bind(fn, me) {
      return function () {
        return fn.apply(me, arguments);
      };
    };

    this.TabsEditingDescriptor = function () {
      TabsEditingDescriptor.isInactiveClass = "is-inactive";

      function TabsEditingDescriptor(element) {
        this.onSwitchEditor = bind(this.onSwitchEditor, this);
        var currentTab;
        this.element = element;

        /*
        Not tested on syncing of multiple editors of same type in tabs
        (Like many CodeMirrors).
         */
        this.$tabs = $(".tab", this.element);
        this.$content = $(".component-tab", this.element);
        this.element.find('.editor-tabs .tab').each(function (_this) {
          return function (index, value) {
            return $(value).on('click', _this.onSwitchEditor);
          };
        }(this));

        /*
        If default visible tab is not setted or if were marked as current
        more than 1 tab just first tab will be shown
         */
        currentTab = this.$tabs.filter('.current');
        if (currentTab.length !== 1) {
          currentTab = this.$tabs.first();
        }
        this.html_id = this.$tabs.closest('.wrapper-comp-editor').data('html_id');
        currentTab.trigger("click", [true, this.html_id]);
      }

      TabsEditingDescriptor.prototype.onSwitchEditor = function (e, firstTime, html_id) {
        var $currentTarget, content_id, isInactiveClass, onSwitchFunction, previousTab;
        e.preventDefault();
        isInactiveClass = TabsEditingDescriptor.isInactiveClass;
        $currentTarget = $(e.currentTarget);
        if (!$currentTarget.hasClass('current') || firstTime === true) {
          previousTab = null;
          this.$tabs.each(function (index, value) {
            if ($(value).hasClass('current')) {
              return previousTab = $(value).data('tab_name');
            }
          });

          /*
          init and save data from previous tab
           */
          TabsEditingDescriptor.Model.updateValue(this.html_id, previousTab);

          /*
          Save data from editor in previous tab to editor in current tab here.
          (to be implemented when there is a use case for this functionality)
           */

          // call onswitch
          onSwitchFunction = TabsEditingDescriptor.Model.modules[this.html_id].tabSwitch[$currentTarget.data('tab_name')];
          if ($.isFunction(onSwitchFunction)) {
            onSwitchFunction();
          }
          this.$tabs.removeClass('current');
          $currentTarget.addClass('current');

          /*
          Tabs are implemeted like anchors. Therefore we can use hash to find
          corresponding content
           */
          content_id = $currentTarget.attr('href');
          return this.$content.addClass(isInactiveClass).filter(content_id).removeClass(isInactiveClass);
        }
      };

      TabsEditingDescriptor.prototype.save = function () {
        var current_tab;
        this.element.off('click', '.editor-tabs .tab', this.onSwitchEditor);
        current_tab = this.$tabs.filter('.current').data('tab_name');
        return {
          data: TabsEditingDescriptor.Model.getValue(this.html_id, current_tab)
        };
      };

      TabsEditingDescriptor.prototype.setMetadataEditor = function (metadataEditor) {
        return TabsEditingDescriptor.setMetadataEditor.apply(TabsEditingDescriptor, arguments);
      };

      TabsEditingDescriptor.prototype.getStorage = function () {
        return TabsEditingDescriptor.getStorage();
      };

      TabsEditingDescriptor.prototype.addToStorage = function (id, data) {
        return TabsEditingDescriptor.addToStorage.apply(TabsEditingDescriptor, arguments);
      };

      TabsEditingDescriptor.Model = {
        addModelUpdate: function addModelUpdate(id, tabName, modelUpdateFunction) {

          /*
          Function that registers  'modelUpdate' functions of every tab.
          These functions are used to update value, which will be returned
          by calling save on component.
           */
          this.initialize(id);
          return this.modules[id].modelUpdate[tabName] = modelUpdateFunction;
        },
        addOnSwitch: function addOnSwitch(id, tabName, onSwitchFunction) {

          /*
          Function that registers functions invoked when switching
          to particular tab.
           */
          this.initialize(id);
          return this.modules[id].tabSwitch[tabName] = onSwitchFunction;
        },
        updateValue: function updateValue(id, tabName) {

          /*
          Function that invokes when switching tabs.
          It ensures that data from previous tab is stored.
          If new tab need this data, it should retrieve it from
          stored value.
           */
          var modelUpdateFunction;
          this.initialize(id);
          modelUpdateFunction = this.modules[id]['modelUpdate'][tabName];
          if ($.isFunction(modelUpdateFunction)) {
            return this.modules[id]['value'] = modelUpdateFunction();
          }
        },
        getValue: function getValue(id, tabName) {

          /*
          Retrieves stored data on component save.
          1. When we switching tabs - previous tab data is always saved to @[id].value
          2. If current tab have registered 'modelUpdate' method, it should be invoked 1st.
          (If we have edited in 1st tab, then switched to 2nd, 2nd tab should
          care about getting data from @[id].value in onSwitch.)
           */
          if (!this.modules[id]) {
            return null;
          }
          if ($.isFunction(this.modules[id]['modelUpdate'][tabName])) {
            return this.modules[id]['modelUpdate'][tabName]();
          } else {
            if (typeof this.modules[id]['value'] === 'undefined') {
              return null;
            } else {
              return this.modules[id]['value'];
            }
          }
        },

        /*
        html_id's of descriptors will be stored in modules variable as
        containers for callbacks.
         */
        modules: {},
        Storage: {},
        initialize: function initialize(id) {

          /*
          Initialize objects per id. Id is html_id of descriptor.
           */
          this.modules[id] = this.modules[id] || {};
          this.modules[id].tabSwitch = this.modules[id]['tabSwitch'] || {};
          return this.modules[id].modelUpdate = this.modules[id]['modelUpdate'] || {};
        }
      };

      TabsEditingDescriptor.setMetadataEditor = function (metadataEditor) {
        return TabsEditingDescriptor.Model.Storage['MetadataEditor'] = metadataEditor;
      };

      TabsEditingDescriptor.addToStorage = function (id, data) {
        return TabsEditingDescriptor.Model.Storage[id] = data;
      };

      TabsEditingDescriptor.getStorage = function () {
        return TabsEditingDescriptor.Model.Storage;
      };

      return TabsEditingDescriptor;
    }();
  }).call(this);
}).call(window);
/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(0)))

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

(function() { module.exports = window["jQuery"]; }());

/***/ }),

/***/ 1:
/***/ (function(module, exports) {

(function() { module.exports = window["_"]; }());

/***/ }),

/***/ 9:
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__("./common/static/xmodule/descriptors/js/000-58032517f54c5c1a704a908d850cbe64.js");
module.exports = __webpack_require__("./common/static/xmodule/descriptors/js/001-d7842ab69993e5eb58e8d4a4e80c23a2.js");


/***/ })

},[9])));
//# sourceMappingURL=VideoDescriptor.js.map