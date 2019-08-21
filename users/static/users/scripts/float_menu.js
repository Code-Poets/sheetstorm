$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('collapsed');
    });
});


$('#sidebarCollapse').on("click", function () {
    $('.toggle').toggleClass('fa-angle-double-right');
});
