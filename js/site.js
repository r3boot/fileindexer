set_authentication_token(false);
set_username(false);
set_realname(false);

function set_username(username) {
	sessionStorage.setItem('username', username);
}

function get_username() {
	return sessionStorage.getItem('username');
}

function set_realname(realname) {
	sessionStorage.setItem('realname', realname);
}

function get_realname() {
	return sessionStorage.getItem('realname');
}

function set_authentication_token(token) {
	sessionStorage.setItem('auth_token', token);
}

function get_authentication_token() {
	return sessionStorage.getItem('auth_token');
}

// Utility functions
function validate_authentication_token() {
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
				set_username(username);
				toggle_auth_button_box();
				$('content').innerHTML = show_search_box();
			} else {
				set_authentication_token(false);
				set_username(false);
				$("content").innerHTML = 'Failed to authenticate';
			}
		},
	}).send();

}

function get_profile() {
	username = get_username();
	if (username == 'false') {
		return false;
	}

	var request = new Request.JSON({
		method: 'get',
		url: '/users/'+username,
		headers: {'Authorization': 'Basic ' + get_authentication_token()},
		data: {},
		onComplete: function(response) {
			set_realname(response['user']['realname']);
			$('i_realname').value = get_realname();
		},
		onFailure: function(response) {
			$('content').innerHTML('unable to retrieve profile');
		}
	}).send();
}

function toggle_auth_button_box() {
	if (sessionStorage.getItem('auth_token') != 'false') {
		$('b_profile').style.display = 'block';
		$('b_auth').innerHTML = 'Sign out';
	} else {
		$('b_profile').style.display = 'none';
		$('b_auth').innerHTML = 'Sign in';
	}
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

function show_profile_box() {
	var content = "<table id=\"t_profile\">";
	content += "<tr>";
	content += "<td>Real Name:</td>";
	content += "<td><input type=\"text\" id=\"i_realname\" name=\"realname\" /></td>";
	content += "</tr><tr>";
	content += "<td>New Password:</td>";
	content += "<td><input type=\"text\" id=\"i_newpass1\" name=\"newpass1\" /></td>";
	content += "</tr><tr>";
	content += "<td>New Password (again):</td>";
	content += "<td><input type=\"text\" id=\"i_newpass2\" name=\"newpass2\" /></td>";
	content += "</tr>";
	content += "</table>"
	content += "<p/><button type=\"button\" id=\"b_update_profile\">Update</button>";
	return content;
}

// Event handling
window.addEvent('domready', function() {

	toggle_auth_button_box();

	$('page').addEvent('domready', function(event) {
		$('content').innerHTML = show_search_box();
	});

	$('b_auth').addEvent('click', function(event) {
		event.stop();
		if (sessionStorage.getItem('auth_token') != 'false') {
			// logout
			set_authentication_token(false);
			set_username(false);
			toggle_auth_button_box();
			$('content').innerHTML = show_search_box();
		} else {
			// login
			$('content').innerHTML = show_login_box();
			$('i_password').addEvent('keydown', function(event) {
				if (event.key == 'enter') {
					event.stop();
					validate_authentication_token();
				}
			});
			$('b_login_submit').addEvent('click', function(event) {
				event.stop();
				validate_authentication_token();
			});
			$('b_login_reset').addEvent('click', function(event) {
				event.stop();
				$('i_username').value = 'Username';
				$('i_username')._haschanged = false;
				$('i_password').value = '';
			});
		}
	});

	$('b_profile').addEvent('click', function(event) {
		event.stop();
		$('content').innerHTML = show_profile_box();
		get_profile();
		$('b_update_profile').addEvent('click', function(event) {
			event.stop();
			username = get_username();
			var meta = {'username': username}
			var has_newpass = false;
			if ($('i_realname').value != get_realname()) {
				meta['realname'] = $('i_realname').value;
			}
			if ($('i_newpass1').value != '') {
				if ($('i_newpass1').value == $('i_newpass2').value) {
					meta['new_password'] = $('i_newpass1').value;
					has_newpass = true;
				}
			}
			var request = new Request.JSON({
				method: 'post',
				url: '/users/'+username,
				headers: {'Authorization': 'Basic ' + get_authentication_token()},
				data: btoa(JSON.encode(meta)),
				onComplete: function(response) {
					if (has_newpass) {
						set_authentication_token(false);
						set_username(false);
						toggle_auth_button_box();
						$('content').innerHTML = show_login_box();
						$('i_password').addEvent('keydown', function(event) {
							if (event.key == 'enter') {
								event.stop();
								validate_authentication_token();
							}
						});
						$('b_login_submit').addEvent('click', function(event) {
							event.stop();
							validate_authentication_token();
						});
						$('b_login_reset').addEvent('click', function(event) {
							event.stop();
							$('i_username').value = 'Username';
							$('i_username')._haschanged = false;
							$('i_password').value = '';
						});
					} else {
						$('content').innerHTML = show_search_box();
					}
				}
			}).send();
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
				console.log("response: "+response);
				$("content").innerHTML = "Request returned from API:" + response;
			}
		}).send();
	});

	$('b_q_reset').addEvent('click', function(event) {
		console.log('reset');
	});

});
