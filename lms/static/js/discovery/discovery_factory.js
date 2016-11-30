;(function (define) {
    'use strict';

    define(['backbone', 'js/discovery/models/search_state', 'js/discovery/collections/filters',
        'js/discovery/views/search_form', 'js/discovery/views/courses_listing',
        'js/discovery/views/filter_bar', 'js/discovery/views/refine_sidebar'],
        function(Backbone, SearchState, Filters, SearchForm, CoursesListing, FilterBar, RefineSidebar) {

            return function (meanings, searchQuery) {

                var dispatcher = _.extend({}, Backbone.Events);
                var search = new SearchState();
                var filters = new Filters();
                var listing = new CoursesListing({ model: search.discovery });
                var form = new SearchForm();
                var filterBar = new FilterBar({ collection: filters });
                var refineSidebar = new RefineSidebar({
                    collection: search.discovery.facetOptions,
                    meanings: meanings
                });

                dispatcher.listenTo(form, 'search', function (query) {



                    var term = search.getTermParameter('term');
                    var mterm = search.getTermParameter('mterm');
                    var linguistics = search.getTermParameter('linguistics');
                    var language = search.getTermParameter('language');

                    filters.reset();
                    form.showLoadingIndicator();

                    if(term){
                        filters.add({type: 'classfy', query: term, name: term});
                        search.refineSearch(filters.getTerms());
                    }else if(mterm){
                        filters.add({type: 'middle_classfy', query: mterm, name: mterm});
                        search.refineSearch(filters.getTerms());
                    }else if(linguistics){
                        filters.add({type: 'linguistics', query: linguistics, name: 'Koreanology'});
                        search.refineSearch(filters.getTerms());
                    }else if(language) {
                        filters.add({type: 'language', query: language, name: language == 'ko' ? 'Korean' : 'English'});
                        search.refineSearch(filters.getTerms());
                    }else{
                        search.performSearch(query, filters.getTerms());
                    }
                });

                dispatcher.listenTo(refineSidebar, 'selectOption', function (type, query, name) {
                    form.showLoadingIndicator();
                    if (filters.get(type)) {
                        removeFilter(type);
                    }
                    else {
                        filters.add({type: type, query: query, name: name});
                        search.refineSearch(filters.getTerms());
                    }
                });

                dispatcher.listenTo(filterBar, 'clearFilter', removeFilter);

                dispatcher.listenTo(filterBar, 'clearAll', function () {
                    if(isRedirect(''))
                        return;
                    form.doSearch('');
                });

                dispatcher.listenTo(listing, 'next', function () {
                    search.loadNextPage()
                });

                dispatcher.listenTo(search, 'next', function () {
                    listing.renderNext();
                });

                dispatcher.listenTo(search, 'search', function (query, total) {
                    if (total > 0) {
                        form.showFoundMessage(total);
                        if (query) {
                            filters.add(
                                {type: 'search_query', query: query, name: quote(query)},
                                {merge: true}
                            );
                        }
                    }
                    else {
                        form.showNotFoundMessage(query);
                        filters.reset();
                    }
                    form.hideLoadingIndicator();
                    listing.render();
                    refineSidebar.render();
                });

                dispatcher.listenTo(search, 'error', function () {
                    form.showErrorMessage();
                    form.hideLoadingIndicator();
                });

                // kick off search on page refresh
                form.doSearch(searchQuery);

                function isRedirect(type){
                    var sPageURL = document.location.href,
                    checkIdx1 = sPageURL.indexOf('term'),
                    checkIdx2 = sPageURL.indexOf('mterm'),
                    checkIdx3 = sPageURL.indexOf('linguistics'),
                    checkIdx4 = sPageURL.indexOf('language')
                    ;

                    if(
                        (type == "" || type == "classfy" || type == "middle_classfy" || type == "linguistics" || type == "language") &&
                        (checkIdx1 > 0 || checkIdx2 > 0 || checkIdx3 > 0 || checkIdx4 > 0)
                    ){
                        document.location.href = '/courses';
                        return true;
                    }
                    return false;
                }


                function removeFilter(type) {
                    if(isRedirect(type))
                        return;

                    form.showLoadingIndicator();
                    filters.remove(type);
                    if (type === 'search_query') {
                        form.doSearch('');
                    }
                    else {
                        search.refineSearch(filters.getTerms());
                    }
                }

                function quote(string) {
                    return '"'+string+'"';
                }

            };

        });

})(define || RequireJS.define);
