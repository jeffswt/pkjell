
blog.url.parse();

var load_tags = function() {
    // Calls ajax load procedure.
    blog.json.load(function(event) {
        var tag_idx = {};
        var jentries = blog.json.data.entries;
        var show_only = blog.url.args['tag'];
        for (var i = 0; i < jentries.length; i++) {
            var obj = jentries[i];
            // Uploading entry tags...
            var objtag = obj.tags;
            for (var j = 0; j < obj.tags.length; j++) {
                if (!tag_idx[objtag[j]])
                    tag_idx[objtag[j]] = [];
                tag_idx[objtag[j]] = tag_idx[objtag[j]].concat(obj);
            }
        }
        // Sort by alphabetical order
        var tag_lst = [];
        for (var tag in tag_idx)
            tag_lst = tag_lst.concat(tag);
        tag_lst.sort();
        // Received index, now pushing to document
        for (var j = 0; j < tag_lst.length; j++) {
            var tag = tag_lst[j];
            var lis = tag_idx[tag];
            if (show_only && show_only != tag)
                continue;
            $('#blog-tags-flag-end').before(
                '<div class="tag-group">\
                    <h5 class="tag-group-title" name="' + tag + '">' + tag + '</h5>\
                </div>');
            for (var i = 0; i < lis.length; i++) {
                var obj = lis[i];
                $('[name="' + tag + '"].tag-group-title').after('\
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

load_tags();
