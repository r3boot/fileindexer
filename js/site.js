var auth_token = false;

function set_authentication_token(token) {
	auth_token = token;
}

// Utility functions
function get_authentication_token() {
	var username = $('i_username').value;
	var password = $('i_password').value;
	var basic_auth = username + ":" + password;
	var basic_auth_token = btoa(basic_auth);

	var request = new Request.JSON({
		method: 'get',
		url: '/auth',
		headers: {'Authorization': 'Basic ' + basic_auth_token},
		data: {},
		onComplete: function(response) {
			if (response) {
				set_authentication_token(basic_auth_token);
				$('content').innerHTML = show_search_box();
			} else {
				set_authentication_token(false);
				$("content").innerHTML = 'Failed to authenticate';
			}
		},
	}).send();

}

function show_search_box() {
	var content = "<div id=\"search\">";
	content += "<input type=\"text\" id=\"q\" value=\"Enter a search query\" onclick=\"if(!this._haschanged){this.value=''};this._haschanged=true;\" />";
	content += "<button class=\"default\" id=\"b_q_submit\">go</button>";
	content += "<button class=\"default\" id=\"b_q_reset\">reset</button>";
	content += "</div>";
	return content;
}

function show_login_box() {
	var content = "<div id=\"login\">";
	content += "<input type=\"text\" id=\"i_username\" name=\"username\" value=\"Username\" onclick=\"if(!this._haschanged){this.value=''};this._haschanged=true;\" /><br />";
	content += "<input type=\"password\" id=\"i_password\" name=\"password\" /><br />";
	content += "<button class=\"default\" id=\"b_login_submit\">submit</button>";
	content += "<button class=\"default\" id=\"b_login_reset\">reset</button>";
	content += "</div>";
	return content;
}

function show_login_failure() {
	var content = "<div id=\"login_failed\">";
	content += "authentication failed";
	content += "</div>";
	return content;
}

// Event handling
window.addEvent('domready', function() {

	$('page').addEvent('domready', function(event) {
		$('content').innerHTML = show_search_box();
	});

	$('b_account').addEvent('click', function(event) {
		event.stop();
		$('content').innerHTML = show_login_box();
		$('i_password').addEvent('keydown', function(event) {
			if (event.key == 'enter') {
				event.stop();
				get_authentication_token();
			}
		});
		$('b_login_submit').addEvent('click', function(event) {
			event.stop();
			get_authentication_token();
		});
		$('b_login_reset').addEvent('click', function(event) {
			event.stop();
			$('i_username').value = 'Username';
			$('i_username')._haschanged = false;
			$('i_password').value = '';
		});
	});

	$('b_q_submit').addEvent('click', function(event) {
		event.stop();
		var request = new Request.JSON({
			method: 'get',
			url: '/files',
			data: {},
			onRequest: function() {
				$("content").innerHTML = "Sending request to API";
			},
			onComplete: function(response) {
				alert("response: "+response);
				$("content").innerHTML = "Request returned from API:" + response;
			}
		}).send();
	});

	$('b_q_reset').addEvent('click', function(event) {
		alert('reset');
	});

});
