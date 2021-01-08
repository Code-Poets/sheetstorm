$(function () {
  $("#dialog_join").dialog ({
      modal: true,
      autoOpen: false,
	})

	$("#opener_join").click(function () {
	    $("#dialog_join").dialog('open');
	});

  $("#dialog_create").dialog ({
      modal: false,
      autoOpen: false,
      resizable: false,
      width: 550,
      height: 1300,
      close: function(event, ui){ $('#opener_create').attr('disabled', false); },
	})

	$("#opener_create").click(function () {
	    $("#dialog_create").dialog('open');
	    $("#opener_create").attr("disabled", true);
	});

  if (form_errors){
    $("#dialog_create").dialog('open');
    $("#opener_create").attr("disabled", true);
  }
});
