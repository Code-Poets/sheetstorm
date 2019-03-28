$(function () {
    $("#dialog").dialog ({
        modal: true,
        autoOpen: false,
        buttons : [
            {
                text: discard_text,
                click: function () {
                    $(this).dialog('close');
                }
            },
            {
                text: confirmation_text,
                click: function () {
                    window.location.href = redirect_url;
                }
            }
        ]
    }).prev().find(".ui-dialog-titlebar-close").hide ();

    $("#opener").click(function () {
        $('#dialog').dialog('open');
    });
});
