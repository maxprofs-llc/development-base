<!--
var cookie="popupmaster";
function popup(filename){
	if (getcookie(cookie)=="" && filename){
		var centerWidth=(screen.width/2)-("+screen.width+"/2);
		var centerHeight=(screen.height/2)-("+screen.height+"/2);
		var popup = window.open(filename, "","height="+screen.height+",width="+screen.width+",top="+centerHeight+",left="+centerWidth+",location=yes,menubar=yes,resizable=yes,scrollbars=yes,status=yes,titlebar=yes,toolbar=yes,directories=yes");
		self.focus();
		setcookie();
		}
	}
	

function getcookie(cookieName) {
	var id = cookieName + "=";
	var cookievalue = "";
	if (document.cookie.length > 0) {
		offset = document.cookie.indexOf(id);
		if (offset != -1) {
			cookievalue = "x";
			}
		}
	return cookievalue;
	}

function setcookie () {
	var today = new Date();
	var expdate = new Date(today.getTime() + 1 * 24 * 60 * 60 * 1000);
	document.cookie = cookie
	+ "="
	+ escape ("done")+ ";expires=" + expdate.toGMTString();

	}

function popuphelp(filename){
	var centerWidth=(screen.width/2)-(548/2);
	var centerHeight=(screen.height/2)-(410/2);
	window.open(filename, "","height=410,width=548,top="+centerHeight+",left="+centerWidth+",location=no,menubar=no,resizable=yes,scrollbars=no,status=no,titlebar=no,toolbar=no,directories=no");
	}

function changeObjectVisibility(objectId, newVisibility) {
    // first get the object's stylesheet
    var styleObject = getStyleObject(objectId);

    // then if we find a stylesheet, set its visibility
    // as requested
    //
    if (styleObject) {
	styleObject.visibility = newVisibility;
	return true;
    } else {
	return false;
    }
}

function checkWholeForm(theForm) {
    var why = "";
    if (theForm.calculator.value == "bac") {
     	why += checkWeight(theForm.weight.value);
    	why += checkSEX(theForm.sex.value);
    	why += checkDropdown(theForm.type.value, "Enter the type of drinks you had.\n");
    	why += checkDrinks(theForm.number.value);
    	why += checkTime(theForm.time.value);
    }
    if (theForm.calculator.value == "bfc") {
    	why += checkSEX(theForm.sex.value);
    	why += checkWaist(theForm.abd2.value, "narrow waist");
    	why += checkWeight(theForm.weight.value);
    }
    if (theForm.calculator.value == "bfn" ) {
     	why += checkHeight(theForm.height.value);
    	why += checkSEX(theForm.sex.value);
    	why += checkWaist(theForm.abd1.value, "narrow waist");
    	why += checkWaist(theForm.abd2.value, "naval waist");
    	why += checkHip(theForm.hip.value);
    	why += checkNeck(theForm.neck.value);
    }
    if (theForm.calculator.value == "bfb") {
     	why += checkHeight(theForm.height.value);
    	why += checkSEX(theForm.sex.value);
    	why += checkWaist(theForm.abd1.value, "narrow waist");
    	why += checkWaist(theForm.abd2.value, "naval waist");
    	why += checkHip(theForm.hip.value);
    	why += checkNeck(theForm.neck.value);
    	why += checkWeight(theForm.weight.value);
    }
    if (theForm.calculator.value == "bmi") {
     	why += checkHeight(theForm.height.value);
    	why += checkWeight(theForm.weight.value);
    }
    if (theForm.calculator.value == "lop" ) {
    	why += checkAge18(theForm.age.value);
    	why += checkWeight(theForm.weight.value);
    }
    if (theForm.calculator.value == "cbc"  ) {
    	why += checkWeight(theForm.weight.value);
    }
    if (theForm.calculator.value == "dee") {
    	why += checkSEX(theForm.sex.value);
    	why += checkAge18(theForm.age.value);
     	why += checkHeight(theForm.height.value);
    	why += checkWeight(theForm.weight.value);
    }
    if (theForm.calculator.value == "due") {
     	why += checkDateDue(theForm.month.value, theForm.day.value, theForm.year.value );
    }
    if (theForm.calculator.value == "ova") {
     	why += checkDateOva(theForm.month.value, theForm.day.value, theForm.year.value );
     	why += checkCycle(theForm.days_in_cycle.value);
    }
    if (theForm.calculator.value == "fsz") {
    	why += checkSEX(theForm.sex.value);
     	why += checkHeight(theForm.height.value);
    	why += checkFrame(theForm.elbow.value,theForm.wrist.value);
    }
    if (theForm.calculator.value == "iwc") {
    	why += checkSEX(theForm.sex.value);
     	why += checkHeight(theForm.height.value);
    }
    if (theForm.calculator.value == "lbm") {
    	why += checkSEX(theForm.sex.value);
     	why += checkHeight(theForm.height.value);
    	why += checkWeight(theForm.weight.value);
    }
    if (theForm.calculator.value == "thr") {
    	why += checkAge18(theForm.age.value);
    }
    if (theForm.calculator.value == "smc") {
    	why += isValue(theForm.cigarettesperday.value, "Enter the number of cigarettes smoked each day.\n");
    	why += isValue(theForm.cigarettesperpack.value, "Enter the number of cigarettes in each pack.\n");
    	why += checkRange(theForm.cigarettesperday.value, 1,90, 0, "The number of cigarettes smoked each day must be 1 or more.\n", 'cigarettes' );
    	why += checkRange(theForm.cigarettesperpack.value, 1,90, 0, "The number of cigarettes in each pack.\n", 'cigarettes');
    	why += checkCigPrice(theForm.priceperpack.value, .2,90, 0,  "The price per pack.\n", 'price');
    }
    if (theForm.calculator.value == "whr") {
    	why += checkSEX(theForm.sex.value);
    	why += checkWaist(theForm.waist.value, "naval waist");
    	why += checkHip(theForm.hip.value);
    }
    if (why != "") {
       alert(why);
       return false;
    }
return true;
}

function checkWeight(weight) {
    var error = "";
    if (weight == "") {
        error = "You did not enter your weight.\n";
    }
    num = parseInt(weight);
    if (num < 50 || num > 700) {
    	error = "The weight must be between 50 and 700 for this calculation.\n";
    }
    return error;
}

function checkHeight(height) {
    var error = "";
    if (height == "" || height == "0") {
        error = "You did not enter your height.\n";
    }
    num = parseInt(height);
    if (num < 55 || num > 89) {
    	error = "The height must be between 55 and 89 inches for this calculation.\n";
    }
    return error;
}

function checkDrinks(drinks) {
    var error = "";
    if (drinks == "" || drinks == "0") {
        error = "You did not enter how many drinks.\n";
    }
    num = parseInt(drinks);
    if (num < 1 || num > 20) {
    	error = "The drinks entered is unreasonable for this calculation.\n";
    }
    return error;
}

function checkTime(time) {
    var error = "";
    if (time == "" || time == "0") {
        error = "You did not enter a period of time.\n";
    }
    num = parseInt(time);
    if (num <= .2 || num > 10) {
    	error = "The time must be between .2 and 10 hours for this calculation.\n";
    }
    return error;
}

function checkCigPrice(price) {
    var error = "";
    if (price == "" || price == "0" || price == "." || price == "0.00" || price == "0.0" || price == "0." || price == ".00") {
        error = price;
        error += " - Enter the price per pack.\n";
    }
    num = niceNum(price);
    if (num == "" || num == "0" || num == "." || num == "0.00" || num == "0.0" || num == "0." || num == ".00") {
        error = num;
        error += " - Enter the price per pack.\n";
    }
    if (num <= .2 || num > 90) {
    	error = "The price per pack must be between .2 and 90 for this calculation.\n";
    }
    return error;
}

function checkAge(age) {
    var error = "";
    if (age == "") {
        error = "You did not enter your age.\n";
    }
    num = parseInt(age);
    if (num < 13 || num > 105) {
    	error = "The age must be between 13 and 105 for this calculation.\n";
    }
    return error;
}

function checkAge18(age) {
    var error = "";
    if (age == "") {
        error = "You did not enter your age.\n";
    }
    num = parseInt(age);
    if (num < 18 || num > 95) {
    	error = "The age must be between 18 and 95 for this calculation.\n";
    }
    return error;
}

function checkFrame(elbow, wrist) {
    var error = "";
    if ((wrist == "0") && (elbow == "0")){
        error = "You did not enter your wrist or elbow size.\n";
    }
    return error;
}

function checkHip(hip) {
    var error = "";
    if (hip == "" ) {
        error = "You did not enter your hip measurement.\n";
    }
    num = parseInt(hip);
    if (num < 10 || num > 96){
    	error = "The hip measurement should be between 10 and 96.\n";
    }
    return error;
}

function checkCycle(Cycle) {
    var error = "";
    if (Cycle == "" ) {
        error = "You did not enter the number of days in your cycle.\n";
    }
    num = parseInt(Cycle);
    if (num < 10 || num > 35){
    	error = "The number of days should be between 10 and 35.\n";
    }
    return error;
}

function checkDateDue( mon , day , year ) {
    var error = "";
    if (mon == "" || day == "" || year == "") {
        error = "You did not enter all the date information.\n";
    }
    num1 = niceNumInt(mon);
    if (num1 < 1 || num1 > 12){
    	error = "The month should be between 1 and 12.\n";
    	error += num1;
    	error += " - ";
    	error += mon;
    }
    num = niceNumInt(day);
    if (num < 1 || num > 31){
    	error = "The days should be between 1 and 31.\n";
    }
    return error;
}

function checkDateOva(mon, day, year) {
    var error = "";
    if (mon == "" || day == "" || year == "") {
        error = "You did not enter all the date information.\n";
    }
    num = niceNumInt(mon);
    if (num < 1 || num > 12){
    	error = "The month should be between 1 and 12.\n";
    }
    num = niceNumInt(day);
    if (num < 1 || num > 31){
    	error = "The days should be between 1 and 31.\n";
    }
    num = niceNumInt(year);
    var d = new Date();
    var curr_year = d.getFullYear();
    curr_year = curr_year + 1;
    if (num < 2000 || num > curr_year){
    	error = "The year you entered is not reasonable.\n";
    }
    return error;
}

function checkNeck(neck) {
    var error = "";
    if (neck == "" ) {
        error = "You did not enter your neck measurement.\n";
    }
    num = parseInt(neck);
    if (num < 4 || num > 36){
    	error = "The neck measurement should be between 4 and 36.\n";
    }
    return error;
}


function checkWaist(waist, desc1) {
    var error = "";
    if (waist == "" ) {
        error = "You did not enter your ";
        error += desc1;
        error += " value.\n";
    }
    num = parseInt(waist);
    if (num < 10 || num > 96){
    	error = "The ";
        error += desc1;
    	error += " must be between 10 and 96.\n";
    }
    return error;
}
// Sex

function checkSEX(sex) {
var error = "";
if (sex == ""){
   error = "You did not enter your gender.\n";
	}
    if ((sex != "Male") && (sex != "Female")){
       error = "You did not enter your gender.\n";
    }
return error;
}       

// non-empty textbox

function isValue(strng, msg) {
var error = "";
  if (strng.length == 0 ) {
     error = msg;
  }
    num = parseInt(strng);
    if (num <= 0 ){
    	error = msg;
    }
return error;	  
}

function checkRange(entered, min, max, zero, msg, fldname) {
    var error = "";
    if (entered == "" && zero != '1') {
        error = "You did not enter your " + fldname + ".\n";
    }
    num = niceNum(entered);
    if (num < min || num > max) {
    	error += msg;
    }
    return error;
}

// non-empty textbox

function isEmpty(strng, msg) {
var error = "";
  if (strng.length == 0) {
     error = msg;
  }
return error;	  
}

// was textbox altered

function isDifferent(strng) {
var error = ""; 
  if (strng != "Can\'t touch this!") {
     error = "You altered the inviolate text area.\n";
  }
return error;
}

// exactly one radio button is chosen

function checkRadio(checkvalue, msg) {
var error = "";
   if (!(checkvalue)) {
       error = msg;
    }
return error;
}

// valid selector from dropdown list

function checkDropdown(choice,msg) {
var error = "";
    if (choice == "") {
    error = msg;
    }    
return error;
}    

function niceNumTxt(textNumIn){
///////THIS FUNCTION RETURNS A TEXT NUMBER WITHOUT COMMAS, ETC.
//Initialipe function vars;
textInMessy=""+textNumIn;
textOutNice="";
digits="01234567890";
foundDigit=0;
foundDecimal=0;
//Only read digits PLUS... minus sign or single decimal point;
for (p=0;p<textInMessy.length;p++){
//Accept any digit.
if(digits.indexOf(textInMessy.substring(p,p+1)) != -1){
textOutNice+=textInMessy.substring(p,p+1);
foundDigit=1;
};
//Accept a minus sign if nothing else found so far:
if(textInMessy.substring(p,p+1) == "\-" && foundDigit==0 ){
textOutNice+=textInMessy.substring(p,p+1);
foundDigit=1;
};
//Accept a decimal point if none found so far:
if(textInMessy.substring(p,p+1) == "\." && foundDecimal==0 ){
textOutNice+=textInMessy.substring(p,p+1);
foundDecimal=1;
};
};
//If no digits at all then use zero.
if (textOutNice ==""){textOutNice="0"};
//Exit function always with nice TEXT
return textOutNice;
};

function niceNum(textNumIn){
////THIS FUNCTION ALWAYS RETURNS A NUMBER
//Exit function always with a valid numeric float
var mynum = num_validate(textNumIn);
return parseFloat(niceNumTxt(mynum));
};

function num_validate(field) {
var valid = "0123456789.-"
var ok = "yes";
var temp;
for (var i=0; i<field.length; i++) {
	temp = "" + field.substring(i, i+1);
	if (valid.indexOf(temp) == "-1") ok = "no";
}
if (ok == "no") {
	return("0");
   }
   	return(field);
}
function niceNumInt(textNumIn){
////THIS FUNCTION ALWAYS RETURNS A NUMBER
//Exit function always with a valid numeric float
var mynum = num_validateInt(textNumIn);
return niceNumTxt(mynum);
};

function num_validateInt(field) {
var valid = "0123456789"
var ok = "yes";
var temp;
for (var i=0; i<field.length; i++) {
	temp = "" + field.substring(i, i+1);
	if (valid.indexOf(temp) == "-1") ok = "no";
}
if (ok == "no") {
	return("0");
   }
   	return(field);
}

//-->