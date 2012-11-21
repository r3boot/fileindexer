function do_authenticate(username, password) {
	var username =  document.getElementById('i_username').value;
	var password =  document.getElementById('i_username').value;
	var basic_auth = username + ":" + password;
	return basic_auth.toBase64();
}

window.addEvent('domready', function() {

	$('page').addEvent('domready', function(event) {
		var request = new Request.JSON({
			method: 'get',
			url: '/files',
			data: {},
			onRequest: function() {
				document.getElementById('content').innerHTML = 'Checking for API availability'
			},
			onComplete: function(response) {
				var content = "<table id='file_results'>";

				for (var i=0; i < response['files'].length; i++) {
					content += "<tr><td>"
					content += "<a href='/files/"+response['files'][i]+"' />";
					content += response['files'][i]
					content += "</a>";
					content += "</td></tr>";
				}
				content += "</table>";
				document.getElementById('content').innerHTML = content;
			},
			onFailure: function(response) {
				document.getElementById('content').innerHTML = 'API unavailable'
			}
		}).send();
	});

	$('b_account').addEvent('click', function(event) {
		event.stop();
		var content = "<input type=\"text\" id=\"i_username\" name=\"username\" value=\"Username\" onclick=\"if(!this._haschanged){this.value=''};this._haschanged=true;\" /><br />";
		content += "<input type=\"password\" id=\"i_password\" name=\"password\" /><br />";
		document.getElementById('content').innerHTML = content;
		$('i_password').addEvent('keydown', function(event) {
			if (event.key == 'enter') {
				event.stop();
				var basic_auth_token = do_authenticate(username, password);
			}
		});
		$('b_auth_submit').addEvent('click', function(event) {
			event.stop();
			var basic_auth_token = do_authenticate(username, password);
		});
		$('b_auth_reset').addEvent('click', function(event) {
			event.stop();
			document.getElementById('i_username').value = 'Username';
			document.getElementById('i_username')._haschanged = false;
			document.getElementById('i_password').value = '';
		});
	});

	$('b_submit').addEvent('click', function(event) {
		event.stop();
		var request = new Request.JSON({
			method: 'get',
			url: '/files',
			data: {},
			onRequest: function() {
				document.getElementById("content").innerHTML = "Sending request to API";
			},
			onComplete: function(response) {
				alert("response: "+response);
				document.getElementById("content").innerHTML = "Request returned from API:" + response;
			}
		}).send();
	});

	$('b_reset').addEvent('click', function(event) {
		alert('reset');
	});

});
