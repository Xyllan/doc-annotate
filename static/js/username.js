function submitUsername() {
	$.post($SCRIPT_ROOT + '/set_username', {
			username: $('input[name="username"]').val()
		}, function(data) {
			if(data.result=="refresh") window.location.reload();
			else alert(data.result);
		}, 'json');
}