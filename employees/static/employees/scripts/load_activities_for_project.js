$("#id_project").change(function () {
    var url = $("#reportForm").attr("data-task-activities-url");
    var projectId = $(this).val();
    $.ajax({
        url: url,
        data: {
            'project': projectId
        },
        success: function (data) {
            $("#id_task_activities").html(data);
        }
    });
});
