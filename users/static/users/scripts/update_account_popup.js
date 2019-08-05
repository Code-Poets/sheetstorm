$(function () {
    $("#dialog_user_account_update").dialog ({
        modal: true,
        autoOpen: false,
        buttons : [
          {
            id: "id_decline_update_button",
            text: "No",
            click: function () {
              $(this).dialog('close');
            }
          },
          {
            id: "id_confirm_update_button",
            text: "Yes",
            click: function () {
                $('form').submit()
            }
          }
        ]
    }).prev().find(".ui-dialog-titlebar-close").hide ();

    $("#opener_user_account_update").click(function () {
        $('#dialog_user_account_update').dialog('open');
    });
});
