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
              $('#dialog_option_yes').dialog('open');
              $(this).dialog('close');
            }
          }
        ]
    }).prev().find(".ui-dialog-titlebar-close").hide ();

    $("#dialog_option_yes").dialog ({
        modal: true,
        autoOpen: false,
        buttons : [
          {
            text: "I surrender",
            click: function () {
              $(this).dialog('close');
            }
          },
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
              $('#dialog_info').dialog('open');
              $(this).dialog('close');
            }
          }
        ]
    }).prev().find(".ui-dialog-titlebar-close").hide ();

     $("#dialog_info").dialog ({
         modal: true,
         autoOpen: false,
         buttons : [
           {
             text: "OK",
             click: function () {
               $(this).dialog('close');
             }
           },
         ]
     }).prev().find(".ui-dialog-titlebar-close").hide ();

    $("#opener_user_account").click(function () {
        $('#dialog_user_account').dialog('open');
    });
});
