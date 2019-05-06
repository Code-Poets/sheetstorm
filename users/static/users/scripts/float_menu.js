$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
});

$('#sidebarCollapse').on("click", function () {
    $('.toggle').toggleClass('glyphicon-chevron-right');
});
