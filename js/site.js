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

function reset_store() {
	sset('username', false)
	sset('realname', false)
	sset('auth_token', false)
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
		error: function(xhr, textStatus, errorThrown) {
			console.log('XHR: '+xhr.status+'; textStatus: '+textStatus+'; errorThrown: '+errorThrown)
			$("#content").html('Failed to authenticate')
		}
		
	})

}

function get_profile() {
	username = sget('username')
	if (username == false) {
		return false
	}

	$.ajax({
		url: '/users/'+username,
		type: 'get',
		data: {},
		headers: {'Authorization': 'Basic ' + sget('auth_token')},
		dataType: 'json',
		success: function(response) {
			if (response['result'] == true) {
				sset('realname', response['user']['realname'])
				$('#i_realname').val(response['user']['realname'])
			} else {
				$('content').html('unable to retrieve profile')
			}
		},
		error: function(xhr, textStatus, errorThrown) {
			$('content').html('unable to retrieve profile')
		}
	})

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
	var content = "<form class=\"form-signin\">"
	content += "<h2 class=\"form-signin-heading\">Please sign in</h2>"
	content += "<input type=\"text\" id=\"i_username\" class=\"input-block-level\" placeholder=\"Username\">"
	content += "<input type=\"password\" id=\"i_password\" class=\"input-block-level\" placeholder=\"Password\">"
	content += "<label class=\"checkbox\">"
	content += "<input type=\"checkbox\" value=\"remember-me\"> Remember me</label>"
	content += "<button class=\"btn btn-large btn-primary\" id=\"b_signin\" type=\"submit\">Sign in</button>"
	content += "</form>"
	return content
}

function show_profile_box() {
	var content = "<form class=\"form-profile\">"
	content += "<h2 class=\"form-signin-heading\">Edit profile for "+sget('username')+"</h2>"
	content += "<table class=\"table-profile\">"
	content += "<tr>"
	content += "<td>Real Name:</td>"
	content += "<td><input type=\"text\" class=\"input-block-level\" id=\"i_realname\" /></td>"
	content += "</tr><tr>"
	content += "<td>New Password:</td>"
	content += "<td><input type=\"password\" class=\"input-block-level\" id=\"i_newpass1\" /></td>"
	content += "</tr><tr>"
	content += "<td>New Password (again):</td>"
	content += "<td><input type=\"password\" class=\"input-block-level\" id=\"i_newpass2\" /></td>"
	content += "</tr>"
	content += "</table>"
	content += "<button class=\"btn btn-large btn-primary\" type=\"submit\" id=\"b_update_profile\">Update</button>"
	content += "</form>"
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
			$('#content').html(show_profile_box())
			get_profile()

			$('#b_update_profile').click(function() {
				username = sget('username')
				var meta = {'username': username}
				var has_newpass = false
				if ($('#i_realname').val() != sget('realname')) {
					meta['realname'] = $('#i_realname').val()
				}
				if ($('#i_newpass1').val() != '') {
					if ($('#i_newpass1').val() == $('#i_newpass2').val()) {
						meta['new_password'] = $('#i_newpass1').val()
						has_newpass = true
					}
				}
				json_data = JSON.stringify(meta)
				b64_data = btoa(json_data)
				console.log('b64_data: '+b64_data)

				$.ajax({
					url: '/users/'+username,
					type: 'post',
					data: b64_data,
					headers: {'Authorization': 'Basic ' + sget('auth_token')},
					dataType: 'json',
					success: function(response) {
						if (has_newpass) {
							reset_store()
							toggle_auth_button_box()
							$('#content').html(show_login_box())
							$('#b_signin').click(function() {
								validate_authentication_token()
							})
						} else {
							$('#content').html(show_search_box())
						}
					},
					error: function(xhr, textStatus, errorThrown) {
						$('#content').html('Failed to update profile')
					}
				})
			})
		})

		$('#a_auth').click(function() {
			if (sget('auth_token') == false) {
				$('#content').html(show_login_box())

				$('#b_signin').click(function() {
					validate_authentication_token()
				})

			} else {
				console.log('doing logout')
				reset_store()
				toggle_auth_button_box()
				$('#content').html(show_search_box())
			}
		})


	})
}

/* GO GO GO */
main()
