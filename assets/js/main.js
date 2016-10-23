
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
    function contentsClass(master) {
        this.loading = false;
        this.current_page = 0;
        this.load = function() {
            // Setting thread lock status
            if (this.loading)
                return false;
            if (master.json.loaded && this.current_page >= master.json.data.entries.length) {
                var load_btn = $('#blog-contents-btn-load-more');
                load_btn.removeClass('btn-info').addClass('btn-success');
                load_btn.attr('disabled', 'disabled');
                load_btn.html('No more articles');
                return false;
            }
            this.loading = true;
            // Changing icon status
            var load_btn = $('#blog-contents-btn-load-more');
            load_btn.removeClass('btn-info').addClass('btn-warning');
            load_btn.html('Loading...');
            // Loading JSON
            master.json.load(function(event) {
            self = event[0];
            master = event[1];
            // Defining, getting sub-article
            function load_articles(rem_count, self, master) {
                // Recursion interrupt
                if (rem_count <= 0)
                    return ;
                // Retrieving object
                jdata = master.json.data;
                if (self.current_page >= jdata.entries.length)
                    return ;
                obj = jdata.entries[self.current_page];
                console.log(jdata.entries, self, self.current_page, obj);
                self.current_page++;
                // Getting data from server
                html_event = $.get('/data/' + obj['date-id'] + '-' + obj['id'] + '-brief.html');
                wait_html = function(self, master, html_event, load_articles) {
                    if (html_event.readyState <= 1) {
                        setTimeout(wait_html, 15, self, master, html_event, load_articles);
                        return ;
                    }
                    // Injecting data into HTML.
                    html_data = html_event.responseText;
                    console.log(html_data);
                    $('#blog-contents-end-flag').before(html_data);
                    load_articles(rem_count - 1, self, master);
                    return ;
                };
                wait_html(self, master, html_event, load_articles);
                // Calling iteration...
            }; load_articles(4, self, master);
            // Setting thread lock status
            self.loading = false;
            // Changing icon status
            var load_btn = $('#blog-contents-btn-load-more');
            load_btn.removeClass('btn-warning').addClass('btn-info');
            load_btn.html('Load more articles');
            }, [this, master])
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
