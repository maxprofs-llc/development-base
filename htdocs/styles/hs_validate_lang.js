<!--
// if(document.theForm.page.value > 1) { window.history.forward(1); };
function checkWholeForm(theForm)
{
	if(theForm.qset.value == "espanol"){
		return doSpanishHRAFormCheck(theForm, true);}
	else	{
		return doHRAFormCheck(theForm, true);}
}
function doHRAFormCheck(theForm, showAlert) {
    var why = "";
    if ((theForm.page.value == 1) || (theForm.assessment.value == "FIT") || (theForm.assessment.value == "DRC")) {
     	why += checkYear(theForm.birth_year.value);
     	why += checkthisdate(theForm.birth_month.value, theForm.birth_date.value, theForm.birth_year.value);
    	why += checkSEX(theForm.sex.value);
    	if (theForm.assessment.value != "GWB") {
			why += checkWeight(theForm.weight.value);
			why += checkDropdown(theForm.height.value, "You did not enter your height.\n");		
    	}
    	if (theForm.assessment.value != "GWB" && theForm.assessment.value != "FIT") {
    		why += checkDropdown(theForm.race.value, "You did not enter your race.\n");
    	}
    	if ((theForm.assessment.value == "GHA")) {
    		why += checkDropdown(theForm.smoke_status.value, "You did not enter your tobacco use.\n");
    	}
    }
    if (theForm.assessment.value == "FIT") {
    		why += checkWaist(theForm.waist.value);
    		why += checkFrame(theForm.elbow.value, theForm.wrist.value);
    		why += checkRange(theForm.flexibility.value, 1, 40, 0, "Your flexibility number must be between 1 and 40.\n", "flexibility");
    		why += checkRange(theForm.pulse_rate_30_seconds.value, 15, 200, 0, "Your step score (30 second pulse) must be between 15 and 200.\n", "step score");
    		why += checkRange(theForm.sit_up.value, 0, 300, 1, "Your situps must be between 0 and 300.\n", "situps");
    		why += checkRange(theForm.push_ups.value, 0, 300, 1, "Your push-ups must be between 0 and 300.\n", "push-ups");
    }
    if (theForm.assessment.value == "DRC") {
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
    if ( ((theForm.page.value == 2) && (theForm.assessment.value == "HRA")) || ( (theForm.page.value == 5) && (theForm.assessment.value == "GHA")) ){
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
    }
    if ( ( (theForm.page.value == 4) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "CRC") ) || ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ) ) {
     	why += checkSys(theForm.bp_sys.value);
     	why += checkDias(theForm.bp_dias.value);
     	why += checkChol(theForm.cholesterol.value);
     	why += checkHDL(theForm.hdl.value);
    }
    if ( (theForm.page.value == 2) && (theForm.assessment.value == "CRC") ){
    		why += checkDropdown(theForm.diabetes.value, "You did not enter your diabetes status.\n");
     		why += checkDropdown(theForm.heart_attack.value, "You did not enter your heart history.\n");
    		why += checkDropdown(theForm.family_heart_attack.value, "You did not enter your family history.\n");
    		why += checkDropdown(theForm.loss.value, "You did not enter information about recent loss.\n");
    		why += checkDropdown(theForm.stress.value, "You did not enter information about stress.\n");
    }
    if ( (theForm.page.value == 4) && (theForm.assessment.value == "CRC") ){
    		why += checkDropdown(theForm.smoke_status.value, "You did not enter your tobacco use.\n");
    		why += isEmpty(theForm.exercise.value, "You did not enter your exercise.\n");
    		why += checkDropdown(theForm.fiber.value, "You did not enter your fiber.\n");
    		why += checkDropdown(theForm.fat.value, "You did not enter information about your fat intake.\n");
    }
    if ( ( (theForm.page.value == 5) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "GHA") ) ){
		if ( (theForm.assessment.value == "HRA") ){
			why += checkDropdown(theForm.smoke_status.value, "You did not enter your tobacco use.\n");
    		}
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
    		if(theForm.smoke_status.value == "Used to smoke or chew"){
    			why += checkRange(theForm.cigarette_years_quit.value, 1, 80, 0, "Your cigarette years quit must be between 1 and 80.\n", "years quit");
    			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "Your cigarettes smoke a day must be between 1 and 80.\n", "cigarettes a day");
    		}
    		if(theForm.smoke_status.value == "Still smoke or chew"){
    			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "Your cigarettes smoke a day must be between 1 and 80.\n", "cigarettes a day");
    		}
    }
    if ( (theForm.page.value == 3) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.fat.value, "You did not enter your fat intake.\n");
    		why += checkDropdown(theForm.fiber.value, "You did not enter your fiber intake.\n");
    }
    if ( (theForm.page.value == 5) && (theForm.assessment.value == "GHA") ){
    		why += checkRange(theForm.drinks_week.value, 0, 100, 1, "Your alcoholic drinks in a week should be between 0 and 100.\n", "alcoholic drinks");
    		why += checkDropdown(theForm.exercise.value, "You did not enter your exercise information.\n");
    }
    if ( (theForm.page.value == 6) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.overall_health.value, "You did not enter your overall health status.\n");
    		why += checkDropdown(theForm.life_satisfaction.value, "You did not enter your life satisfaction.\n");
    		why += checkDropdown(theForm.loss.value, "You did not enter about any losses.\n");
    		why += checkDropdown(theForm.violence.value, "You did not enter about any violence.\n");
    }
    if ( (theForm.page.value == 7) && (theForm.assessment.value == "HRA") ){
    		why += checkDropdown(theForm.breads_check.value, "You did not enter your bread intake.\n");
    		why += checkDropdown(theForm.fruits_check.value, "You did not enter your fruit intake.\n");
    		why += checkDropdown(theForm.vegetables_check.value, "You did not enter vegetables intake.\n");
    		why += checkDropdown(theForm.meats_check.value, "You did not enter your meats intake.\n");
    		why += checkDropdown(theForm.fatty_meats_check.value, "You did not enter your fatty meats intake.\n");
    		why += checkDropdown(theForm.rich_breads_check.value, "You did not enter your rich breads intake.\n");
    		why += checkDropdown(theForm.desserts_check.value, "You did not enter your desserts intake.\n");
    }
    if ( (theForm.page.value == 8) && (theForm.assessment.value == "HRA") ){
    		why += checkRange(theForm.drinks_week.value, 0, 100, 1, "Your alcoholic drinks in a week should be between 0 and 100.\n", "alcoholic drinks");
    }
    if ( ( (theForm.page.value == 9) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 4) && (theForm.assessment.value == "GHA") ) ){
    		theForm.miles_car.value = niceNum(theForm.miles_car.value);
  		theForm.miles_motorcycle.value = niceNum(theForm.miles_motorcycle.value);
    		why += checkDropdown(theForm.travel_mode.value, "You did not enter your travel mode.\n");
    		why += checkDropdown(theForm.seat_belt.value, "You did not enter your seat belt habits.\n");
    		why += checkDropdown(theForm.helmet.value, "You did not enter your helmet information.\n");
    		why += checkDropdown(theForm.speed.value, "You did not enter your driving speed habits.\n");
    		why += checkRange(theForm.drink_and_drive.value, 0, 25, 1, "Your riding with drunk drivers number should be between 0 and 25.\n", "riding with drunk drivers");
    }
    if ( (theForm.page.value == 10) && (theForm.assessment.value == "HRA") ){
    		why += checkDropdown(theForm.exercise.value, "You did not enter your exercise information.\n");
    }
    if ( (theForm.page.value == 12) && (theForm.assessment.value == "HRA") ){
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
       if (showAlert) {
        alert(why);
        }
       return false;
    }
return true;
}

function doSpanishHRAFormCheck(theForm, showAlert) {
    var why = "";
    if ((theForm.page.value == 1) || (theForm.assessment.value == "FIT") || (theForm.assessment.value == "DRC")) {
     	why += checkYear(theForm.birth_year.value);
     	why += checkthisdate(theForm.birth_month.value, theForm.birth_date.value, theForm.birth_year.value);
    	why += checkSEX(theForm.sex.value);
    	if (theForm.assessment.value != "GWB") {
			why += checkWeight(theForm.weight.value);
			why += checkDropdown(theForm.height.value, "Usted no ingresó su altura.\n");		
    	}
    	if (theForm.assessment.value != "GWB" && theForm.assessment.value != "FIT") {
    		why += checkDropdown(theForm.race.value, "Usted no ingresó su raza.\n");
    	}
    	if ((theForm.assessment.value == "GHA")) {
    		why += checkDropdown(theForm.smoke_status.value, "Usted no ingresó su uso de tabaco.\n");
    	}
    }
    if ( ((theForm.page.value == 2) && (theForm.assessment.value == "HRA")) || ( (theForm.page.value == 5) && (theForm.assessment.value == "GHA")) ){
    	if (theForm.sex.value == "Male"){
    		why += checkDropdown(theForm.rectal_male.value, "Usted no ingresó la información de su examen de próstata.\n");
    	}
    	if (theForm.sex.value == "Female"){
    		why += checkDropdown(theForm.menarche_female.value, "Usted no ingresó su información menstrual.\n");
    		why += checkDropdown(theForm.birth_age_female.value, "Usted no ingresó su información de parto.\n");
    		why += checkDropdown(theForm.mammogram_female.value, "Usted no ingresó el historial de sus mamografías.\n");
    		why += checkDropdown(theForm.fam_breast_cancer.value, "Usted no ingresó su historial familiar.\n");
    		why += checkDropdown(theForm.pap_female.value, "Usted no ingresó el historial de su examen de Papanicolau.\n");
    		why += checkDropdown(theForm.hyst_female.value, "Usted no ingresó el estado de su histerectomía.\n");
    		why += checkDropdown(theForm.self_breast_exam.value, "Usted no ingresó la información de su autoexamen de mama.\n");
    		why += checkDropdown(theForm.clinic_breast_exam.value, "Usted no ingresó la información de su examen clínico de mama.\n");
    		why += checkDropdown(theForm.rectal_female.value, "Usted no ingresó la información de su examen rectal.\n");
    	}
    }
    if ( ( (theForm.page.value == 4) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "CRC") ) || ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ) ) {
     	why += checkSys(theForm.bp_sys.value);
     	why += checkDias(theForm.bp_dias.value);
     	why += checkChol(theForm.cholesterol.value);
     	why += checkHDL(theForm.hdl.value);
    }
    if ( ( (theForm.page.value == 5) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "GHA") ) ){
    		if(theForm.smoke_status.value != "Never smoked"){
			why += checkDropdown(theForm.cigars_day.value, "Usted no ingresó cuántos puros fuma.\n");
			why += checkDropdown(theForm.chews_day.value, "Usted no ingresó si usa tabaco sin humo.\n");
			why += checkDropdown(theForm.pipes_day.value, "Usted no ingresó cuántas pipas fuma.\n");
		}
    		if(theForm.smoke_status.value == "Never smoked"){
    			if(theForm.cigars_day.value == ''){ theForm.cigars_day.value = 'None'; }
    			if(theForm.chews_day.value == ''){ theForm.chews_day.value = 'None'; }
    			if(theForm.pipes_day.value == ''){ theForm.pipes_day.value = 'None'; }
    		}
    		if(theForm.smoke_status.value == "Used to smoke or chew"){
    			why += checkRange(theForm.cigarette_years_quit.value, 1, 80, 0, "Los años durante los que dejó de fumar deben fluctuar entre 1 y 80.\n", "año dejar de fumar ");
    			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "Los cigarrillos fumados por día deben fluctuar entre 1 y 80.\n", "cigarrillos al día");
    		}
    		if(theForm.smoke_status.value == "Still smoke or chew"){
    			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "Los cigarrillos fumados por día deben fluctuar entre 1 y 80.\n", "cigarrillos al día");
    		}
    }
    if ( (theForm.page.value == 3) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.fat.value, "Usted no ingresó información sobre su consumo de grasas.\n");
    		why += checkDropdown(theForm.fiber.value, "Usted no ingresó su consumo de fibra.\n");
    }
    if ( (theForm.page.value == 5) && (theForm.assessment.value == "GHA") ){
    		why += checkRange(theForm.drinks_week.value, 0, 100, 1, "Los tragos que toma por semana deberían fluctuar entre 0 y 100.\n", "bebidas alcohólicas");
    		why += checkDropdown(theForm.exercise.value, "Usted no ingresó información de su ejercicio.\n");
    }
    if ( (theForm.page.value == 6) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.overall_health.value, "Usted no ingresó su estado de salud en general.\n");
    		why += checkDropdown(theForm.life_satisfaction.value, "Usted no ingresó el nivel de satisfacción con su vida.\n");
    		why += checkDropdown(theForm.loss.value, "Usted no ingresó información sobre alguna pérdida.\n");
    		why += checkDropdown(theForm.violence.value, "Usted no ingresó información sobre alguna violencia.\n");
    }
    if ( ( (theForm.page.value == 9) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 4) && (theForm.assessment.value == "GHA") ) ){
    		theForm.miles_car.value = niceNum(theForm.miles_car.value);
  		theForm.miles_motorcycle.value = niceNum(theForm.miles_motorcycle.value);
    		why += checkDropdown(theForm.travel_mode.value, "Usted no ingresó su modalidad de viaje.\n");
    		why += checkDropdown(theForm.seat_belt.value, "Usted no ingresó sus hábitos de uso del cinturón de seguridad.\n");
    		why += checkDropdown(theForm.helmet.value, "Usted no ingresó información de su casco.\n");
    		why += checkDropdown(theForm.speed.value, "Usted no ingresó sus hábitos de velocidad de manejo.\n");
    		why += checkRange(theForm.drink_and_drive.value, 0, 25, 1, "Su número de viajes con conductores ebrios debería fluctuar entre 0 y 25.\n", "caballo con conductores ebrios");
    }

    if (why != "") {
       if (showAlert) {
        alert(why);
        }
       return false;
    }
return true;
}
function checkRange(entered, min, max, zero, msg, fldname) {
    var error = "";
    if (entered == "" && zero != '1') {
    	if(theForm.qset.value == 'espanol'){
    		error = "Usted no ingresó su " + fldname + ".\n";}
    	else	{
        	error = "You did not enter your " + fldname + ".\n";}
    }
    num = niceNum(entered);
    if (num < min || num > max) {
    	error += msg;
    }
    return error;
}

function checkWeight(weight) {
    var error = "";
    if (weight == "") 
    {
    	if(theForm.qset.value == 'espanol'){
    		error = "Usted no ingresó su peso.\n";}
    	else	{
        	error = "You did not enter your weight.\n";}
    }

    num = niceNum(weight);

    if (num < 50 || num > 700) {
    	if(theForm.qset.value == 'espanol'){
    		error = "El peso debe fluctuar entre 50 y 700 para esta evaluación.\n";}
    	else	{
	    error += "The weight must be between 50 and 700 for this assessment.\n";}
    }
    return error;
}

function checkWaist(waist) {
    var error = "";
    if (waist == "") {
    	if(theForm.qset.value == 'espanol'){
    		error = "Usted no ingresó el tamaño de su cintura.\n";}
    	else	{
       		error = "You didn't enter your waist size.\n";}
    }
    num = niceNum(waist);
   if(theForm.units.value == "Metric" && num < 10 || num >60 )
	{
    	if(theForm.qset.value == 'espanol'){
    		error += "El tamaño de su cintura debe fluctuar entre 10 y 60 para esta evaluación.\n";}
    	else	{
      		error += "The waist must be between 10 and 60 for this assessment.\n";}
	}
	else
	{
    if (num < 10 || num > 90) {
    	if(theForm.qset.value == 'espanol'){
    		error += "El tamaño de su cintura debe fluctuar entre 10 y 90 para esta evaluación.\n";}
    	else	{
    		error += "The waist size must be between 10 and 90 for this assessment.\n";}
    }
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
    var d = new Date();
    var curr_year = d.getFullYear();
    var max_year = curr_year - 17;
    if (year == "") {
    	error = "The year of birth must be between 1900 and ";
    	error += max_year;
    	error += " for this assessment.\n";
    	document.theForm.birth_year.focus();
    }
    num = niceNum(year);
    num = parseInt(num);
    if (num < 1900 || num > max_year) {
    	if(theForm.qset.value == 'espanol'){
    		error = "El año de su nacimiento debe fluctuar entre 1900 y ";}
    	else	{
    		error = "The year of birth must be between 1900 and ";}
    	error += max_year;
    	if(theForm.qset.value == 'espanol'){
    		error += "para esta evaluación.\n";}
    	else	{
    		error += " for this assessment.\n";}
    	document.theForm.birth_year.focus();
    }
    return error;
}

function checkthisdate(month, day, year) {
    var error = "";
    var monthminus = month - 1;
    var dteDate;    
    //set up a Date object based on the day, month and year arguments
    //javascript months start at 0 (0-11 instead of 1-12)
    dteDate=new Date(year,monthminus,day);    
    /*
    Javascript Dates are a little too forgiving and will change the date to a reasonable guess if it's invalid. We'll use this to our advantage by creating the date object and then comparing it to the details we put it. If the Date object is different, then it must have been an invalid date to start with...
    */    
    if((day==dteDate.getDate()) && (monthminus==dteDate.getMonth()) && (year==dteDate.getFullYear())){
    	return error;}
    else	{
    	if(theForm.qset.value == 'espanol'){
    		error = "Usted no ingresó una fecha válida.\n";}
    	else	{
    		error = "You did not enter a valid date.\n";}
    	return error;}
}
    	

function checkSys(systolic) {
    var error = "";
    if (systolic == "" && (theForm.bp_check.value <= 0)) {
    	if(theForm.qset.value == 'espanol'){
    		error = "Usted no ingresó el valor de su presión arterial sistólica.\n";}
    	else	{
        	error = "You didn't enter your systolic blood pressure value.\n";}
    }
    num = niceNum(systolic)
    num = parseInt(num);
  
    if ((num < 90 || num > 300) && (theForm.bp_check.value <= 0)) {
    	if(theForm.qset.value == 'espanol'){
    		error += "El número de su presión arterial sistólica debe fluctuar entre 90 y 300 para esta evaluación.\n";}
    	else	{
    		error += "The systolic blood pressure number must be between 90 and 300 for this assessment.\n";}
    }
	
    return error;
}

function checkDias(diastolic) {
    var error = "";
    if (diastolic == "" && (theForm.bp_check.value <= 0)) {
    	if(theForm.qset.value == 'espanol'){
    		error += "Usted no ingresó el valor de su presión arterial diastólica.\n";}
    	else	{
        	error = "You did not enter your diastolic blood pressure value.\n";}
    }
    num = parseInt(diastolic);
    if ((num < 50 || num > 150) && (theForm.bp_check.value <= 0)) {
    	if(theForm.qset.value == 'espanol'){
    		error += "El número de su presión arterial diastólica debe fluctuar entre 50 y 150 para esta evaluación.\n";}
    	else	{
    		error += "The diastolic blood pressure number must be between 50 and 150 for this assessment.\n";}
    }
    return error;
}

function checkChol(cholesterol) {
    var error = "";
    if (cholesterol == "" && (theForm.cholesterol_check.value <= 0)) {
    	if(theForm.qset.value == 'espanol'){
    		error += "Usted no ingresó el valor total de su colesterol.\n";}
    	else	{
        	error = "You did not enter your total cholesterol value.\n";}
    }

    num = niceNum(cholesterol);
    num = parseInt(num);

    if ((num < 80 || num > 350) && (theForm.cholesterol_check.value <= 0)){
    	if(theForm.qset.value == 'espanol'){
    		error += "El número de su colesterol total debe fluctuar entre 80 y 350 para esta evaluación.\n";}
    	else	{
	    	error += "The total cholesterol number must be between 80 and 350 for this assessment.\n";}
    }

    return error;
}

function checkHDL(hdl) {
    var error = "";
    if (hdl == "" && (theForm.cholesterol_check.value <= 0)) {
    	if(theForm.qset.value == 'espanol'){
    		error = "Usted no ingresó el valor de su colesterol LAD (bueno).\n";}
    	else	{
        	error = "You did not enter your HDL (good) cholesterol value.\n";}
    }
    num = niceNum(hdl);
    num = parseInt(num);
    if ((num < 5 || num > 150) && (theForm.cholesterol_check.value <= 0)){
    	if(theForm.qset.value == 'espanol'){
    		error += "El número de su colesterol total debe fluctuar entre 5 y 150 para esta evaluación.\n";}
    	else	{
    		error += "The total cholesterol number must be between 5 and 150 for this assessment.\n";}
    }
    return error;
}

// Sex

function checkSEX (strng) {
var error = "";
if (strng == "") {
   error = "You did not enter your gender.\n";
}

    if (!(strng == "Male") && !(strng == "Female") ) {
    	if(theForm.qset.value == 'espanol'){
    		error = "El número de su colesterol total debe fluctuar entre 5 y 150 para esta evaluación.\n";}
    	else	{
       		error = "Usted no ingresó su sexo.\n";}
    }
return error;
}


function disable_smoke() {
		if(document.theForm.assessment.value == "CRC" && document.theForm.smoke_status.value == "Never smoked"){
		document.theForm.cigs_a_day.disabled = true;
		var notationS = document.getElementById("cigsdayStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
	}
	if(document.theForm.assessment.value == "DRC" && document.theForm.sex.value != "Male"){
		document.theForm.cigs_a_day.disabled = false;
		var notationS = document.getElementById("cigsdayStatus")
		notationS.innerText = notationS.textContent = ''; 
	}
}

function disable_sex() {
		if(document.theForm.assessment.value == "DRC" && document.theForm.sex.value == "Male"){
		document.theForm.big_kid.disabled = true;
		document.theForm.diabetes_gdm.disabled = true;
		var notationS = document.getElementById("gdmStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
		var notationS = document.getElementById("bigkidStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
	}
	if(document.theForm.assessment.value == "DRC" && document.theForm.sex.value != "Male"){
		document.theForm.big_kid.disabled = false;
		document.theForm.diabetes_gdm.disabled = false;
		var notationS = document.getElementById("gdmStatus")
		notationS.innerText = notationS.textContent = ''; 
		var notationS = document.getElementById("bigkidStatus")
		notationS.innerText = notationS.textContent = ''; 
	}
}

function r2c_weight_check() {
	if(document.theForm.height.value < 30 || document.theForm.weight.value < 10 ){ return }
	var bmi = document.theForm.weight.value / ( document.theForm.height.value  *  document.theForm.height.value  ) * 703;
	if( bmi <= 27 ) {
		document.theForm.r2c_weight.disabled = true;
		var notationS = document.getElementById("r2c_weightStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
		document.theForm.race.focus();
	}
	if( bmi > 27 ) {
		document.theForm.r2c_weight.disabled = false;
		var notationS = document.getElementById("r2c_weightStatus")
		notationS.innerText = notationS.textContent = ''; 
		document.theForm.r2c_weight.focus();
	}
}

function r2c_exercise_check() {

	if(  document.theForm.assessment.value == "DRC" && document.theForm.exercise.value == "Yes") {
		document.theForm.r2c_exercise.disabled = true;
		var notationS = document.getElementById("r2c_exerciseStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
         document.getElementById("dis").style.visibility="visible";
		document.theForm.siblings_have_diabetes.focus();
	}
	if(  document.theForm.assessment.value == "DRC" && document.theForm.exercise.value != "Yes") {
		document.theForm.r2c_exercise.disabled = false;
		var notationS = document.getElementById("r2c_exerciseStatus")
		notationS.innerText = notationS.textContent = ''; 
          document.getElementById("dis").style.visibility="hidden"; 
		document.theForm.r2c_exercise.focus();
	}
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


function num_validate_err(field, name) {
var valid = "0123456789.-"
var ok = "yes";
var temp;
for (var i=0; i<field.length; i++) {
	temp = "" + field.substring(i, i+1);
	if (valid.indexOf(temp) == "-1") ok = "no";
}
if (ok == "no") {
	frmfield = "document.theForm." + name ;
	alert("This must be a number! No commas, spaces or characters. \n"); 
	eval(frmfield + ".value = ''");
	eval(frmfield + ".focus()");
	return false;
   }
   	return true;
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

function gorecords(){
	if (confirm("This will take you back to your Assessment Records page and you will lose any data\n entered on this assessment.  Is this what you want to do?")){
		 window.location.href = "/cgi-bin/hs/assessment_recs.cgi";
	}
}
function logout() {
	if (confirm("You are leaving the assessments area, continue?")) {
		 window.location.href = "/homepage.html"
	}
}
function gohome() {
	if (confirm("If you choose to leave the assessment it\nwill cause your session to logout and you\nwill lose any data entered.  You are leaving\n the assessments area, continue?")) {
		 window.location.href = "/homepage.html"
	}
}

function checkRegForm(theForm) {
    var why = "";
    why += checkName(theForm.db_fullname.value);
    why += checkEmail(theForm.db_email.value);
    why += checkUsername(theForm.db_id.value);
    why += checkPassword(theForm.auth_password.value,theForm.auth_password_entry.value);
    if (why != "") {
       alert(why);
       return false;
    }
return true;
}

function holdThis (theForm) {
//    why += isEmptyString(theForm.siteid.value, "You do not have a valid site ID, check with your administrator.\n");
//    why += checkRegnum(theForm.db_employer.value);
//    why += checkZip(theForm.auth_postal_code.value);
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

    var illegalChars = /[\W]/; // allow only letters and numbers
    
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
	if ((strng.length < 6) || (strng.length > 24)) {
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
	if ((strng.length < 6) || (strng.length > 12)) {
		error = "The registration code must be at least 6 characters long and less than 12.\n";
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


// ZIP 5 or 9 numeric.

function checkZIP (strng) {
var error = "";
if (strng == "") {
   error = "You didn't enter a zip code.\n";
	}
return error;
}       

-->