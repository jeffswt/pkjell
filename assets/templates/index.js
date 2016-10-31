
// Bind scroll to bottom event to load function
$('.post-listing').scroll(function(event) {
    var scrolled_bottom = function(obj) {
        if (obj.scrollTop + obj.clientHeight >= obj.scrollHeight - 50)
            return true;
        return false;
    }
    if (scrolled_bottom(this))
        blog.contents.load();
    return ;
});

// Bind `load articles` button to function
$('#blog-contents-btn-load-more').click(blog.contents.load);

// Automatically initiate load procedure
blog.contents.load();
