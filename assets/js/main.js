
var blog = {
    url : {
        args : {},
        parse : function() {
            var uri = window.location.href;
            var dict = {};
            if (uri.lastIndexOf('?') > 0) {
                var params_list = uri.substring(uri.lastIndexOf("?") + 1, uri.length);
                var params = params_list.split('&');
                for (i = 0; i < params.length; i++) {
                    var tuple = params[i].split('=');
                    dict[tuple[0]] = tuple[1];
                }
            }
            blog.url.args = dict;
            return dict;
        }
    },
    json : {
        loading : false,
        loaded : false,
        data : {},
        load : function(callback, args) {
            if (blog.json.loaded) {
                callback(args);
                return ;
            }
            blog.json.loading = true;
            var json_event = $.getJSON('/data/index.json');
            var wait_json = function(json_event, callback, args) {
                if (json_event.readyState <= 1) {
                    setTimeout(wait_json, 15, json_event, callback, args);
                    return ;
                }
                blog.json.loading = false;
                blog.json.loaded = true;
                blog.json.data = json_event.responseJSON;
                if (callback)
                    callback(args);
                return ;
            };
            wait_json(json_event, callback, args);
            return ;
        }
    },
    contents : {
        loading : false,
        current_page : 0,
        load : function() {
            // Setting thread lock status
            if (blog.contents.loading)
                return false;
            if (blog.json.loaded && blog.contents.current_page >= blog.json.data.entries.length) {
                var load_btn = $('#blog-contents-btn-load-more');
                load_btn.removeClass('btn-info').addClass('btn-success');
                load_btn.attr('disabled', 'disabled');
                load_btn.html('No more articles');
                return false;
            }
            blog.contents.loading = true;
            // Changing icon status
            var load_btn = $('#blog-contents-btn-load-more');
            load_btn.removeClass('btn-info').addClass('btn-warning');
            load_btn.html('Loading...');
            // Loading JSON
            blog.json.load(function(event) {
            // Defining, getting sub-article
            function load_articles(rem_count) {
                // Recursion interrupt
                if (rem_count <= 0)
                    return ;
                // Retrieving object
                var jdata = blog.json.data;
                if (blog.contents.current_page >= jdata.entries.length)
                    return ;
                var obj = jdata.entries[blog.contents.current_page];
                blog.contents.current_page++;
                // Getting data from server
                var html_event = $.get('/data/' + obj['date-id'] + '-' + obj['id'] + '-brief.html');
                var wait_html = function(html_event, load_articles) {
                    if (html_event.readyState <= 1) {
                        setTimeout(wait_html, 15, html_event, load_articles);
                        return ;
                    }
                    // Injecting data into HTML.
                    var html_data = html_event.responseText;
                    $('#blog-contents-end-flag').before(html_data);
                    load_articles(rem_count - 1);
                    return ;
                };
                wait_html(html_event, load_articles);
                // Calling iteration...
            }; load_articles(4);
            // Setting thread lock status
            blog.contents.loading = false;
            // Changing icon status
            var load_btn = $('#blog-contents-btn-load-more');
            load_btn.removeClass('btn-warning').addClass('btn-info');
            load_btn.html('Load more articles');
            }, [])
            // Finished procedure
            return true;
        }
    }
};
