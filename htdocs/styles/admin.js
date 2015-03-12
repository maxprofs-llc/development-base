
/***********************************************
* Show Hint script- © Dynamic Drive (www.dynamicdrive.com)
* This notice MUST stay intact for legal use
* Visit http://www.dynamicdrive.com/ for this script and 100s more.
***********************************************/
		
var horizontal_offset="9px" //horizontal offset of hint box from anchor link

/////No further editting needed

var vertical_offset="0" //horizontal offset of hint box from anchor link. No need to change.
var ie=document.all
var ns6=document.getElementById&&!document.all

function getposOffset(what, offsettype){
var totaloffset=(offsettype=="left")? what.offsetLeft : what.offsetTop;
var parentEl=what.offsetParent;
while (parentEl!=null){
totaloffset=(offsettype=="left")? totaloffset+parentEl.offsetLeft : totaloffset+parentEl.offsetTop;
parentEl=parentEl.offsetParent;
}
return totaloffset;
}

function iecompattest(){
return (document.compatMode && document.compatMode!="BackCompat")? document.documentElement : document.body
}

function clearbrowseredge(obj, whichedge){
var edgeoffset=(whichedge=="rightedge")? parseInt(horizontal_offset)*-1 : parseInt(vertical_offset)*-1
if (whichedge=="rightedge"){
var windowedge=ie && !window.opera? iecompattest().scrollLeft+iecompattest().clientWidth-30 : window.pageXOffset+window.innerWidth-40
dropmenuobj.contentmeasure=dropmenuobj.offsetWidth
if (windowedge-dropmenuobj.x < dropmenuobj.contentmeasure)
edgeoffset=dropmenuobj.contentmeasure+obj.offsetWidth+parseInt(horizontal_offset)
}
else{
var windowedge=ie && !window.opera? iecompattest().scrollTop+iecompattest().clientHeight-15 : window.pageYOffset+window.innerHeight-18
dropmenuobj.contentmeasure=dropmenuobj.offsetHeight
if (windowedge-dropmenuobj.y < dropmenuobj.contentmeasure)
edgeoffset=dropmenuobj.contentmeasure-obj.offsetHeight
}
return edgeoffset
}

function showhint(menucontents, obj, e, tipwidth){
if ((ie||ns6) && document.getElementById("hintbox")){
dropmenuobj=document.getElementById("hintbox")
dropmenuobj.innerHTML=menucontents
dropmenuobj.style.left=dropmenuobj.style.top=-500
if (tipwidth!=""){
dropmenuobj.widthobj=dropmenuobj.style
dropmenuobj.widthobj.width=tipwidth
}
dropmenuobj.x=getposOffset(obj, "left")
dropmenuobj.y=getposOffset(obj, "top")
dropmenuobj.style.left=dropmenuobj.x-clearbrowseredge(obj, "rightedge")+obj.offsetWidth+"px"
dropmenuobj.style.top=dropmenuobj.y-clearbrowseredge(obj, "bottomedge")+"px"
dropmenuobj.style.visibility="visible"
obj.onmouseout=hidetip
}
}

function hidetip(e){
dropmenuobj.style.visibility="hidden"
dropmenuobj.style.left="-500px"
}

function createhintbox(){
var divblock=document.createElement("div")
divblock.setAttribute("id", "hintbox")
document.body.appendChild(divblock)
}

if (window.addEventListener)
window.addEventListener("load", createhintbox, false)
else if (window.attachEvent)
window.attachEvent("onload", createhintbox)
else if (document.getElementById)
window.onload=createhintbox

/**
 * DatePicker widget using Prototype and Scriptaculous.
 * (c) 2007-2008 Mathieu Jondet <mathieu@eulerian.com>
 * Eulerian Technologies
 * (c) 2009 Titi Ala'ilima <tigre@pobox.com>
 *
 * DatePicker is freely distributable under the same terms as Prototype.
 *
 * v1.0.0
 */

/***
 * Some general things to keep in mind:
 * - months, when passed around by themselves, typically go from 0 to 11
 */

/**
 * DatePickerUtils object.  Not a class to be instantiated, just an object
 * that holds commonly used values and methods
 */

var DatePickerUtils = {
  oneDayInMs		: 24 * 3600 * 1000,
  _daysInMonth	: [31,28,31,30,31,30,31,31,30,31,30,31],
  /**
   * getMonthDays : given the year and month find the number of days.
   */
  getMonthDays	: function ( year, month ) {
    if (((0 == (year%4)) && 
	 ( (0 != (year%100)) || (0 == (year%400)))) && (month == 1))
      return 29;
    return this._daysInMonth[month];
  },
  /**
   * convertDate : turn an ANSI date or (real) number of days relative to now
   * and returns a Date object.
   */
  parseDate : function(dateString) {
    var dateObj = DatePickerUtils.ansiDateToObject(dateString);
    if (!dateObj) {
      var relDate = parseFloat(dateString);
      dateObj = new Date();
      dateObj.setTime(dateObj.getTime() + dateString * this.oneDayInMs);
    }
    return dateObj;
  },
  /**
   * dateObjectToAnsi - note: year is padded to 4 digits, just in case
   */
  dateObjectToAnsi: function(dateObj) {
    if (!dateObj) return null;
    return dateObj.getFullYear().toPaddedString(4) + '-' +
        (dateObj.getMonth() + 1).toPaddedString(2) + '-' +
        dateObj.getDate().toPaddedString(2);
  },
  /**
   * ansiDateToObject - returns null of it fails to parse
   */
  ansiDateToObject: function(ansiDate) {
    var dateObj = null;
    var parsedDate = String(ansiDate).match(/^(\d+)-0*(\d+)-0*(\d+)$/);
    if (parsedDate)
      dateObj = new Date(parsedDate[1],parsedDate[2] - 1,parsedDate[3]);
    return dateObj;
  },
  /**
   * yearMonthToAnsiStub takes year and (0-based) month and returns the
   * ANSI date minus the two digit date-of-month, e.g. "2009-03-"
   */
  yearMonthToAnsiStub: function(year, month) {
    return year.toPaddedString(4)+'-'+(month+1).toPaddedString(2)+'-';
  },
  /**
   * Standard default filter generators which return DatePickerFilter objects
   */
  /**
   * noDatesBefore takes an ISO date string or a real number indicating how
   * many days relative to the current time to set the cutoff of valid dates.
   * If any time during a given date is valid, the date is allowed.
   */
  noDatesBefore: function (firstDate) {
    return new DatePickerFilter(
      function(year, month) {
	/* Perform our date comparisons with ANSI/ISO date strings */
        var testDate = DatePickerUtils.dateObjectToAnsi(
			     DatePickerUtils.parseDate(firstDate));
	var dateFilter = new Array();
	var monthDays = DatePickerUtils.getMonthDays(year, month);
	var calDate = DatePickerUtils.yearMonthToAnsiStub(year,month);
	for (var i = 1; i <= monthDays; i++)
	  dateFilter[i] = (testDate > (calDate+i.toPaddedString(2)) );

	return dateFilter;
      },
      function(year, month) {
	/* Perform our date comparisons with ANSI/ISO date strings */
        var testDate = 
	  DatePickerUtils.dateObjectToAnsi(DatePickerUtils.parseDate(firstDate));
	var calDate = DatePickerUtils.yearMonthToAnsiStub(year,month) +
	  DatePickerUtils.getMonthDays(year,month);
	return (testDate <= calDate);
      }
      );  
  },
  /**
   * noDatesAfter takes an ISO date string or a real number indicating how
   * many days relative to the current time to set the cutoff of valid dates.
   * If any time during a given date is valid, the date is allowed.
   */
  noDatesAfter: function (firstDate) {
    return new DatePickerFilter(
      function(year, month) {
	/* Perform our date comparisons with ANSI/ISO date strings */
        var testDate = DatePickerUtils.dateObjectToAnsi(
			     DatePickerUtils.parseDate(firstDate));
	var dateFilter = new Array();
	var monthDays = DatePickerUtils.getMonthDays(year, month);
	var calDate = DatePickerUtils.yearMonthToAnsiStub(year,month);
	for (var i = 1; i <= monthDays; i++)
	  dateFilter[i] = (testDate < (calDate+i.toPaddedString(2)) );

	return dateFilter;
      },
      function(year, month) {
	/* Perform our date comparisons with ANSI/ISO date strings */
        var testDate = 
	  DatePickerUtils.dateObjectToAnsi(DatePickerUtils.parseDate(firstDate));
	var calDate = DatePickerUtils.yearMonthToAnsiStub(year,month) + '01';
	return (testDate >= calDate);
      }
      );  
  },
  /**
   * noWeekends returns a filter that excludes Saturdays and Sundays.  No
   * time or demand at the moment for something that deals with locale-specific
   * weekend configurations (e.g. Fri, Sat in the Middle East).
   */
  noWeekends: function () {
    return new DatePickerFilter(
      function(year, month) {
	var dateFilter = new Array();
	var monthDays = DatePickerUtils.getMonthDays(year, month);
	var calDate = new Date(year,month,1);
	for (var i = 1; i <= monthDays; calDate.setFullYear(year,month,++i))
	  dateFilter[i] = ((calDate.getDay() % 6) == 0); // 0 = Sun, 6 = Sat
	return dateFilter;
      },
      null
      );  
  }
}

/**
 * DatePickerFormatter class for matching and stringifying dates.
 *
 * By Arturas Slajus <x11@arturaz.net>.
 */
var DatePickerFormatter = Class.create();
DatePickerFormatter.prototype = {
  /**
   * Create a DatePickerFormatter.
   *
   * format: specify a format by passing 3 value array consisting of
   *   "yyyy", "mm", "dd". Default: ["yyyy", "mm", "dd"].
   *
   * separator: string for splitting the values. Default: "-".
   *
   * Use it like this:
   *   var df = new DatePickerFormatter(["dd", "mm", "yyyy"], "/");
   *   df.current_date();
   *   df.match("7/7/2007");
   */
  initialize: function(format, separator) {
    if (Object.isUndefined(format))
      format = ["yyyy", "mm", "dd"];
    if (Object.isUndefined(separator))
      separator = "-";

    this._format 	= format;
    this.separator	= separator;
                
    this._formatYearIndex	= format.indexOf("yyyy");
    this._formatMonthIndex= format.indexOf("mm");
    this._formatDayIndex	= format.indexOf("dd");
                
    this._yearRegexp	= /^\d{4}$/;
    this._monthRegexp 	= /^0\d|1[012]|\d$/;
    this._dayRegexp 	= /^0\d|[12]\d|3[01]|\d$/;
  },
    
  /**
   * Match a string against date format.
   * Returns: [year, month, day]
   */
  match: function(str) {
    var d = str.split(this.separator);
        
    if (d.length < 3)
      return false;
        
    var year = d[this._formatYearIndex].match(this._yearRegexp);
    if (year) { year = year[0] } else { return false }
    var month = d[this._formatMonthIndex].match(this._monthRegexp);
    if (month) { month = month[0] } else { return false }
    var day = d[this._formatDayIndex].match(this._dayRegexp);
    if (day) { day = day[0] } else { return false }
        
    return [year, month, day];
  },
    
  /**
   * Return current date according to format.
   */
  currentDate: function() {
    var d = new Date;
    return this.dateToString(
			     d.getFullYear(),
			     d.getMonth() + 1,
			     d.getDate()
			     );
  },
    
  /**
   * Return a stringified date according to format.  Note, month is from
   * 1 to 12 here.
   */
  dateToString: function(year, month, day, separator) {
    if (Object.isUndefined(separator))
      separator = this.separator;

    var a = [0, 0, 0];
    a[this._formatYearIndex]	= year;
    a[this._formatMonthIndex] 	= month.toPaddedString(2);
    a[this._formatDayIndex] 	= day.toPaddedString(2);
        
    return a.join(separator);
  }
}; 

/**
 * DatePickerFilter
 * Titi Ala'ilima <tigre@pobox.com>
 */

var DatePickerFilter = Class.create();

DatePickerFilter.prototype = {
  /* A flexible way of blocking dates off from being selected.  Should
     be able to go so far as to hook it into an AJAX-based holiday filter,
     should anyone be kind enough to build one.  Note that validDates and
     validMonthP take 0-based months.
  */
  initialize : function (dateFilterFunction, monthFilterFunction) {
    if (dateFilterFunction) this.badDates = dateFilterFunction;
    if (monthFilterFunction) this.validMonthP = monthFilterFunction;
  },
  /**
   * badDates is a method which takes a fear and (0-based) month and
   * returns an array indexed by the (1-based) date, with value true if
   * the filter says this date is not allowed.  (This way,
   * an empty array equates to an unfiltered month.)
   */
  badDates : null,
  /**
   * validMonthP is a method which takes a fear and (0-based) month and
   * returns a Boolean saying whether or not the month is allowed by this
   * filter
   */
  validMonthP : null,
  /* Using "append" we can string filters together, such as "before date a",
     "after date b", and "not on weekends".  Note: this changes the current
     DatePickerFilter rather than returning a new one.
     Caveat Integrator: This uses closures. These can cause memory leaks (in
     IE) so be careful!
  */
  append : function (nextFilter) {
    if (!this.badDates)
      this.badDates = nextFilter.badDates;
    else if (nextFilter.badDates) {
      var firstBadDates = this.badDates;
      this.badDates = function (year, month) {
	  var results1 = firstBadDates(year,month);
	  var results2 = nextFilter.badDates(year,month);
	  /* An element-wise "or", since if it's bad in one filter, it's
	     bad for the aggregate. */
	  for (var i = 0; i < results1.length; i++)
	    results1[i] = results1[i] || results2[i];
	  return results1;
	};
    }
    if (!this.validMonthP)
      this.validMonthP = nextFilter.validMonthP;
    else if (nextFilter.validMonthP) {
      var firstValidMonthP = this.validMonthP;
      this.validMonthP = function (year, month) {
	  return firstValidMonthP(year,month) && nextFilter.validMonthP(year,month);
      };
    }
    return this; // Just so we can chain filters inline
  }
};


/***********************************************
 Fool-Proof Date Input Script with DHTML Calendar
 by Jason Moon - http://calendar.moonscript.com/dateinput.cfm
 ************************************************/

// Customizable variables
var DefaultDateFormat = 'MM/DD/YYYY'; // If no date format is supplied, this will be used instead
var HideWait = 3; // Number of seconds before the calendar will disappear
var Y2kPivotPoint = 76; // 2-digit years before this point will be created in the 21st century
var UnselectedMonthText = ''; // Text to display in the 1st month list item when the date isn't required
var FontSize = 11; // In pixels
var FontFamily = 'Tahoma';
var CellWidth = 18;
var CellHeight = 16;
var ImageURL = 'images/global/calendar.jpg';
var NextURL = 'images/global/calendar_next.gif';
var PrevURL = 'images/global/calendar_prev.gif';
var CalBGColor = 'white';
var TopRowBGColor = 'buttonface';
var DayBGColor = 'lightgrey';

// Global variables
var ZCounter = 100;
var Today = new Date();
var WeekDays = new Array('S','M','T','W','T','F','S');
var MonthDays = new Array(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
var MonthNames = new Array('January','February','March','April','May','June','July','August','September','October','November','December');

// Write out the stylesheet definition for the calendar
with (document) {
   writeln('<style>');
   writeln('td.calendarDateInput {letter-spacing:normal;line-height:normal;font-family:' + FontFamily + ',Sans-Serif;font-size:' + FontSize + 'px;}');
   writeln('select.calendarDateInput {letter-spacing:.06em;font-family:Verdana,Sans-Serif;font-size:11px;}');
   writeln('input.calendarDateInput {letter-spacing:.06em;font-family:Verdana,Sans-Serif;font-size:11px;}');
   writeln('</style>');
}

// Only allows certain keys to be used in the date field
function YearDigitsOnly(e) {
   var KeyCode = (e.keyCode) ? e.keyCode : e.which;
   return ((KeyCode == 8) // backspace
        || (KeyCode == 9) // tab
        || (KeyCode == 37) // left arrow
        || (KeyCode == 39) // right arrow
        || (KeyCode == 46) // delete
        || ((KeyCode > 47) && (KeyCode < 58)) // 0 - 9
   );
}

// Gets the absolute pixel position of the supplied element
function GetTagPixels(StartTag, Direction) {
   var PixelAmt = (Direction == 'LEFT') ? StartTag.offsetLeft : StartTag.offsetTop;
   while ((StartTag.tagName != 'BODY') && (StartTag.tagName != 'HTML')) {
      StartTag = StartTag.offsetParent;
      PixelAmt += (Direction == 'LEFT') ? StartTag.offsetLeft : StartTag.offsetTop;
   }
   return PixelAmt;
}

// Is the specified select-list behind the calendar?
function BehindCal(SelectList, CalLeftX, CalRightX, CalTopY, CalBottomY, ListTopY) {
   var ListLeftX = GetTagPixels(SelectList, 'LEFT');
   var ListRightX = ListLeftX + SelectList.offsetWidth;
   var ListBottomY = ListTopY + SelectList.offsetHeight;
   return (((ListTopY < CalBottomY) && (ListBottomY > CalTopY)) && ((ListLeftX < CalRightX) && (ListRightX > CalLeftX)));
}

// For IE, hides any select-lists that are behind the calendar
function FixSelectLists(Over) {
   if (navigator.appName == 'Microsoft Internet Explorer') {
      var CalDiv = this.getCalendar();
      var CalLeftX = CalDiv.offsetLeft;
      var CalRightX = CalLeftX + CalDiv.offsetWidth;
      var CalTopY = CalDiv.offsetTop;
      var CalBottomY = CalTopY + (CellHeight * 9);
      var FoundCalInput = false;
      formLoop :
      for (var j=this.formNumber;j<document.forms.length;j++) {
         for (var i=0;i<document.forms[j].elements.length;i++) {
            if (typeof document.forms[j].elements[i].type == 'string') {
               if ((document.forms[j].elements[i].type == 'hidden') && (document.forms[j].elements[i].name == this.hiddenFieldName)) {
                  FoundCalInput = true;
                  i += 3; // 3 elements between the 1st hidden field and the last year input field
               }
               if (FoundCalInput) {
                  if (document.forms[j].elements[i].type.substr(0,6) == 'select') {
                     ListTopY = GetTagPixels(document.forms[j].elements[i], 'TOP');
                     if (ListTopY < CalBottomY) {
                        if (BehindCal(document.forms[j].elements[i], CalLeftX, CalRightX, CalTopY, CalBottomY, ListTopY)) {
                           document.forms[j].elements[i].style.visibility = (Over) ? 'hidden' : 'visible';
                        }
                     }
                     else break formLoop;
                  }
               }
            }
         }
      }
   }
}

// Displays a message in the status bar when hovering over the calendar days
function DayCellHover(Cell, Over, Color, HoveredDay) {
   Cell.style.backgroundColor = (Over) ? DayBGColor : Color;
   if (Over) {
      if ((this.yearValue == Today.getFullYear()) && (this.monthIndex == Today.getMonth()) && (HoveredDay == Today.getDate())) self.status = 'Click to select today';
      else {
         var Suffix = HoveredDay.toString();
         switch (Suffix.substr(Suffix.length - 1, 1)) {
            case '1' : Suffix += (HoveredDay == 11) ? 'th' : 'st'; break;
            case '2' : Suffix += (HoveredDay == 12) ? 'th' : 'nd'; break;
            case '3' : Suffix += (HoveredDay == 13) ? 'th' : 'rd'; break;
            default : Suffix += 'th'; break;
         }
         self.status = 'Click to select ' + this.monthName + ' ' + Suffix;
      }
   }
   else self.status = '';
   return true;
}

// Sets the form elements after a day has been picked from the calendar
function PickDisplayDay(ClickedDay) {
   this.show();
   var MonthList = this.getMonthList();
   var DayList = this.getDayList();
   var YearField = this.getYearField();
   FixDayList(DayList, GetDayCount(this.displayed.yearValue, this.displayed.monthIndex));
   // Select the month and day in the lists
   for (var i=0;i<MonthList.length;i++) {
      if (MonthList.options[i].value == this.displayed.monthIndex) MonthList.options[i].selected = true;
   }
   for (var j=1;j<=DayList.length;j++) {
      if (j == ClickedDay) DayList.options[j-1].selected = true;
   }
   this.setPicked(this.displayed.yearValue, this.displayed.monthIndex, ClickedDay);
   // Change the year, if necessary
   YearField.value = this.picked.yearPad;
   YearField.defaultValue = YearField.value;
}

// Builds the HTML for the calendar days
function BuildCalendarDays() {
   var Rows = 5;
   if (((this.displayed.dayCount == 31) && (this.displayed.firstDay > 4)) || ((this.displayed.dayCount == 30) && (this.displayed.firstDay == 6))) Rows = 6;
   else if ((this.displayed.dayCount == 28) && (this.displayed.firstDay == 0)) Rows = 4;
   var HTML = '<table width="' + (CellWidth * 7) + '" cellspacing="0" cellpadding="1" style="cursor:default">';
   for (var j=0;j<Rows;j++) {
      HTML += '<tr>';
      for (var i=1;i<=7;i++) {
         Day = (j * 7) + (i - this.displayed.firstDay);
         if ((Day >= 1) && (Day <= this.displayed.dayCount)) {
            if ((this.displayed.yearValue == this.picked.yearValue) && (this.displayed.monthIndex == this.picked.monthIndex) && (Day == this.picked.day)) {
               TextStyle = 'color:white;font-weight:bold;'
               BackColor = DayBGColor;
            }
            else {
               TextStyle = 'color:black;'
               BackColor = CalBGColor;
            }
            if ((this.displayed.yearValue == Today.getFullYear()) && (this.displayed.monthIndex == Today.getMonth()) && (Day == Today.getDate())) TextStyle += 'border:1px solid darkred;padding:0px;';
            HTML += '<td align="center" class="calendarDateInput" style="cursor:default;height:' + CellHeight + ';width:' + CellWidth + ';' + TextStyle + ';background-color:' + BackColor + '" onClick="' + this.objName + '.pickDay(' + Day + ')" onMouseOver="return ' + this.objName + '.displayed.dayHover(this,true,\'' + BackColor + '\',' + Day + ')" onMouseOut="return ' + this.objName + '.displayed.dayHover(this,false,\'' + BackColor + '\')">' + Day + '</td>';
         }
         else HTML += '<td class="calendarDateInput" style="height:' + CellHeight + '">&nbsp;</td>';
      }
      HTML += '</tr>';
   }
   return HTML += '</table>';
}

// Determines which century to use (20th or 21st) when dealing with 2-digit years
function GetGoodYear(YearDigits) {
   if (YearDigits.length == 4) return YearDigits;
   else {
      var Millennium = (YearDigits < Y2kPivotPoint) ? 2000 : 1900;
      return Millennium + parseInt(YearDigits,10);
   }
}

// Returns the number of days in a month (handles leap-years)
function GetDayCount(SomeYear, SomeMonth) {
   return ((SomeMonth == 1) && ((SomeYear % 400 == 0) || ((SomeYear % 4 == 0) && (SomeYear % 100 != 0)))) ? 29 : MonthDays[SomeMonth];
}

// Highlights the buttons
function VirtualButton(Cell, ButtonDown) {
   if (ButtonDown) {
      Cell.style.borderLeft = 'buttonshadow 1px solid';
      Cell.style.borderTop = 'buttonshadow 1px solid';
      Cell.style.borderBottom = 'buttonhighlight 1px solid';
      Cell.style.borderRight = 'buttonhighlight 1px solid';
   }
   else {
      Cell.style.borderLeft = 'buttonhighlight 1px solid';
      Cell.style.borderTop = 'buttonhighlight 1px solid';
      Cell.style.borderBottom = 'buttonshadow 1px solid';
      Cell.style.borderRight = 'buttonshadow 1px solid';
   }
}

// Mouse-over for the previous/next month buttons
function NeighborHover(Cell, Over, DateObj) {
   if (Over) {
      VirtualButton(Cell, false);
      self.status = 'Click to view ' + DateObj.fullName;
   }
   else {
      Cell.style.border = 'buttonface 1px solid';
      self.status = '';
   }
   return true;
}

// Adds/removes days from the day list, depending on the month/year
function FixDayList(DayList, NewDays) {
   var DayPick = DayList.selectedIndex + 1;
   if (NewDays != DayList.length) {
      var OldSize = DayList.length;
      for (var k=Math.min(NewDays,OldSize);k<Math.max(NewDays,OldSize);k++) {
         (k >= NewDays) ? DayList.options[NewDays] = null : DayList.options[k] = new Option(k+1, k+1);
      }
      DayPick = Math.min(DayPick, NewDays);
      DayList.options[DayPick-1].selected = true;
   }
   return DayPick;
}

// Resets the year to its previous valid value when something invalid is entered
function FixYearInput(YearField) {
   var YearRE = new RegExp('\\d{' + YearField.defaultValue.length + '}');
   if (!YearRE.test(YearField.value)) YearField.value = YearField.defaultValue;
}

// Displays a message in the status bar when hovering over the calendar icon
function CalIconHover(Over) {
   var Message = (this.isShowing()) ? 'hide' : 'show';
   self.status = (Over) ? 'Click to ' + Message + ' the calendar' : '';
   return true;
}

// Starts the timer over from scratch
function CalTimerReset() {
   eval('clearTimeout(' + this.timerID + ')');
   eval(this.timerID + '=setTimeout(\'' + this.objName + '.show()\',' + (HideWait * 1000) + ')');
}

// The timer for the calendar
function DoTimer(CancelTimer) {
   if (CancelTimer) eval('clearTimeout(' + this.timerID + ')');
   else {
      eval(this.timerID + '=null');
      this.resetTimer();
   }
}

// Show or hide the calendar
function ShowCalendar() {
   if (this.isShowing()) {
      var StopTimer = true;
      this.getCalendar().style.zIndex = --ZCounter;
      this.getCalendar().style.visibility = 'hidden';
      this.fixSelects(false);
   }
   else {
      var StopTimer = false;
      this.fixSelects(true);
      this.getCalendar().style.zIndex = ++ZCounter;
      this.getCalendar().style.visibility = 'visible';
   }
   this.handleTimer(StopTimer);
   self.status = '';
}

// Hides the input elements when the "blank" month is selected
function SetElementStatus(Hide) {
   this.getDayList().style.visibility = (Hide) ? 'hidden' : 'visible';
   this.getYearField().style.visibility = (Hide) ? 'hidden' : 'visible';
   this.getCalendarLink().style.visibility = (Hide) ? 'hidden' : 'visible';
}

// Sets the date, based on the month selected
function CheckMonthChange(MonthList) {
   var DayList = this.getDayList();
   if (MonthList.options[MonthList.selectedIndex].value == '') {
      DayList.selectedIndex = 0;
      this.hideElements(true);
      this.setHidden('');
   }
   else {
      this.hideElements(false);
      if (this.isShowing()) {
         this.resetTimer(); // Gives the user more time to view the calendar with the newly-selected month
         this.getCalendar().style.zIndex = ++ZCounter; // Make sure this calendar is on top of any other calendars
      }
      var DayPick = FixDayList(DayList, GetDayCount(this.picked.yearValue, MonthList.options[MonthList.selectedIndex].value));
      this.setPicked(this.picked.yearValue, MonthList.options[MonthList.selectedIndex].value, DayPick);
   }
}

// Sets the date, based on the day selected
function CheckDayChange(DayList) {
   if (this.isShowing()) this.show();
   this.setPicked(this.picked.yearValue, this.picked.monthIndex, DayList.selectedIndex+1);
}

// Changes the date when a valid year has been entered
function CheckYearInput(YearField) {
   if ((YearField.value.length == YearField.defaultValue.length) && (YearField.defaultValue != YearField.value)) {
      if (this.isShowing()) {
         this.resetTimer(); // Gives the user more time to view the calendar with the newly-entered year
         this.getCalendar().style.zIndex = ++ZCounter; // Make sure this calendar is on top of any other calendars
      }
      var NewYear = GetGoodYear(YearField.value);
      var MonthList = this.getMonthList();
      var NewDay = FixDayList(this.getDayList(), GetDayCount(NewYear, this.picked.monthIndex));
      this.setPicked(NewYear, this.picked.monthIndex, NewDay);
      YearField.defaultValue = YearField.value;
   }
}

// Holds characteristics about a date
function dateObject() {
   if (Function.call) { // Used when 'call' method of the Function object is supported
      var ParentObject = this;
      var ArgumentStart = 0;
   }
   else { // Used with 'call' method of the Function object is NOT supported
      var ParentObject = arguments[0];
      var ArgumentStart = 1;
   }
   ParentObject.date = (arguments.length == (ArgumentStart+1)) ? new Date(arguments[ArgumentStart+0]) : new Date(arguments[ArgumentStart+0], arguments[ArgumentStart+1], arguments[ArgumentStart+2]);
   ParentObject.yearValue = ParentObject.date.getFullYear();
   ParentObject.monthIndex = ParentObject.date.getMonth();
   ParentObject.monthName = MonthNames[ParentObject.monthIndex];
   ParentObject.fullName = ParentObject.monthName + ' ' + ParentObject.yearValue;
   ParentObject.day = ParentObject.date.getDate();
   ParentObject.dayCount = GetDayCount(ParentObject.yearValue, ParentObject.monthIndex);
   var FirstDate = new Date(ParentObject.yearValue, ParentObject.monthIndex, 1);
   ParentObject.firstDay = FirstDate.getDay();
}

// Keeps track of the date that goes into the hidden field
function storedMonthObject(DateFormat, DateYear, DateMonth, DateDay) {
   (Function.call) ? dateObject.call(this, DateYear, DateMonth, DateDay) : dateObject(this, DateYear, DateMonth, DateDay);
   this.yearPad = this.yearValue.toString();
   this.monthPad = (this.monthIndex < 9) ? '0' + String(this.monthIndex + 1) : this.monthIndex + 1;
   this.dayPad = (this.day < 10) ? '0' + this.day.toString() : this.day;
   this.monthShort = this.monthName.substr(0,3).toUpperCase();
   // Formats the year with 2 digits instead of 4
   if (DateFormat.indexOf('YYYY') == -1) this.yearPad = this.yearPad.substr(2);
   // Define the date-part delimiter
   if (DateFormat.indexOf('/') >= 0) var Delimiter = '/';
   else if (DateFormat.indexOf('-') >= 0) var Delimiter = '-';
   else var Delimiter = '';
   // Determine the order of the months and days
   if (/DD?.?((MON)|(MM?M?))/.test(DateFormat)) {
      this.formatted = this.dayPad + Delimiter;
      this.formatted += (RegExp.$1.length == 3) ? this.monthShort : this.monthPad;
   }
   else if (/((MON)|(MM?M?))?.?DD?/.test(DateFormat)) {
      this.formatted = (RegExp.$1.length == 3) ? this.monthShort : this.monthPad;
      this.formatted += Delimiter + this.dayPad;
   }
   // Either prepend or append the year to the formatted date
   this.formatted = (DateFormat.substr(0,2) == 'YY') ? this.yearPad + Delimiter + this.formatted : this.formatted + Delimiter + this.yearPad;
}

// Object for the current displayed month
function displayMonthObject(ParentObject, DateYear, DateMonth, DateDay) {
   (Function.call) ? dateObject.call(this, DateYear, DateMonth, DateDay) : dateObject(this, DateYear, DateMonth, DateDay);
   this.displayID = ParentObject.hiddenFieldName + '_Current_ID';
   this.getDisplay = new Function('return document.getElementById(this.displayID)');
   this.dayHover = DayCellHover;
   this.goCurrent = new Function(ParentObject.objName + '.getCalendar().style.zIndex=++ZCounter;' + ParentObject.objName + '.setDisplayed(Today.getFullYear(),Today.getMonth());');
   if (ParentObject.formNumber >= 0) this.getDisplay().innerHTML = this.fullName;
}

// Object for the previous/next buttons
function neighborMonthObject(ParentObject, IDText, DateMS) {
   (Function.call) ? dateObject.call(this, DateMS) : dateObject(this, DateMS);
   this.buttonID = ParentObject.hiddenFieldName + '_' + IDText + '_ID';
   this.hover = new Function('C','O','NeighborHover(C,O,this)');
   this.getButton = new Function('return document.getElementById(this.buttonID)');
   this.go = new Function(ParentObject.objName + '.getCalendar().style.zIndex=++ZCounter;' + ParentObject.objName + '.setDisplayed(this.yearValue,this.monthIndex);');
   if (ParentObject.formNumber >= 0) this.getButton().title = this.monthName;
}

// Sets the currently-displayed month object
function SetDisplayedMonth(DispYear, DispMonth) {
   this.displayed = new displayMonthObject(this, DispYear, DispMonth, 1);
   // Creates the previous and next month objects
   this.previous = new neighborMonthObject(this, 'Previous', this.displayed.date.getTime() - 86400000);
   this.next = new neighborMonthObject(this, 'Next', this.displayed.date.getTime() + (86400000 * (this.displayed.dayCount + 1)));
   // Creates the HTML for the calendar
   if (this.formNumber >= 0) this.getDayTable().innerHTML = this.buildCalendar();
}

// Sets the current selected date
function SetPickedMonth(PickedYear, PickedMonth, PickedDay) {
   this.picked = new storedMonthObject(this.format, PickedYear, PickedMonth, PickedDay);
   this.setHidden(this.picked.formatted);
   this.setDisplayed(PickedYear, PickedMonth);
}

// The calendar object
function calendarObject(DateName, DateFormat, DefaultDate) {

   /* Properties */
   this.hiddenFieldName = DateName;
   this.monthListID = DateName + '_Month_ID';
   this.dayListID = DateName + '_Day_ID';
   this.yearFieldID = DateName + '_Year_ID';
   this.monthDisplayID = DateName + '_Current_ID';
   this.calendarID = DateName + '_ID';
   this.dayTableID = DateName + '_DayTable_ID';
   this.calendarLinkID = this.calendarID + '_Link';
   this.timerID = this.calendarID + '_Timer';
   this.objName = DateName + '_Object';
   this.format = DateFormat;
   this.formNumber = -1;
   this.picked = null;
   this.displayed = null;
   this.previous = null;
   this.next = null;

   /* Methods */
   this.setPicked = SetPickedMonth;
   this.setDisplayed = SetDisplayedMonth;
   this.checkYear = CheckYearInput;
   this.fixYear = FixYearInput;
   this.changeMonth = CheckMonthChange;
   this.changeDay = CheckDayChange;
   this.resetTimer = CalTimerReset;
   this.hideElements = SetElementStatus;
   this.show = ShowCalendar;
   this.handleTimer = DoTimer;
   this.iconHover = CalIconHover;
   this.buildCalendar = BuildCalendarDays;
   this.pickDay = PickDisplayDay;
   this.fixSelects = FixSelectLists;
   this.setHidden = new Function('D','if (this.formNumber >= 0) this.getHiddenField().value=D');
   // Returns a reference to these elements
   this.getHiddenField = new Function('return document.forms[this.formNumber].elements[this.hiddenFieldName]');
   this.getMonthList = new Function('return document.getElementById(this.monthListID)');
   this.getDayList = new Function('return document.getElementById(this.dayListID)');
   this.getYearField = new Function('return document.getElementById(this.yearFieldID)');
   this.getCalendar = new Function('return document.getElementById(this.calendarID)');
   this.getDayTable = new Function('return document.getElementById(this.dayTableID)');
   this.getCalendarLink = new Function('return document.getElementById(this.calendarLinkID)');
   this.getMonthDisplay = new Function('return document.getElementById(this.monthDisplayID)');
   this.isShowing = new Function('return !(this.getCalendar().style.visibility != \'visible\')');

   /* Constructor */
   // Functions used only by the constructor
   function getMonthIndex(MonthAbbr) { // Returns the index (0-11) of the supplied month abbreviation
      for (var MonPos=0;MonPos<MonthNames.length;MonPos++) {
         if (MonthNames[MonPos].substr(0,3).toUpperCase() == MonthAbbr.toUpperCase()) break;
      }
      return MonPos;
   }
   function SetGoodDate(CalObj, Notify) { // Notifies the user about their bad default date, and sets the current system date
      CalObj.setPicked(Today.getFullYear(), Today.getMonth(), Today.getDate());
      if (Notify) alert('WARNING: The supplied date is not in valid \'' + DateFormat + '\' format: ' + DefaultDate + '.\nTherefore, the current system date will be used instead: ' + CalObj.picked.formatted);
   }
   // Main part of the constructor
   if (DefaultDate != '') {
      if ((this.format == 'YYYYMMDD') && (/^(\d{4})(\d{2})(\d{2})$/.test(DefaultDate))) this.setPicked(RegExp.$1, parseInt(RegExp.$2,10)-1, RegExp.$3);
      else {
         // Get the year
         if ((this.format.substr(0,2) == 'YY') && (/^(\d{2,4})(-|\/)/.test(DefaultDate))) { // Year is at the beginning
            var YearPart = GetGoodYear(RegExp.$1);
            // Determine the order of the months and days
            if (/(-|\/)(\w{1,3})(-|\/)(\w{1,3})$/.test(DefaultDate)) {
               var MidPart = RegExp.$2;
               var EndPart = RegExp.$4;
               if (/D$/.test(this.format)) { // Ends with days
                  var DayPart = EndPart;
                  var MonthPart = MidPart;
               }
               else {
                  var DayPart = MidPart;
                  var MonthPart = EndPart;
               }
               MonthPart = (/\d{1,2}/i.test(MonthPart)) ? parseInt(MonthPart,10)-1 : getMonthIndex(MonthPart);
               this.setPicked(YearPart, MonthPart, DayPart);
            }
            else SetGoodDate(this, true);
         }
         else if (/(-|\/)(\d{2,4})$/.test(DefaultDate)) { // Year is at the end
            var YearPart = GetGoodYear(RegExp.$2);
            // Determine the order of the months and days
            if (/^(\w{1,3})(-|\/)(\w{1,3})(-|\/)/.test(DefaultDate)) {
               if (this.format.substr(0,1) == 'D') { // Starts with days
                  var DayPart = RegExp.$1;
                  var MonthPart = RegExp.$3;
               }
               else { // Starts with months
                  var MonthPart = RegExp.$1;
                  var DayPart = RegExp.$3;
               }
               MonthPart = (/\d{1,2}/i.test(MonthPart)) ? parseInt(MonthPart,10)-1 : getMonthIndex(MonthPart);
               this.setPicked(YearPart, MonthPart, DayPart);
            }
            else SetGoodDate(this, true);
         }
         else SetGoodDate(this, true);
      }
   }
}

// Main function that creates the form elements
function DateInput(DateName, Required, DateFormat, DefaultDate) {
   if (arguments.length == 0) document.writeln('<span style="color:red;font-size:' + FontSize + 'px;font-family:' + FontFamily + ';">ERROR: Missing required parameter in call to \'DateInput\': [name of hidden date field].</span>');
   else {
      // Handle DateFormat
      if (arguments.length < 3) { // The format wasn't passed in, so use default
         DateFormat = DefaultDateFormat;
         if (arguments.length < 2) Required = false;
      }
      else if (/^(Y{2,4}(-|\/)?)?((MON)|(MM?M?)|(DD?))(-|\/)?((MON)|(MM?M?)|(DD?))((-|\/)Y{2,4})?$/i.test(DateFormat)) DateFormat = DateFormat.toUpperCase();
      else { // Passed-in DateFormat was invalid, use default format instead
         var AlertMessage = 'WARNING: The supplied date format for the \'' + DateName + '\' field is not valid: ' + DateFormat + '\nTherefore, the default date format will be used instead: ' + DefaultDateFormat;
         DateFormat = DefaultDateFormat;
         if (arguments.length == 4) { // DefaultDate was passed in with an invalid date format
            var CurrentDate = new storedMonthObject(DateFormat, Today.getFullYear(), Today.getMonth(), Today.getDate());
            AlertMessage += '\n\nThe supplied date (' + DefaultDate + ') cannot be interpreted with the invalid format.\nTherefore, the current system date will be used instead: ' + CurrentDate.formatted;
            DefaultDate = CurrentDate.formatted;
         }
         alert(AlertMessage);
      }
      // Define the current date if it wasn't set already
      if (!CurrentDate) var CurrentDate = new storedMonthObject(DateFormat, Today.getFullYear(), Today.getMonth(), Today.getDate());
      // Handle DefaultDate
      if (arguments.length < 4) { // The date wasn't passed in
         DefaultDate = (Required) ? CurrentDate.formatted : ''; // If required, use today's date
      }
      // Creates the calendar object!
      eval(DateName + '_Object=new calendarObject(\'' + DateName + '\',\'' + DateFormat + '\',\'' + DefaultDate + '\')');
      // Determine initial viewable state of day, year, and calendar icon
      if ((Required) || (arguments.length == 4)) {
         var InitialStatus = '';
         var InitialDate = eval(DateName + '_Object.picked.formatted');
      }
      else {
         var InitialStatus = ' style="visibility:hidden"';
         var InitialDate = '';
         eval(DateName + '_Object.setPicked(' + Today.getFullYear() + ',' + Today.getMonth() + ',' + Today.getDate() + ')');
      }
      // Create the form elements
      with (document) {
         writeln('<input type="hidden" name="' + DateName + '" value="' + InitialDate + '">');
         // Find this form number
         for (var f=0;f<forms.length;f++) {
            for (var e=0;e<forms[f].elements.length;e++) {
               if (typeof forms[f].elements[e].type == 'string') {
                  if ((forms[f].elements[e].type == 'hidden') && (forms[f].elements[e].name == DateName)) {
                     eval(DateName + '_Object.formNumber='+f);
                     break;
                  }
               }
            }
         }
         writeln('<table cellpadding="0" cellspacing="2"><tr>' + String.fromCharCode(13) + '<td valign="middle">');
         writeln('<select class="calendarDateInput" id="' + DateName + '_Month_ID" onChange="' + DateName + '_Object.changeMonth(this)">');
         if (!Required) {
            var NoneSelected = (DefaultDate == '') ? ' selected' : '';
            writeln('<option value=""' + NoneSelected + '>' + UnselectedMonthText + '</option>');
         }
         for (var i=0;i<12;i++) {
            MonthSelected = ((DefaultDate != '') && (eval(DateName + '_Object.picked.monthIndex') == i)) ? ' selected' : '';
            writeln('<option value="' + i + '"' + MonthSelected + '>' + MonthNames[i].substr(0,3) + '</option>');
         }
         writeln('</select>' + String.fromCharCode(13) + '</td>' + String.fromCharCode(13) + '<td valign="middle">');
         writeln('<select' + InitialStatus + ' class="calendarDateInput" id="' + DateName + '_Day_ID" onChange="' + DateName + '_Object.changeDay(this)">');
         for (var j=1;j<=eval(DateName + '_Object.picked.dayCount');j++) {
            DaySelected = ((DefaultDate != '') && (eval(DateName + '_Object.picked.day') == j)) ? ' selected' : '';
            writeln('<option' + DaySelected + '>' + j + '</option>');
         }
         writeln('</select>' + String.fromCharCode(13) + '</td>' + String.fromCharCode(13) + '<td valign="middle">');
         writeln('<input' + InitialStatus + ' class="calendarDateInput" type="text" id="' + DateName + '_Year_ID" size="' + eval(DateName + '_Object.picked.yearPad.length') + '" maxlength="' + eval(DateName + '_Object.picked.yearPad.length') + '" title="Year" value="' + eval(DateName + '_Object.picked.yearPad') + '" onKeyPress="return YearDigitsOnly(window.event)" onKeyUp="' + DateName + '_Object.checkYear(this)" onBlur="' + DateName + '_Object.fixYear(this)">');
         write('<td valign="middle">' + String.fromCharCode(13) + '<a' + InitialStatus + ' id="' + DateName + '_ID_Link" href="javascript:' + DateName + '_Object.show()" onMouseOver="return ' + DateName + '_Object.iconHover(true)" onMouseOut="return ' + DateName + '_Object.iconHover(false)"><img src="' + ImageURL + '" align="baseline" title="Calendar" border="0"></a>&nbsp;');
         writeln('<span id="' + DateName + '_ID" style="position:absolute;visibility:hidden;width:' + (CellWidth * 7) + 'px;background-color:' + CalBGColor + ';border:1px solid dimgray;" onMouseOver="' + DateName + '_Object.handleTimer(true)" onMouseOut="' + DateName + '_Object.handleTimer(false)">');
         writeln('<table width="' + (CellWidth * 7) + '" cellspacing="0" cellpadding="1">' + String.fromCharCode(13) + '<tr style="background-color:' + TopRowBGColor + ';">');
         writeln('<td id="' + DateName + '_Previous_ID" style="cursor:default" align="center" class="calendarDateInput" style="height:' + CellHeight + '" onClick="' + DateName + '_Object.previous.go()" onMouseDown="VirtualButton(this,true)" onMouseUp="VirtualButton(this,false)" onMouseOver="return ' + DateName + '_Object.previous.hover(this,true)" onMouseOut="return ' + DateName + '_Object.previous.hover(this,false)" title="' + eval(DateName + '_Object.previous.monthName') + '"><img src="' + PrevURL + '"></td>');
         writeln('<td id="' + DateName + '_Current_ID" style="cursor:pointer" align="center" class="calendarDateInput" style="height:' + CellHeight + '" colspan="5" onClick="' + DateName + '_Object.displayed.goCurrent()" onMouseOver="self.status=\'Click to view ' + CurrentDate.fullName + '\';return true;" onMouseOut="self.status=\'\';return true;" title="Show Current Month">' + eval(DateName + '_Object.displayed.fullName') + '</td>');
         writeln('<td id="' + DateName + '_Next_ID" style="cursor:default" align="center" class="calendarDateInput" style="height:' + CellHeight + '" onClick="' + DateName + '_Object.next.go()" onMouseDown="VirtualButton(this,true)" onMouseUp="VirtualButton(this,false)" onMouseOver="return ' + DateName + '_Object.next.hover(this,true)" onMouseOut="return ' + DateName + '_Object.next.hover(this,false)" title="' + eval(DateName + '_Object.next.monthName') + '"><img src="' + NextURL + '"></td></tr>' + String.fromCharCode(13) + '<tr>');
         for (var w=0;w<7;w++) writeln('<td width="' + CellWidth + '" align="center" class="calendarDateInput" style="height:' + CellHeight + ';width:' + CellWidth + ';font-weight:bold;border-top:1px solid dimgray;border-bottom:1px solid dimgray;">' + WeekDays[w] + '</td>');
         writeln('</tr>' + String.fromCharCode(13) + '</table>' + String.fromCharCode(13) + '<span id="' + DateName + '_DayTable_ID">' + eval(DateName + '_Object.buildCalendar()') + '</span>' + String.fromCharCode(13) + '</span>' + String.fromCharCode(13) + '</td>' + String.fromCharCode(13) + '</tr>' + String.fromCharCode(13) + '</table>');
      }
   }
}