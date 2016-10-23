
function blogClass() {
    function contentsClass() {
        this.loading = false;
        this.load = function() {
            // Setting thread lock status
            if (this.loading)
                return false;
            this.loading = true;
            // Changing icon status
            var load_btn = $('#blog-contents-btn-load-more');
            load_btn.removeClass('btn-info').addClass('btn-warning');
            load_btn.html('Loading...');
            // Load data...
            this.loading = false;
            // Changing icon status
            var load_btn = $('#blog-contents-btn-load-more');
            load_btn.removeClass('btn-warning').addClass('btn-info');
            load_btn.html('Load more articles');
            // Finished procedure
            return true;
        };
        return this;
    };
    this.contents = new contentsClass();
    function urlClass() {
        this.args = {};
        this.parse = function() {
            uri = window.location.href;
            dict = {};
            if (uri.lastIndexOf('?') > 0) {
                params_list = uri.substring(uri.lastIndexOf("?") + 1, uri.length);
                params = params_list.split('&');
                for (i = 0; i < params.length; i++) {
                    tuple = params[i].split('=');
                    dict[tuple[0]] = tuple[1];
                }
            }
            this.args = dict;
            return dict;
        };
        return this;
    };
    this.url = new urlClass();
    return this;
};
blog = new blogClass();
