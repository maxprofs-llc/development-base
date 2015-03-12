/*
sample submitAjaxForm call back function
var myHandler = function(responseText, responseStatus, responseXML) {
	if (responseStatus==200) {
		getEle('result').innerHTML=responseText;
	}	
}

sample form
<form name="frmForm" id="frmForm" action="/ajaxtest/post.php" method="post" enctype="application/x-www-form-urlencoded">
	<input type="button" name="subButton" value="Submit" onclick="submitAjaxForm('frmForm',myHandler)" />
</form>
*/
function submitAjaxForm(form_id,callback_func) {
	var form = getEle(form_id);
	if (form == false) return false;
	setSubField(form);
	var form_data = getFormData(form_id);
	var ajax_url = form.getAttribute("action");
	var ajax_method = form.getAttribute("method");

	var ajax = new ajaxObject(ajax_url, callback_func);

	if (ajax_method.toLowerCase() == 'post') {
		ajax.update(form_data, 'POST');
	} else {
		ajax.update(form_data);
	}
}

function setSubField(form_ele) {
	form_inputs = form_ele.getElementsByTagName('input');
	for (var e=0; e < form_inputs.length; e++) { if (form_inputs[e].getAttribute('name') == 'submitted') form_inputs[e].value='yes'; }
}

function getFormData(form_id) {
	var form = getEle(form_id);
	if (form == false) return false;
	
	var inputs = Array('input','select','textarea');
	var form_inputs; var post_string = '';
	
	for (var i=0; i < inputs.length; i++) {
		form_inputs = form.getElementsByTagName(inputs[i]);
		for (var p=0; p < form_inputs.length; p++) {
			switch (inputs[i]) {
				case 'input':
					switch (form_inputs[p].getAttribute("type")) {
						case 'checkbox':
						case 'radio':
							if (form_inputs[p].checked == true) {
								post_string = addToPostString(post_string, form_inputs[p].getAttribute('name'), form_inputs[p].value);
							}
							break;
						default:
							post_string = addToPostString(post_string, form_inputs[p].getAttribute('name'), form_inputs[p].value);
					}
					break;
				case 'select':
					if (form_inputs[p].getAttribute('multiple') == 'multiple') {
						for (s = 0; s < form_inputs[p].length; s++) {
							if (form_inputs[p][s].selected == true) {
								post_string = addToPostString(post_string, form_inputs[p].getAttribute('name'), form_inputs[p][s].value);
							}
						}
					} else {
						post_string = addToPostString(post_string, form_inputs[p].getAttribute('name'), form_inputs[p][form_inputs[p].selectedIndex].value);
					}
					break;
				case 'textarea':
					post_string = addToPostString(post_string, form_inputs[p].getAttribute('name'), form_inputs[p].value);
					break;
			}
		}
	}
	return post_string;
}

function addToPostString(post_string, add_name, add_value) {
	post_string += (post_string != '') ? "&" : "";
	post_string += add_name + '=' + encodeURIComponent(add_value);
	return post_string;
}

function addOptionsToSelect(select_id, opt_val, opt_text) {
	var option = document.createElement('option');
	option.setAttribute('value', opt_val);
	option.appendChild(document.createTextNode(opt_text));
	getEle(select_id).appendChild(option);
}

function selectRemoveOptions(id) {
	var dd = getEle(id);	
	for (i=dd.getElementsByTagName("option").length; i > 0; i--) {
		dd.removeChild( dd.getElementsByTagName("option")[i-1] );
	}

}