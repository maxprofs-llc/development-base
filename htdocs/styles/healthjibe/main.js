//=====================================================================
//  USE THIS FILE FOR YOUR MAIN JS FUNTIONS. 
//
//  This could include pop up windows, any google javascript, etc. 
//=====================================================================
// DOM Helper functions
function getEle(id) { var ele = document.getElementById(id); if (ele == 'undefined' || ele == null) return false; else return ele; }
function getEleName(name) { var ele = document.getElementsByName(name); if (ele == 'undefined' || ele == null) return false; else return ele; }
function getVal(id) { if (ele = getEle(id)) return getEle(id).value; return false; }
function getEleVal(id) { if (ele = getEle(id)) return getEle(id).value; return false; }
function getSelVal(id) { if (ele = getEle(id))	return ele[ele.selectedIndex].value; return false; }
function hideEle(id) {var ele = getEle(id); if (ele) ele.style.display = 'none';}
function showEle(id) {var ele = getEle(id); if (ele) ele.style.display = '';}
function getRadVal(name) { if (ele = getEleName(name)) { for (i = 0; i < ele.length; i++) { if (ele[i].checked == true) { return ele[i].value; alert(ele[i].value); } } } return ''; }
function getFrmEle(form_id, ele_name) {
	var form = getEle(form_id);
	if (form == false) return false;
	var inputs = Array('input','select','textarea');
	for (var i=0; i < inputs.length; i++) {
		eles = form.getElementsByTagName(inputs[i]);
		for (var p=0; p < eles.length; p++) { if (eles[p].name == ele_name) return eles[p]; }
	}
}
function hideEles(eles) { for (i=0; i < eles.length; i++) hideEle(eles[i]); }
function setFrmEle(form_id, ele_name, val) {
	var frmEle = getFrmEle(form_id, ele_name);
	if (frmEle == false) return false;
	switch (frmEle.tagName.toLowerCase()) {
		case 'input':
			switch (frmEle.getAttribute("type")) {
				case 'checkbox' || 'radio':
					frmEle.checked = true;
					break;
				default:
					frmEle.value = val;
			}
			break;
		case 'select':
			for (s = 0; s < frmEle.length; s++) {
				if (frmEle[s].value == val) frmEle[s].selected = true;
			}
			break;
		case 'textarea':
			frmEle.value = val;
			break;
	}
}

function clearSelect(which_select) {
	// clear the specified select box's contents
	var selectBox = document.getElementById(which_select);
	for (i=selectBox.length-1; i>=0; i--) {
		selectBox.remove(i);
	}
}

function populateSelect(sel_id,values,add_select,sel_val) {
	var form_elem	= document.getElementById(sel_id);
	var start_idx=0;
	if (add_select == true) {
		sel_option = new Option('-select-', '');
		form_elem.options[0] = sel_option;
		start_idx=1;
	}
	
	for (i=0; i < values.length; i++) {
		var vals = values[i].split('|');
		var selected = (vals[0] == sel_val) ? true : false;
		opt = new Option(vals[1], vals[0], selected);
		form_elem.options[i+start_idx] = opt;
	}	
}

function submitForm(which) {
	which.submitted.value = 'yes';
	which.submit();
}

function isArray(testObject) {   
    return testObject && !(testObject.propertyIsEnumerable('length')) && typeof testObject === 'object' && typeof testObject.length === 'number';
}

function trim(str) {
	return str.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}

function popUp(url,width,height,scrollbars,resizable,querystring,windowname) {
	/*
	Ultimate Pop Up Script
	Simple Example <a href="javascript:void(0);" onclick="popUp('test.php')">Pop Up</a>
	Normal Example <a href="javascript:void(0);" onclick="popUp('test.php','200','300')">Test</a>
	Full Example   <a href="javascript:void(0);" onclick="popUp('test.php','200','300', 0, 1,'?cid=1', 'popup1')">Test 2</a>
	
	To use default just use null in t place of the variable
	  IE: <a href="javascript:void(0);" onclick="popUp('test.php','200','300', null, null,'?cid=1', 'popup1')">Test 2</a>
	  This uses the default variable for scrollbars and resizable
	*/ 
	if(typeof width == "undefined" || width == null)	var width	= 500;
	if(typeof height == "undefined" || height == null)	var height	= 400;
	
	if(typeof scrollbars == "undefined" || scrollbars == null)		var scrollbars	= 0;
	if(typeof resizable == "undefined" || resizable == null)		var resizable	= 0;
	if(typeof querystring == "undefined" || querystring == null)	var querystring	= '';
	if(typeof windowname == "windowname" || windowname == null)		var windowname	= 'popup';
	
	var full_url = url + querystring;

	var w;
	w = window.open(full_url, windowname, "width="+width+",height="+height+",toolbar=0,location=0,directories=0,status=0,menubar=0,scrollbars="+scrollbars+",resizable="+resizable);
	w.focus();
}

function swapListingImage(whichImage, image_div, image_resizer, width) {
	if (whichImage != '') {
		if(typeof image_resizer == "undefined" || width == null)	var image_resizer	= 'img.php';
		if(typeof width == "undefined" || width == null)			var width			= 200;
		
		document.getElementById(image_div).src = '/app/helpers/'+image_resizer+'?w='+width+'&constrain&img='+whichImage;
	}
}

function bookmarkSite(page_url, page_title) {
	/*
	Ultimate Bookmark/Add-to-Favorites Script
	Browsers Compatible: IE5+ Win, IE5 Mac, FF (Win/*nix), Netscape 6+, Opera 7+, Safari, Konqueror 3, iCab 3
	*/
	var user_agent	= navigator.userAgent.toLowerCase();
	var isKonq		= (user_agent.indexOf('konqueror') != -1);
	var isSafari	= (user_agent.indexOf('webkit') != -1);
	var isMac		= (user_agent.indexOf('mac') != -1);
	var buttonStr	= isMac ? 'Command/Cmd' : 'CTRL';

	if(window.external && (!document.createTextNode || (typeof(window.external.AddFavorite) == 'unknown'))) {
		// IE5+ Win
		window.external.AddFavorite(page_url, page_title);
	} else if (window.sidebar) {
		// FF Win
		window.sidebar.addPanel(page_title, page_url, "");
	} else if(isKonq) {
		// Konquerer
		alert('You need to press CTRL + B to bookmark our site.');
	} else if(window.opera) {
		// Opera (doesn't support bookmarking
		void(0);
	} else if(window.home || isSafari) {
		// FF *nix, Netscape, Safari, iCab
		alert('You need to press '+buttonStr+' + D to bookmark our site.');
	} else if(!window.print || isMac) {
		// IE Mac and Safari 1.0
		alert('You need to press Command/Cmd + D to bookmark our site.');    
	} else {
		alert('In order to bookmark this site you need to do so manually through your browser.');
	}
}

function uTimeout() {
	/*
	Ultimate Timeout Script
	--creating the timeout object--
	var myTimeout = new uTimeout()
	--standard--
	myTimeout.init(myFunction, 1000); // dont use the '()' on the function name..
	--repeating--
	myTimeout.init(myFunction, 1000, 3); // will repeat 3 times
	--passing arguments--
	myTimeout.init(myFunction, 1000, null, 'foo', 'bar', 1.6); // will call myFunction('foo', 'bar', 1.6)
	--cancelling the timeout--
	myTimeout.cancel();
	*/
    var _func				= null;		// function to call when the timeout expires
    var _timeout			= null;		// timeout length (milliseconds)
    var _repeat				= 0;		// number of times to repeat the function
    var _args				= [];		// array of arguments to pass to the function
    var _timeoutRunning		= false;	// flag to see if timeout is already running
    var _cancelled			= false;	// flag to see if timeout has been cancelled
	var _timeoutNum			= null;		// holder for the timeout
	
    this.init = function(func, timeout, repeat) {
        var i;
        
		if (_timeoutRunning || !func || !timeout)
			return false; // timeout exists, no function specified, or no timeout specified
        
        _func				= func;
        _timeout			= timeout;
        _timeoutRunning	= true;
        _cancelled			= false;
        _repeat				= repeat ? repeat : 0;
        
        _args				= [];
        for (i=3; i<arguments.length; i++) {
			// build the argument list
            _args[_args.length] = arguments[i];
        }
		
		// set the timeout!!
        _timeoutNum = setTimeout(_exec, _timeout);
    }

    this.cancel = function() {
		// cancel the timeout
		clearTimeout(_timeoutNum);
        _cancelled			= true;
        _timeoutRunning		= false;
        _repeat				= 0;
    }
    
    function _exec() {
        _timeoutRunning = false;
        if (_cancelled)
			return; // timeout was cancelled
			
        _func.apply(null, _args);
        
        if (_repeat > 0) {
			// the timeout is to be repeated!
            _repeat--;
            _timeoutNum = setTimeout(_exec, _timeout);
        }
    }
}

function isValidEmail(str) {
	var at="@"
	var dot="."
	var lat=str.indexOf(at)
	var lstr=str.length
	var ldot=str.indexOf(dot)
	if (str.indexOf(at)==-1) return false;
	if (str.indexOf(at)==-1 || str.indexOf(at)==0 || str.indexOf(at)==lstr)  return false;
	if (str.indexOf(dot)==-1 || str.indexOf(dot)==0 || str.indexOf(dot)==lstr) return false;
	if (str.indexOf(at,(lat+1))!=-1) return false;
	if (str.substring(lat-1,lat)==dot || str.substring(lat+1,lat+2)==dot) return false;
	if (str.indexOf(dot,(lat+2))==-1) return false;
	if (str.indexOf(" ")!=-1) return false;
	return true;
}

function toggleDivSimple(id) {
	ele = getEle(id);
	ele.style.display = (ele.style.display == 'none') ? '' : 'none';
}

function toggleDiv(anchorId, contentId, anchorShowContents, anchorHideContents) {
	if (document.getElementById(contentId).style.display == '') {
		document.getElementById(contentId).style.display = 'none';
		document.getElementById(anchorId).innerHTML = anchorShowContents;
	} else {
		document.getElementById(contentId).style.display = '';
		document.getElementById(anchorId).innerHTML = anchorHideContents;
	}
}

function getPageSize(returnWhat) {
	var xScroll, yScroll;
		
	if (window.innerHeight && window.scrollMaxY) {	
		xScroll = window.innerWidth + window.scrollMaxX;
		yScroll = window.innerHeight + window.scrollMaxY;
	} else if (document.body.scrollHeight > document.body.offsetHeight){ // all but Explorer Mac
		xScroll = document.body.scrollWidth;
		yScroll = document.body.scrollHeight;
	} else { // Explorer Mac...would also work in Explorer 6 Strict, Mozilla and Safari
		xScroll = document.body.offsetWidth;
		yScroll = document.body.offsetHeight;
	}
		
	var windowWidth, windowHeight;
		
	if (self.innerHeight) {	// all except Explorer
		if(document.documentElement.clientWidth){
			windowWidth = document.documentElement.clientWidth; 
		} else {
			windowWidth = self.innerWidth;
		}
		windowHeight = self.innerHeight;
	} else if (document.documentElement && document.documentElement.clientHeight) { // Explorer 6 Strict Mode
		windowWidth = document.documentElement.clientWidth;
		windowHeight = document.documentElement.clientHeight;
	} else if (document.body) { // other Explorers
		windowWidth = document.body.clientWidth;
		windowHeight = document.body.clientHeight;
	}	
	
	// for small pages with total height less then height of the viewport
	if(yScroll < windowHeight){
		pageHeight = windowHeight;
	} else { 
		pageHeight = yScroll;
	}

	// for small pages with total width less then width of the viewport
	if(xScroll < windowWidth){	
		pageWidth = xScroll;		
	} else {
		pageWidth = windowWidth;
	}
	
	if (returnWhat == 'width') {
		return pageWidth;
	} else if (returnWhat == 'height') {
		return pageHeight;
	} else {
		return [pageWidth,pageHeight];
	}
}

// onkeyup="isNumber(this)"
function isNumber(field) {
	var re = /^[0-9-'.'-']*$/;
	if (!re.test(field.value)) {
		field.value = field.value.replace(/[^0-9-'.'-']/g,"");
	}
}