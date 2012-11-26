var s

function sget(k) {
	try {
		v = s.get(k)
		if (v == 'false') {
			v = false
		} else if (v == 'true') {
			v = true
		}
		console.log('sget: '+k+' = '+v)
		return v
	} catch (err) {
		console.log('sget: could not retrieve '+k)
		return null
	}
}

function sset(k, v) {
	console.log('sset: '+k+' = '+v)
	s.set(k, v)
	s.save()
}


// Utility functions
function validate_authentication_token() {
	var username = $('#i_username').val()
	var password = $('#i_password').val()
	var basic_auth = username + ":" + password
	var basic_auth_token = btoa(basic_auth)

	$.ajax({
		url: "/auth",
		type: 'get',
		data: {},
		headers: {'Authorization': 'Basic ' + basic_auth_token},
		dataType: 'json',
		success: function(response) {
			if (response['result']) {
				sset('auth_token', basic_auth_token)
				sset('username', username)
				toggle_auth_button_box()
				$('#content').html(show_search_box())
			} else {
				sset('auth_token', false)
				sset('username', false)
				$("#content").html('Failed to authenticate')
			}
		},
		error: function(xhr, textStatus, errorThrown){
			$("#content").html('Failed to authenticate')
		}
		
	})

}

function get_profile() {
	username = get_username()
	if (username == 'false') {
		return false
	}

	var request = new Request.JSON({
		method: 'get',
		url: '/users/'+username,
		headers: {'Authorization': 'Basic ' + get_authentication_token()},
		data: {},
		onComplete: function(response) {
			set_realname(response['user']['realname'])
			$('i_realname').value = get_realname()
		},
		onFailure: function(response) {
			$('content').html('unable to retrieve profile')
		}
	}).send()
}

function toggle_auth_button_box() {
	if (sget('auth_token') == false) {
		$('#a_servers').css("display", "none")
		$('#a_profile').css("display", "none")
		$('#a_auth').html('Sign in')
	} else {
		$('#a_servers').css("display", "block")
		$('#a_profile').css("display", "block")
		$('#a_auth').html('Sign out')
	}
}

function show_search_box() {
	var content = "<div id=\"search\">"
	content += "<input type=\"text\" id=\"q\" value=\"Enter a search query\" onclick=\"if(!this._haschanged){this.value=''};this._haschanged=true;\" />"
	content += "<button class=\"default\" id=\"b_q_submit\">go</button>"
	content += "<button class=\"default\" id=\"b_q_reset\">reset</button>"
	content += "</div>"
	return content
}

function show_login_box() {
	var content = "<div id=\"login\">"
	content += "<input type=\"text\" id=\"i_username\" name=\"username\" value=\"Username\" onclick=\"if(!this._haschanged){this.value=''};this._haschanged=true;\" /><br />"
	content += "<input type=\"password\" id=\"i_password\" name=\"password\" /><br />"
	content += "<button class=\"default\" id=\"b_login_submit\">submit</button>"
	content += "<button class=\"default\" id=\"b_login_reset\">reset</button>"
	content += "</div>"
	return content
}

function show_login_failure() {
	var content = "<div id=\"login_failed\">"
	content += "authentication failed"
	content += "</div>"
	return content
}

function show_profile_box() {
	var content = "<table id=\"t_profile\">"
	content += "<tr>"
	content += "<td>Real Name:</td>"
	content += "<td><input type=\"text\" id=\"i_realname\" name=\"realname\" /></td>"
	content += "</tr><tr>"
	content += "<td>New Password:</td>"
	content += "<td><input type=\"text\" id=\"i_newpass1\" name=\"newpass1\" /></td>"
	content += "</tr><tr>"
	content += "<td>New Password (again):</td>"
	content += "<td><input type=\"text\" id=\"i_newpass2\" name=\"newpass2\" /></td>"
	content += "</tr>"
	content += "</table>"
	content += "<p/><button type=\"button\" id=\"b_update_profile\">Update</button>"
	return content
}

function main() {
	$(document).ready(function() {
		s = new Persist.Store('fileindexer')

		if (sget('auth_token') == null) {
			sset('auth_token', false)
		}

		if (sget('username') == null) {
			sset('username', false)
		}

		if (sget('realname') == null) {
			sset('realname', false)
		}

		toggle_auth_button_box()

		$('#content').html(show_search_box())

		$('#a_home').click(function() {
			$('#content').html(show_search_box())
		})

		$('#a_servers').click(function() {
			console.log("a_servers clicked")
		})

		$('#a_profile').click(function() {
			console.log("a_profile clicked")
		})

		$('#a_auth').click(function() {
			if (sget('auth_token') == false) {
				$('#content').html(show_login_box())

				$('#b_login_submit').click(function() {
					validate_authentication_token()
				})

				$('#b_login_reset').click(function() {
					$('#i_username').value = 'Username'
					$('#i_username')._haschanged = false
					$('#i_password').value = ''
				})

			} else {
				console.log('doing logout')
				sset('auth_token', false)
				sset('username', false)
				sset('realname', false)
				toggle_auth_button_box()
				$('#content').html(show_search_box())
			}
		})
	})
}

main()

/*
// Event handling
window.addEvent('domready', function() {

	toggle_auth_button_box()

	$('page').addEvent('domready', function(event) {
		$('content').html = show_search_box()
	})

	$('b_auth').addEvent('click', function(event) {
		event.stop()
		if (localStorage.getItem('auth_token') != 'false') {
			// logout
			set_authentication_token(false)
			set_username(false)
			toggle_auth_button_box()
			$('content').html = show_search_box()
		} else {
			// login
			$('content').html = show_login_box()
			$('i_password').addEvent('keydown', function(event) {
				if (event.key == 'enter') {
					event.stop()
					validate_authentication_token()
				}
			})
			$('b_login_submit').addEvent('click', function(event) {
				event.stop()
				validate_authentication_token()
			})
			$('b_login_reset').addEvent('click', function(event) {
				event.stop()
				$('i_username').value = 'Username'
				$('i_username')._haschanged = false
				$('i_password').value = ''
			})
		}
	})

	$('b_profile').addEvent('click', function(event) {
		event.stop()
		$('content').html = show_profile_box()
		get_profile()
		$('b_update_profile').addEvent('click', function(event) {
			event.stop()
			username = get_username()
			var meta = {'username': username}
			var has_newpass = false
			if ($('i_realname').value != get_realname()) {
				meta['realname'] = $('i_realname').value
			}
			if ($('i_newpass1').value != '') {
				if ($('i_newpass1').value == $('i_newpass2').value) {
					meta['new_password'] = $('i_newpass1').value
					has_newpass = true
				}
			}
			var request = new Request.JSON({
				method: 'post',
				url: '/users/'+username,
				headers: {'Authorization': 'Basic ' + get_authentication_token()},
				data: btoa(JSON.encode(meta)),
				onComplete: function(response) {
					if (has_newpass) {
						set_authentication_token(false)
						set_username(false)
						toggle_auth_button_box()
						$('content').html = show_login_box()
						$('i_password').addEvent('keydown', function(event) {
							if (event.key == 'enter') {
								event.stop()
								validate_authentication_token()
							}
						})
						$('b_login_submit').addEvent('click', function(event) {
							event.stop()
							validate_authentication_token()
						})
						$('b_login_reset').addEvent('click', function(event) {
							event.stop()
							$('i_username').value = 'Username'
							$('i_username')._haschanged = false
							$('i_password').value = ''
						})
					} else {
						$('content').html = show_search_box()
					}
				}
			}).send()
		})
	})

	$('b_q_submit').addEvent('click', function(event) {
		event.stop()
		var request = new Request.JSON({
			method: 'get',
			url: '/files',
			data: {},
			onRequest: function() {
				$("content").html = "Sending request to API"
			},
			onComplete: function(response) {
				console.log("response: "+response)
				$("content").html = "Request returned from API:" + response
			}
		}).send()
	})

	$('b_q_reset').addEvent('click', function(event) {
		console.log('reset')
	})

})
*/
