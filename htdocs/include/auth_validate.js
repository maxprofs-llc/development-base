function checkWholeForm(theForm) {
    var why = "";
    why += checkUsername(theForm.db_id.value);
    why += checkPassword(theForm.auth_password.value,theForm.auth_password_entry.value);
    why += checkName(theForm.db_fullname.value);
    why += checkEmail(theForm.db_email.value);
    why += checkZIP(theForm.auth_postal_code.value,theForm.country.value);
    if (why != "") {
       alert(why);
       return false;
    }
return true;
}

// ajax functions to lookup existing user id
function requestUserLookup() {
	var sId = document.getElementById("db_id").value;
	top.frames["hiddenFrame"].location = "GetUserID.php?id=" + sId;
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
		top.frames["hiddenFrame"].location = "GetZipCode.php?id=" + sId;
		}
	else { return ""; }
}

function displayZipLookup(sText) {
	var divZipLookup = document.getElementById("divZipLookup");
	divZipLookup.innerHTML = sText;
}
// ajax end

function displayEmail() {
	var sText = "";
	var myEmail = document.getElementById("db_email").value;
	sText = checkEmail(myEmail);
	var imgTxt = "<img src=/images/global/green_check.gif border=0>";
        if(sText != ""){ imgTxt = "<img src=/images/global/red_x.gif border=0>&nbsp;<span class=bodytextboldRedCC0000>";
        		 imgTxt += sText;
        		 imgTxt += "</span>";
			document.getElementById("db_email").focus();
			document.getElementById("db_email").select();
			}
	var divEmailCheck = document.getElementById("divEmailCheck");
	divEmailCheck.innerHTML = imgTxt;
}

function checkEmail(strng) {
var error="";
	if (strng == "") {
	   error = "You didn't enter an email address.\n";
	}
	else {
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
    
    if ((strng.length < 6) || (strng.length > 12)) {
       error = "The password must be at least 6 characters long and less than 12.\n";
    }
    else if (illegalChars.test(strng)) {
      error = "The password contains illegal characters.\n";
    }
    if (!(strng==strng1)) {
    	error += "The two passwords you entered, don't match.\n";
    }
return error;    
}    

function checkPasswordEach (strng) {
var error = "";
if (strng == "") {
   error = "You didn't enter a password.\n";
}

    var illegalChars = /[\W_]/; // allow only letters and numbers
    
    if ((strng.length < 6) || (strng.length > 12)) {
       error = "The password must be at least 6 characters long and less than 12.\n";
    }
    else if (illegalChars.test(strng)) {
      error = "The password contains illegal characters.\n";
    }
return error;    
}    


function displayPassword(which) {
	var myName;
	var sText;
	if(which == 1) { myPass = document.getElementById("auth_password_entry").value; 
			 var myPass1 = document.getElementById("auth_password").value; 
			 sText = checkPassword(myPass, myPass1);}
	else { myPass = document.getElementById("auth_password").value; 
		sText = checkPasswordEach(myPass);}
	var imgTxt = "<img src=/images/global/green_check.gif border=0>";
        if(sText != ""){ imgTxt = "<img src=/images/global/red_x.gif border=0>&nbsp;<span class=bodytextboldRedCC0000>";
        		 imgTxt += sText;
        		 imgTxt += "</span>";}
        if(which == 1) {
		var divNameCheck = document.getElementById("divPassword1Check");
		divPassword1Check.innerHTML = imgTxt;
		}
	else	{
		var divPassLookup = document.getElementById("divPasswordCheck");
		divPasswordCheck.innerHTML = imgTxt;
		}
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
		error = "The username must be at least 6 characters long and less than 12.\n";
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

function displayName() {
	var myName = document.getElementById("db_fullname").value;
	var sText = checkName(myName);
	var imgTxt = "<img src=/images/global/green_check.gif border=0>";
        if(sText != ""){ imgTxt = "<img src=/images/global/red_x.gif border=0>&nbsp;<span class=bodytextboldRedCC0000>";
        		 imgTxt += sText;
        		 imgTxt += "</span>";}
	var divNameCheck = document.getElementById("divNameCheck");
	divNameCheck.innerHTML = imgTxt;
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


// non-empty textbox

function isEmpty(strng) {
var error = "";
  if (strng.length == 0) {
     error = "The mandatory text area has not been filled in.\n"
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
