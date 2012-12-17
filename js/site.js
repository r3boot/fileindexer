var s

var archive_mimetypes = Array('application/bzip2', 'vnd.ms-cab-compressed', 'application/gzip', 'application/gzip-compressed', 'application/gzipped', 'application/x-gzip', 'gzip/document', 'application/x-gzip-compressed', 'application/tar', 'application/x-gtar', 'application/x-gtar', 'applicaton/x-gtar', 'application/x-lzip', 'application/x-winzip', 'application/x-zip-compressed', 'application/zip', 'application/x-zip', 'application/x-zip-compressed', 'multipart/x-zip')
var audio_mimetypes = Array('audio/aiff', 'audio/x-aiff', 'audio/x-pn-aiff', 'sound/aiff', 'audio/flac', 'audio/mpeg', 'audio/x-mpegaudio', 'audio/vnd.rn-realaudio', 'audio/vnd.rn-realaudio-secure', 'audio/x-pm-realaudio-plugin', 'audio/x-pn-realaudio', 'audio/x-pnrealaudio-plugin', 'audio/x-pn-realaudio-plugin', 'audio/x-realaudio', 'audio/x-realaudio-secure', 'audio/basic', 'application/ogg', 'audio/ogg', 'audio/x-ogg', 'application/x-ogg')
var video_mimetypes = Array('application/vnd.rn-realmedia', 'application/vnd.rn-realmedia-secure', 'application/vnd.rn-realmedia-vbr', 'application/x-pn-realmedia', 'audio/vnd.rn-realvideo', 'audio/vnd.rrn-realvideo', 'audio/x-pn-realvideo', 'video/vnd.rn-realvideo', 'video/vnd.rn-realvideo-secure', 'video/vnd-rn-realvideo', 'video/x-pn-realvideo', 'video/x-pn-realvideo-plugin', 'audio/avi', 'image/avi', 'video/avi', 'video/msvideo', 'video/x-msvideo', 'application/futuresplash', 'application/x-shockwave-flash', 'application/x-shockwave-flash2-preview', 'video/vnd.sealed.swf', 'application/wmf', 'application/x-msmetafile', 'application/x-wmf', 'application/vnd.ms-asf', 'application/x-mplayer2', 'audio/asf', 'video/x-ms-asf', 'video/x-la-asf', 'video/x-ms-asf', 'video/x-ms-asf-plugin', 'video/x-ms-wm', 'video/x-ms-wmx', 'video/x-flv', 'image/mov', 'video/quicktime', 'video/sgi-movie', 'video/vnd.sealedmedia.softseal.mov', 'video/x-quicktime', 'video/x-sgi-movie')
var image_mimetypes = Array('application/bmp', 'application/preview', 'application/x-bmp', 'application/x-win-bitmap', 'image/bmp', 'image/ms-bmp', 'image/vnd.wap.wbmp', 'image/x-bitmap', 'image/x-bmp', 'image/x-ms-bmp', 'image/x-win-bitmap', 'image/x-windows-bmp', 'image/x-xbitmap', 'image/gi_', 'image/gif', 'image/vnd.sealedmedia.softseal.gif', 'application/ico', 'application/x-ico', 'application/x-iconware', 'image/ico', 'image/x-icon', 'image/jpe_', 'image/jpeg', 'image/jpeg2000', 'image/jpeg2000-image', 'image/jpg', 'image/pjpeg', 'image/vnd.sealedmedia.softseal.jpeg', 'image/vnd.swiftview-jpeg', 'image/x-jpeg2000-image', 'video/x-motion-jpeg', 'application/pcx', 'application/x-pcx', 'image/pcx', 'image/vnd.swiftview-pcx', 'image/x-pc-paintbrush', 'image/x-pcx', 'zz-application/zz-winassoc-pcx', 'application/png', 'application/x-png', 'image/png', 'image/vnd.sealed.png', 'application/psd', 'image/photoshop', 'image/psd', 'image/x-photoshop', 'zz-application/zz-winassoc-psd', 'application/x-targa', 'image/targa', 'image/x-targa', 'application/tga', 'application/x-tga', 'image/tga', 'image/x-tga', 'application/tiff', 'application/vnd.sealed.tiff', 'application/x-tiff', 'image/tiff', 'image/x-tiff', 'application/xcf', 'application/x-xcf', 'image/xcf', 'image/x-xcf', 'image/wmf', 'image/x-win-metafile', 'image/x-wmf')

var int_to_month = Array('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

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

function is_dir(mode) {
	if ((mode & 61440) == 16384) {
		return true
	} else {
		return false
	}
}

function is_archive(mimetype) {
	for (var i=0; i<archive_mimetypes.length; i++) {
		if (archive_mimetypes[i] == mimetype) {
			return true
		}
	}
	return false
}

function is_audio(mimetype) {
	for (var i=0; i<audio_mimetypes.length; i++) {
		if (audio_mimetypes[i] == mimetype) {
			return true
		}
	}
	return false
}

function is_video(mimetype) {
	for (var i=0; i<video_mimetypes.length; i++) {
		if (video_mimetypes[i] == mimetype) {
			return true
		}
	}
	return false
}

function is_image(mimetype) {
	for (var i=0; i<image_mimetypes.length; i++) {
		if (image_mimetypes[i] == mimetype) {
			return true
		}
	}
	return false
}

function set_href(url) {
	window.location.href = url
}

// Utility functions
function validate_authentication_token(username, password) {
	var basic_auth_token = btoa(username+':'+password)

	console.log('basic_auth_token: '+basic_auth_token)

	$.ajax({
		url: '/auth',
		type: 'get',
		data: {},
		headers: {'Authorization': 'Basic ' + basic_auth_token},
		dataType: 'json',
		success: function(response) {
			if (response['result']) {
				sset('auth_token', basic_auth_token)
				sset('username', username)
				toggle_auth_button_box()
				view_search()
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

function edit_server(server) {
	$('#content').html(show_edit_server_box())

	$.ajax({
		url: '/server',
		type: 'put',
		data: JSON.stringify({'hostname': server}),
		headers: {'Authorization': 'Basic ' + sget('auth_token')},
		dataType: 'json',
		success: function(response) {
			console.log(response)
			if (response['result'] == true) {
				var hostname = response['server'][0]['hostname']
				$('#i_hostname').val(hostname)
			} else {
				$('#content').html(response['message'])
			}
		},
		error: function(xhr, textStatus, errorThrown) {
			$('#content').html('unable to retrieve indexes')
		}
	})

	$('#b_update_server').click(function(e) {
		e.preventDefault()
	})

	$('#b_rewrites').click(function(e) {
		e.preventDefault()
	})
}

function remove_server(server) {
	$.ajax({
		url: '/servers',
		type: 'delete',
		data: JSON.stringify({'hostname': server}),
		headers: {'Authorization': 'Basic ' + sget('auth_token')},
		dataType: 'json',
		success: function(response) {
			if (response['result'] == true) {
				console.log('server removed')
				show_servers_box()
			} else {
				console.log(response['message'])
				$('#content').html('unable to remove server')
			}
		},
		error: function(xhr, textStatus, errorThrown) {
			$('#content').html('unable to remove server')
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
	content += "<div class=\"span12\" id=\"mainpage\">"
	content += "<table class=\"table table-hover\" id=\"t_indexes\">"
	content += "<tr><thead>"
	content += "<th>Server</th>"
	content += "<th>Index</th>"
	content += "<th>Description</th>"
	content += "<th># Files</th>"
	content += "<th>Operator</th>"
	content += "</thead></tr>"
	content += "<tbody id=\"t_indexes_tbody\">"
	content += "</tbody>"
	content += "</table>"
	content += "</div>"
	content += "</div>"
	content += "</div>"
	return content
}

function view_auth() {
	var content = "<form class=\"form-signin\">"
	content += "<h2 class=\"form-signin-heading\">Please sign in</h2>"
	content += "<input type=\"text\" id=\"i_username\" class=\"input-block-level\" placeholder=\"Username\">"
	content += "<input type=\"password\" id=\"i_password\" class=\"input-block-level\" placeholder=\"Password\">"
	content += "<label class=\"checkbox\">"
	content += "<input type=\"checkbox\" value=\"remember-me\"> Remember me</label>"
	content += "<button class=\"btn btn-large btn-primary\" id=\"b_signin\" type=\"submit\">Sign in</button>"
	content += "</form>"

	$('#content').html(content)

	$('#a_servers').removeClass('active');
	$('#a_profile').removeClass('active');
	$('#a_auth').addClass('active');

	$('#b_signin').click(function(e) {
		e.preventDefault()
		var username = $('#i_username').val()
		var password = $('#i_password').val()

		validate_authentication_token(username, password)
	})
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

function view_servers() {

	var content = "<form class=\"form-servers\">"
	content += '<h2 class=\"form-servers-heading\">Edit servers for '+sget('username')+'</h2>'
	content += '<div id=\"servers_content\"></div>'
	content += '<button class=\"btn\" id=\"b_add_new_server\"><i class=\"icon-plus\"/> Add server</button>'
	content += "</form>"

	$('#a_servers').addClass('active');
	$('#a_profile').removeClass('active');
	$('#a_auth').removeClass('active');

	$('#content').html(content)

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
					var hostname = response['servers'][i]['hostname']
					var apikey = response['servers'][i]['apikey']

					content += '<tr>'
					content += '<td onclick=\"edit_server(\''+hostname+'\')\">'+hostname+'</td>'
					content += '<td onclick=\"edit_server(\''+hostname+'\')\">'+apikey+'</td>'
					content += '<td><i class=\"icon-remove-circle\" onclick=\"remove_server(\''+hostname+'\')\"></td>'
					content += '</tr>'
				}
				$('#t_servers_content').html(content)

			} else {
				$('#servers_content').html('no servers found')
			}
		},
		error: function(xhr, textStatus, errorThrown) {
			$('#servers_content').html('Failed to fetch servers')
		}
	})

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
						view_servers()
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
}

function show_servers_table() {
	var content = "<table class=\"table table-hover\">"
	content += "<thead><tr>"
	content += "<th>Hostname</th>"
	content += "<th>Api key</th>"
	content += "</tr></thead>"
	content += "<tbody id=\"t_servers_content\"></tbody>"
	content += "</table>"
	return content
}

function show_add_server_box() {
	var content = "<form class=\"form-servers\">"
	content += "<h2 class=\"form-servers-heading\">Add server for "+sget('username')+"</h2>"
	content += "<table class=\"table\">"
	content += "<tr><td>Fqdn or ip</td>"
	content += "<td><input type=\"text\" class=\"input-block-level\" id=\"i_hostname\" /></td></tr>"
	content += "</table>"
	content += "<button class=\"btn\" id=\"b_add_new_server\"><i class=\"icon-plus\" />Add</button>"
	content += "</form>"
	return content
}

function show_edit_server_box() {
	var content = '<form class=\"form-servers\">'
	content += '<h2 class=\"form-servers-heading\">Edit server</h2>'
	content += '<table class=\"table\">'
	content += '<tr>'
	content += '<td>Fqdn or ip</td>'
	content += '<td><input type=\"text\" class=\"input-block-level\" id=\"i_hostname\" /></td></tr>'
	content += '</tr>'
	content += '</table>'
	content += "<button class=\"btn\" id=\"b_update_server\"><i class=\"icon-plus\" />Update</button>"
	content += "<button class=\"btn\" id=\"b_rewrites\"><i class=\"icon-filter\" />Rewrites</button>"
	content += '</form>'
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

function view_search() {
	var content = '<div class=\"container-fluid\" id=\"d_search\">'
	content += '<div class=\"center hero-unit\">'
	content += '<div class=\"row-fluid\">'
	content += '<div class=\"span12\">'
	content += '<div class=\"span10\">'
	content += '<input type=\"text\" class=\"input-block-level search-query\" id=\"i_q\" />'
	content += '</div>'
	content += '<div class=\"span2\">'
	content += '<div class=\"btn-group\">'
	content += '<button class=\"btn\" id=\"b_main_search\"><i class=\"icon-thumbs-up\" /> Go</button>'
	content += '<button class=\"btn\" id=\"b_main_adv_search\"><i class=\"icon-filter\" /> Advanced</button>'
	content += '</div>'
	content += '</div>'
	content += '</div>'
	content += '</div>'
	content += '</div>'
	content += '</div>'

	$('#content').html(content)

	$('#b_main_search').click(function(e) {
		e.preventDefault()
		view_search_results($('#i_q').val(), 1)
	})

}

function format_search_meta(results) {
	var query = results['query']
	var pagenum = results['pagenum']
	var pagecount = results['pagecount']
	var result_start = results['result_start']
	var result_end = results['result_end']
	var result_total = results['result_total']

	var content = '<div class=\"span12\">'
	content += '<div class=\"span2\">'
	content += '<h3>Page '+pagenum+' of '+pagecount+'</h3>'
	content += '</div>'
	content += '<div class=\"span10\">'
	content += '<div class=\"pagination pagination-right\"><ul>'
	for (var i=0; i<pagecount; i++) {
		page_id = i+1
		content += '<li><a href=\"#\" onclick=\"view_search_results(\''+query+'\', '+page_id+')\">'+page_id+'</a></li>'
	}
	content += '</ul></div>'
	content += '</div>'
	content += '</div>'
	return content
}

function format_search_results(results) {
	var content = '<div class=\"accordion\" id=\"accordion2\">'
	for (var i=0; i<results['documents'].length; i++) {
		var url = results['documents'][i]['url']
		var uid = results['documents'][i]['uid']
		var gid = results['documents'][i]['gid']
		var mtime = results['documents'][i]['mtime']
		var size = results['documents'][i]['size']
		var rank = results['documents'][i]['rank']
		var score = results['documents'][i]['score'].toPrecision(3)

		mtime_t = mtime.split('-')
		var year = mtime_t[0]
		var month = int_to_month[parseInt(mtime_t[1], 10)]
		var day = mtime_t[2].split('T')[0]
		var time = mtime_t[2].split('T')[1]
		var date = month+' '+day+' '+time+' CEST '+year

		var url_t = url.split('/')
		var proto = url_t[0].replace(':', '')
		var server = url_t[2]
		var safe_url = proto+'://'+server
		var raw_path = url.replace(safe_url, '')
		safe_url += escape(raw_path)

		content += '<div class=\"accordion-group\">'
		content += '<div class=\"accordion-heading\">'
		content += '<a class=\"accordion-toggle\" data-toggle=\"collapse\" data-parent=\"#accordion2\" href=\"#c'+rank+'\">'
		content += '<span onclick=\"window.location.href=\''+safe_url+'\'; event.stopPropagation()\">'+url+'</span>'
		content += '</a>'
		content += '</div>'
		content += '<div id=\"c'+rank+'\" class=\"accordion-body collapse\">'
		content += '<div class=\"accordion-inner\">'
		content += 'Rank: '+rank+', Score: '+score+', Size: '+size+'B, Last modified: '+date
		content += '</div>'
		content += '</div>'
		content += '</div>'

	}
	content += '</div>'
	return content
}

function view_search_results(query, page) {
	if (!page) {
		page = 1
	}
	var content = '<div class=\"row-fluid\">'
	content += '<div class=\"span12\">'
	content += '<div class=\"span10\">'
	content += '<input type=\"text\" class=\"input-block-level search-query\" id=\"i_q\" />'
	content += '</div>'
	content += '<div class=\"span2\">'
	content += '<div class=\"btn-group\">'
	content += '<button class=\"btn\" id=\"b_search\"><i class=\"icon-thumbs-up\" /> Go</button>'
	content += '<button class=\"btn\" id=\"b_adv_search\"><i class=\"icon-filter\" /> Advanced</button>'
	content += '</div>'
	content += '</div>'
	content += '</div>'
	content += '<div class=\"span12\" id=\"d_search_meta\">'
	content += '</div>'
	content += '<div class=\"span12\" id=\"d_search_results\">'
	content += '</div>'
	content += '</div>'

	$('#content').html(content)
	$('#i_q').val(query)

	var meta = {
		'query': query,
		'page': page,
		'pagelen': 10,
	}

	$.ajax({
		url: '/q',
		type: 'post',
		data: JSON.stringify(meta),
		headers: {'Authorization': 'Basic ' + sget('auth_token')},
		dataType: 'json',
		success: function(response) {
			if (response['result']) {
				results = response['results']
				results['query'] = query
				$('#d_search_meta').html(format_search_meta(results))
				$('#d_search_results').html(format_search_results(results))
			} else {
				$('#content').html('Query returned a failure')
			}
		},
		error: function(xhr, textStatus, errorThrown) {
			$('#content').html('Failed to submit query')
		}
	})

	$('#b_search').click(function(e) {
		e.preventDefault()
		var meta = {'query': $('#i_q').val()}
		console.log('here')

		$.ajax({
			url: '/q',
			type: 'post',
			data: JSON.stringify(meta),
			headers: {'Authorization': 'Basic ' + sget('auth_token')},
			dataType: 'json',
			success: function(response) {
				if (response['result']) {
					results = response['results']
					results['query'] = query
					$('#d_search_meta').html(format_search_meta(results))
					$('#d_search_results').html(format_search_results(results))
				} else {
					$('#content').html('Query returned a failure')
				}
			},
			error: function(xhr, textStatus, errorThrown) {
				$('#content').html('Failed to submit query')
			}
		})
	})
}

function view_profile() {
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

					$('#b_signin').click(function(e) {
						e.preventDefault()
						validate_authentication_token()
					})
				} else {
					view_search()
				}
			},
			error: function(xhr, textStatus, errorThrown) {
				$('#content').html('Failed to update profile')
			}
		})
	})
}

function main() {
	$(document).ready(function() {
		s = new Persist.Store('fileindexer')
		reset_store()

		toggle_auth_button_box()

		view_search()

		$('#a_home').click(function(e) {
			e.preventDefault()
			view_search()
		})

		$('#a_profile').click(function(e) {
			e.preventDefault()
			view_profile()
		})

		$('#a_servers').click(function(e) {
			e.preventDefault()
			view_servers()
		})

		$('#a_auth').click(function(e) {
			e.preventDefault()
			if (sget('auth_token') == false) {
				view_auth()
			} else {
				console.log('doing logout')
				reset_store()
				toggle_auth_button_box()
				view_search()
			}
		})

	})
}

/* GO GO GO */
main()
