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
	console.log('basic_auth_token: '+basic_auth_token)

	$.ajax({
		url: '/auth',
		type: 'get',
		data: {},
		headers: {'Authorization': 'Basic ' + basic_auth_token},
		dataType: 'json',
		/*beforeSend : function(req) {
			req.setRequestHeader('Authorization', 'Basic ' + basic_auth_token)
		},*/
		success: function(response) {
			if (response['result']) {
				sset('auth_token', basic_auth_token)
				sset('username', username)
				toggle_auth_button_box()
				$('#content').html(show_search_page())
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
		url: '/user',
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

function show_search_page() {
	var content = "<div class=\"container-fluid\">"
	content += "<div class=\"row-fluid\">"
	content += "<div class=\"span4 offset4\" id=\"mainpage\">"
	content += "<table class=\"table table-hover\" id=\"t_indexes\">"
	content += "</table>"
	content += "</div>"
	content += "</div>"
	content += "</div>"
	return content
}

function sb_search_content() {
	var content = "<div class=\"btn-group btn-group-vertical\">"
	content += "<button class=\"btn\">search</button>"
	content += "<button class=\"btn\">browse</button>"
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
	content += "<h2 class=\"form-profile-heading\">Edit profile for "+sget('username')+"</h2>"
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

function show_servers_box() {
	var content = "<form class=\"form-servers\">"
	content += "<h2 class=\"form-servers-heading\">Edit servers for "+sget('username')+"</h2>"
	content += "<div id=\"servers_content\"></div>"
	content += "<button class=\"btn btn-large btn-primary\" type=\"button\" id=\"b_add_new_server\">Add server</button>&nbsp;"
	content += "</form>"
	return content
}

function show_servers_table() {
	var content = "<table class=\"table-servers\">"
	content += "<thead><tr>"
	content += "<th>Hostname</th>"
	content += "<th>Api key</th>"
	content += "</tr></thead>"
	content += "<tbody id=\"table_servers_content\"></tbody>"
	content += "</table>"
	return content
}

function show_add_server_box() {
	var content = "<form class=\"form-servers\">"
	content += "<h2 class=\"form-servers-heading\">Add server for "+sget('username')+"</h2>"
	content += "<table class=\"table-servers\">"
	content += "<tr><td>Fqdn or ip</td>"
	content += "<td><input type=\"text\" class=\"input-block-level\" id=\"i_hostname\" /></td></tr>"
	content += "</table>"
	content += "<button class=\"btn btn-large btn-primary\" type=\"button\" id=\"b_add_new_server\">Add</button>&nbsp;"
	content += "</form>"
	return content
}

function show_add_rewrite_box() {
	var content = "<form class=\"form-servers\">"
	content += "<h2 class=\"form-servers-heading\">Add rewrite for "+sget('username')+"</h2>"
	content += "<input type=\"text\" class=\"input-block-level\" id=\"i_rewrite_rule\" />"
	content += "<button class=\"btn btn-large btn-primary\" type=\"button\" id=\"b_add_new_rewrite\">Add</button>"
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

		$('#content').html(show_search_page())

		$('#a_home').click(function() {
			$('#content').html(show_search_page())
		})

		$('#a_profile').click(function() {
			$('#content').html(show_profile_box())
			get_profile()

			$('#a_servers').removeClass('active');
			$('#a_profile').addClass('active');
			$('#a_auth').removeClass('active');

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

				$.ajax({
					url: '/user',
					type: 'post',
					data: JSON.stringify(meta),
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
							$('#content').html(show_search_page())
						}
					},
					error: function(xhr, textStatus, errorThrown) {
						$('#content').html('Failed to update profile')
					}
				})
			})
		})

		$('#a_servers').click(function() {
			$('#content').html(show_servers_box())

			$.ajax({
				url: '/servers',
				type: 'get',
				headers: {'Authorization': 'Basic ' + sget('auth_token')},
				dataType: 'json',
				success: function(response) {
					if (response['result']) {
						$('#servers_content').html(show_servers_table())
						var content = ''

						for (var i=0; i<response['servers'].length; i++) {
							content += '<tr>'
							content += '<td>'+response['servers'][i]['hostname']+'</td>'
							content += '<td>'+response['servers'][i]['apikey']+'</td>'
							content += '</tr>'
						}
						$('#table_servers_content').html(content)

					} else {
						$('#servers_content').html('no servers found')
					}
				},
				error: function(xhr, textStatus, errorThrown) {
					$('#servers_content').html('Failed to fetch servers')
				}
			})

			$('#a_servers').addClass('active');
			$('#a_profile').removeClass('active');
			$('#a_auth').removeClass('active');

			$('#b_add_new_server').click(function() {
				$('#content').html(show_add_server_box())

				$('#b_add_new_server').click(function() {
					var hostname = $('#i_hostname').val()
					var meta = {'hostname': hostname, 'username': sget('username')}

					$.ajax({
						url: '/servers',
						type: 'post',
						headers: {'Authorization': 'Basic ' + sget('auth_token')},
						data: JSON.stringify(meta),
						dataType: 'json',
						success: function(response) {
							if (response['result']) {
								$('#content').html('Successfully added server')
							} else {
								$('#content').html('Failed to add server')
							}
						},
						error: function(xhr, textStatus, errorThrown) {
							$('#content').html('Error adding server')
						}
					})
				})
			})

			$('#b_add_new_rewrite').click(function() {
				$('#content').html(show_add_rewrite_box())

				$('#b_add_new_rewrite').click(function() {
					console.log("add rewrite")
				})
			})

		})

		$('#a_auth').click(function() {
			if (sget('auth_token') == false) {
				$('#content').html(show_login_box())

				$('#a_servers').removeClass('active');
				$('#a_profile').removeClass('active');
				$('#a_auth').addClass('active');

				$('#b_signin').click(function() {
					validate_authentication_token()
				})

			} else {
				console.log('doing logout')
				reset_store()
				toggle_auth_button_box()
				$('#content').html(show_search_page())
			}
		})

	})
}

/* GO GO GO */
main()
