<!--

// ajax functions to lookup existing user id
function requestUserLookup() {
	var sId = document.getElementById("db_id").value;
	top.frames["hiddenFrame"].location = "/GetUserID.php?id=" + sId;
}

// ajax functions to lookup existing user nickname
function requestNickNameLookup() {
	var sId = document.getElementById("db_id").value;
	top.frames["hiddenFrame"].location = "/GetUserNN.php?id=" + sId;
}

// ajax functions to lookup existing user nickname
function requestSSNLookup() {
	var sId = document.getElementById("auth_ssn4").value;
	top.frames["hiddenFrame"].location = "http://lvh.healthstatus.com/GetUserSNN.php?id=" + sId;
}

function displaySSNLookup(sText) {
	var divSSNLookup = document.getElementById("divSSNLookup");
	divSSNLookup.innerHTML = sText;
}
function displayUserLookup(sText) {
	var divUserLookup = document.getElementById("divUserLookup");
	divUserLookup.innerHTML = sText;
}
// ajax functions to lookup the zipcode
function requestZipLookup() {
	var sLoc = document.getElementById("country").value;
	if(sLoc == "US"){
		var sId = document.getElementById("auth_postal_code").value;
		top.frames["hiddenFrame"].location = "/GetZipCode.php?id=" + sId;
		}
	else { return ""; }
}

function displayZipLookup(sText) {
	var divZipLookup = document.getElementById("divZipLookup");
	divZipLookup.innerHTML = sText;
}
// ajax end



function checkRegForm(theForm) {
    var why = "";
    why += checkRegnum(theForm.db_employer.value);
    why += checkName(theForm.db_fullname.value);
    why += checkEmail(theForm.db_email.value);
    why += checkUsername(theForm.db_id.value);
    why += checkPassword(theForm.auth_password.value,theForm.auth_password_entry.value);
    why += isEmptyString(theForm.siteid.value, "You do not have a valid site ID, check with your administrator.\n");
    if (why != "") {
       alert(why);
       return false;
    }
return true;
}

function checkRegFormCMOG(theForm) {
    var why = "";
    why += checkRegnum(theForm.db_employer.value);
    why += checkName(theForm.db_fullname.value);
    why += checkEmail(theForm.db_email.value);
    why += checkUsername(theForm.db_id.value);
    why += checkPassword(theForm.auth_password.value,theForm.auth_password_entry.value);
    why += isEmptyString(theForm.siteid.value, "You do not have a valid site ID, check with your administrator.\n");
    why += checkSelect(theForm.db_relation.value, "You did not enter your status as employee or household member of employee.\n");
    why += checkSelect(theForm.client1.value, "You did not indicate whether you want to be asked questions about your family history.\n");
    if (why != "") {
       alert(why);
       return false;
    }
return true;
}

function checkLoginForm(theForm) {
    var why = "";
    why += checkUsername(theForm.db_id.value);
    why += checkPassword_in(theForm.auth_password_entry.value);
    if (why != "") {
       alert(why);
       return false;
    }
return true;
}
function checkEmail (strng) {
var error="";
if (strng == "") {
   error = "You didn't enter an email address.\n";
}

    var emailFilter=/^.+@.+\..{2,3}$/;
    if (!(emailFilter.test(strng))) { 
       error = "Please enter a valid email address.\n";
    }
    else {
//test email for illegal characters
       var illegalChars= /[\(\)\<\>\,\;\:\\\"\[\]]/
         if (strng.match(illegalChars)) {
          error = "The email address contains illegal characters.\n";
       }
    }
return error;    
}


// phone number - strip out delimiters and check for 10 digits if they enter something

function checkPhone (strng) {
var error = "";
if (!(strng == "")) {

	var stripped = strng.replace(/[\(\)\.\-\ ]/g, ''); //strip out acceptable non-numeric characters
    if (isNaN(parseInt(stripped))) {
       error = "The phone number contains illegal characters.";
  
    }
    if (!(stripped.length == 10)) {
	error = "The phone number is the wrong length. Make sure you included an area code.\n";
    }
}
return error;
}


// password - between 6 chars min, uppercase, lowercase, and numeral

function checkPassword (strng,strng1) {
var error = "";
if (strng == "") {
   error = "You didn't enter a password.\n";
}

    var illegalChars = /[\W_]/; // allow only letters and numbers
    
    if ((strng.length < 6) || (strng.length > 24)) {
       error = "The password must be at least 6 characters long and less than 25.\n";
    }
    else if (illegalChars.test(strng)) {
      error = "The password contains illegal characters.\n";
    }
    if (!(strng==strng1)) {
    	error += "The two passwords you entered, don't match.\n";
    }
return error;    
}    


function checkPassword_in (strng) {
var error = "";
if (strng == "") {
   error = "You didn't enter a password.\n";
}

    var illegalChars = /\W/; // allow only letters and numbers
    
    if ((strng.length < 6) || (strng.length > 24)) {
       error = "The password must be at least 6 characters long and less than 25.\n";
    }
    else if (illegalChars.test(strng)) {
      error = "The password contains illegal characters.\n";
    }
return error;    
}    


// username - 6 chars min, uc, lc, and underscore only.

function checkUsername (strng) {
	var error = "";
	if (strng == "") {
		error = "You didn't enter a username.\n";
		return error;
		}
	var illegalChars = /\w/; // allow letters, numbers, and underscores
	if ((strng.length < 6) || (strng.length > 12)) {
		error = "The username must be at least 6 characters long and less than 25.\n";
		}
return error;
}       

// username - 6 chars min, uc, lc, and underscore only.

function checkRegnum (strng) {
	var error = "";
	if (strng == "") {
		error = "You didn't enter a registration number.\n";
		return error;
		}
	var stripped = strng.replace(/[\(\)\.\-\ ]/g, '');
	//strip out acceptable non-numeric characters
	if (isNaN(parseInt(stripped))) {
   		error = "The registration code contains illegal characters.";
	}
	if ((strng.length < 6) || (strng.length > 24)) {
		error = "The registration code must be at least 6 characters long and less than 25.\n";
		}
return error;
}       


// name - 2 chars min.

function checkName (strng) {
var error = "";
if (strng == "") {
   error = "You didn't enter your complete name.\n";
}


    var illegalChars = /\w/; // allow letters, numbers, and underscores
    if ((strng.length < 2) ) {
       error = "Your name is longer than that.\n";
    }
return error;
}       

// Sex

function checkSEX (strng) {
var error = "";
if (strng == "") {
   error = "You didn't enter your gender.\n";
}

    if (!(strng == "Male") && !(strng == "Female") ) {
       error = "You did not enter your gender.\n";
    }
return error;
}       



// ZIP 5 or 9 numeric.

function checkZIP (strng,country) {
var error = "";
if (strng == "") {
   error = "You didn't enter a zip code.\n";
}
if (country == "US"){
	var stripped = strng.replace(/[\(\)\.\-\ ]/g, '');
	//strip out acceptable non-numeric characters
	if (isNaN(parseInt(stripped))) {
   		error = "The zip code contains illegal characters.";
	}
    if (!(strng.length == 5) && !(strng.length == 9) ) {
       error += "Your zip code is the wrong length.\n";
    }
}
return error;
}       


function isEmptyString(strng,msg) {
var error = "";
  if (strng.length == 0) {
     error = msg;
  }
return error;	  
}

// non-empty textbox

function isEmpty(strng) {
var error = "";
  if (strng.length == 0) {
     error = "The mandatory text area has not been filled in.\n"
  }
return error;	  
}

function checkSelect(choice,msg) {
var error = "";
    if (choice == 0 || choice.length == 0) {
    error = msg;
    }    
return error;
}    
// valid selector from age dropdown list

function checkDropdown(choice) {
var error = "";
    if (choice == 0) {
    error = "You didn't choose an option from the age drop-down list.\n";
    }    
return error;
}    
-->