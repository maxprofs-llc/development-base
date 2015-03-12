/*
AjaxObject
----------
Below I have created an example of the usage of the AjaxObject.  It begins by setting up an object, defining its callback function/actions, and also
defining a function that will change the page associated with the object and load the new data.  All of the data for this example is being loaded into
a div onto the page, but you can easily change the way that all of this works.

var my_div = new String('my_div');					// div id to load data into
my_page_object = new ajaxObject('my_page.php'); 	// setup the ajax object

my_page_object.callback = function(response_data) {	// setup the callback function/actions to perform when the object's page has loaded
	// do some actions
	// example: (this will place the contents of the loaded page into the div)
	document.getElementById(my_div).innerHTML = response_data;
}

function display_page(what_page, query_string) {	// function that will change the url of the object
	// this will display a loading message inside of the div as a placeholder
	document.getElementById(my_div).innerHTML = "<div style=\"margin-top: 10px; text-align: center; width: 100%;\">loading...</div>";

	my_page_object.change_url(what_page);			// change the url
	if (typeof(query_string) != 'undefined')
		my_page_object.update(query_string); 		// pass the query string to the object
}

// make the first call to load the object!
my_page_object.update();
*/
function ajaxObject(url, callbackFunction) {
	var that = this;      
	this.updating = false;
	
	this.change_url = function(new_url) {
		this.abort();
		urlCall = new_url;
	}
	
	this.abort = function() {
		if (that.updating) {
			that.updating = false;
			that.AJAX.abort();
			that.AJAX = null;
		}
	}
	
	this.update = function(passData, postMethod) { 
		if (that.updating)
			return false;

		that.AJAX = null;                          
		if (window.XMLHttpRequest)
			that.AJAX = new XMLHttpRequest();              
		else
			that.AJAX = new ActiveXObject("Microsoft.XMLHTTP");

		if (that.AJAX == null)
			return false;                               
		else {
			that.AJAX.onreadystatechange = function() {  
				if (that.AJAX.readyState == 4) {             
					that.updating = false;                
					that.callback(that.AJAX.responseText, that.AJAX.status, that.AJAX.responseXML);        
					that.AJAX = null;                                         
				}                                                      
			}     
			that.updating = new Date();                              
			if (/post/i.test(postMethod)) {
				var uri = urlCall + '?' + that.updating.getTime();
				that.AJAX.open("POST", uri, true);
				that.AJAX.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
				that.AJAX.setRequestHeader("Content-Length", passData.length);
				that.AJAX.send(passData);
			} else {
				var uri = urlCall + '?' + passData + '&timestamp=' + (that.updating.getTime()); 
				that.AJAX.open("GET", uri, true);                             
				that.AJAX.send(null);                                         
			}   
			
			return true;                                             
		}                                                                           
	}
	
	var urlCall = url;        
	this.callback = callbackFunction || function () { };
}