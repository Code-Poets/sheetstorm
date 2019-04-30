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
              $("#form").submit();
            }
          }
        ]
    }).prev().find(".ui-dialog-titlebar-close").hide ();

    $("#opener").click(function () {
        $('#dialog').dialog('open');
    });
});
