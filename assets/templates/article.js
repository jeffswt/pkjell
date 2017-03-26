
var params = blog.url.parse();
var get_path = '/data/' + params['date'] + '-' + params['id'] + '-post.html';

$.get(get_path).success(function(event) {
    $('#blog-article-share-buttons').before(event);
    var b_title = RegExp('<h1 title="(.*?)">').exec(event)[1];
    document.title = b_title + " - " + document.title;
    renderMathInElement(document.body);
    return ;
});

$('.twitter').attr('href', $('.twitter').attr('href') + window.location.href);
$('.facebook').attr('href', $('.facebook').attr('href') + window.location.href);
$('.google-plus').attr('href', $('.google-plus').attr('href') + window.location.href);
$('.reddit').attr('href', $('.reddit').attr('href') + window.location.href);
