function submit_d3form(which) {
	which.form.submitted.value = 'yes';
	which.form.submit();
}

var d3forms_submit_buttons = new Array();
var d3forms_ajax_handler = function(responseText, responseStatus, responseXML) {
	if (responseStatus == 200) {
		response = responseText.split("|");
		var form_id = trim(response[0]);

		if (response.length == 2) {
			// form was successfully submitted, remove the error/form divs and display the success =]
			if (getEle(form_id + "_error") != false) getEle(form_id + "_error").style.display = 'none';
			tmp_id = form_id.replace("_friend", "");
			getEle(tmp_id + "_form_container").style.display = 'none';
			getEle(tmp_id + "_success_container").style.display = '';
			
			if (tmp_id != form_id) {
				// show any available "success" message
				if (getEle(form_id + "_success") != false) getEle(form_id + "_success").style.display = '';
				// we're on a "signup a friend" form, reset the fields
				getEle(form_id).reset();
				// replace the submit button
				var sub_btn = getEle(form_id + '_submit_button');
				sub_btn.disabled = false;
				sub_btn.setAttribute("value", d3forms_submit_buttons[form_id]);
			}
		} else {
			// there was an error submitting the form
			
			// highlight each "field/label" that has an error
			for (var i=1; i<(response.length - 1); i++) {
				var el = getEle(form_id + '_' + trim(response[i]) + '_label');
				if (el != false) {
					var contents = el.innerHTML;
					var em = document.createElement('em');
					em.setAttribute('class', 'frm-required');
					em.setAttribute('className', 'frm-required');
					em.appendChild(document.createTextNode(contents));
					el.innerHTML = '';
					el.appendChild(em);
				}
			}

			// display the actual form error
			var err = getEle(form_id + "_error");
			if (err != false) {
				var err_div = document.createElement('div');
				err_div.setAttribute('class', 'frm-error-messages');
				err_div.setAttribute('className', 'frm-error-messages'); // IE6/7
				err_div.innerHTML = response[i];
				err.innerHTML = '';
				err.appendChild(err_div);
				err.style.display = '';
			}
			
			// replace the submit button
			var sub_btn = getEle(form_id + '_submit_button');
			sub_btn.disabled = false;
			sub_btn.setAttribute("value", d3forms_submit_buttons[form_id]);
		}
	}	
}

function submit_d3forms_ajax(form_id, callback_func) {
	var form = getEle(form_id);
	if (form == false) return false;
	
	// disable the submit button
	var sub_btn = getEle(form_id + '_submit_button');
	d3forms_submit_buttons[form_id] = sub_btn.getAttribute("value");
	sub_btn.disabled = true;
	sub_btn.setAttribute("value", "Submitting...");
	
	// hide the displayed error/success message and remove all "error" css from the form
	if (getEle(form_id + "_error") != false) getEle(form_id + "_error").style.display = 'none';
	if (getEle(form_id + "_success") != false) getEle(form_id + "_success").style.display = 'none';
	var labels = form.getElementsByTagName('label');
	if ((labels != false) && (labels.length > 0)) {
		for (var i=0; i<labels.length; i++) {
			var em = labels[i].getElementsByTagName('em');
			var contents;
			if (em.length > 0) {
				contents = em[0].innerHTML;
				labels[i].innerHTML = contents;
			}
		}
	}
	
	setSubField(form);
	var form_data = getFormData(form_id);
	form_data += '&d3forms_ajax_submit=yes&html_form_id='+encodeURIComponent(form_id);
	
	var ajax_url = form.getAttribute("action");
	if (typeof(ajax_url) == 'object') {
		// apparently, when you have a field named "action", IE6/7 don't realize that we don't want the field
		// so, we need to get this attribute the hard way =[
		var action_field = form.action;
		var i = 0;
		for (i=0; i<form.elements.length; i++) if (form.elements[i] == action_field) break;
		form.removeChild(action_field);
		ajax_url = form.getAttribute("action");
		if (form.elements[i] != null) form.insertBefore(action_field, form.elements[i]);
		else form.appendChild(action_field);
	}
	var ajax = new ajaxObject(ajax_url, callback_func);
	ajax.update(form_data, 'POST');
}