
blog.url.parse();

var load_categories = function() {
    // Calls ajax load procedure.
    blog.json.load(function(event) {
        var cat_idx = {};
        var jentries = blog.json.data.entries;
        var show_only = blog.url.args['category'];
        for (var i = 0; i < jentries.length; i++) {
            var obj = jentries[i];
            // Uploading entry categories.
            var objcat = obj.categories;
            for (var j = 0; j < obj.categories.length; j++) {
                if (!cat_idx[objcat[j]])
                    cat_idx[objcat[j]] = [];
                cat_idx[objcat[j]] = cat_idx[objcat[j]].concat(obj);
            }
        }
        // Sort by alphabetical order
        var cat_lst = [];
        for (var cat in cat_idx)
            cat_lst = cat_lst.concat(cat);
        cat_lst.sort();
        // Received index, now pushing to document
        for (var j = 0; j < cat_lst.length; j++) {
            var cat = cat_lst[j];
            var lis = cat_idx[cat];
            if (show_only && show_only != cat)
                continue;
            $('#blog-categories-flag-end').before(
                '<div class="tag-group">\
                    <h5 class="tag-group-title" name="' + cat + '">' + cat + '</h5>\
                </div>');
            for (var i = 0; i < lis.length; i++) {
                var obj = lis[i];
                $('[name="' + cat + '"].tag-group-title').after('\
                    <article class="tag-item">\
                        <a class="tag-item-title" href="/article/?date=' + obj['date-id'] + '&id=' + obj['id'] + '">' + obj['title'] + '</a>\
                    </article>');
                continue;
            }
            continue;
        };
        // Finishing ajax procedure.
        $('[name="blog-loading-identifier"]').html('');
        return ;
    }, []);
    return ;
}

load_categories();
