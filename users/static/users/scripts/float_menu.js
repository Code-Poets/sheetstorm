$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
});

$('.btn').on("click", function () {
    $('.glyphicon').toggleClass('glyphicon-chevron-left glyphicon-chevron-right');
});
