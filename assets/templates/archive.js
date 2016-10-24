
var load_archive = function() {
    // Calls ajax load procedure.
    blog.json.load(function(event) {
        var tag_idx = {};
        var jentries = blog.json.data.entries;
        var last_date = ['0000', '00']; // Ensure no duplications
        for (var i = 0; i < jentries.length; i++) {
            var obj = jentries[i];
            // Create new title if needed
            var cur_date_all = obj.date.split('-');
            cur_date = [cur_date_all[0], cur_date_all[1]];
            if (last_date[0] != cur_date[0] || last_date[1] != cur_date[1]) {
                $('#blog-archive-flag-begin').after('\
                    <div class="archive-title">\
                        <h4 class="archive-year">' + blog.utils.month_to_string(cur_date[1]) + ', ' + cur_date[0] + '</h4>\
                    </div>\
                    <ul name="blog-archive-' + cur_date[0] + '-' + cur_date[1] + '">\
                    <div id="blog-archive-' + cur_date[0] + '-' + cur_date[1] + '-flag-begin"></div>\
                    </ul>');
                last_date = cur_date;
            }
            // Inserting this article into corresponding title
            $('#blog-archive-' + cur_date[0] + '-' + cur_date[1] + '-flag-begin').after('\
                <li><div style="width:60px;float:left;">' + cur_date_all[2] + ' ' + blog.utils.month_to_string(cur_date[1]) + '</div>\
                    <a href="/article/?date=' + obj['date-id'] + '&id=' + obj['id'] + '">' + obj['title'] + '</a>\
                </li>');
            continue;
        }
        // Finalizing operation...
        $('[name="blog-loading-identifier"]').html('');
        return ;
    }, []);
    return ;
}

load_archive();
