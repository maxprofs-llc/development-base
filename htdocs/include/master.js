// warn users about small resolution
var screenW = screen.width;
var screenH	= screen.height;
//if (screenW < 1024 || screenH < 768) alert(UserSettingsAlertsArr['resolution']);

// universal JS centered window-opening function 
function windowOpen(url, winName, width, height, peripherals)
{
	if (!width || !height) 
	{
		var win = window.open(url, 'popWindow');
		win.focus();
		return false;
	}
	
	// adjust for window sizes that are larger than the user's screen:	
	if (width > (screenW - 50)) 	width = screenW - 50;
	if (height > (screenH - 50))	height = screenH - 50;

	// determine x,y for centered window
	var winLeft	= ((screenW - width) / 2) - 16;
	var winTop	= (screenH - height) / 2;

	// open it (peripherals may include resizable, scrollbars, menubar, toolbar, etc)
	var win = window.open(url, winName, "width=" + width + ",height=" + height + ",left=" + winLeft + ",top=" + winTop + (peripherals ? "," + peripherals : ""));
	win.focus();
	
	return false;
}

