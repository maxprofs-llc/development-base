<!--
function setfocus() {
  document.theForm.siteid.focus();
}

function checkWholeForm(theForm) {
    var why = "";

    if (theForm.assessment.value == "FIT") {
		why += checkYear(theForm.birth_year.value);
		why += checkSEX(theForm.sex.value);
    		why += checkWeight(theForm.weight.value);
    		why += checkWaist(theForm.waist.value);
    		why += checkFrame(theForm.elbow.value, theForm.wrist.value);
    		why += checkRange(theForm.flexibility.value, 1, 40, 0, "Your flexibility number must be between 1 and 40.\n", "flexibility");
    		why += checkRange(theForm.pulse_rate_30_seconds.value, 15, 200, 0, "Your pulse rate must be between 15 and 200.\n", "step score");
    		why += checkRange(theForm.sit_up.value, 0, 300, 1, "Your situps must be between 0 and 300.\n", "situps");
    		why += checkRange(theForm.push_ups.value, 0, 300, 1, "Your push-ups must be between 0 and 300.\n", "push-ups");
    }
    if (theForm.assessment.value == "DRC") {
		why += checkYear(theForm.birth_year.value);
		why += checkSEX(theForm.sex.value);
    		why += checkDropdown(theForm.race.value, "You did not enter your race.\n");
    		why += checkWeight(theForm.weight.value);
    		why += isEmpty(theForm.exercise.value, "You did not enter your exercise.\n");
    		why += checkDropdown(theForm.siblings_have_diabetes.value, "You did not enter your sibling history.\n");
    		why += checkDropdown(theForm.parents_have_diabetes.value, "You did not enter your parents history.\n");
    		if(theForm.sex.value == "Male"){
    			theForm.big_kid.value = 'No';
    			theForm.diabetes_gdm.value = 'No';
    		}
    		why += checkDropdown(theForm.big_kid.value, "You did not enter your childbirth information.\n");
    		why += checkDropdown(theForm.diabetes_gdm.value, "You did not enter your Gestational Diabetes information.\n");
    }
    if (theForm.assessment.value == "GHA") {
		why += checkYear(theForm.birth_year.value);
		why += checkSEX(theForm.sex.value);
    		why += checkWeight(theForm.weight.value);
    		why += checkDropdown(theForm.race.value, "You did not enter your race.\n");
    		why += checkDropdown(theForm.smoke_status.value, "You did not enter your tobacco use.\n");
		if (theForm.sex.value == "Male"){
			why += checkDropdown(theForm.rectal_male.value, "You did not enter your prostate exam information.\n");
		}
		if (theForm.sex.value == "Female"){
			why += checkDropdown(theForm.menarche_female.value, "You did not enter your menstrual information.\n");
			why += checkDropdown(theForm.birth_age_female.value, "You did not enter your childbirth information.\n");
			why += checkDropdown(theForm.mammogram_female.value, "You did not enter your mammogram history.\n");
			why += checkDropdown(theForm.fam_breast_cancer.value, "You did not enter your family history.\n");
			why += checkDropdown(theForm.pap_female.value, "You did not enter your pap exam history.\n");
			why += checkDropdown(theForm.hyst_female.value, "You did not enter your hysterectomy status.\n");
			why += checkDropdown(theForm.self_breast_exam.value, "You did not enter your self breast exam information.\n");
			why += checkDropdown(theForm.clinic_breast_exam.value, "You did not enter your clinical breast exam information.\n");
			why += checkDropdown(theForm.rectal_female.value, "You did not enter your rectal exam information.\n");
		}
		why += checkSys(theForm.bp_sys.value);
		why += checkDias(theForm.bp_dias.value);
		why += checkChol(theForm.cholesterol.value);
		why += checkHDL(theForm.hdl.value);
    		if(theForm.smoke_status.value != "Never smoked"){
			why += checkDropdown(theForm.cigars_day.value, "You did not enter how many cigars you smoke.\n");
			why += checkDropdown(theForm.chews_day.value, "You did not enter if you use smokeless tobacco.\n");
			why += checkDropdown(theForm.pipes_day.value, "You did not enter how many pipes you smoke.\n");
		}
    		if(theForm.smoke_status.value == "Never smoked"){
    			if(theForm.cigars_day.value == ''){ theForm.cigars_day.value = 'None'; }
    			if(theForm.chews_day.value == ''){ theForm.chews_day.value = 'None'; }
    			if(theForm.pipes_day.value == ''){ theForm.pipes_day.value = 'None'; }
    		}
     		theForm.miles_car.value = niceNum(theForm.miles_car.value);
  		theForm.miles_motorcycle.value = niceNum(theForm.miles_motorcycle.value);
    		why += checkDropdown(theForm.travel_mode.value, "You did not enter your travel mode.\n");
    		why += checkDropdown(theForm.seat_belt.value, "You did not enter your seat belt habits.\n");
    		why += checkDropdown(theForm.helmet.value, "You did not enter your helmet information.\n");
    		why += checkDropdown(theForm.speed.value, "You did not enter your driving speed habits.\n");
    		why += checkRange(theForm.drink_and_drive.value, 0, 25, 1, "Your riding with drunk drivers number should be between 0 and 25.\n", "riding with drunk drivers");
    		why += checkDropdown(theForm.fat.value, "You did not enter your fat intake.\n");
    		why += checkDropdown(theForm.fiber.value, "You did not enter your fiber intake.\n");
   		why += checkRange(theForm.drinks_week.value, 0, 100, 1, "Your alcoholic drinks in a week should be between 0 and 100.\n", "alcoholic drinks");
    		why += checkDropdown(theForm.exercise.value, "You did not enter your exercise information.\n");
    		why += checkDropdown(theForm.overall_health.value, "You did not enter your overall health status.\n");
    		why += checkDropdown(theForm.life_satisfaction.value, "You did not enter your life satisfaction.\n");
    		why += checkDropdown(theForm.loss.value, "You did not enter about any losses.\n");
    		why += checkDropdown(theForm.violence.value, "You did not enter about any violence.\n");
   }
    if (theForm.assessment.value == "GWB") {
		why += checkYear(theForm.birth_year.value);
		why += checkSEX(theForm.sex.value);
    }
    if ( theForm.assessment.value == "CRC" ){
		why += checkYear(theForm.birth_year.value);
		why += checkSEX(theForm.sex.value);
    		why += checkDropdown(theForm.race.value, "You did not enter your race.\n");
    		why += checkWeight(theForm.weight.value);
    		why += checkDropdown(theForm.diabetes.value, "You did not enter your diabetes status.\n");
     		why += checkDropdown(theForm.heart_attack.value, "You did not enter your heart history.\n");
    		why += checkDropdown(theForm.family_heart_attack.value, "You did not enter your family history.\n");
    		why += checkDropdown(theForm.loss.value, "You did not enter information about recent loss.\n");
    		why += checkDropdown(theForm.stress.value, "You did not enter information about stress.\n");
		why += checkSys(theForm.bp_sys.value);
		why += checkDias(theForm.bp_dias.value);
		why += checkChol(theForm.cholesterol.value);
		why += checkHDL(theForm.hdl.value);
    		why += checkDropdown(theForm.smoke_status.value, "You did not enter your tobacco use.\n");
    		why += isEmpty(theForm.exercise.value, "You did not enter your exercise.\n");
    		why += checkDropdown(theForm.fiber.value, "You did not enter your fiber.\n");
    		why += checkDropdown(theForm.fat.value, "You did not enter information about your fat intake.\n");
    }
    if ( theForm.assessment.value == "HRA" ){
		why += checkSys(theForm.bp_sys.value);
		why += checkDias(theForm.bp_dias.value);
		why += checkChol(theForm.cholesterol.value);
		why += checkHDL(theForm.hdl.value);
		why += checkDropdown(theForm.smoke_status.value, "You did not enter your tobacco use.\n");
    		if(theForm.smoke_status.value != "Never smoked"){
			why += checkDropdown(theForm.cigars_day.value, "You did not enter how many cigars you smoke.\n");
			why += checkDropdown(theForm.chews_day.value, "You did not enter if you use smokeless tobacco.\n");
			why += checkDropdown(theForm.pipes_day.value, "You did not enter how many pipes you smoke.\n");
		}
    		if(theForm.smoke_status.value == "Never smoked"){
    			if(theForm.cigars_day.value == ''){ theForm.cigars_day.value = 'None'; }
    			if(theForm.chews_day.value == ''){ theForm.chews_day.value = 'None'; }
    			if(theForm.pipes_day.value == ''){ theForm.pipes_day.value = 'None'; }
    		}
		if (theForm.sex.value == "Male"){
			why += checkDropdown(theForm.rectal_male.value, "You did not enter your prostate exam information.\n");
		}
		if (theForm.sex.value == "Female"){
			why += checkDropdown(theForm.menarche_female.value, "You did not enter your menstrual information.\n");
			why += checkDropdown(theForm.birth_age_female.value, "You did not enter your childbirth information.\n");
			why += checkDropdown(theForm.mammogram_female.value, "You did not enter your mammogram history.\n");
			why += checkDropdown(theForm.fam_breast_cancer.value, "You did not enter your family history.\n");
			why += checkDropdown(theForm.pap_female.value, "You did not enter your pap exam history.\n");
			why += checkDropdown(theForm.hyst_female.value, "You did not enter your hysterectomy status.\n");
			why += checkDropdown(theForm.self_breast_exam.value, "You did not enter your self breast exam information.\n");
			why += checkDropdown(theForm.clinic_breast_exam.value, "You did not enter your clinical breast exam information.\n");
			why += checkDropdown(theForm.rectal_female.value, "You did not enter your rectal exam information.\n");
		}
    		why += checkDropdown(theForm.breads_check.value, "You did not enter your bread intake.\n");
    		why += checkDropdown(theForm.fruits_check.value, "You did not enter your fruit intake.\n");
    		why += checkDropdown(theForm.vegetables_check.value, "You did not enter vegetables intake.\n");
    		why += checkDropdown(theForm.meats_check.value, "You did not enter your meats intake.\n");
    		why += checkDropdown(theForm.fatty_meats_check.value, "You did not enter your fatty meats intake.\n");
    		why += checkDropdown(theForm.rich_breads_check.value, "You did not enter your rich breads intake.\n");
    		why += checkDropdown(theForm.desserts_check.value, "You did not enter your desserts intake.\n");
    		why += checkRange(theForm.drinks_week.value, 0, 100, 1, "Your alcoholic drinks in a week should be between 0 and 100.\n", "alcoholic drinks");
    		theForm.miles_car.value = niceNum(theForm.miles_car.value);
  		theForm.miles_motorcycle.value = niceNum(theForm.miles_motorcycle.value);
    		why += checkDropdown(theForm.travel_mode.value, "You did not enter your travel mode.\n");
    		why += checkDropdown(theForm.seat_belt.value, "You did not enter your seat belt habits.\n");
    		why += checkDropdown(theForm.helmet.value, "You did not enter your helmet information.\n");
    		why += checkDropdown(theForm.speed.value, "You did not enter your driving speed habits.\n");
    		why += checkRange(theForm.drink_and_drive.value, 0, 25, 1, "Your riding with drunk drivers number should be between 0 and 25.\n", "riding with drunk drivers");
    		why += checkDropdown(theForm.exercise.value, "You did not enter your exercise information.\n");
    		why += checkDropdown(theForm.overall_health.value, "You did not enter your overall health status.\n");
    		why += checkDropdown(theForm.life_satisfaction.value, "You did not enter your life satisfaction.\n");
    		why += checkDropdown(theForm.loss.value, "You did not enter about any losses.\n");
    		why += checkDropdown(theForm.q3.value, "You did not enter about your feeling depressed.\n");
    		why += checkDropdown(theForm.q5.value, "You did not enter about your feeling nervous.\n");
    		why += checkDropdown(theForm.q7.value, "You did not enter about your feeling downhearted.\n");
    		why += checkDropdown(theForm.q8.value, "You did not enter about your feeling tense.\n");
    		why += checkDropdown(theForm.q11.value, "You did not enter about your feeling sad.\n");
    		why += checkDropdown(theForm.q17.value, "You did not enter about your feeling anxious.\n");
    		why += checkDropdown(theForm.q19.value, "You did not enter about your feeling relaxed.\n");
    		why += checkDropdown(theForm.q22.value, "You did not enter about your feeling pressure.\n");
    }
    if (why != "") {
       alert(why);
       return false;
    }
return true;
}

function disable_sex() {
	if(document.theForm.sex.value == "M" || document.theForm.sex.value == "m"){
		document.theForm.sex.value = "Male";
		}
	if(document.theForm.sex.value == "F" || document.theForm.sex.value == "f"){
		document.theForm.sex.value = "Female";
		}
	if(document.theForm.sex.value != "Male" && document.theForm.sex.value != "Female"){
		alert("Invalid sex, must be M or F");
		return false;
		}
	if(document.theForm.sex.value == "Male"){
		if(document.theForm.assessment.value == "DRC"){
			document.theForm.big_kid.disabled = true;
			document.theForm.diabetes_gdm.disabled = true;
			}
		if(document.theForm.assessment.value == "GHA"){
			document.theForm.menarche_female.disabled = true;
			document.theForm.birth_age_female.disabled = true;
			document.theForm.mammogram_female.disabled = true;
			document.theForm.fam_breast_cancer.disabled = true;
			document.theForm.self_breast_exam.disabled = true;
			document.theForm.clinic_breast_exam.disabled = true;
			document.theForm.hyst_female.disabled = true;
			document.theForm.pap_female.disabled = true;
			document.theForm.rectal_female.disabled = true;
			document.theForm.rectal_male.disabled = false;
			}
		}
	else 	{
		if(document.theForm.assessment.value == "DRC"){
			document.theForm.big_kid.disabled = false;
			document.theForm.diabetes_gdm.disabled = false;
			}
		if(document.theForm.assessment.value == "GHA"){
			document.theForm.menarche_female.disabled = false;
			document.theForm.birth_age_female.disabled = false;
			document.theForm.mammogram_female.disabled = false;
			document.theForm.fam_breast_cancer.disabled = false;
			document.theForm.self_breast_exam.disabled = false;
			document.theForm.clinic_breast_exam.disabled = false;
			document.theForm.hyst_female.disabled = false;
			document.theForm.pap_female.disabled = false;
			document.theForm.rectal_female.disabled = false;
			document.theForm.rectal_male.disabled = true;
			}
		}
}

function disable_sex_old() {
	if(document.theForm.sex.value == "M" || document.theForm.sex.value == "m"){
		document.theForm.sex.value = "Male";
		}
	if(document.theForm.sex.value == "F" || document.theForm.sex.value == "f"){
		document.theForm.sex.value = "Female";
		}
	if(document.theForm.sex.value != "Male" && document.theForm.sex.value != "Female"){
		alert("Invalid sex, must be M or F");
		return false;
		}
	if(document.theForm.assessment.value == "DRC" && document.theForm.sex.value == "Male"){
		document.theForm.big_kid.disabled = true;
		document.theForm.diabetes_gdm.disabled = true;
	}
	if(document.theForm.assessment.value == "DRC" && document.theForm.sex.value != "Male"){
		document.theForm.big_kid.disabled = false;
		document.theForm.diabetes_gdm.disabled = false;
	}
}

function convert_childage(entered){
	if(entered <= "0" || entered == " " || entered == "No children"){
		entered = "No children";
		}
	else if(entered <= 19 || entered == "Under 20"){
		entered = "Under 20";
		}
	else if((entered >= 20 && entered <= 24) || entered == "20-24"){
		entered = "20-24";
		}
	else if((entered >= 25 && entered <= 29) || entered == "25-29"){
		entered = "25-29";
		}
	else if(entered >= 30 || entered == "Over 30"){
		entered = "Over 30";
		}
	return entered;
	}

function convert_menarche(entered){
	if(entered <= 11 || entered == " " || entered == "11 or under"){
		entered = "11 or under";
		}
	else if((entered == 12 && entered == 13) || entered == "12-13"){
		entered = "12-13";
		}
	else if(entered >= 14 || entered == "14 or older"){
		entered = "14 or older";
		}
	return entered;
	}

function convert_fambreast(entered){
	if(entered == "0" || entered == " " || entered == "None" || entered == "none"){
		entered = "None";
		}
	else if(entered == 1 || entered == "One"  || entered == "one"){
		entered = "One";
		}
	else if(entered >= 2 || entered == "Two or More"){
		entered = "Two or More";
		}
	else if(entered >= "u" || entered == "U" || entered == "Don't know"){
		entered = "Don't know";
		}
	return entered;
	}

function convert_smokes(entered){
	if(entered == 0 || entered == " " || entered == "None" || entered == "none"){
		entered = "None";
		}
	else if(entered == 1 || entered == "One"  || entered == "one"){
		entered = "One";
		}
	else if(entered >= 2 || entered == "Two or more"){
		entered = "Two or more";
		}
	return entered;
	}

function convert_seatbelts(entered){
	if(entered == 0 || entered == " " || entered == "Never" || entered == "never"){
		entered = "Never";
		}
	else if(entered >= 100 || entered == "Always, 100%"){
		entered = "Always, 100%";
		}
	else if((entered >= 1 && entered <= 40) || entered == "Seldom, 1%-40%"){
		entered = "Seldom, 1%-40%";
		}
	else if((entered >= 41 && entered <= 80) || entered == "Sometimes, 41%-80%"){
		entered = "Sometimes, 41%-80%";
		}
	else if((entered >= 81 && entered <= 99) || entered == "Nearly always, 81%-99%"){
		entered = "Nearly always, 81%-99%";
		}
	return entered;
	}

function convert_helmet(entered){
	if(entered == 0 || entered == " " || entered == "Never" || entered == "never"){
		entered = "Never";
		}
	else if(entered >= 100 || entered == "Always, 100%"){
		entered = "Always, 100%";
		}
	else if((entered >= 1 && entered <= 25) || entered == "Seldom, 1%-25%"){
		entered = "Seldom, 1%-25%";
		}
	else if((entered >= 26 && entered <= 75) || entered == "Sometimes, 41%-80%"){
		entered = "Sometimes, 26%-75%";
		}
	else if((entered >= 76 && entered <= 99) || entered == "Nearly always, 81%-99%"){
		entered = "Nearly always, 76%-99%";
		}
	else if(entered == "d" || entered == "D" || entered == "Do not ride"){
		entered = "Do not ride";
		}
	return entered;
	}

function check_yn(entered){
	if(entered == "Y" || entered == "y" || entered == "Yes" || entered == "yes" || entered == "YES"){
		entered = "Yes";
		}
	if(entered == "N" || entered == "n"  || entered == "no"  || entered == "NO" || entered == "No"){
		entered = "No";
		}
	if(entered != "Yes" && entered != "No"){
		alert("Invalid value, must be Y or N");
		return "";
		}
	return entered;
	}

function check_ynu(entered) {
	if(entered == "Y" || entered == "y" || entered == "Yes" || entered == "yes" || entered == "YES"){
		entered = "Yes";
		}
	if(entered == "N" || entered == "n"  || entered == "no"  || entered == "NO" || entered == "No"  || entered == "U" || entered == "u"){
		entered = "No";
		}
	if(entered != "Yes" && entered != "No"){
		alert("Invalid value, must be Y, N or U");
		return "";
		}
	return entered;
	}

function check_batch_date() {
    	var monthLength = new Array(31,28,31,30,31,30,31,31,30,31,30,31);
	var day = niceNum(theForm.birth_date.value);
	var month = niceNum(theForm.birth_month.value);
	var year = niceNum(theForm.birth_year.value);

	if (!day || !month || !year)
		alert("Invalid date please check.");
		return "";

	if (year/4 == niceNum(year/4))
		monthLength[1] = 29;

	if (day > monthLength[month-1])
		alert("Invalid number of days for that month please check.");
		return "";

	monthLength[1] = 28;

	alert("Valid date.");return true;
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

function checkWeight(weight) {
    var error = "";
    if (weight == "") {
        error = "You did not enter your weight.\n";
    }
    num = niceNum(weight);
    if (num < 50 || num > 700) {
    	error += "The weight must be between 50 and 700 for this assessment.\n";
    }
    return error;
}

function checkWaist(waist) {
    var error = "";
    if (waist == "") {
        error = "You didn't enter your waist size.\n";
    }
    num = niceNum(waist);
    if (num < 10 || num > 90) {
    	error += "The waist size must be between 10 and 90 for this assessment.\n";
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

function checkYear(year) {
    var error = "";
    if (year == "") {
        error = "The year of birth must be between 1900 and 1990 for this assessment.\n";
    }
    num = niceNum(year);
    num = parseInt(num);
    if (num < 1900 || num > 1990) {
    	error = "The year of birth must be between 1900 and 1990 for this assessment.\n";
    }
    return error;
}

function checkSys(systolic) {
    var error = "";
    if (systolic == "" && (theForm.bp_check.value <= 0)) {
        error = "You didn't enter your systolic blood pressure value.\n";
    }
    num = niceNum(systolic)
    num = parseInt(num);
    if ((num < 90 || num > 300) && (theForm.bp_check.value <= 0)) {
    	error += "The systolic blood pressure number must be between 90 and 300 for this assessment.\n";
    }
    return error;
}

function checkDias(diastolic) {
    var error = "";
    if (diastolic == "" && (theForm.bp_check.value <= 0)) {
        error = "You did not enter your diastolic blood pressure value.\n";
    }
    num = parseInt(diastolic);
    if ((num < 50 || num > 150) && (theForm.bp_check.value <= 0)) {
    	error += "The diastolic blood pressure number must be between 50 and 150 for this assessment.\n";
    }
    return error;
}

function checkBP() {
    var error = "";
    error = checkSys(theForm.bp_sys.value);
    if (error != "") {
       alert(why);
       theForm.bp_sys.focus();
       return false;
    }
    checkDias(theForm.bp_dias.value);
    if (error != "") {
       alert(why);
       theForm.bp_dias.focus();
       return false;
    }
}


function checkChol(cholesterol) {
    var error = "";
    if (cholesterol == "" && (theForm.cholesterol_check.value <= 0)) {
        error = "You did not enter your total cholesterol value.\n";
    }
    num = niceNum(cholesterol);
    num = parseInt(num);
    if ((num < 110 || num > 350) && (theForm.cholesterol_check.value <= 0)){
    	error += "The total cholesterol number must be between 110 and 350 for this assessment.\n";
    }
    return error;
}

function checkHDL(hdl) {
    var error = "";
    if (hdl == "" && (theForm.cholesterol_check.value <= 0)) {
        error = "You did not enter your HDL (good) cholesterol value.\n";
    }
    num = niceNum(hdl);
    num = parseInt(num);
    if ((num < 5 || num > 150) && (theForm.cholesterol_check.value <= 0)){
    	error += "The total cholesterol number must be between 5 and 150 for this assessment.\n";
    }
    return error;
}

function checkCholesterol() {
    var error = "";
    error = checkChol(theForm.cholesterol.value);
    if (error != "") {
       alert(why);
       theForm.bp_sys.focus();
       return false;
    }
    checkDias(theForm.hdl.value);
    if (error != "") {
       alert(why);
       theForm.bp_dias.focus();
       return false;
    }
}

// Sex

function checkSEX (strng) {
var error = "";
if (strng == "") {
   error = "You did not enter your gender.\n";
}
if(document.theForm.sex.value == "M" || document.theForm.sex.value == "m"){
	document.theForm.sex.value = "Male";
	}
if(document.theForm.sex.value == "F" || document.theForm.sex.value == "f"){
	document.theForm.sex.value = "Female";
	}
    strng = document.theForm.sex.value;	
    if (!(strng == "Male") && !(strng == "Female") ) {
       error = "You did not enter your gender.\n";
    }
return error;
}

function check_exer() {
if(document.theForm.exercise.value == "Y" || document.theForm.exercise.value == "y"){
	document.theForm.exercise.value = "Yes";
	}
if(document.theForm.exercise.value == "N" || document.theForm.exercise.value == "n"){
	document.theForm.exercise.value = "No";
	}
if(document.theForm.exercise.value != "Yes" && document.theForm.exercise.value != "No"){
	alert("Invalid, must be Y or N");
	return false;
	}
}

function check_diabetes_gdm() {
if(document.theForm.diabetes_gdm.value == "Y" || document.theForm.diabetes_gdm.value == "y"){
	document.theForm.diabetes_gdm.value = "Yes";
	}
if(document.theForm.diabetes_gdm.value == "N" || document.theForm.diabetes_gdm.value == "n" || document.theForm.sex.value == "Male"){
	document.theForm.diabetes_gdm.value = "No";
	}
if(document.theForm.diabetes_gdm.value != "Yes" && document.theForm.diabetes_gdm.value != "No"){
	alert("Invalid, must be Y or N");
	return false;
	}
}

function check_big_kid() {
if(document.theForm.big_kid.value == "Y" || document.theForm.big_kid.value == "y"){
	document.theForm.big_kid.value = "Yes";
	}
if(document.theForm.big_kid.value == "N" || document.theForm.big_kid.value == "n" || document.theForm.sex.value == "Male"){
	document.theForm.big_kid.value = "No";
	}
if(document.theForm.big_kid.value != "Yes" && document.theForm.big_kid.value != "No"){
	alert("Invalid, must be Y or N");
	return false;
	}
}

function check_siblings_have_diabetes() {
if(document.theForm.siblings_have_diabetes.value == "Y" || document.theForm.siblings_have_diabetes.value == "y"){
	document.theForm.siblings_have_diabetes.value = "Yes";
	}
if(document.theForm.siblings_have_diabetes.value == "N" || document.theForm.siblings_have_diabetes.value == "n"){
	document.theForm.siblings_have_diabetes.value = "No";
	}
if(document.theForm.siblings_have_diabetes.value != "Yes" && document.theForm.siblings_have_diabetes.value != "No"){
	alert("Invalid, must be Y or N");
	return false;
	}
}

function check_parents_have_diabetes() {
if(document.theForm.parents_have_diabetes.value == "Y" || document.theForm.parents_have_diabetes.value == "y"){
	document.theForm.parents_have_diabetes.value = "Yes";
	}
if(document.theForm.parents_have_diabetes.value == "N" || document.theForm.parents_have_diabetes.value == "n"){
	document.theForm.parents_have_diabetes.value = "No";
	}
if(document.theForm.parents_have_diabetes.value != "Yes" && document.theForm.parents_have_diabetes.value != "No"){
	alert("Invalid, must be Y or N");
	return false;
	}
}

function check_weight() {
    var error = "";
    var weight= document.theForm.weight.value;
    if (weight == "") {
        error = "You did not enter the weight.\n";
    }
    num = niceNum(weight);
    if (num < 50 || num > 700) {
    	error += "The weight must be between 50 and 700.\n";
    }
    if (error != "") {
       alert(error);
       return false;
    }
}

function convert_height(feet, inches) {
    var error = "";
    num_feet = niceNum(feet);
    num_inches = niceNum(inches);
    num_feet = parseInt(num_feet);
    num_inches = parseInt(num_inches);
    if (num_feet < 3 || num_feet > 7) {
    	error += "The feet must be between 3 and 7.\n";
    }
    if (num_inches < 0 || num_inches > 11) {
    	error += "The inches must be between 0 and 11. num_inches=";
    	error += num_inches;
    	error += "\n";
    }
    if (error != "") {
       alert(error);
       return false;
    }
    document.theForm.height.value = (num_feet * 12) + num_inches;
}
function xcheck_batch_date() {
    var error = "";
    var year = document.theForm.birth_year.value;
    var month = document.theForm.birth_month.value;
    var day = document.theForm.birth_date.value;
    if (year == "") {
        alert("The year of birth must be between 1900 and 1990 for this assessment.\n");
        return false;
    }
    num = niceNum(year);
    num = parseInt(num);
    if (num < 1900 || num > 1990) {
    	alert("The year of birth must be between 1900 and 1990 for this assessment.\n");
    	return false;
    }
    var myDateStr = day + ' ' + month + ' ' + year;
    
    /* Using form values, create a new date object
    which looks like "Wed Jan 1 00:00:00 EST 1975". */
    var myDate = new Date( myDateStr );
    
    // Convert the date to a string so we can parse it.
    var myDate_string = myDate.toGMTString();
    
    /* Split the string at every space and put the values into an array so,
    using the previous example, the first element in the array is "Wed", the
    second element is "Jan", the third element is "1", etc. */
    var myDate_array = myDate_string.split( ' ' );
    
    /* If we entered "Feb 31, 1975" in the form, the "new Date()" function
    converts the value to "Mar 3, 1975". Therefore, we compare the month
    in the array with the month we entered into the form. If they match,
    then the date is valid, otherwise, the date is NOT valid. */
    if ( myDate_array[2] != myMonthStr ) {
      alert( myDateStr + '" is NOT a valid date.' );
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
function displayWindow(theURL,winName,width,height,features) {
    var window_width = width;
    var window_height = height;
    var newfeatures= features;
    var window_top = (screen.height-window_height)/2;
    var window_left = (screen.width-window_width)/2;
    newWindow=window.open(''+ theURL + '',''+ winName + '','width=' + window_width + ',height=' + window_height + ',top=' + window_top + ',left=' + window_left + ',features=' + newfeatures + '');
    newWindow.focus();
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



function validateNonZero(eventCalled)
{
	if((eventCalled.smoke_status.value != "Never Smoked") && (eventCalled.cigs_a_day.value == "") || (eventCalled.cigs_a_day.value == 0) )
	{
		alert(" Please enter the number of cigarettes smoked each day.");
		eventCalled.cigs_a_day.focus();
		return false;
	}
}
function disableThis(eventCalled)
{
	if(eventCalled.smoke_status.value == "Never smoked")
	{
		eventCalled.cigs_a_day.value="";
		eventCalled.cigs_a_day.disabled=true;
	}
	else
	{
		eventCalled.cigs_a_day.disabled=false;
	}
}
function validateBP(eventCalled)
{
	if(eventCalled.bp_check.disabled)
	{
		if(eventCalled.bp_sys.value =="")
		{
		alert ("please type the BP details correctly");
		eventCalled.bp_sys.focus();
		return false;
		}
	}
	if(eventCalled.bp_check.disabled)
	{
		if(eventCalled.bp_dias.value =="")
		{
		alert ("please type the BP details correctly");
		eventCalled.bp_dias.focus();
		return false;
		}
	}
	if((!(eventCalled.bp_check.disabled)) && (eventCalled.bp_check.value==""))
	{
		alert ("please Choose the BP details correctly");
		eventCalled.bp_dias.focus();
		return false;
	}

}
function checkOption(eventCalled)
{
	if((eventCalled.bp_sys.value !="" ) || (eventCalled.bp_dias.value !=""))
	{
		eventCalled.bp_check.disabled = true;
	}
	else
	{
		eventCalled.bp_check.disabled = false;
	}
}

-->