
function blogClass() {
    function jsonClass(master) {
        this.loading = false;
        this.loaded = false;
        this.data = {};
        this.load = function(callback, args) {
            if (this.loaded) {
                callback(args);
                return ;
            }
            this.loading = true;
            json_event = $.getJSON('/data/index.json');
            wait_json = function(self, json_event, callback, args) {
                if (json_event.readyState <= 1) {
                    setTimeout(wait_json, 15, self, json_event, callback, args);
                    return ;
                }
                self.loading = false;
                self.loaded = true;
                self.data = json_event.responseJSON;
                if (callback)
                    callback(args);
                return ;
            };
            wait_json(this, json_event, callback, args);
            return ;
        };
        return this;
    };
    this.json = new jsonClass(this);
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
    this.contents = new contentsClass(this);
    function urlClass(master) {
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
    this.url = new urlClass(this);
    return this;
};
blog = new blogClass();
