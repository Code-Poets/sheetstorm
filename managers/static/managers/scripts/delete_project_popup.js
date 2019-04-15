$(function () {
    $("#dialog").dialog ({
        modal: true,
        autoOpen: false,
        buttons : [
          {
            text: "No",
            click: function () {
              $(this).dialog('close');
            }
          },
          {
            text: "Yes",
            click: function () {
              window.location.href = delete_project_path;
            }
          }
        ]
    }).prev().find(".ui-dialog-titlebar-close").hide ();

    $("#opener").click(function () {
        $('#dialog').dialog('open');
    });
});
