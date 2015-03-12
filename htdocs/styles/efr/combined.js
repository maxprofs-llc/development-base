/*common.js*/
function Trim(str) {
    if (str != null && str != '') {
        var whitespace = ' \n\r\t\f\x0b\xa0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u200b\u2028\u2029\u3000';
        for (var i = 0; i < str.length; i++) {
            if (whitespace.indexOf(str.charAt(i)) === -1) {
                str = str.substring(i);
                break;
            }
        }
        for (i = str.length - 1; i >= 0; i--) {
            if (whitespace.indexOf(str.charAt(i)) === -1) {
                str = str.substring(0, i + 1);
                break;
            }
        }
        return whitespace.indexOf(str.charAt(0)) === -1 ? str : '';
    }
    else {
        return '';
    }
}


/*
==================================================================
ClearSummary(summaryvalidator) : Clears the DIV tag containing the error messages.
==================================================================
*/

function ClearSummary(summaryvalidator) {
    summaryvalidator.style.display = 'none';
    summaryvalidator.innerHTML = '';
}
//==============================================================
//******function for validate date in a multiple textbox******//
//==============================================================

function single_textbox_date_validation(textbox1) {
    //Checking leap year validation
    var mystring = new String(textbox1.value)
    m = mystring.indexOf("/", 0)
    if (parseInt(m) == -1) {
        m = mystring.indexOf("-", 0)
    }
    mm = mystring.slice(0, m)

    d = mystring.indexOf("/", m + 1)
    if (parseInt(d) == -1) {
        d = mystring.indexOf("-", m + 1)
    }
    dd = mystring.slice(m + 1, d)

    yyyy = mystring.slice(d + 1, mystring.length)
    if ((isNaN(mm)) || (mm.length > 2) || parseInt(mm) > 12 || mm < 1) {
        alert("Invalid month");
        return false;
    }

    if ((isNaN(dd)) || (dd.length > 2) || parseInt(dd) > 31 || dd < 1) {
        alert("Invalid day");
        return false;
    }

    if ((isNaN(yyyy)) || (yyyy.length > 4)) {
        alert("Invalid year");
        //textbox1.focus();
        return false;
    }

    var monthInt = +(parseInt(mm))
    if (monthInt == 4) {
        var month = "April"
    }
    if (monthInt == 6) {
        var month = "June"
    }
    if (monthInt == 9) {
        var month = "September"
    }
    if (monthInt == 11) {
        var month = "November"
    }
    if ((parseInt(yyyy) % 400 == 0) || (!((parseInt(yyyy) % 100 == 0) && (parseInt(yyyy) % 4 == 0)) && (parseInt(yyyy) % 4 == 0))) {
        //Leap Year
        if ((parseInt(mm) == 2) && (parseInt(dd) > 29)) //februry
        {
            alert("Day of Februry month in a leap year should not be greater than 29")
            textbox1.focus();
            return false;
        }
    }
    else {
        //Simple Year
        if ((parseInt(mm) == 2) && (parseInt(dd) > 28)) //februry
        {
            alert("Day of Februry month in a simple year should not be greater than 28")
            textbox1.focus();
            return false;
        }

    }
    if (((parseInt(mm) == 4) || (parseInt(mm) == 6) || (parseInt(mm) == 9) || (parseInt(mm) == 11)) && (parseInt(dd) > 30)) {	  //month=april		      month=June         month=September	  month=November				
        alert("In " + month + " month day should not be greater than 30")
        textbox1.focus();
        return false;
    }

    return true;
}


/*
=========================================
SPECIAL CHARACTER VALIDATION IN STRINGS
=========================================
*/

function check_special_char(obj, nam) {
    var iChars = "!@#$%^&*()+=-[]\\\';,./{}|\":<>?";

    for (var i = 0; i < obj.value.length; i++) {
        if (iChars.indexOf(obj.value.charAt(i)) != -1) {
            alert(nam + " has special characters. \nThese are not allowed.\n Please remove them and try again.");
            return false;
        }
    }
    return true;
}

function CheckSpecialChars(obj, nam, blankAllowed) {
    var iChars = new String();
    iChars = Trim(obj);
    var charArray = new Array(';', '\'', '\\', '--', '/*', '*/', 'xp_', '%', '<', '>', '&', '&quot;', '&lt;', '&gt;', '[', ']', ':');

    if (!blankAllowed) {
        if (iChars.toString().length == 0) {
            alert(nam + " can not be blank.\n Please try again.");
            return false;
        }
    }
    for (var i = 0; i < charArray.length; i++) {
        if (iChars.toString().indexOf(charArray[i], 0) != -1) {
            alert(nam + " has special characters. \nThese are not allowed.\n Please remove them and try again.");
            return false;
        }
    }
    return true;
}


/*
============================================
SPECIAL CHARACTER VALIDATION IN FLOAT VALUES
============================================
*/

function check_special_numeric(obj, nam) {
    var iChars = "!@#$%^&*()+=-[]\\\';,/{}|\":<>?";

    for (var i = 0; i < obj.value.length; i++) {
        if (iChars.indexOf(obj.value.charAt(i)) != -1) {
            alert(nam + " has special characters. \nThese are not allowed.\n Please remove them and try again.");
            return false;
        }
    }
    return true;
}

/*
============================================
SPECIAL CHARACTER VALIDATION IN FLOAT VALUES
============================================
*/

function check_special(obj, nam) {
    var strValidChars = "0123456789.-";
    var strChar;
    var blnResult = true;

    if (obj.length == 0) return false;

    for (i = 0; i < obj.length && blnResult == true; i++) {
        strChar = obj.charAt(i);
        if (strValidChars.indexOf(strChar) == -1) {
            blnResult = false;
        }
    }
    return blnResult;
}

/*
============================================
SPECIAL CHARACTER VALIDATION IN DATE VALUE
============================================
*/

function check_special_date(obj, nam) {
    var flag = 1;
    var iChars = "!@#$%^&*()+=-[]\';,.{}|\":<>?";

    for (var i = 0; i < obj.value.length; i++) {
        if (iChars.indexOf(obj.value.charAt(i)) != -1) {
            alert(nam + " has special characters. \nThese are not allowed.\n Please remove them and try again.");
            flag = 0;
            return false;
        }

    }
    return true;
}

/*==================================
DATE VALIDATION IN SINGLE TEXT BOX
====================================*/

function check_date(obj, nam) {
    var er = true;
    er = check_special_date(obj, nam);
    if (er == false)
        return false;
    if (obj.value.length > 0) {
        var dtCh = "/";
        var minYear = 1990;
        var maxYear = 9999;

        function isInteger(s) {
            var i;
            for (i = 0; i < s.length; i++) {
                // Check that current character is number.
                var c = s.charAt(i);
                if (((c < "0") || (c > "9"))) return false;
            }
            // All characters are numbers.
            return true;
        }

        function stripCharsInBag(s, bag) {
            var i;
            var returnString = "";
            // Search through string's characters one by one.
            // If character is not in bag, append to returnString.
            for (i = 0; i < s.length; i++) {
                var c = s.charAt(i);
                if (bag.indexOf(c) == -1) returnString += c;
            }
            return returnString;
        }

        function daysInFebruary(year) {
            // February has 29 days in any year evenly divisible by four,
            // EXCEPT for centurial years which are not also divisible by 400.
            return (((year % 4 == 0) && ((!(year % 100 == 0)) || (year % 400 == 0))) ? 29 : 28);
        }
        function DaysArray(n) {
            for (var i = 1; i <= n; i++) {
                this[i] = 31
                if (i == 4 || i == 6 || i == 9 || i == 11) { this[i] = 30 }
                if (i == 2) { this[i] = 29 }
            }
            return this
        }

        function isDate(dtStr) {
            var daysInMonth = DaysArray(12)
            var pos1 = dtStr.indexOf(dtCh)
            var pos2 = dtStr.indexOf(dtCh, pos1 + 1)
            var strMonth = dtStr.substring(0, pos1)
            var strDay = dtStr.substring(pos1 + 1, pos2)
            var strYear = dtStr.substring(pos2 + 1)
            strYr = strYear
            if (strDay.charAt(0) == "0" && strDay.length > 1) strDay = strDay.substring(1)
            if (strMonth.charAt(0) == "0" && strMonth.length > 1) strMonth = strMonth.substring(1)
            for (var i = 1; i <= 3; i++) {
                if (strYr.charAt(0) == "0" && strYr.length > 1) strYr = strYr.substring(1)
            }
            month = parseInt(strMonth)
            day = parseInt(strDay)
            year = parseInt(strYr)
            if (pos1 == -1 || pos2 == -1) {
                alert("The date format should be : mm/dd/yyyy")
                return false
            }
            if (strMonth.length < 1 || month < 1 || month > 12) {
                alert("Please enter a valid month")
                return false
            }
            if (strDay.length < 1 || day < 1 || day > 31 || (month == 2 && day > daysInFebruary(year)) || day > daysInMonth[month]) {
                alert("Please enter a valid day")
                return false
            }
            if (strYear.length != 4 || year == 0 || year < minYear || year > maxYear) {
                alert("Please enter a valid 4 digit year between " + minYear + " and " + maxYear)
                return false
            }
            if (dtStr.indexOf(dtCh, pos2 + 1) != -1 || isInteger(stripCharsInBag(dtStr, dtCh)) == false) {
                alert("Please enter a valid date")
                return false
            }
            return true
        }

        var dt = obj;
        if (isDate(dt.value) == false) {
            er = false
            if (er == false) {
                return er
            }
        }
    }
}
//----------**end of function for validate date in a single textbox**----------//

/* =============================
FUNCTION RETURNS TRUE OR FALSE
===============================*/

function chkErr(er, obj) {
    if (er == false)
        return (false);
    if (obj == false) {
        return (false);
    }
    else {
        return (true);
    }
}

/*===================================================
FUNCTION CHECKS FOR VALID LENGTH OF CHARACTER FIELDS
===================================================*/

function chkval(obj, val, Nam) {
    var str = Trim(obj.value);
    var er = true;
    er = check_special_char(obj, Nam);
    if (er == false)
        return false;
    if (str.length > val) {
        alert(Nam + " length should be <= " + val);
        return false;
    }
}

/*===================================================
FUNCTION CHECKS FOR VALID LENGTH OF NUMERIC FIELDS
===================================================*/

function chkval1(obj, val, Nam) {
    var str = Trim(obj.value);
    var er = true;
    er = chkNmeric(obj, Nam);
    if (er == false)
        return false;
    if (obj.value < val) {
        alert(Nam + "value should not be less then" + val);
        return false;
    }
    er = check_special_numeric(obj, Nam);
    if (er == false)
        return false;
    var str = Trim(obj.value);
    if (str.length > val) {
        alert(Nam + " length should be  " + val + "Digit");
        return false;
    }
}

/*===================================================
FUNCTION CHECKS FOR VALIDITY OF ACCOUNT NUMBER
===================================================*/

function chkacc(obj, val, nam) {
    var str = Trim(obj.value);
    if (str.length == val) {
        var st, i, flag = 1;
        for (i = 0; i < 3; i++) {
            st = str.substr(i, 1);
            if ((st >= 'A' && st <= 'Z') || (st >= 'a' && st <= 'z')) {
                flag = 1;
            }
            else {
                flag = 0;
                break;
            }
        }
        if (flag == 0) {
            alert("First 3 characters of " + nam + " should be Alphabets");
            return false;
        }
    }
    else {
        alert(nam + " length should be = " + val);
        return false;
    }
    var len;
    len = str.substr(3, 5);

    if (isNaN(len)) {
        alert("Last 5 characters of " + nam + " should be digits");
        return false;
    }
}

/*===================================================
FUNCTION CHECKS FOR VALIDITY OF NUMERIC OR NOT
===================================================*/

function chkNmeric(obj, Nam) {
    if (isNaN(obj.value)) {
        alert(Nam + " is not Numeric");
        return false;
    }
}
/*==========================================================
FUNCTION FOR EMAIL VALIDATION
==========================================================*/
function echeck(str) {

    var at = "@"
    var dot = "."
    var lat = str.indexOf(at)
    var lstr = str.length
    var ldot = str.indexOf(dot)
    if (str.indexOf(at) == -1) {
        return false
    }

    if (str.indexOf(at) == -1 || str.indexOf(at) == 0 || str.indexOf(at) == lstr) {
        return false
    }

    if (str.indexOf(dot) == -1 || str.indexOf(dot) == 0 || str.indexOf(dot) == lstr) {
        return false
    }

    if (str.indexOf(at, (lat + 1)) != -1) {
        return false
    }

    if (str.substring(lat - 1, lat) == dot || str.substring(lat + 1, lat + 2) == dot) {
        return false
    }

    if (str.indexOf(dot, (lat + 2)) == -1) {
        return false
    }

    if (str.indexOf(" ") != -1) {
        return false
    }

    return true
}

function emailCheck(emailStr) {
    var sw = true;
    var checkTLD = 0;
    var knownDomsPat = /^(com|net|org|edu|int|mil|gov|arpa|biz|aero|name|coop|info|pro|museum)$/;
    var emailPat = /^(.+)@(.+)$/;
    var specialChars = "\\(\\)><@,;:\\\\\\\"\\.\\[\\]";
    var validChars = "\[^\\s" + specialChars + "\]";
    var quotedUser = "(\"[^\"]*\")";
    var ipDomainPat = /^\[(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\]$/;
    var atom = validChars + '+';
    var word = "(" + atom + "|" + quotedUser + ")";
    var userPat = new RegExp("^" + word + "(\\." + word + ")*$");
    var domainPat = new RegExp("^" + atom + "(\\." + atom + ")*$");
    var matchArray = emailStr.match(emailPat);

    if (matchArray == null) {
        sw = false; return sw;
    }
    var user = matchArray[1];
    var domain = matchArray[2];
    for (i = 0; i < user.length; i++) {
        if (user.charCodeAt(i) > 127) {
            sw = false;
        }
    }

    for (i = 0; i < domain.length; i++) {
        if (domain.charCodeAt(i) > 127) {
            sw = false;
        }
    }

    if (user.match(userPat) == null) {
        sw = false;
    }

    var IPArray = domain.match(ipDomainPat);
    if (IPArray != null) {
        for (var i = 1; i <= 4; i++) {
            if (IPArray[i] > 255) {
                sw = false;
            }
        }
        return true;
    }

    var atomPat = new RegExp("^" + atom + "$");
    var domArr = domain.split(".");
    var len = domArr.length;
    for (i = 0; i < len; i++) {
        if (domArr[i].search(atomPat) == -1) {
            sw = false;
        }
    }

    if (checkTLD && domArr[domArr.length - 1].length != 2 && domArr[domArr.length - 1].search(knownDomsPat) == -1) {
        sw = false;
    }

    if (len < 2) {
        sw = false;
    }
    return sw;
}
function GroupCheckBoxesCountWithReturnIDs(frm, aspCheckBoxID, varLimit, ServerControl, ParentControlID) {
    var varCount = 0
    if (ServerControl) {
        re = new RegExp(aspCheckBoxID)  		//generated controlname starts with a colon
    }
    else {
        re = new RegExp(aspCheckBoxID + '_')  		//generated controlname starts with a colon
    }
    for (i = 0; i < document.forms[frm].elements.length; i++) {
        elm = document.forms[frm].elements[i]
        if (elm.type == 'checkbox') {
            if (re.test(elm.id)) {

                if (ParentControlID != null) {
                    if (elm.id.indexOf(ParentControlID) != -1) {
                        if (elm.checked) {
                            gblCheckBoxes = gblCheckBoxes + elm.id + ',';
                            gblSelectedIDs = gblSelectedIDs + elm.getAttribute("DataKeyID") + ',';
                            varCount = varCount + 1;

                        }
                    }
                }
                else {
                    if (elm.checked) {
                        gblCheckBoxes = gblCheckBoxes + elm.id + ',';
                        gblSelectedIDs = gblSelectedIDs + elm.getAttribute("DataKeyID") + ',';
                        varCount = varCount + 1;
                    }
                }
            }
        }
    }
    if (varLimit > varCount) {
        return false
    }
    return true
}
function checkUnCheckAllGroupCheckBoxes(frm, aspCheckBoxObj, aspCheckBoxID, chkVal, ServerControl, ParentControlID) {
    var re;
    if (ServerControl) {
        re = new RegExp(aspCheckBoxID)  		//generated controlname starts with a colon
    }
    else {
        re = new RegExp(aspCheckBoxID + '_')  		//generated controlname starts with a colon
    }
    for (i = 0; i < document.forms[frm].elements.length; i++) {
        elm = document.forms[frm].elements[i]
        if (elm.type == 'checkbox') {
            if ((re.test(elm.id)) && (elm.id != aspCheckBoxObj.id)) {
                if (ParentControlID != null) {
                    if (elm.id.indexOf(ParentControlID) != -1) {
                        elm.checked = chkVal;
                    }
                }
                else {
                    elm.checked = chkVal;
                }
            }
        }
    }
}

function unCheckAllGroupCheckBoxes(frm, aspCheckBoxObj, aspCheckBoxID, chkVal) {
    if (chkVal) {
        re = new RegExp(aspCheckBoxID + '_')  		//generated controlname starts with a colon
        for (i = 0; i < document.forms[frm].elements.length; i++) {
            elm = document.forms[frm].elements[i]
            if (elm.type == 'checkbox') {
                if ((re.test(elm.id)) && (elm.id != aspCheckBoxObj.id)) {
                    elm.checked = false;
                }
            }
        }
    }
}
function unCheckAllGroupCheckBoxesWithLimit(frm, aspCheckBoxObj, aspCheckBoxID, chkVal, varLimit) {
    var varCount = 0
    if (chkVal) {
        re = new RegExp(aspCheckBoxID + '_')  		//generated controlname starts with a colon
        for (i = 0; i < document.forms[frm].elements.length; i++) {
            elm = document.forms[frm].elements[i]
            if (elm.type == 'checkbox') {
                if (re.test(elm.id)) {
                    if (elm.checked)
                        varCount = varCount + 1;
                }
            }
        }
        if (varCount > varLimit) {
            aspCheckBoxObj.checked = false;
            alert("Can not select more than " + varLimit + " options !")
        }
    }
}

function GroupCheckBoxesCount(frm, aspCheckBoxID, varLimit, ParentControlID) {
    var varCount = 0
    re = new RegExp(aspCheckBoxID)  		//generated controlname starts with a colon
    for (i = 0; i < document.forms[frm].elements.length; i++) {
        elm = document.forms[frm].elements[i]
        if (elm.type == 'checkbox') {
            if (re.test(elm.id)) {
                if (ParentControlID != null) {
                    if (elm.id.indexOf(ParentControlID) != -1) {
                        if (elm.checked)
                            varCount = varCount + 1;
                    }
                }
                else {
                    if (elm.checked)
                        varCount = varCount + 1;
                }
            }
        }
    }
    if (varLimit > varCount) {
        return false
    }
    return true
}
function GroupRadioButtonCount(frm, radioButtonID, varLimit) {
    var varCount = 0
    re = new RegExp(radioButtonID + '_')  		//generated controlname starts with a colon
    for (i = 0; i < document.forms[frm].elements.length; i++) {
        elm = document.forms[frm].elements[i]
        if (elm.type == 'radio') {
            if (re.test(elm.id)) {
                if (elm.checked)
                    varCount = varCount + 1;
            }
        }
    }
    if (varLimit > varCount) {
        return false
    }
    return true
}
function deSelectID(idToDeselect, callingID) {
    if (callingID.checked) {
        var idDeselect = document.getElementById(idToDeselect);
        idDeselect.checked = false;
    }
}
function totalLimit(initialLimit, objToEvaluate) {
    var addLimitObj = eval(objToEvaluate)
    if (addLimitObj.checked)
        initialLimit = initialLimit + 1;
    return initialLimit
}

function redirect(url) {
    window.location.href = url;
    return false;
}

function MM_openBrWindow(theURL, winName, features) {
    window.open(theURL, winName, features);
    return false;
}
function catchEnterKey(e, btnId) {
    if (!e) var e = window.event;
    if (e.which || e.keyCode) {
        if ((e.which == 13) || (e.keyCode == 13)) {
            e.cancelBubble = true;
            if (e.stopPropagation) e.stopPropagation();
            document.getElementById(btnId).click();
            return false;
        }
    }
    else {
        return true;
    }
}
function num1(e) {
    var evt = e;
    if (evt.keyCode < 48 || evt.keyCode > 57) evt.returnValue = false;
}

function ValidateDate(mid, did, yid) {
    var bmonth = 0;
    var bday = 0;
    var byear = 0;
    if (mid.value != "")
        bmonth = mid.value;
    if (did.value != "")
        bday = did.value;
    if (yid.value != "")
        byear = yid.value;
    if (bmonth == 0 || bday == 0 || byear == 0)
        return true;
    else {
        var dt = new Date(byear, bmonth - 1, bday);
        if (bmonth == dt.getMonth() + 1)
            return true;
        else
            return false;
    }
}

function SuppressIllegalCharactersFromPost(e, s, sk) {
    if (!e) var e = window.event;
    if (e.which || e.keyCode) {
        // < > 
        if (e.which == 60 || e.keyCode == 60 || e.which == 62 || e.keyCode == 62) {
            return false;
        } else if (/&#[0-9]{1,5};/g.test(s)) {
            return false;
        } else if (/&[A-Z]{2,6};/gi.test(s)) {
            return false;
        } else if (!sk && /\'/g.test(s)) {
            return false;
        } else if (!sk && /\"/g.test(s)) {
            return false;
        } else if (/</g.test(s)) {
            return false;
        } else if (/>/g.test(s)) {
            return false;
        } else { return true; }
    }
    else {
        return true;
    }
}
function RemoveIllegalCharactersFromPost(obj, sk) {
    var s = obj.value;
    s = s.replace(/&#[0-9]{1,5};/g, "");
    s = s.replace(/&[A-Z]{2,6};/gi, "");
    if (!sk) {
        s = s.replace(/\'/g, ""); //no HTML equivalent as &apos is not cross browser supported
        s = s.replace(/\"/g, "");
    }
    s = s.replace(/</g, "");
    s = s.replace(/>/g, "");
    obj.value = s;
}
/*
Encoder
*/
Encoder = {

    // When encoding do we convert characters into html or numerical entities
    EncodeType: "entity",  // entity OR numerical

    isEmpty: function(val) {
        if (val) {
            return ((val === null) || val.length == 0 || /^\s+$/.test(val));
        } else {
            return true;
        }
    },
    // Convert HTML entities into numerical entities
    HTML2Numerical: function(s) {
        var arr1 = new Array('&nbsp;', '&iexcl;', '&cent;', '&pound;', '&curren;', '&yen;', '&brvbar;', '&sect;', '&uml;', '&copy;', '&ordf;', '&laquo;', '&not;', '&shy;', '&reg;', '&macr;', '&deg;', '&plusmn;', '&sup2;', '&sup3;', '&acute;', '&micro;', '&para;', '&middot;', '&cedil;', '&sup1;', '&ordm;', '&raquo;', '&frac14;', '&frac12;', '&frac34;', '&iquest;', '&agrave;', '&aacute;', '&acirc;', '&atilde;', '&Auml;', '&aring;', '&aelig;', '&ccedil;', '&egrave;', '&eacute;', '&ecirc;', '&euml;', '&igrave;', '&iacute;', '&icirc;', '&iuml;', '&eth;', '&ntilde;', '&ograve;', '&oacute;', '&ocirc;', '&otilde;', '&Ouml;', '&times;', '&oslash;', '&ugrave;', '&uacute;', '&ucirc;', '&Uuml;', '&yacute;', '&thorn;', '&szlig;', '&agrave;', '&aacute;', '&acirc;', '&atilde;', '&auml;', '&aring;', '&aelig;', '&ccedil;', '&egrave;', '&eacute;', '&ecirc;', '&euml;', '&igrave;', '&iacute;', '&icirc;', '&iuml;', '&eth;', '&ntilde;', '&ograve;', '&oacute;', '&ocirc;', '&otilde;', '&ouml;', '&divide;', '&Oslash;', '&ugrave;', '&uacute;', '&ucirc;', '&uuml;', '&yacute;', '&thorn;', '&yuml;', '&quot;', '&amp;', '&lt;', '&gt;', '&oelig;', '&oelig;', '&scaron;', '&scaron;', '&yuml;', '&circ;', '&tilde;', '&ensp;', '&emsp;', '&thinsp;', '&zwnj;', '&zwj;', '&lrm;', '&rlm;', '&ndash;', '&mdash;', '&lsquo;', '&rsquo;', '&sbquo;', '&ldquo;', '&rdquo;', '&bdquo;', '&dagger;', '&dagger;', '&permil;', '&lsaquo;', '&rsaquo;', '&euro;', '&fnof;', '&alpha;', '&beta;', '&gamma;', '&delta;', '&epsilon;', '&zeta;', '&eta;', '&theta;', '&iota;', '&kappa;', '&lambda;', '&mu;', '&nu;', '&xi;', '&omicron;', '&pi;', '&rho;', '&sigma;', '&tau;', '&upsilon;', '&phi;', '&chi;', '&psi;', '&omega;', '&alpha;', '&beta;', '&gamma;', '&delta;', '&epsilon;', '&zeta;', '&eta;', '&theta;', '&iota;', '&kappa;', '&lambda;', '&mu;', '&nu;', '&xi;', '&omicron;', '&pi;', '&rho;', '&sigmaf;', '&sigma;', '&tau;', '&upsilon;', '&phi;', '&chi;', '&psi;', '&omega;', '&thetasym;', '&upsih;', '&piv;', '&bull;', '&hellip;', '&prime;', '&prime;', '&oline;', '&frasl;', '&weierp;', '&image;', '&real;', '&trade;', '&alefsym;', '&larr;', '&uarr;', '&rarr;', '&darr;', '&harr;', '&crarr;', '&larr;', '&uarr;', '&rarr;', '&darr;', '&harr;', '&forall;', '&part;', '&exist;', '&empty;', '&nabla;', '&isin;', '&notin;', '&ni;', '&prod;', '&sum;', '&minus;', '&lowast;', '&radic;', '&prop;', '&infin;', '&ang;', '&and;', '&or;', '&cap;', '&cup;', '&int;', '&there4;', '&sim;', '&cong;', '&asymp;', '&ne;', '&equiv;', '&le;', '&ge;', '&sub;', '&sup;', '&nsub;', '&sube;', '&supe;', '&oplus;', '&otimes;', '&perp;', '&sdot;', '&lceil;', '&rceil;', '&lfloor;', '&rfloor;', '&lang;', '&rang;', '&loz;', '&spades;', '&clubs;', '&hearts;', '&diams;');
        var arr2 = new Array('&#160;', '&#161;', '&#162;', '&#163;', '&#164;', '&#165;', '&#166;', '&#167;', '&#168;', '&#169;', '&#170;', '&#171;', '&#172;', '&#173;', '&#174;', '&#175;', '&#176;', '&#177;', '&#178;', '&#179;', '&#180;', '&#181;', '&#182;', '&#183;', '&#184;', '&#185;', '&#186;', '&#187;', '&#188;', '&#189;', '&#190;', '&#191;', '&#192;', '&#193;', '&#194;', '&#195;', '&#196;', '&#197;', '&#198;', '&#199;', '&#200;', '&#201;', '&#202;', '&#203;', '&#204;', '&#205;', '&#206;', '&#207;', '&#208;', '&#209;', '&#210;', '&#211;', '&#212;', '&#213;', '&#214;', '&#215;', '&#216;', '&#217;', '&#218;', '&#219;', '&#220;', '&#221;', '&#222;', '&#223;', '&#224;', '&#225;', '&#226;', '&#227;', '&#228;', '&#229;', '&#230;', '&#231;', '&#232;', '&#233;', '&#234;', '&#235;', '&#236;', '&#237;', '&#238;', '&#239;', '&#240;', '&#241;', '&#242;', '&#243;', '&#244;', '&#245;', '&#246;', '&#247;', '&#248;', '&#249;', '&#250;', '&#251;', '&#252;', '&#253;', '&#254;', '&#255;', '&#34;', '&#38;', '&#60;', '&#62;', '&#338;', '&#339;', '&#352;', '&#353;', '&#376;', '&#710;', '&#732;', '&#8194;', '&#8195;', '&#8201;', '&#8204;', '&#8205;', '&#8206;', '&#8207;', '&#8211;', '&#8212;', '&#8216;', '&#8217;', '&#8218;', '&#8220;', '&#8221;', '&#8222;', '&#8224;', '&#8225;', '&#8240;', '&#8249;', '&#8250;', '&#8364;', '&#402;', '&#913;', '&#914;', '&#915;', '&#916;', '&#917;', '&#918;', '&#919;', '&#920;', '&#921;', '&#922;', '&#923;', '&#924;', '&#925;', '&#926;', '&#927;', '&#928;', '&#929;', '&#931;', '&#932;', '&#933;', '&#934;', '&#935;', '&#936;', '&#937;', '&#945;', '&#946;', '&#947;', '&#948;', '&#949;', '&#950;', '&#951;', '&#952;', '&#953;', '&#954;', '&#955;', '&#956;', '&#957;', '&#958;', '&#959;', '&#960;', '&#961;', '&#962;', '&#963;', '&#964;', '&#965;', '&#966;', '&#967;', '&#968;', '&#969;', '&#977;', '&#978;', '&#982;', '&#8226;', '&#8230;', '&#8242;', '&#8243;', '&#8254;', '&#8260;', '&#8472;', '&#8465;', '&#8476;', '&#8482;', '&#8501;', '&#8592;', '&#8593;', '&#8594;', '&#8595;', '&#8596;', '&#8629;', '&#8656;', '&#8657;', '&#8658;', '&#8659;', '&#8660;', '&#8704;', '&#8706;', '&#8707;', '&#8709;', '&#8711;', '&#8712;', '&#8713;', '&#8715;', '&#8719;', '&#8721;', '&#8722;', '&#8727;', '&#8730;', '&#8733;', '&#8734;', '&#8736;', '&#8743;', '&#8744;', '&#8745;', '&#8746;', '&#8747;', '&#8756;', '&#8764;', '&#8773;', '&#8776;', '&#8800;', '&#8801;', '&#8804;', '&#8805;', '&#8834;', '&#8835;', '&#8836;', '&#8838;', '&#8839;', '&#8853;', '&#8855;', '&#8869;', '&#8901;', '&#8968;', '&#8969;', '&#8970;', '&#8971;', '&#9001;', '&#9002;', '&#9674;', '&#9824;', '&#9827;', '&#9829;', '&#9830;');
        return this.swapArrayVals(s, arr1, arr2);
    },

    // Convert Numerical entities into HTML entities
    NumericalToHTML: function(s) {
        var arr1 = new Array('&#160;', '&#161;', '&#162;', '&#163;', '&#164;', '&#165;', '&#166;', '&#167;', '&#168;', '&#169;', '&#170;', '&#171;', '&#172;', '&#173;', '&#174;', '&#175;', '&#176;', '&#177;', '&#178;', '&#179;', '&#180;', '&#181;', '&#182;', '&#183;', '&#184;', '&#185;', '&#186;', '&#187;', '&#188;', '&#189;', '&#190;', '&#191;', '&#192;', '&#193;', '&#194;', '&#195;', '&#196;', '&#197;', '&#198;', '&#199;', '&#200;', '&#201;', '&#202;', '&#203;', '&#204;', '&#205;', '&#206;', '&#207;', '&#208;', '&#209;', '&#210;', '&#211;', '&#212;', '&#213;', '&#214;', '&#215;', '&#216;', '&#217;', '&#218;', '&#219;', '&#220;', '&#221;', '&#222;', '&#223;', '&#224;', '&#225;', '&#226;', '&#227;', '&#228;', '&#229;', '&#230;', '&#231;', '&#232;', '&#233;', '&#234;', '&#235;', '&#236;', '&#237;', '&#238;', '&#239;', '&#240;', '&#241;', '&#242;', '&#243;', '&#244;', '&#245;', '&#246;', '&#247;', '&#248;', '&#249;', '&#250;', '&#251;', '&#252;', '&#253;', '&#254;', '&#255;', '&#34;', '&#38;', '&#60;', '&#62;', '&#338;', '&#339;', '&#352;', '&#353;', '&#376;', '&#710;', '&#732;', '&#8194;', '&#8195;', '&#8201;', '&#8204;', '&#8205;', '&#8206;', '&#8207;', '&#8211;', '&#8212;', '&#8216;', '&#8217;', '&#8218;', '&#8220;', '&#8221;', '&#8222;', '&#8224;', '&#8225;', '&#8240;', '&#8249;', '&#8250;', '&#8364;', '&#402;', '&#913;', '&#914;', '&#915;', '&#916;', '&#917;', '&#918;', '&#919;', '&#920;', '&#921;', '&#922;', '&#923;', '&#924;', '&#925;', '&#926;', '&#927;', '&#928;', '&#929;', '&#931;', '&#932;', '&#933;', '&#934;', '&#935;', '&#936;', '&#937;', '&#945;', '&#946;', '&#947;', '&#948;', '&#949;', '&#950;', '&#951;', '&#952;', '&#953;', '&#954;', '&#955;', '&#956;', '&#957;', '&#958;', '&#959;', '&#960;', '&#961;', '&#962;', '&#963;', '&#964;', '&#965;', '&#966;', '&#967;', '&#968;', '&#969;', '&#977;', '&#978;', '&#982;', '&#8226;', '&#8230;', '&#8242;', '&#8243;', '&#8254;', '&#8260;', '&#8472;', '&#8465;', '&#8476;', '&#8482;', '&#8501;', '&#8592;', '&#8593;', '&#8594;', '&#8595;', '&#8596;', '&#8629;', '&#8656;', '&#8657;', '&#8658;', '&#8659;', '&#8660;', '&#8704;', '&#8706;', '&#8707;', '&#8709;', '&#8711;', '&#8712;', '&#8713;', '&#8715;', '&#8719;', '&#8721;', '&#8722;', '&#8727;', '&#8730;', '&#8733;', '&#8734;', '&#8736;', '&#8743;', '&#8744;', '&#8745;', '&#8746;', '&#8747;', '&#8756;', '&#8764;', '&#8773;', '&#8776;', '&#8800;', '&#8801;', '&#8804;', '&#8805;', '&#8834;', '&#8835;', '&#8836;', '&#8838;', '&#8839;', '&#8853;', '&#8855;', '&#8869;', '&#8901;', '&#8968;', '&#8969;', '&#8970;', '&#8971;', '&#9001;', '&#9002;', '&#9674;', '&#9824;', '&#9827;', '&#9829;', '&#9830;');
        var arr2 = new Array('&nbsp;', '&iexcl;', '&cent;', '&pound;', '&curren;', '&yen;', '&brvbar;', '&sect;', '&uml;', '&copy;', '&ordf;', '&laquo;', '&not;', '&shy;', '&reg;', '&macr;', '&deg;', '&plusmn;', '&sup2;', '&sup3;', '&acute;', '&micro;', '&para;', '&middot;', '&cedil;', '&sup1;', '&ordm;', '&raquo;', '&frac14;', '&frac12;', '&frac34;', '&iquest;', '&agrave;', '&aacute;', '&acirc;', '&atilde;', '&Auml;', '&aring;', '&aelig;', '&ccedil;', '&egrave;', '&eacute;', '&ecirc;', '&euml;', '&igrave;', '&iacute;', '&icirc;', '&iuml;', '&eth;', '&ntilde;', '&ograve;', '&oacute;', '&ocirc;', '&otilde;', '&Ouml;', '&times;', '&oslash;', '&ugrave;', '&uacute;', '&ucirc;', '&Uuml;', '&yacute;', '&thorn;', '&szlig;', '&agrave;', '&aacute;', '&acirc;', '&atilde;', '&auml;', '&aring;', '&aelig;', '&ccedil;', '&egrave;', '&eacute;', '&ecirc;', '&euml;', '&igrave;', '&iacute;', '&icirc;', '&iuml;', '&eth;', '&ntilde;', '&ograve;', '&oacute;', '&ocirc;', '&otilde;', '&ouml;', '&divide;', '&Oslash;', '&ugrave;', '&uacute;', '&ucirc;', '&uuml;', '&yacute;', '&thorn;', '&yuml;', '&quot;', '&amp;', '&lt;', '&gt;', '&oelig;', '&oelig;', '&scaron;', '&scaron;', '&yuml;', '&circ;', '&tilde;', '&ensp;', '&emsp;', '&thinsp;', '&zwnj;', '&zwj;', '&lrm;', '&rlm;', '&ndash;', '&mdash;', '&lsquo;', '&rsquo;', '&sbquo;', '&ldquo;', '&rdquo;', '&bdquo;', '&dagger;', '&dagger;', '&permil;', '&lsaquo;', '&rsaquo;', '&euro;', '&fnof;', '&alpha;', '&beta;', '&gamma;', '&delta;', '&epsilon;', '&zeta;', '&eta;', '&theta;', '&iota;', '&kappa;', '&lambda;', '&mu;', '&nu;', '&xi;', '&omicron;', '&pi;', '&rho;', '&sigma;', '&tau;', '&upsilon;', '&phi;', '&chi;', '&psi;', '&omega;', '&alpha;', '&beta;', '&gamma;', '&delta;', '&epsilon;', '&zeta;', '&eta;', '&theta;', '&iota;', '&kappa;', '&lambda;', '&mu;', '&nu;', '&xi;', '&omicron;', '&pi;', '&rho;', '&sigmaf;', '&sigma;', '&tau;', '&upsilon;', '&phi;', '&chi;', '&psi;', '&omega;', '&thetasym;', '&upsih;', '&piv;', '&bull;', '&hellip;', '&prime;', '&prime;', '&oline;', '&frasl;', '&weierp;', '&image;', '&real;', '&trade;', '&alefsym;', '&larr;', '&uarr;', '&rarr;', '&darr;', '&harr;', '&crarr;', '&larr;', '&uarr;', '&rarr;', '&darr;', '&harr;', '&forall;', '&part;', '&exist;', '&empty;', '&nabla;', '&isin;', '&notin;', '&ni;', '&prod;', '&sum;', '&minus;', '&lowast;', '&radic;', '&prop;', '&infin;', '&ang;', '&and;', '&or;', '&cap;', '&cup;', '&int;', '&there4;', '&sim;', '&cong;', '&asymp;', '&ne;', '&equiv;', '&le;', '&ge;', '&sub;', '&sup;', '&nsub;', '&sube;', '&supe;', '&oplus;', '&otimes;', '&perp;', '&sdot;', '&lceil;', '&rceil;', '&lfloor;', '&rfloor;', '&lang;', '&rang;', '&loz;', '&spades;', '&clubs;', '&hearts;', '&diams;');
        return this.swapArrayVals(s, arr1, arr2);
    },


    // Numerically encodes all unicode characters
    numEncode: function(s) {

        if (this.isEmpty(s)) return "";

        var e = "";
        for (var i = 0; i < s.length; i++) {
            var c = s.charAt(i);
            if (c < " " || c > "~") {
                c = "&#" + c.charCodeAt() + ";";
            }
            e += c;
        }
        return e;
    },

    // HTML Decode numerical and HTML entities back to original values
    htmlDecode: function(s) {

        var c, m, d = s;

        if (this.isEmpty(d)) return "";

        // convert HTML entites back to numerical entites first
        d = this.HTML2Numerical(d);

        // look for numerical entities &#34;
        arr = d.match(/&#[0-9]{1,5};/g);

        // if no matches found in string then skip
        if (arr != null) {
            for (var x = 0; x < arr.length; x++) {
                m = arr[x];
                c = m.substring(2, m.length - 1); //get numeric part which is refernce to unicode character
                // if its a valid number we can decode
                if (c >= -32768 && c <= 65535) {
                    // decode every single match within string
                    d = d.replace(m, String.fromCharCode(c));
                } else {
                    d = d.replace(m, ""); //invalid so replace with nada
                }
            }
        }

        return d;
    },

    // encode an input string into either numerical or HTML entities
    htmlEncode: function(s, dbl) {

        if (this.isEmpty(s)) return "";

        // do we allow double encoding? E.g will &amp; be turned into &amp;amp;
        dbl = dbl | false; //default to prevent double encoding

        // if allowing double encoding we do ampersands first
        if (dbl) {
            if (this.EncodeType == "numerical") {
                s = s.replace(/&/g, "&#38;");
            } else {
                s = s.replace(/&/g, "&amp;");
            }
        }

        // convert the xss chars to numerical entities ' " < >
        s = this.XSSEncode(s, false);

        if (this.EncodeType == "numerical" || !dbl) {
            // Now call function that will convert any HTML entities to numerical codes
            s = this.HTML2Numerical(s);
        }

        // Now encode all chars above 127 e.g unicode
        s = this.numEncode(s);

        // now we know anything that needs to be encoded has been converted to numerical entities we
        // can encode any ampersands & that are not part of encoded entities
        // to handle the fact that I need to do a negative check and handle multiple ampersands &&&
        // I am going to use a placeholder

        // if we don't want double encoded entities we ignore the & in existing entities
        if (!dbl) {
            s = s.replace(/&#/g, "##AMPHASH##");

            if (this.EncodeType == "numerical") {
                s = s.replace(/&/g, "&#38;");
            } else {
                s = s.replace(/&/g, "&amp;");
            }

            s = s.replace(/##AMPHASH##/g, "&#");
        }

        // replace any malformed entities
        s = s.replace(/&#\d*([^\d;]|$)/g, "$1");

        if (!dbl) {
            // safety check to correct any double encoded &amp;
            s = this.correctEncoding(s);
        }

        // now do we need to convert our numerical encoded string into entities
        if (this.EncodeType == "entity") {
            s = this.NumericalToHTML(s);
        }

        return s;
    },

    // Encodes the basic 4 characters used to malform HTML in XSS hacks
    XSSEncode: function(s, en) {
        if (!this.isEmpty(s)) {
            en = en || true;
            // do we convert to numerical or html entity?
            if (en) {
                s = s.replace(/\'/g, "&#39;"); //no HTML equivalent as &apos is not cross browser supported
                s = s.replace(/\"/g, "&quot;");
                s = s.replace(/</g, "&lt;");
                s = s.replace(/>/g, "&gt;");
            } else {
                s = s.replace(/\'/g, "&#39;"); //no HTML equivalent as &apos is not cross browser supported
                s = s.replace(/\"/g, "&#34;");
                s = s.replace(/</g, "&#60;");
                s = s.replace(/>/g, "&#62;");
            }
            return s;
        } else {
            return "";
        }
    },

    // returns true if a string contains html or numerical encoded entities
    hasEncoded: function(s) {
        if (/&#[0-9]{1,5};/g.test(s)) {
            return true;
        } else if (/&[A-Z]{2,6};/gi.test(s)) {
            return true;
        } else {
            return false;
        }
    },

    // will remove any unicode characters
    stripUnicode: function(s) {
        return s.replace(/[^\x20-\x7E]/g, "");

    },

    // corrects any double encoded &amp; entities e.g &amp;amp;
    correctEncoding: function(s) {
        return s.replace(/(&amp;)(amp;)+/, "$1");
    },


    // Function to loop through an array swaping each item with the value from another array e.g swap HTML entities with Numericals
    swapArrayVals: function(s, arr1, arr2) {
        if (this.isEmpty(s)) return "";
        var re;
        if (arr1 && arr2) {
            //ShowDebug("in swapArrayVals arr1.length = " + arr1.length + " arr2.length = " + arr2.length)
            // array lengths must match
            if (arr1.length == arr2.length) {
                for (var x = 0, i = arr1.length; x < i; x++) {
                    re = new RegExp(arr1[x], 'g');
                    s = s.replace(re, arr2[x]); //swap arr1 item with matching item from arr2	
                }
            }
        }
        return s;
    },

    inArray: function(item, arr) {
        for (var i = 0, x = arr.length; i < x; i++) {
            if (arr[i] === item) {
                return i;
            }
        }
        return -1;
    }

}
var is_chrome = navigator.userAgent.toLowerCase().indexOf('chrome') > -1;
var closeBrowserMessage = 'You are about to close your browser and leave this website. If you do not wish to leave this website, but just want to close the popup, click the "Cancel" button below, and then click the "Close" link located in the upper right hand corner of the popup. Otherwise to proceed with closing your browser and leaving this website, click the "Ok" button';
var closeScreenerBrowserMessage = '';

if (is_chrome)
    closeScreenerBrowserMessage = 'Are you sure you want to navigate away from this page?\n\n'
closeScreenerBrowserMessage += 'This message is appearing because you have either attempted to close your browser, hit your "back" button, or clicked on another link.'
closeScreenerBrowserMessage += ' If you proceed, you will leave this screening module and all data from the preceding pages will be lost.'
closeScreenerBrowserMessage += ' If you do not wish to lose your data, click the "' + (is_chrome ? 'Stay on this Page' : 'Cancel') + '" button below, and you will remain on this screener module.'
closeScreenerBrowserMessage += ' Otherwise to proceed with leaving this screening module, click the "' + (is_chrome ? 'Leave this Page' : 'OK') + '" button below.'
if (is_chrome)
    closeScreenerBrowserMessage += '\n\nPress "Leave this Page" to continue or "Stay on this Page" to stay on the current page.'

function setCursor(el, st, end) {
    if (el.setSelectionRange) {
        el.focus();
        el.setSelectionRange(st, end);
    }
    else {
        if (el.createTextRange) {
            range = el.createTextRange();
            range.collapse(true);
            range.moveEnd('character', end);
            range.moveStart('character', st);
            range.select();
        }
    }
}
function parseXML(data, xml, tmp) {
    if (window.DOMParser) { // Standard
        tmp = new DOMParser();
        xml = tmp.parseFromString(data, "text/xml");
    } else { // IE
        xml = new ActiveXObject("Microsoft.XMLDOM");
        xml.async = "false";
        xml.loadXML(data);
    }
    tmp = xml.documentElement;
    if (!tmp || !tmp.nodeName || tmp.nodeName === "parsererror") {
        return null;
    }
    return xml;
}
function rssTicker(key,newskeyword,force) {
    if (force || $('#rssTicker').is(':visible') || $('#rssNewsContent').html() != '') {
        var results;
        $.getJSON(('https:' == document.location.protocol ? 'https://' : 'http://') + "ajax.googleapis.com/ajax/services/search/news?v=1.0&rsz=large&key=" + key + "&q=" + encodeURIComponent(newskeyword) + "&callback=?", function(json) {
            if (json)
                results = json.responseData.results;
            var cont = $('#rssTicker');
            if (results && results.length) {
                // if specifically Show News called
                if (cont.is(':visible') || force) {
                    $('#ShowNews').hide();
                    cont.html('');

                    $('<span/>').html("View All").attr({ "class": "viewall" }).click(function() { return rssNewsContent(key, newskeyword); }).appendTo(cont);
                    var inner = $('<ul></ul>').attr({ "id": "ticker01", "class": "newsticker" }).appendTo(cont);
                    var alternate = '';
                    for (var i = 0; i < results.length; i++) {

                        var jsonItem = results[i];
                        var inner2 = $('<li/>').attr({ "id": "tickeritem" }).appendTo(inner);
                        $('<a/>').html(jsonItem.title).attr({ "href": jsonItem.unescapedUrl, "target": "_blank", "class": alternate }).appendTo(inner2);
                        if (alternate == '')
                            alternate = "alternate";
                        else
                            alternate = '';
                    }
                    cont.slideDown();
                    $("ul#ticker01").liScroll();
                    $('<span/>').html(" [x]").attr({ "class": "close" }).click(function() { var cont = $('#rssTicker'); cont.slideUp(function() { var cont = $('#rssTicker'); cont.html(''); $('#ShowNews').slideDown(); }); return false; }).appendTo(cont);
                    $('<div/>').html("powered by<a class='logo'></a>").attr({ "id": "NewsBranding" }).appendTo(cont);
                }

                var cont = $('#rssNewsContent');
                if (cont.html() != '') {
                    cont.fadeOut();
                    cont.html('');

                    $('<div class="clear"></div>').appendTo(cont);
                    $('<span></span>').html('<b>Channel: ' + newskeyword + ' </b>').attr({ "class": "txtblue", "style": "float:left;" }).appendTo(cont);
                    $('<span/>').html("close [x]").attr({ "class": "txtblue", "style": "float:right;cursor:pointer;cursor:hand;" }).click(function() { var cont = $('#rssNewsContent'); cont.slideUp(function() { var cont = $('#rssNewsContent'); cont.html(''); }); return false; }).appendTo(cont);
                    $('<div/>').html("powered by<a class='logo'></a>").attr({ "id": "NewsBranding", "style": "float:left;margin-left:10px" }).appendTo(cont);
                    $('<div class="clear"></div>').appendTo(cont);
                    var inner = $('<ul></ul>').attr({ "id": "ticker02" }).appendTo(cont);
                    var alternate = '';
                    for (var i = 0; i < results.length; i++) {
                        var jsonItem = results[i];
                        var inner2 = $('<li/>').attr({ "id": "tickeritem" }).appendTo(inner);
                        $('<a/>').html(jsonItem.title).attr({ "href": jsonItem.unescapedUrl, "target": "_blank", "class": "txtblue" }).appendTo(inner2);
                        $('<div/>').html(jsonItem.content).css({ "color": "#000", "margin-bottom": "10px" }).appendTo(inner2);
                        if (alternate == '')
                            alternate = "alternate";
                        else
                            alternate = '';
                    }
                    var start = 0;
                    var currentstart = start;
                    if (json.responseData.cursor && json.responseData.cursor != '') {
                        if (json.responseData.cursor.pages && json.responseData.cursor.pages.length > 0) {
                            if (start <  json.responseData.cursor.pages[json.responseData.cursor.pages.length - 1].start) {
                                currentstart = 8;
                                $('<a/>').html("More Articles").attr({ "class": "txtblue morearticles", "style": "float:right;cursor:pointer;cursor:hand;", "data-start": currentstart }).click(function() { var cont = $('#rssNewsContent'); cont.slideUp(function() { var cont = $('#rssNewsContent'); rssNewsContent(key, newskeyword, parseInt($('#rssNewsContent a.morearticles').attr('data-start'))); }); return false; }).appendTo(cont);
                            }
                            else if (json.responseData.cursor.moreResultsUrl && json.responseData.cursor.moreResultsUrl != '') {
                                $('<a/>').html("More Articles").attr({ "class": "txtblue", "style": "float:right;", "target": "_blank", "href": json.responseData.cursor.moreResultsUrl }).appendTo(cont);
                            }
                        }
                        else if (json.responseData.cursor.moreResultsUrl && json.responseData.cursor.moreResultsUrl != '') {
                            $('<a/>').html("More Articles").attr({ "class": "txtblue", "style": "float:right;", "target": "_blank", "href": json.responseData.cursor.moreResultsUrl }).appendTo(cont);
                        }
                    }
                    if (start != 0) {
                        currentstart = start - 8;
                        $('<a/>').html("Back").attr({ "class": "txtblue prevarticles", "style": "float:right;cursor:pointer;cursor:hand;margin-right:10px;", "data-start": currentstart }).click(function() { var cont = $('#' + obj); cont.slideUp(function() { var cont = $('#rssNewsContent'); rssNewsContent(key, newskeyword, parseInt($('#rssNewsContent a.prevarticles').attr('data-start'))); }); return false; }).appendTo(cont);
                    }
                    cont.fadeIn();
                }

            }
            else {
                cont.html('');
            }
            setTimeout("rssTicker('" + key + "','" + newskeyword + "')", 1000 * 60 * 10);
        })
    }
}


function rssNewsContent(key, newskeyword, start, obj, hideclose) {
    $.getJSON(('https:' == document.location.protocol ? 'https://' : 'http://') + "ajax.googleapis.com/ajax/services/search/news?v=1.0&rsz=large" + (start ? '&start=' + start : '') + "&key=" + key + "&q=" + encodeURIComponent(newskeyword) + "&callback=?", function(json) {
        var results;
        if (json)
            results = json.responseData.results;
        if (obj == undefined || obj == null)
            obj = 'rssNewsContent';
        var cont = $('#' + obj);
        if (results && results.length) {
            if (cont.html() != '')
                cont.fadeOut();
            cont.html('');
            $('<div class="clear"></div>').appendTo(cont);
            $('<span></span>').html('<b>Channel: ' + newskeyword + ' </b>').attr({ "class": "txtblue", "style": "float:left;" }).appendTo(cont);
            if (!hideclose)
                $('<span/>').html("close [x]").attr({ "class": "txtblue", "style": "float:right;cursor:pointer;cursor:hand;" }).click(function() { var cont = $('#' + obj); cont.slideUp(function() { var cont = $('#' + obj); cont.html(''); }); return false; }).appendTo(cont);
            $('<div/>').html("powered by<a class='logo'></a>").attr({ "id": "NewsBranding", "style": "float:left;margin-left:10px" }).appendTo(cont);
            $('<div class="clear"></div>').appendTo(cont);
            var inner = $('<ul></ul>').attr({ "id": "ticker02" }).appendTo(cont);
            var alternate = '';
            for (var i = 0; i < results.length; i++) {

                var jsonItem = results[i];
                var inner2 = $('<li/>').attr({ "id": "tickeritem" }).appendTo(inner);
                $('<a/>').html(jsonItem.title).attr({ "href": jsonItem.unescapedUrl, "target": "_blank", "class": "txtblue" }).appendTo(inner2);
                $('<div/>').html(jsonItem.content).css({ "color": "#000", "margin-bottom": "10px" }).appendTo(inner2);
                if (alternate == '')
                    alternate = "alternate";
                else
                    alternate = '';
            }
            var currentstart = start;
            if (json.responseData.cursor && json.responseData.cursor != '') {
                if ((start == undefined || start == null || start != 56) && json.responseData.cursor.pages && json.responseData.cursor.pages.length > 0) {
                    if (start == undefined || start == null) {
                        currentstart = 8;
                        $('<a/>').html("More Articles").attr({ "class": "txtblue morearticles", "style": "float:right;cursor:pointer;cursor:hand;", "data-start": currentstart }).click(function() { var cont = $('#' + obj); cont.slideUp(function() { var cont = $('#' + obj); rssNewsContent(key, newskeyword, parseInt($('#' + obj + ' a.morearticles').attr('data-start')), obj, true); }); return false; }).appendTo(cont);
                    }
                    else if (start < parseInt(json.responseData.cursor.pages[json.responseData.cursor.pages.length - 1].start)) {
                        currentstart = start + 8;
                        $('<a/>').html("More Articles").attr({ "class": "txtblue morearticles", "style": "float:right;cursor:pointer;cursor:hand;", "data-start": currentstart }).click(function() { var cont = $('#' + obj); cont.slideUp(function() { var cont = $('#' + obj); rssNewsContent(key, newskeyword, parseInt($('#' + obj + ' a.morearticles').attr('data-start')), obj, true); }); return false; }).appendTo(cont);
                    }
                    else if (json.responseData.cursor.moreResultsUrl && json.responseData.cursor.moreResultsUrl != '') {
                        $('<a/>').html("More Articles").attr({ "class": "txtblue", "style": "float:right;", "target": "_blank", "href": json.responseData.cursor.moreResultsUrl }).appendTo(cont);
                    }
                }
                else if (json.responseData.cursor.moreResultsUrl && json.responseData.cursor.moreResultsUrl != '') {
                    $('<a/>').html("More Articles").attr({ "class": "txtblue", "style": "float:right;", "target": "_blank", "href": json.responseData.cursor.moreResultsUrl }).appendTo(cont);
                }
                if (start != undefined && start != null && start != 0) {
                    currentstart = start - 8;
                    $('<a/>').html("Back").attr({ "class": "txtblue prevarticles", "style": "float:right;cursor:pointer;cursor:hand;margin-right:10px;", "data-start": currentstart }).click(function() { var cont = $('#' + obj); cont.slideUp(function() { var cont = $('#' + obj); rssNewsContent(key, newskeyword, parseInt($('#' + obj + ' a.prevarticles').attr('data-start')), obj, true); }); return false; }).appendTo(cont);
                }

            }
            cont.slideDown();
        }
        else {
            cont.html('');
        }
    })
    return false;
}

/*!
 * jQuery Tools v1.2.6 - The missing UI library for the Web
 * 
 * overlay/overlay.js
 * overlay/overlay.apple.js
 * scrollable/scrollable.js
 * scrollable/scrollable.autoscroll.js
 * scrollable/scrollable.navigator.js
 * tabs/tabs.js
 * tabs/tabs.slideshow.js
 * toolbox/toolbox.expose.js
 * toolbox/toolbox.flashembed.js
 * toolbox/toolbox.history.js
 * toolbox/toolbox.mousewheel.js
 * tooltip/tooltip.js
 * tooltip/tooltip.dynamic.js
 * tooltip/tooltip.slide.js
 * 
 * NO COPYRIGHTS OR LICENSES. DO WHAT YOU LIKE.
 * 
 * http://flowplayer.org/tools/
 * 
 * jquery.event.wheel.js - rev 1 
 * Copyright (c) 2008, Three Dub Media (http://threedubmedia.com)
 * Liscensed under the MIT License (MIT-LICENSE.txt)
 * http://www.opensource.org/licenses/mit-license.php
 * Created: 2008-07-01 | Updated: 2008-07-14
 * 
 * -----
 * 
 */
(function(a){a.tools=a.tools||{version:"v1.2.6"},a.tools.overlay={addEffect:function(a,b,d){c[a]=[b,d]},conf:{close:null,closeOnClick:!0,closeOnEsc:!0,closeSpeed:"fast",effect:"default",fixed:!a.browser.msie||a.browser.version>6,left:"center",load:!1,mask:null,oneInstance:!0,speed:"normal",target:null,top:"10%"}};var b=[],c={};a.tools.overlay.addEffect("default",function(b,c){var d=this.getConf(),e=a(window);d.fixed||(b.top+=e.scrollTop(),b.left+=e.scrollLeft()),b.position=d.fixed?"fixed":"absolute",this.getOverlay().css(b).fadeIn(d.speed,c)},function(a){this.getOverlay().fadeOut(this.getConf().closeSpeed,a)});function d(d,e){var f=this,g=d.add(f),h=a(window),i,j,k,l=a.tools.expose&&(e.mask||e.expose),m=Math.random().toString().slice(10);l&&(typeof l=="string"&&(l={color:l}),l.closeOnClick=l.closeOnEsc=!1);var n=e.target||d.attr("rel");j=n?a(n):null||d;if(!j.length)throw"Could not find Overlay: "+n;d&&d.index(j)==-1&&d.click(function(a){f.load(a);return a.preventDefault()}),a.extend(f,{load:function(d){if(f.isOpened())return f;var i=c[e.effect];if(!i)throw"Overlay: cannot find effect : \""+e.effect+"\"";e.oneInstance&&a.each(b,function(){this.close(d)}),d=d||a.Event(),d.type="onBeforeLoad",g.trigger(d);if(d.isDefaultPrevented())return f;k=!0,l&&a(j).expose(l);var n=e.top,o=e.left,p=j.outerWidth({margin:!0}),q=j.outerHeight({margin:!0});typeof n=="string"&&(n=n=="center"?Math.max((h.height()-q)/2,0):parseInt(n,10)/100*h.height()),o=="center"&&(o=Math.max((h.width()-p)/2,0)),i[0].call(f,{top:n,left:o},function(){k&&(d.type="onLoad",g.trigger(d))}),l&&e.closeOnClick&&a.mask.getMask().one("click",f.close),e.closeOnClick&&a(document).bind("click."+m,function(b){a(b.target).parents(j).length||f.close(b)}),e.closeOnEsc&&a(document).bind("keydown."+m,function(a){a.keyCode==27&&f.close(a)});return f},close:function(b){if(!f.isOpened())return f;b=b||a.Event(),b.type="onBeforeClose",g.trigger(b);if(!b.isDefaultPrevented()){k=!1,c[e.effect][1].call(f,function(){b.type="onClose",g.trigger(b)}),a(document).unbind("click."+m).unbind("keydown."+m),l&&a.mask.close();return f}},getOverlay:function(){return j},getTrigger:function(){return d},getClosers:function(){return i},isOpened:function(){return k},getConf:function(){return e}}),a.each("onBeforeLoad,onStart,onLoad,onBeforeClose,onClose".split(","),function(b,c){a.isFunction(e[c])&&a(f).bind(c,e[c]),f[c]=function(b){b&&a(f).bind(c,b);return f}}),i=j.find(e.close||".close"),!i.length&&!e.close&&(i=a("<a class=\"close\"></a>"),j.prepend(i)),i.click(function(a){f.close(a)}),e.load&&f.load()}a.fn.overlay=function(c){var e=this.data("overlay");if(e)return e;a.isFunction(c)&&(c={onBeforeLoad:c}),c=a.extend(!0,{},a.tools.overlay.conf,c),this.each(function(){e=new d(a(this),c),b.push(e),a(this).data("overlay",e)});return c.api?e:this}})(jQuery);
(function(a){var b=a.tools.overlay,c=a(window);a.extend(b.conf,{start:{top:null,left:null},fadeInSpeed:"fast",zIndex:9999});function d(a){var b=a.offset();return{top:b.top+a.height()/2,left:b.left+a.width()/2}}var e=function(b,e){var f=this.getOverlay(),g=this.getConf(),h=this.getTrigger(),i=this,j=f.outerWidth({margin:!0}),k=f.data("img"),l=g.fixed?"fixed":"absolute";if(!k){var m=f.css("backgroundImage");if(!m)throw"background-image CSS property not set for overlay";m=m.slice(m.indexOf("(")+1,m.indexOf(")")).replace(/\"/g,""),f.css("backgroundImage","none"),k=a("<img src=\""+m+"\"/>"),k.css({border:0,display:"none"}).width(j),a("body").append(k),f.data("img",k)}var n=g.start.top||Math.round(c.height()/2),o=g.start.left||Math.round(c.width()/2);if(h){var p=d(h);n=p.top,o=p.left}g.fixed?(n-=c.scrollTop(),o-=c.scrollLeft()):(b.top+=c.scrollTop(),b.left+=c.scrollLeft()),k.css({position:"absolute",top:n,left:o,width:0,zIndex:g.zIndex}).show(),b.position=l,f.css(b),k.animate({top:f.css("top"),left:f.css("left"),width:j},g.speed,function(){f.css("zIndex",g.zIndex+1).fadeIn(g.fadeInSpeed,function(){i.isOpened()&&!a(this).index(f)?e.call():f.hide()})}).css("position",l)},f=function(b){var e=this.getOverlay().hide(),f=this.getConf(),g=this.getTrigger(),h=e.data("img"),i={top:f.start.top,left:f.start.left,width:0};g&&a.extend(i,d(g)),f.fixed&&h.css({position:"absolute"}).animate({top:"+="+c.scrollTop(),left:"+="+c.scrollLeft()},0),h.animate(i,f.closeSpeed,b)};b.addEffect("apple",e,f)})(jQuery);
(function(a){a.tools=a.tools||{version:"v1.2.6"},a.tools.scrollable={conf:{activeClass:"active",circular:!1,clonedClass:"cloned",disabledClass:"disabled",easing:"swing",initialIndex:0,item:"> *",items:".items",keyboard:!0,mousewheel:!1,next:".next",prev:".prev",size:1,speed:400,vertical:!1,touch:!0,wheelSpeed:0}};function b(a,b){var c=parseInt(a.css(b),10);if(c)return c;var d=a[0].currentStyle;return d&&d.width&&parseInt(d.width,10)}function c(b,c){var d=a(c);return d.length<2?d:b.parent().find(c)}var d;function e(b,e){var f=this,g=b.add(f),h=b.children(),i=0,j=e.vertical;d||(d=f),h.length>1&&(h=a(e.items,b)),e.size>1&&(e.circular=!1),a.extend(f,{getConf:function(){return e},getIndex:function(){return i},getSize:function(){return f.getItems().size()},getNaviButtons:function(){return n.add(o)},getRoot:function(){return b},getItemWrap:function(){return h},getItems:function(){return h.find(e.item).not("."+e.clonedClass)},move:function(a,b){return f.seekTo(i+a,b)},next:function(a){return f.move(e.size,a)},prev:function(a){return f.move(-e.size,a)},begin:function(a){return f.seekTo(0,a)},end:function(a){return f.seekTo(f.getSize()-1,a)},focus:function(){d=f;return f},addItem:function(b){b=a(b),e.circular?(h.children().last().before(b),h.children().first().replaceWith(b.clone().addClass(e.clonedClass))):(h.append(b),o.removeClass("disabled")),g.trigger("onAddItem",[b]);return f},seekTo:function(b,c,k){b.jquery||(b*=1);if(e.circular&&b===0&&i==-1&&c!==0)return f;if(!e.circular&&b<0||b>f.getSize()||b<-1)return f;var l=b;b.jquery?b=f.getItems().index(b):l=f.getItems().eq(b);var m=a.Event("onBeforeSeek");if(!k){g.trigger(m,[b,c]);if(m.isDefaultPrevented()||!l.length)return f}var n=j?{top:-l.position().top}:{left:-l.position().left};i=b,d=f,c===undefined&&(c=e.speed),h.animate(n,c,e.easing,k||function(){g.trigger("onSeek",[b])});return f}}),a.each(["onBeforeSeek","onSeek","onAddItem"],function(b,c){a.isFunction(e[c])&&a(f).bind(c,e[c]),f[c]=function(b){b&&a(f).bind(c,b);return f}});if(e.circular){var k=f.getItems().slice(-1).clone().prependTo(h),l=f.getItems().eq(1).clone().appendTo(h);k.add(l).addClass(e.clonedClass),f.onBeforeSeek(function(a,b,c){if(!a.isDefaultPrevented()){if(b==-1){f.seekTo(k,c,function(){f.end(0)});return a.preventDefault()}b==f.getSize()&&f.seekTo(l,c,function(){f.begin(0)})}});var m=b.parents().add(b).filter(function(){if(a(this).css("display")==="none")return!0});m.length?(m.show(),f.seekTo(0,0,function(){}),m.hide()):f.seekTo(0,0,function(){})}var n=c(b,e.prev).click(function(a){a.stopPropagation(),f.prev()}),o=c(b,e.next).click(function(a){a.stopPropagation(),f.next()});e.circular||(f.onBeforeSeek(function(a,b){setTimeout(function(){a.isDefaultPrevented()||(n.toggleClass(e.disabledClass,b<=0),o.toggleClass(e.disabledClass,b>=f.getSize()-1))},1)}),e.initialIndex||n.addClass(e.disabledClass)),f.getSize()<2&&n.add(o).addClass(e.disabledClass),e.mousewheel&&a.fn.mousewheel&&b.mousewheel(function(a,b){if(e.mousewheel){f.move(b<0?1:-1,e.wheelSpeed||50);return!1}});if(e.touch){var p={};h[0].ontouchstart=function(a){var b=a.touches[0];p.x=b.clientX,p.y=b.clientY},h[0].ontouchmove=function(a){if(a.touches.length==1&&!h.is(":animated")){var b=a.touches[0],c=p.x-b.clientX,d=p.y-b.clientY;f[j&&d>0||!j&&c>0?"next":"prev"](),a.preventDefault()}}}e.keyboard&&a(document).bind("keydown.scrollable",function(b){if(!(!e.keyboard||b.altKey||b.ctrlKey||b.metaKey||a(b.target).is(":input"))){if(e.keyboard!="static"&&d!=f)return;var c=b.keyCode;if(j&&(c==38||c==40)){f.move(c==38?-1:1);return b.preventDefault()}if(!j&&(c==37||c==39)){f.move(c==37?-1:1);return b.preventDefault()}}}),e.initialIndex&&f.seekTo(e.initialIndex,0,function(){})}a.fn.scrollable=function(b){var c=this.data("scrollable");if(c)return c;b=a.extend({},a.tools.scrollable.conf,b),this.each(function(){c=new e(a(this),b),a(this).data("scrollable",c)});return b.api?c:this}})(jQuery);
(function(a){var b=a.tools.scrollable;b.autoscroll={conf:{autoplay:!0,interval:3e3,autopause:!0}},a.fn.autoscroll=function(c){typeof c=="number"&&(c={interval:c});var d=a.extend({},b.autoscroll.conf,c),e;this.each(function(){var b=a(this).data("scrollable"),c=b.getRoot(),f,g=!1;function h(){f=setTimeout(function(){b.next()},d.interval)}b&&(e=b),b.play=function(){f||(g=!1,c.bind("onSeek",h),h())},b.pause=function(){f=clearTimeout(f),c.unbind("onSeek",h)},b.resume=function(){g||b.play()},b.stop=function(){g=!0,b.pause()},d.autopause&&c.add(b.getNaviButtons()).hover(b.pause,b.resume),d.autoplay&&b.play()});return d.api?e:this}})(jQuery);
(function(a){var b=a.tools.scrollable;b.navigator={conf:{navi:".navi",naviItem:null,activeClass:"active",indexed:!1,idPrefix:null,history:!1}};function c(b,c){var d=a(c);return d.length<2?d:b.parent().find(c)}a.fn.navigator=function(d){typeof d=="string"&&(d={navi:d}),d=a.extend({},b.navigator.conf,d);var e;this.each(function(){var b=a(this).data("scrollable"),f=d.navi.jquery?d.navi:c(b.getRoot(),d.navi),g=b.getNaviButtons(),h=d.activeClass,i=d.history&&history.pushState,j=b.getConf().size;b&&(e=b),b.getNaviButtons=function(){return g.add(f)},i&&(history.pushState({i:0}),a(window).bind("popstate",function(a){var c=a.originalEvent.state;c&&b.seekTo(c.i)}));function k(a,c,d){b.seekTo(c),d.preventDefault(),i&&history.pushState({i:c})}function l(){return f.find(d.naviItem||"> *")}function m(b){var c=a("<"+(d.naviItem||"a")+"/>").click(function(c){k(a(this),b,c)});b===0&&c.addClass(h),d.indexed&&c.text(b+1),d.idPrefix&&c.attr("id",d.idPrefix+b);return c.appendTo(f)}l().length?l().each(function(b){a(this).click(function(c){k(a(this),b,c)})}):a.each(b.getItems(),function(a){a%j==0&&m(a)}),b.onBeforeSeek(function(a,b){setTimeout(function(){if(!a.isDefaultPrevented()){var c=b/j,d=l().eq(c);d.length&&l().removeClass(h).eq(c).addClass(h)}},1)}),b.onAddItem(function(a,c){var d=b.getItems().index(c);d%j==0&&m(d)})});return d.api?e:this}})(jQuery);
(function(a){a.tools=a.tools||{version:"v1.2.6"},a.tools.tabs={conf:{tabs:"a",current:"current",onBeforeClick:null,onClick:null,effect:"default",initialIndex:0,event:"click",rotate:!1,slideUpSpeed:400,slideDownSpeed:400,history:!1},addEffect:function(a,c){b[a]=c}};var b={"default":function(a,b){this.getPanes().hide().eq(a).show(),b.call()},fade:function(a,b){var c=this.getConf(),d=c.fadeOutSpeed,e=this.getPanes();d?e.fadeOut(d):e.hide(),e.eq(a).fadeIn(c.fadeInSpeed,b)},slide:function(a,b){var c=this.getConf();this.getPanes().slideUp(c.slideUpSpeed),this.getPanes().eq(a).slideDown(c.slideDownSpeed,b)},ajax:function(a,b){this.getPanes().eq(0).load(this.getTabs().eq(a).attr("href"),b)}},c,d;a.tools.tabs.addEffect("horizontal",function(b,e){if(!c){var f=this.getPanes().eq(b),g=this.getCurrentPane();d||(d=this.getPanes().eq(0).width()),c=!0,f.show(),g.animate({width:0},{step:function(a){f.css("width",d-a)},complete:function(){a(this).hide(),e.call(),c=!1}}),g.length||(e.call(),c=!1)}});function e(c,d,e){var f=this,g=c.add(this),h=c.find(e.tabs),i=d.jquery?d:c.children(d),j;h.length||(h=c.children()),i.length||(i=c.parent().find(d)),i.length||(i=a(d)),a.extend(this,{click:function(c,d){var i=h.eq(c);typeof c=="string"&&c.replace("#","")&&(i=h.filter("[href*="+c.replace("#","")+"]"),c=Math.max(h.index(i),0));if(e.rotate){var k=h.length-1;if(c<0)return f.click(k,d);if(c>k)return f.click(0,d)}if(!i.length){if(j>=0)return f;c=e.initialIndex,i=h.eq(c)}if(c===j)return f;d=d||a.Event(),d.type="onBeforeClick",g.trigger(d,[c]);if(!d.isDefaultPrevented()){b[e.effect].call(f,c,function(){j=c,d.type="onClick",g.trigger(d,[c])}),h.removeClass(e.current),i.addClass(e.current);return f}},getConf:function(){return e},getTabs:function(){return h},getPanes:function(){return i},getCurrentPane:function(){return i.eq(j)},getCurrentTab:function(){return h.eq(j)},getIndex:function(){return j},next:function(){return f.click(j+1)},prev:function(){return f.click(j-1)},destroy:function(){h.unbind(e.event).removeClass(e.current),i.find("a[href^=#]").unbind("click.T");return f}}),a.each("onBeforeClick,onClick".split(","),function(b,c){a.isFunction(e[c])&&a(f).bind(c,e[c]),f[c]=function(b){b&&a(f).bind(c,b);return f}}),e.history&&a.fn.history&&(a.tools.history.init(h),e.event="history"),h.each(function(b){a(this).bind(e.event,function(a){f.click(b,a);return a.preventDefault()})}),i.find("a[href^=#]").bind("click.T",function(b){f.click(a(this).attr("href"),b)}),location.hash&&e.tabs=="a"&&c.find("[href="+location.hash+"]").length?f.click(location.hash):(e.initialIndex===0||e.initialIndex>0)&&f.click(e.initialIndex)}a.fn.tabs=function(b,c){var d=this.data("tabs");d&&(d.destroy(),this.removeData("tabs")),a.isFunction(c)&&(c={onBeforeClick:c}),c=a.extend({},a.tools.tabs.conf,c),this.each(function(){d=new e(a(this),b,c),a(this).data("tabs",d)});return c.api?d:this}})(jQuery);
(function(a){var b;b=a.tools.tabs.slideshow={conf:{next:".forward",prev:".backward",disabledClass:"disabled",autoplay:!1,autopause:!0,interval:3e3,clickable:!0,api:!1}};function c(b,c){var d=this,e=b.add(this),f=b.data("tabs"),g,h=!0;function i(c){var d=a(c);return d.length<2?d:b.parent().find(c)}var j=i(c.next).click(function(){f.next()}),k=i(c.prev).click(function(){f.prev()});function l(){g=setTimeout(function(){f.next()},c.interval)}a.extend(d,{getTabs:function(){return f},getConf:function(){return c},play:function(){if(g)return d;var b=a.Event("onBeforePlay");e.trigger(b);if(b.isDefaultPrevented())return d;h=!1,e.trigger("onPlay"),e.bind("onClick",l),l();return d},pause:function(){if(!g)return d;var b=a.Event("onBeforePause");e.trigger(b);if(b.isDefaultPrevented())return d;g=clearTimeout(g),e.trigger("onPause"),e.unbind("onClick",l);return d},resume:function(){h||d.play()},stop:function(){d.pause(),h=!0}}),a.each("onBeforePlay,onPlay,onBeforePause,onPause".split(","),function(b,e){a.isFunction(c[e])&&a(d).bind(e,c[e]),d[e]=function(b){return a(d).bind(e,b)}}),c.autopause&&f.getTabs().add(j).add(k).add(f.getPanes()).hover(d.pause,d.resume),c.autoplay&&d.play(),c.clickable&&f.getPanes().click(function(){f.next()});if(!f.getConf().rotate){var m=c.disabledClass;f.getIndex()||k.addClass(m),f.onBeforeClick(function(a,b){k.toggleClass(m,!b),j.toggleClass(m,b==f.getTabs().length-1)})}}a.fn.slideshow=function(d){var e=this.data("slideshow");if(e)return e;d=a.extend({},b.conf,d),this.each(function(){e=new c(a(this),d),a(this).data("slideshow",e)});return d.api?e:this}})(jQuery);
(function(a){a.tools=a.tools||{version:"v1.2.6"};var b;b=a.tools.expose={conf:{maskId:"exposeMask",loadSpeed:"slow",closeSpeed:"fast",closeOnClick:!0,closeOnEsc:!0,zIndex:9998,opacity:.8,startOpacity:0,color:"#fff",onLoad:null,onClose:null}};function c(){if(a.browser.msie){var b=a(document).height(),c=a(window).height();return[window.innerWidth||document.documentElement.clientWidth||document.body.clientWidth,b-c<20?c:b]}return[a(document).width(),a(document).height()]}function d(b){if(b)return b.call(a.mask)}var e,f,g,h,i;a.mask={load:function(j,k){if(g)return this;typeof j=="string"&&(j={color:j}),j=j||h,h=j=a.extend(a.extend({},b.conf),j),e=a("#"+j.maskId),e.length||(e=a("<div/>").attr("id",j.maskId),a("body").append(e));var l=c();e.css({position:"absolute",top:0,left:0,width:l[0],height:l[1],display:"none",opacity:j.startOpacity,zIndex:j.zIndex}),j.color&&e.css("backgroundColor",j.color);if(d(j.onBeforeLoad)===!1)return this;j.closeOnEsc&&a(document).bind("keydown.mask",function(b){b.keyCode==27&&a.mask.close(b)}),j.closeOnClick&&e.bind("click.mask",function(b){a.mask.close(b)}),a(window).bind("resize.mask",function(){a.mask.fit()}),k&&k.length&&(i=k.eq(0).css("zIndex"),a.each(k,function(){var b=a(this);/relative|absolute|fixed/i.test(b.css("position"))||b.css("position","relative")}),f=k.css({zIndex:Math.max(j.zIndex+1,i=="auto"?0:i)})),e.css({display:"block"}).fadeTo(j.loadSpeed,j.opacity,function(){a.mask.fit(),d(j.onLoad),g="full"}),g=!0;return this},close:function(){if(g){if(d(h.onBeforeClose)===!1)return this;e.fadeOut(h.closeSpeed,function(){d(h.onClose),f&&f.css({zIndex:i}),g=!1}),a(document).unbind("keydown.mask"),e.unbind("click.mask"),a(window).unbind("resize.mask")}return this},fit:function(){if(g){var a=c();e.css({width:a[0],height:a[1]})}},getMask:function(){return e},isLoaded:function(a){return a?g=="full":g},getConf:function(){return h},getExposed:function(){return f}},a.fn.mask=function(b){a.mask.load(b);return this},a.fn.expose=function(b){a.mask.load(b,this);return this}})(jQuery);
(function(){var a=document.all,b="http://www.adobe.com/go/getflashplayer",c=typeof jQuery=="function",d=/(\d+)[^\d]+(\d+)[^\d]*(\d*)/,e={width:"100%",height:"100%",id:"_"+(""+Math.random()).slice(9),allowfullscreen:!0,allowscriptaccess:"always",quality:"high",version:[3,0],onFail:null,expressInstall:null,w3c:!1,cachebusting:!1};window.attachEvent&&window.attachEvent("onbeforeunload",function(){__flash_unloadHandler=function(){},__flash_savedUnloadHandler=function(){}});function f(a,b){if(b)for(var c in b)b.hasOwnProperty(c)&&(a[c]=b[c]);return a}function g(a,b){var c=[];for(var d in a)a.hasOwnProperty(d)&&(c[d]=b(a[d]));return c}window.flashembed=function(a,b,c){typeof a=="string"&&(a=document.getElementById(a.replace("#","")));if(a){typeof b=="string"&&(b={src:b});return new j(a,f(f({},e),b),c)}};var h=f(window.flashembed,{conf:e,getVersion:function(){var a,b;try{b=navigator.plugins["Shockwave Flash"].description.slice(16)}catch(c){try{a=new ActiveXObject("ShockwaveFlash.ShockwaveFlash.7"),b=a&&a.GetVariable("$version")}catch(e){try{a=new ActiveXObject("ShockwaveFlash.ShockwaveFlash.6"),b=a&&a.GetVariable("$version")}catch(f){}}}b=d.exec(b);return b?[b[1],b[3]]:[0,0]},asString:function(a){if(a===null||a===undefined)return null;var b=typeof a;b=="object"&&a.push&&(b="array");switch(b){case"string":a=a.replace(new RegExp("([\"\\\\])","g"),"\\$1"),a=a.replace(/^\s?(\d+\.?\d*)%/,"$1pct");return"\""+a+"\"";case"array":return"["+g(a,function(a){return h.asString(a)}).join(",")+"]";case"function":return"\"function()\"";case"object":var c=[];for(var d in a)a.hasOwnProperty(d)&&c.push("\""+d+"\":"+h.asString(a[d]));return"{"+c.join(",")+"}"}return String(a).replace(/\s/g," ").replace(/\'/g,"\"")},getHTML:function(b,c){b=f({},b);var d="<object width=\""+b.width+"\" height=\""+b.height+"\" id=\""+b.id+"\" name=\""+b.id+"\"";b.cachebusting&&(b.src+=(b.src.indexOf("?")!=-1?"&":"?")+Math.random()),b.w3c||!a?d+=" data=\""+b.src+"\" type=\"application/x-shockwave-flash\"":d+=" classid=\"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000\"",d+=">";if(b.w3c||a)d+="<param name=\"movie\" value=\""+b.src+"\" />";b.width=b.height=b.id=b.w3c=b.src=null,b.onFail=b.version=b.expressInstall=null;for(var e in b)b[e]&&(d+="<param name=\""+e+"\" value=\""+b[e]+"\" />");var g="";if(c){for(var i in c)if(c[i]){var j=c[i];g+=i+"="+encodeURIComponent(/function|object/.test(typeof j)?h.asString(j):j)+"&"}g=g.slice(0,-1),d+="<param name=\"flashvars\" value='"+g+"' />"}d+="</object>";return d},isSupported:function(a){return i[0]>a[0]||i[0]==a[0]&&i[1]>=a[1]}}),i=h.getVersion();function j(c,d,e){if(h.isSupported(d.version))c.innerHTML=h.getHTML(d,e);else if(d.expressInstall&&h.isSupported([6,65]))c.innerHTML=h.getHTML(f(d,{src:d.expressInstall}),{MMredirectURL:location.href,MMplayerType:"PlugIn",MMdoctitle:document.title});else{c.innerHTML.replace(/\s/g,"")||(c.innerHTML="<h2>Flash version "+d.version+" or greater is required</h2><h3>"+(i[0]>0?"Your version is "+i:"You have no flash plugin installed")+"</h3>"+(c.tagName=="A"?"<p>Click here to download latest version</p>":"<p>Download latest version from <a href='"+b+"'>here</a></p>"),c.tagName=="A"&&(c.onclick=function(){location.href=b}));if(d.onFail){var g=d.onFail.call(this);typeof g=="string"&&(c.innerHTML=g)}}a&&(window[d.id]=document.getElementById(d.id)),f(this,{getRoot:function(){return c},getOptions:function(){return d},getConf:function(){return e},getApi:function(){return c.firstChild}})}c&&(jQuery.tools=jQuery.tools||{version:"v1.2.6"},jQuery.tools.flashembed={conf:e},jQuery.fn.flashembed=function(a,b){return this.each(function(){jQuery(this).data("flashembed",flashembed(this,a,b))})})})();
(function(a){var b,c,d,e;a.tools=a.tools||{version:"v1.2.6"},a.tools.history={init:function(g){e||(a.browser.msie&&a.browser.version<"8"?c||(c=a("<iframe/>").attr("src","javascript:false;").hide().get(0),a("body").prepend(c),setInterval(function(){var d=c.contentWindow.document,e=d.location.hash;b!==e&&a(window).trigger("hash",e)},100),f(location.hash||"#")):setInterval(function(){var c=location.hash;c!==b&&a(window).trigger("hash",c)},100),d=d?d.add(g):g,g.click(function(b){var d=a(this).attr("href");c&&f(d);if(d.slice(0,1)!="#"){location.href="#"+d;return b.preventDefault()}}),e=!0)}};function f(a){if(a){var b=c.contentWindow.document;b.open().close(),b.location.hash=a}}a(window).bind("hash",function(c,e){e?d.filter(function(){var b=a(this).attr("href");return b==e||b==e.replace("#","")}).trigger("history",[e]):d.eq(0).trigger("history",[e]),b=e}),a.fn.history=function(b){a.tools.history.init(this);return this.bind("history",b)}})(jQuery);
(function(a){a.fn.mousewheel=function(a){return this[a?"bind":"trigger"]("wheel",a)},a.event.special.wheel={setup:function(){a.event.add(this,b,c,{})},teardown:function(){a.event.remove(this,b,c)}};var b=a.browser.mozilla?"DOMMouseScroll"+(a.browser.version<"1.9"?" mousemove":""):"mousewheel";function c(b){switch(b.type){case"mousemove":return a.extend(b.data,{clientX:b.clientX,clientY:b.clientY,pageX:b.pageX,pageY:b.pageY});case"DOMMouseScroll":a.extend(b,b.data),b.delta=-b.detail/3;break;case"mousewheel":b.delta=b.wheelDelta/120}b.type="wheel";return a.event.handle.call(this,b,b.delta)}})(jQuery);
(function(a){a.tools=a.tools||{version:"v1.2.6"},a.tools.tooltip={conf:{effect:"toggle",fadeOutSpeed:"fast",predelay:0,delay:30,opacity:1,tip:0,fadeIE:!1,position:["top","center"],offset:[0,0],relative:!1,cancelDefault:!0,events:{def:"mouseenter,mouseleave",input:"focus,blur",widget:"focus mouseenter,blur mouseleave",tooltip:"mouseenter,mouseleave"},layout:"<div/>",tipClass:"tooltip"},addEffect:function(a,c,d){b[a]=[c,d]}};var b={toggle:[function(a){var b=this.getConf(),c=this.getTip(),d=b.opacity;d<1&&c.css({opacity:d}),c.show(),a.call()},function(a){this.getTip().hide(),a.call()}],fade:[function(b){var c=this.getConf();!a.browser.msie||c.fadeIE?this.getTip().fadeTo(c.fadeInSpeed,c.opacity,b):(this.getTip().show(),b())},function(b){var c=this.getConf();!a.browser.msie||c.fadeIE?this.getTip().fadeOut(c.fadeOutSpeed,b):(this.getTip().hide(),b())}]};function c(b,c,d){var e=d.relative?b.position().top:b.offset().top,f=d.relative?b.position().left:b.offset().left,g=d.position[0];e-=c.outerHeight()-d.offset[0],f+=b.outerWidth()+d.offset[1],/iPad/i.test(navigator.userAgent)&&(e-=a(window).scrollTop());var h=c.outerHeight()+b.outerHeight();g=="center"&&(e+=h/2),g=="bottom"&&(e+=h),g=d.position[1];var i=c.outerWidth()+b.outerWidth();g=="center"&&(f-=i/2),g=="left"&&(f-=i);return{top:e,left:f}}function d(d,e){var f=this,g=d.add(f),h,i=0,j=0,k=d.attr("title"),l=d.attr("data-tooltip"),m=b[e.effect],n,o=d.is(":input"),p=o&&d.is(":checkbox, :radio, select, :button, :submit"),q=d.attr("type"),r=e.events[q]||e.events[o?p?"widget":"input":"def"];if(!m)throw"Nonexistent effect \""+e.effect+"\"";r=r.split(/,\s*/);if(r.length!=2)throw"Tooltip: bad events configuration for "+q;d.bind(r[0],function(a){clearTimeout(i),e.predelay?j=setTimeout(function(){f.show(a)},e.predelay):f.show(a)}).bind(r[1],function(a){clearTimeout(j),e.delay?i=setTimeout(function(){f.hide(a)},e.delay):f.hide(a)}),k&&e.cancelDefault&&(d.removeAttr("title"),d.data("title",k)),a.extend(f,{show:function(b){if(!h){l?h=a(l):e.tip?h=a(e.tip).eq(0):k?h=a(e.layout).addClass(e.tipClass).appendTo(document.body).hide().append(k):(h=d.next(),h.length||(h=d.parent().next()));if(!h.length)throw"Cannot find tooltip for "+d}if(f.isShown())return f;h.stop(!0,!0);var o=c(d,h,e);e.tip&&h.html(d.data("title")),b=a.Event(),b.type="onBeforeShow",g.trigger(b,[o]);if(b.isDefaultPrevented())return f;o=c(d,h,e),h.css({position:"absolute",top:o.top,left:o.left}),n=!0,m[0].call(f,function(){b.type="onShow",n="full",g.trigger(b)});var p=e.events.tooltip.split(/,\s*/);h.data("__set")||(h.unbind(p[0]).bind(p[0],function(){clearTimeout(i),clearTimeout(j)}),p[1]&&!d.is("input:not(:checkbox, :radio), textarea")&&h.unbind(p[1]).bind(p[1],function(a){a.relatedTarget!=d[0]&&d.trigger(r[1].split(" ")[0])}),e.tip||h.data("__set",!0));return f},hide:function(c){if(!h||!f.isShown())return f;c=a.Event(),c.type="onBeforeHide",g.trigger(c);if(!c.isDefaultPrevented()){n=!1,b[e.effect][1].call(f,function(){c.type="onHide",g.trigger(c)});return f}},isShown:function(a){return a?n=="full":n},getConf:function(){return e},getTip:function(){return h},getTrigger:function(){return d}}),a.each("onHide,onBeforeShow,onShow,onBeforeHide".split(","),function(b,c){a.isFunction(e[c])&&a(f).bind(c,e[c]),f[c]=function(b){b&&a(f).bind(c,b);return f}})}a.fn.tooltip=function(b){var c=this.data("tooltip");if(c)return c;b=a.extend(!0,{},a.tools.tooltip.conf,b),typeof b.position=="string"&&(b.position=b.position.split(/,?\s/)),this.each(function(){c=new d(a(this),b),a(this).data("tooltip",c)});return b.api?c:this}})(jQuery);
(function(a){var b=a.tools.tooltip;b.dynamic={conf:{classNames:"top right bottom left"}};function c(b){var c=a(window),d=c.width()+c.scrollLeft(),e=c.height()+c.scrollTop();return[b.offset().top<=c.scrollTop(),d<=b.offset().left+b.width(),e<=b.offset().top+b.height(),c.scrollLeft()>=b.offset().left]}function d(a){var b=a.length;while(b--)if(a[b])return!1;return!0}a.fn.dynamic=function(e){typeof e=="number"&&(e={speed:e}),e=a.extend({},b.dynamic.conf,e);var f=a.extend(!0,{},e),g=e.classNames.split(/\s/),h;this.each(function(){var b=a(this).tooltip().onBeforeShow(function(b,e){var i=this.getTip(),j=this.getConf();h||(h=[j.position[0],j.position[1],j.offset[0],j.offset[1],a.extend({},j)]),a.extend(j,h[4]),j.position=[h[0],h[1]],j.offset=[h[2],h[3]],i.css({visibility:"hidden",position:"absolute",top:e.top,left:e.left}).show();var k=a.extend(!0,{},f),l=c(i);if(!d(l)){l[2]&&(a.extend(j,k.top),j.position[0]="top",i.addClass(g[0])),l[3]&&(a.extend(j,k.right),j.position[1]="right",i.addClass(g[1])),l[0]&&(a.extend(j,k.bottom),j.position[0]="bottom",i.addClass(g[2])),l[1]&&(a.extend(j,k.left),j.position[1]="left",i.addClass(g[3]));if(l[0]||l[2])j.offset[0]*=-1;if(l[1]||l[3])j.offset[1]*=-1}i.css({visibility:"visible"}).hide()});b.onBeforeShow(function(){var a=this.getConf(),b=this.getTip();setTimeout(function(){a.position=[h[0],h[1]],a.offset=[h[2],h[3]]},0)}),b.onHide(function(){var a=this.getTip();a.removeClass(e.classNames)}),ret=b});return e.api?ret:this}})(jQuery);
(function(a){var b=a.tools.tooltip;a.extend(b.conf,{direction:"up",bounce:!1,slideOffset:10,slideInSpeed:200,slideOutSpeed:200,slideFade:!a.browser.msie});var c={up:["-","top"],down:["+","top"],left:["-","left"],right:["+","left"]};b.addEffect("slide",function(a){var b=this.getConf(),d=this.getTip(),e=b.slideFade?{opacity:b.opacity}:{},f=c[b.direction]||c.up;e[f[1]]=f[0]+"="+b.slideOffset,b.slideFade&&d.css({opacity:0}),d.show().animate(e,b.slideInSpeed,a)},function(b){var d=this.getConf(),e=d.slideOffset,f=d.slideFade?{opacity:0}:{},g=c[d.direction]||c.up,h=""+g[0];d.bounce&&(h=h=="+"?"-":"+"),f[g[1]]=h+"="+e,this.getTip().animate(f,d.slideOutSpeed,function(){a(this).hide(),b.call()})})})(jQuery);

/*anylinkcssmenu.js*/
if (typeof dd_domreadycheck == "undefined") //global variable to detect if DOM is ready
    var dd_domreadycheck = false

var anylinkcssmenu = {

    menusmap: {},
    preloadimages: [],
    effects: { delayhide: 200, shadow: { enabled: true, opacity: 0.3, depth: [5, 5] }, fade: { enabled: true, duration: 500} }, //customize menu effects

    dimensions: {},
    ismobile: navigator.userAgent.match(/(iPad)|(iPhone)|(iPod)|(android)|(webOS)/i) != null, //boolean check for popular mobile browsers

    getoffset: function(what, offsettype) {
        return (what.offsetParent) ? what[offsettype] + this.getoffset(what.offsetParent, offsettype) : what[offsettype]
    },

    getoffsetof: function(el) {
        el._offsets = { left: this.getoffset(el, "offsetLeft"), top: this.getoffset(el, "offsetTop"), h: el.offsetHeight }
    },

    getdimensions: function(menu) {
        this.dimensions = { anchorw: menu.anchorobj.offsetWidth, anchorh: menu.anchorobj.offsetHeight,
            docwidth: (window.innerWidth || this.standardbody.clientWidth) - 20,
            docheight: (window.innerHeight || this.standardbody.clientHeight) - 15,
            docscrollx: window.pageXOffset || this.standardbody.scrollLeft,
            docscrolly: window.pageYOffset || this.standardbody.scrollTop
        }
        if (!this.dimensions.dropmenuw) {
            this.dimensions.dropmenuw = menu.dropmenu.offsetWidth
            this.dimensions.dropmenuh = menu.dropmenu.offsetHeight
        }
    },

    isContained: function(m, e) {
        var e = window.event || e
        var c = e.relatedTarget || ((e.type == "mouseover") ? e.fromElement : e.toElement)
        while (c && c != m) try { c = c.parentNode } catch (e) { c = m }
        if (c == m)
            return true
        else
            return false
    },

    setopacity: function(el, value) {
        el.style.opacity = value
        if (typeof el.style.opacity != "string") { //if it's not a string (ie: number instead), it means property not supported
            el.style.MozOpacity = value
            if (document.all && typeof el.style.filter == "string") {
                el.style.filter = "progid:DXImageTransform.Microsoft.alpha(opacity=" + value * 100 + ")"
            }
        }
    },

    showmenu: function(menuid) {
        var menu = anylinkcssmenu.menusmap[menuid]
        clearTimeout(menu.hidetimer)
        this.getoffsetof(menu.anchorobj)
        this.getdimensions(menu)
        var posx = menu.anchorobj._offsets.left + (menu.orientation == "lr" ? this.dimensions.anchorw : 0) //base x pos
        var posy = menu.anchorobj._offsets.top + this.dimensions.anchorh - (menu.orientation == "lr" ? this.dimensions.anchorh : 0)//base y pos
        if (posx + this.dimensions.dropmenuw + this.effects.shadow.depth[0] > this.dimensions.docscrollx + this.dimensions.docwidth) { //drop left instead?
            posx = posx - this.dimensions.dropmenuw + (menu.orientation == "lr" ? -this.dimensions.anchorw : this.dimensions.anchorw)
        }
        if (posy + this.dimensions.dropmenuh > this.dimensions.docscrolly + this.dimensions.docheight) {  //drop up instead?
            posy = Math.max(posy - this.dimensions.dropmenuh - (menu.orientation == "lr" ? -this.dimensions.anchorh : this.dimensions.anchorh), this.dimensions.docscrolly) //position above anchor or window's top edge
        }
        if (this.effects.fade.enabled) {
            this.setopacity(menu.dropmenu, 0) //set opacity to 0 so menu appears hidden initially
            if (this.effects.shadow.enabled)
                this.setopacity(menu.shadow, 0) //set opacity to 0 so shadow appears hidden initially
        }
        menu.dropmenu.setcss({ left: posx + 'px', top: posy + 'px', visibility: 'visible' })
        if (this.effects.shadow.enabled)
            menu.shadow.setcss({ left: posx + anylinkcssmenu.effects.shadow.depth[0] + 'px', top: posy + anylinkcssmenu.effects.shadow.depth[1] + 'px', visibility: 'visible' })
        if (this.effects.fade.enabled) {
            clearInterval(menu.animatetimer)
            menu.curanimatedegree = 0
            menu.starttime = new Date().getTime() //get time just before animation is run
            menu.animatetimer = setInterval(function() { anylinkcssmenu.revealmenu(menuid) }, 20)
        }
    },

    revealmenu: function(menuid) {
        var menu = anylinkcssmenu.menusmap[menuid]
        var elapsed = new Date().getTime() - menu.starttime //get time animation has run
        if (elapsed < this.effects.fade.duration) {
            this.setopacity(menu.dropmenu, menu.curanimatedegree)
            if (this.effects.shadow.enabled)
                this.setopacity(menu.shadow, menu.curanimatedegree * this.effects.shadow.opacity)
        }
        else {
            clearInterval(menu.animatetimer)
            this.setopacity(menu.dropmenu, 1)
            menu.dropmenu.style.filter = ""
        }
        menu.curanimatedegree = (1 - Math.cos((elapsed / this.effects.fade.duration) * Math.PI)) / 2
    },

    setcss: function(param) {
        for (prop in param) {
            this.style[prop] = param[prop]
        }
    },

    setcssclass: function(el, targetclass, action) {
        var needle = new RegExp("(^|\\s+)" + targetclass + "($|\\s+)", "ig")
        if (action == "check")
            return needle.test(el.className)
        else if (action == "remove")
            el.className = el.className.replace(needle, "")
        else if (action == "add" && !needle.test(el.className))
            el.className += " " + targetclass
    },

    hidemenu: function(menuid) {
        var menu = anylinkcssmenu.menusmap[menuid]
        clearInterval(menu.animatetimer)
        menu.dropmenu.setcss({ visibility: 'hidden', left: 0, top: 0 })
        menu.shadow.setcss({ visibility: 'hidden', left: 0, top: 0 })
    },

    getElementsByClass: function(targetclass) {
        if (document.querySelectorAll)
            return document.querySelectorAll("." + targetclass)
        else {
            var classnameRE = new RegExp("(^|\\s+)" + targetclass + "($|\\s+)", "i") //regular expression to screen for classname
            var pieces = []
            var alltags = document.all ? document.all : document.getElementsByTagName("*")
            for (var i = 0; i < alltags.length; i++) {
                if (typeof alltags[i].className == "string" && alltags[i].className.search(classnameRE) != -1)
                    pieces[pieces.length] = alltags[i]
            }
            return pieces
        }
    },

    addEvent: function(targetarr, functionref, tasktype) {
        if (targetarr.length > 0) {
            var target = targetarr.shift()
            if (target.addEventListener)
                target.addEventListener(tasktype, functionref, false)
            else if (target.attachEvent)
                target.attachEvent('on' + tasktype, function() { return functionref.call(target, window.event) })
            this.addEvent(targetarr, functionref, tasktype)
        }
    },

    domready: function(functionref) { //based on code from the jQuery library
        if (dd_domreadycheck) {
            functionref()
            return
        }
        // Mozilla, Opera and webkit nightlies currently support this event
        if (document.addEventListener) {
            // Use the handy event callback
            document.addEventListener("DOMContentLoaded", function() {
                document.removeEventListener("DOMContentLoaded", arguments.callee, false)
                functionref();
                dd_domreadycheck = true
            }, false)
        }
        else if (document.attachEvent) {
            // If IE and not an iframe
            // continually check to see if the document is ready
            if (document.documentElement.doScroll && window == window.top) (function() {
                if (dd_domreadycheck) return
                try {
                    // If IE is used, use the trick by Diego Perini
                    // http://javascript.nwbox.com/IEContentLoaded/
                    document.documentElement.doScroll("left")
                } catch (error) {
                    setTimeout(arguments.callee, 0)
                    return;
                }
                //and execute any waiting functions
                functionref();
                dd_domreadycheck = true
            })();
        }
        if (document.attachEvent && parent.length > 0) //account for page being in IFRAME, in which above doesn't fire in IE
            this.addEvent([window], function() { functionref() }, "load");
    },

    addState: function(anchorobj, state) {
        if (anchorobj.getAttribute('data-image')) {
            var imgobj = (anchorobj.tagName == "IMG") ? anchorobj : anchorobj.getElementsByTagName('img')[0]
            if (imgobj) {
                imgobj.src = (state == "add") ? anchorobj.getAttribute('data-overimage') : anchorobj.getAttribute('data-image')
            }
        }
        else
            anylinkcssmenu.setcssclass(anchorobj, "selectedanchor", state)
    },


    setupmenu: function(targetclass, anchorobj, pos) {
        this.standardbody = (document.compatMode == "CSS1Compat") ? document.documentElement : document.body
        var relattr = anchorobj.getAttribute("rel")
        var dropmenuid = relattr.replace(/\[(\w+)\]/, '')
        var menu = this.menusmap[targetclass + pos] = {
            id: targetclass + pos,
            anchorobj: anchorobj,
            dropmenu: document.getElementById(dropmenuid),
            revealtype: (relattr.length != dropmenuid.length && RegExp.$1 == "click") || anylinkcssmenu.ismobile ? "click" : "mouseover",
            orientation: anchorobj.getAttribute("rev") == "lr" ? "lr" : "ud",
            shadow: document.createElement("div")
        }
        menu.anchorobj._internalID = targetclass + pos
        menu.anchorobj._isanchor = true
        menu.dropmenu._internalID = targetclass + pos
        menu.shadow._internalID = targetclass + pos
        menu.shadow.className = "anylinkshadow"
        document.body.appendChild(menu.dropmenu) //move drop down div to end of page
        document.body.appendChild(menu.shadow)
        menu.dropmenu.setcss = this.setcss
        menu.shadow.setcss = this.setcss
        menu.shadow.setcss({ width: menu.dropmenu.offsetWidth + "px", height: menu.dropmenu.offsetHeight + "px" })
        this.setopacity(menu.shadow, this.effects.shadow.opacity)
        this.addEvent([menu.anchorobj, menu.dropmenu, menu.shadow], function(e) { //MOUSEOVER event for anchor, dropmenu, shadow
            var menu = anylinkcssmenu.menusmap[this._internalID]
            if (this._isanchor && menu.revealtype == "mouseover" && !anylinkcssmenu.isContained(this, e)) { //event for anchor
                anylinkcssmenu.showmenu(menu.id)
                anylinkcssmenu.addState(this, "add")
            }
            else if (typeof this._isanchor == "undefined") { //event for drop down menu and shadow
                clearTimeout(menu.hidetimer)
            }
        }, "mouseover")
        this.addEvent([menu.anchorobj, menu.dropmenu, menu.shadow], function(e) { //MOUSEOUT event for anchor, dropmenu, shadow
            if (!anylinkcssmenu.isContained(this, e)) {
                var menu = anylinkcssmenu.menusmap[this._internalID]
                menu.hidetimer = setTimeout(function() {
                    anylinkcssmenu.addState(menu.anchorobj, "remove")
                    anylinkcssmenu.hidemenu(menu.id)
                }, anylinkcssmenu.effects.delayhide)
            }
        }, "mouseout")
        this.addEvent([menu.anchorobj, menu.dropmenu], function(e) { //CLICK event for anchor, dropmenu
            var menu = anylinkcssmenu.menusmap[this._internalID]
            if (this._isanchor && menu.revealtype == "click") {
                if (menu.dropmenu.style.visibility == "visible")
                    anylinkcssmenu.hidemenu(menu.id)
                else {
                    anylinkcssmenu.addState(this, "add")
                    anylinkcssmenu.showmenu(menu.id)
                }
                if (e.preventDefault)
                    e.preventDefault()
                return false
            }
            else
                menu.hidetimer = setTimeout(function() { anylinkcssmenu.hidemenu(menu.id) }, anylinkcssmenu.effects.delayhide)
        }, "click")
    },

    init: function(targetclass) {
        this.domready(function() { anylinkcssmenu.trueinit(targetclass) })
    },

    trueinit: function(targetclass) {
        var anchors = this.getElementsByClass(targetclass)
        var preloadimages = this.preloadimages
        for (var i = 0; i < anchors.length; i++) {
            if (anchors[i].getAttribute('data-image')) { //preload anchor image?
                preloadimages[preloadimages.length] = new Image()
                preloadimages[preloadimages.length - 1].src = anchors[i].getAttribute('data-image')
            }
            if (anchors[i].getAttribute('data-overimage')) { //preload anchor image?
                preloadimages[preloadimages.length] = new Image()
                preloadimages[preloadimages.length - 1].src = anchors[i].getAttribute('data-overimage')
            }
            this.setupmenu(targetclass, anchors[i], i)
        }
    }

}
/* Flex Level Drop Down Menu
* Created: Jan 5th, 2010 by DynamicDrive.com. This notice must stay intact for usage 
* Author: Dynamic Drive at http://www.dynamicdrive.com/
* Visit http://www.dynamicdrive.com/ for full source code
*/

//Version 1.1 (Feb 19th, 2010): Each flex menu (UL) can now be associated with a link dynamically, and/or defined using JavaScript instead of as markup.
//Version 1.2 (July 2nd, 2011): Menu updated to work properly in popular mobile devices such as iPad/iPhone and Android tablets.
//Version 1.3 (Nov 28th, 2011): Script now dynamically adds a class of "selected" to the anchor link while its drop down menu is expanded, for easy styling of the anchor link during its "open" state.

//Usage: $(elementselector).addflexmenu('menuid', options)
//ie:
//jQuery(document).ready(function($){
//$('a.mylinks').addflexmenu('flexmenu1') //apply flex menu with ID "flexmenu1" to links with class="mylinks"
//})

var flexdropdownmenu = {
    arrowpath: '/images/arrow-menu.gif', //full URL or path to arrow image
    animspeed: 200, //reveal animation speed (in milliseconds)
    showhidedelay: [150, 150], //delay before menu appears and disappears when mouse rolls over it, in milliseconds

    //***** NO NEED TO EDIT BEYOND HERE
    startzindex: 1000,
    ismobile: navigator.userAgent.match(/(iPad)|(iPhone)|(iPod)|(android)|(webOS)/i) != null, //boolean check for popular mobile browsers
    builtflexmenuids: [], //ids of flex menus already built (to prevent repeated building of same flex menu)

    positionul: function($, $ul, e, $anchor) {
        var istoplevel = $ul.hasClass('jqflexmenu') //Bool indicating whether $ul is top level flex menu DIV
        var docrightedge = $(document).scrollLeft() + $(window).width() - 40 //40 is to account for shadows in FF
        var docbottomedge = $(document).scrollTop() + $(window).height() - 40
        if (istoplevel) { //if main flex menu DIV
            var offsets = $anchor.offset()
            var anchorsetting = $anchor.data('setting')
            var x = offsets.left + anchorsetting.useroffsets[0] + (anchorsetting.dir == "h" ? $anchor.outerWidth() : 0) //x pos of main flex menu UL
            var y = offsets.top + anchorsetting.useroffsets[1] + (anchorsetting.dir == "h" ? 0 : $anchor.outerHeight())
            x = (x + $ul.data('dimensions').w > docrightedge) ? x - (anchorsetting.useroffsets[0] * 2) - $ul.data('dimensions').w + $anchor.outerWidth() + (anchorsetting.dir == "h" ? -($anchor.outerWidth() * 2) : 0) : x //if not enough horizontal room to the ridge of the cursor
            y = (y + $ul.data('dimensions').h > docbottomedge) ? y - (anchorsetting.useroffsets[1] * 2) - $ul.data('dimensions').h - $anchor.outerHeight() + (anchorsetting.dir == "h" ? ($anchor.outerHeight() * 2) : 0) : y
        }
        else { //if sub level flex menu UL
            var $parentli = $ul.data('$parentliref')
            var parentlioffset = $parentli.offset()
            var x = $ul.data('dimensions').parentliw //x pos of sub UL
            var y = 0
            x = (parentlioffset.left + x + $ul.data('dimensions').w > docrightedge) ? x - $ul.data('dimensions').parentliw - $ul.data('dimensions').w : x //if not enough horizontal room to the ridge parent LI
            y = (parentlioffset.top + $ul.data('dimensions').h > docbottomedge) ? y - $ul.data('dimensions').h + $ul.data('dimensions').parentlih : y
        }
        $ul.css({ left: x, top: y })
    },

    showbox: function($, $target, $flexmenu, e) {
        clearTimeout($flexmenu.data('timers').hidetimer)
        $flexmenu.data('timers').showtimer = setTimeout(function() { $target.addClass('selected'); $flexmenu.show(flexdropdownmenu.animspeed) }, this.showhidedelay[0])
    },

    hidebox: function($, $target, $flexmenu) {
        clearTimeout($flexmenu.data('timers').showtimer)
        $flexmenu.data('timers').hidetimer = setTimeout(function() { $target.removeClass('selected'); $flexmenu.hide(100) }, this.showhidedelay[1]) //hide flex menu plus all of its sub ULs
    },


    buildflexmenu: function($, $menu, $target) {
        $menu.css({ display: 'block', visibility: 'hidden', zIndex: this.startzindex }).addClass('jqflexmenu').appendTo(document.body)
        $menu.bind('mouseenter', function() {
            clearTimeout($menu.data('timers').hidetimer)
        })
        $menu.bind('mouseleave', function() { //hide menu when mouse moves out of it
            flexdropdownmenu.hidebox($, $target, $menu)
        })
        $menu.data('dimensions', { w: $menu.outerWidth(), h: $menu.outerHeight() }) //remember main menu's dimensions
        $menu.data('timers', {})
        var $lis = $menu.find("ul").parent() //find all LIs within menu with a sub UL
        $lis.each(function(i) {
            var $li = $(this).css({ zIndex: 1000 + i })
            var $subul = $li.find('ul:eq(0)').css({ display: 'block' }) //set sub UL to "block" so we can get dimensions
            $subul.data('dimensions', { w: $subul.outerWidth(), h: $subul.outerHeight(), parentliw: this.offsetWidth, parentlih: this.offsetHeight })
            $subul.data('$parentliref', $li) //cache parent LI of each sub UL
            $subul.data('timers', {})
            $li.data('$subulref', $subul) //cache sub UL of each parent LI
            $li.children("a:eq(0)").append( //add arrow images
				'<img src="' + flexdropdownmenu.arrowpath + '" class="rightarrowclass" style="border:0;" />'
			)
            $li.bind(flexdropdownmenu.triggerevt, function(e) { //show sub UL when mouse moves over parent LI
                var $targetul = $(this).css('zIndex', ++flexdropdownmenu.startzindex).addClass("selected").data('$subulref')
                if ($targetul.queue().length <= 1) { //if 1 or less queued animations
                    clearTimeout($targetul.data('timers').hidetimer)
                    $targetul.data('timers').showtimer = setTimeout(function() {
                        flexdropdownmenu.positionul($, $targetul, e)
                        $targetul.show(flexdropdownmenu.animspeed)
                    }, flexdropdownmenu.showhidedelay[0])
                    if (flexdropdownmenu.triggerevt == "click" && $(e.target).next('ul').length == 1) //if LI being clicked on is a menu header
                        return false
                }
            })
            $li.bind('mouseleave', function(e) { //hide sub UL when mouse moves out of parent LI
                var $targetul = $(this).data('$subulref')
                clearTimeout($targetul.data('timers').showtimer)
                $targetul.data('timers').hidetimer = setTimeout(function() { $targetul.hide(100).data('$parentliref').removeClass('selected') }, flexdropdownmenu.showhidedelay[1])
            })
        })
        $menu.find('ul').andSelf().css({ display: 'none', visibility: 'visible' }) //collapse all ULs again
        this.builtflexmenuids.push($menu.get(0).id) //remember id of flex menu that was just built
    },



    init: function($, $target, $flexmenu) {
        this.triggerevt = (this.ismobile) ? "click" : "mouseenter"
        this.showhidedelay[0] = (this.ismobile) ? 0 : this.showhidedelay[0]
        if (this.builtflexmenuids.length == 0) { //only bind click event to document once
            $(document).bind("click", function(e) {
                if (e.button == 0) { //hide all flex menus (and their sub ULs) when left mouse button is clicked
                    $('.jqflexmenu').find('ul').andSelf().hide()
                }
            })
        }
        if (jQuery.inArray($flexmenu.get(0).id, this.builtflexmenuids) == -1) //if this flex menu hasn't been built yet
            this.buildflexmenu($, $flexmenu, $target)
        if ($target.parents().filter('ul.jqflexmenu').length > 0) //if $target matches an element within the flex menu markup, don't bind onflexmenu to that element
            return
        var useroffsets = $target.attr('data-offsets') ? $target.attr('data-offsets').split(',') : [0, 0] //get additional user offsets of menu
        useroffsets = [parseInt(useroffsets[0]), parseInt(useroffsets[1])]
        $target.data('setting', { dir: $target.attr('data-dir'), useroffsets: useroffsets }) //store direction (drop right or down) of menu plus user offsets
        $target.bind(flexdropdownmenu.triggerevt, function(e) {
            $flexmenu.css('zIndex', ++flexdropdownmenu.startzindex)
            flexdropdownmenu.positionul($, $flexmenu, e, $target)
            flexdropdownmenu.showbox($, $target, $flexmenu, e)
            if (flexdropdownmenu.triggerevt == "click")
                e.preventDefault()
        })
        $target.bind("mouseleave", function(e) {
            flexdropdownmenu.hidebox($, $target, $flexmenu)
        })
    }
}

jQuery.fn.addflexmenu = function(flexmenuid, options) {
    var $ = jQuery
    return this.each(function() { //return jQuery obj
        var $target = $(this)
        if (typeof options == "object") { //if options parameter defined
            if (options.dir)
                $target.attr('data-dir', options.dir) //set/overwrite data-dir attr with defined value
            if (options.offsets)
                $target.attr('data-offsets', options.offsets) //set/overwrite data-offsets attr with defined value
        }
        if ($('#' + flexmenuid).length == 1) //check flex menu is defined
            flexdropdownmenu.init($, $target, $('#' + flexmenuid))
    })
};

//By default, add flex menu to anchor links with attribute "data-flexmenu"
jQuery(document).ready(function($) {
    var $anchors = $('*[data-flexmenu]')
    $anchors.each(function() {
        $(this).addflexmenu(this.getAttribute('data-flexmenu'))
    })
})


//ddlistmenu: Function to define a UL list menu dynamically

function ddlistmenu(id, className) {
    var menu = document.createElement('ul')
    if (id)
        menu.id = id
    if (className)
        menu.className = className
    this.menu = menu
}

ddlistmenu.prototype = {
    addItem: function(url, text, target) {
        var li = document.createElement('li')
        li.innerHTML = '<a href="' + url + '" target="' + target + '">' + text + '</a>'
        this.menu.appendChild(li)
        this.li = li
        return this
    },
    addSubMenu: function() {
        var s = new ddlistmenu(null, null)
        this.li.appendChild(s.menu)
        return s

    }
}
$.maxZIndex = $.fn.maxZIndex = function(opt) {
    var def = { inc: 10, group: "*" };
    $.extend(def, opt);
    var zmax = 0;
    $(def.group).each(function() {
        var cur = parseInt($(this).css('z-index'));
        zmax = cur > zmax ? cur : zmax;
    });
    if (!this.jquery)
        return zmax;

    return this.each(function() {
        zmax += def.inc;
        $(this).css("z-index", zmax);
    });
}