$(function () {
    $("#dialog_own_account").dialog ({
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
              window.location.href = "{% url 'custom-account-delete' pk=user.pk %}";
            }
          }
        ]
    }).prev().find(".ui-dialog-titlebar-close").hide ();
    
    $("#opener_own_account").click(function () {
        $('#dialog_own_account').dialog('open');
    });


    $("#dialog_user_account").dialog ({
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
              window.location.href = "{% url 'custom-user-delete' pk=user_detail.pk %}";              }
          }
        ]
    }).prev().find(".ui-dialog-titlebar-close").hide ();

    $("#opener_user_account").click(function () {
        $('#dialog_user_account').dialog('open');
    });
});
