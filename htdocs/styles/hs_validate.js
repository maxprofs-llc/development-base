<!--
// if(document.theForm.page.value > 1) { window.history.forward(1); };
var doValidate=true;

function checkWholeForm(theForm)
{ 
	if(theForm.language.value == "espanol" || theForm.language.value == "spanish"){
		return doCheckSpanish(theForm, true);
	}else if(theForm.language.value == "chinese"){
		return doCheckChinese(theForm, true);
	}else{
		return doCheckEnglish(theForm, true);
	}
}

function doCheckEnglish(theForm) {
  if(doValidate){
    var why = "";
		
    if ((theForm.page.value == 1) || (theForm.assessment.value == "FIT") || (theForm.assessment.value == "DRC")) {
    	why += isEmpty(theForm.first_name.value, "You did not enter your first name.\n");
    	why += isEmpty(theForm.last_name.value, "You did not enter your last name.\n");
     	why += checkYear(theForm.birth_year.value);
     	why += checkthisdate(theForm.birth_month.value, theForm.birth_date.value, theForm.birth_year.value);
    	why += checkSEX(theForm.sex.value);
    	if (theForm.assessment.value != "GWB") {
			why += checkWeight(theForm.weight.value);
			why += checkDropdown(theForm.height.value, "You did not enter your height.\n");			
    	}
		if (theForm.assessment.value == 'HRA') {
    		why += isEmpty(theForm.frame_size.value, "You did not enter your frame size.\n");
    	}
    	if (theForm.assessment.value != "GWB" && theForm.assessment.value != "FIT" && !noRace) {
    		why += checkDropdown(theForm.race.value, "You did not enter your race.\n");
    	}
		
    	if ((theForm.assessment.value == "GHA")) {
			if(theForm.waist){
				why += checkWaist(theForm.waist.value);
			}
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
    		if(!noGina){why += checkDropdown(theForm.siblings_have_diabetes.value, "You did not enter your sibling history.\n");}
    		if(!noGina){why += checkDropdown(theForm.parents_have_diabetes.value, "You did not enter your parents history.\n");}
    		if(theForm.sex.value == "Male"){
    			theForm.big_kid.value = 'No';
    			theForm.diabetes_gdm.value = 'No';
    		}
    		why += checkDropdown(theForm.big_kid.value, "You did not enter your childbirth information.\n");
    		why += checkDropdown(theForm.diabetes_gdm.value, "You did not enter your Gestational Diabetes information.\n");
    }
    if ( ( theForm.page.value == 2 && theForm.assessment.value == "HRA" ) || ( theForm.page.value == 5 && theForm.assessment.value == "GHA" ) ){
    	  
		if (theForm.sex.value == "Male"){
    		why += checkDropdown(theForm.rectal_male.value, "You did not enter your prostate exam information.\n");
    	}
    	if (theForm.sex.value == "Female"){
    		why += checkDropdown(theForm.menarche_female.value, "You did not enter your menstrual information.\n");
    		why += checkDropdown(theForm.birth_age_female.value, "You did not enter your childbirth information.\n");
     		why += checkDropdown(theForm.pregnant_female.value, "You did not enter if you are pregnant.\n");
   		why += checkDropdown(theForm.mammogram_female.value, "You did not enter your mammogram history.\n");
  		if(!noGina){why += checkDropdown(theForm.fam_breast_cancer.value, "You did not enter your family history.\n");}
    		why += checkDropdown(theForm.self_breast_exam.value, "You did not enter your self breast exam information.\n");
    		why += checkDropdown(theForm.clinic_breast_exam.value, "You did not enter your clinical breast exam information.\n");
    		why += checkDropdown(theForm.hyst_female.value, "You did not enter your hysterectomy status.\n");
    		why += checkDropdown(theForm.pap_female.value, "You did not enter your pap exam history.\n");
    		why += checkDropdown(theForm.rectal_female.value, "You did not enter your rectal exam information.\n");
    	}
    }
    if ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.diabetes.value, "You did not enter your diabetes status.\n");
    		if(!noGina){why += checkDropdown(theForm.family_diabetes.value, "You did not enter your family history of diabetes.\n");}
     		why += checkDropdown(theForm.heart_attack.value, "You did not enter your heart history.\n");
    		if(!noGina){why += checkDropdown(theForm.family_heart_attack.value, "You did not enter your family history of heart attack.\n");}
    		why += checkDropdown(theForm.bp_meds.value, "You did not enter your blood pressures medication status.\n");
    }
    if ( ( (theForm.page.value == 4) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "CRC") ) || ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ) ) {
     	why += checkSys(theForm.bp_sys.value);
     	why += checkDias(theForm.bp_dias.value);
     	why += checkChol(theForm.cholesterol.value);
		why += checkLDL(theForm.ldl.value);
     	why += checkHDL(theForm.hdl.value);
    }
    
    
    if (  ( (theForm.page.value == 3) && (theForm.assessment.value == "CRC") ) || ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ) ) {
     	if(!noBio){why += checkLDL(theForm.ldl.value);}
     	if(!noBio){why += checkGlucose(theForm.glucose.value);}
     	if(!noBio){why += checkTri(theForm.triglycerides.value);}
    }
    if ( (theForm.page.value == 2) && (theForm.assessment.value == "CRC") ){
    		why += checkDropdown(theForm.diabetes.value, "You did not enter your diabetes status.\n");
     		why += checkDropdown(theForm.heart_attack.value, "You did not enter your heart history.\n");
    		if(!noGina){why += checkDropdown(theForm.family_heart_attack.value, "You did not enter your family history.\n");}
    		why += checkDropdown(theForm.loss.value, "You did not enter information about recent loss.\n");
    		why += checkDropdown(theForm.stress.value, "You did not enter information about stress.\n");
    }
    if ( (theForm.page.value == 4) && (theForm.assessment.value == "CRC") ){
    		var smokeStatus = theForm.smoke_status.value;
			why += checkDropdown(theForm.smoke_status.value, "You did not enter your tobacco use.\n");
			if(smokeStatus == "Used to smoke" || smokeStatus == "Still smoke"){
			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "Your cigarettes smoke a day must be between 1 and 80.\n", "cigarettes a day");
			}
    		why += isEmpty(theForm.exercise.value, "You did not enter your exercise.\n");
    		why += checkDropdown(theForm.fiber.value, "You did not enter your fiber.\n");
    		why += checkDropdown(theForm.fat.value, "You did not enter information about your fat intake.\n");
    }
    if ( ( (theForm.page.value == 5) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "GHA") ) ){
           var smokeStatus = theForm.smoke_status.value;
		if ( (theForm.assessment.value == "HRA") ){
			why += checkDropdown(theForm.smoke_status.value, "You did not enter your tobacco use.\n");
    		}
    		if(smokeStatus != "Never smoked" ){
			why += checkDropdown(theForm.cigars_day.value, "You did not enter how many cigars you smoke.\n");
			why += checkDropdown(theForm.chews_day.value, "You did not enter if you use smokeless tobacco.\n");
			why += checkDropdown(theForm.pipes_day.value, "You did not enter how many pipes you smoke.\n");
		}
    		if(smokeStatus == "Never smoked"){
    			if(theForm.cigars_day.value == ''){ theForm.cigars_day.value = 'None'; }
    			if(theForm.chews_day.value == ''){ theForm.chews_day.value = 'None'; }
    			if(theForm.pipes_day.value == ''){ theForm.pipes_day.value = 'None'; }
    		}
    		if(smokeStatus == "Used to smoke"){
    			why += checkRange(theForm.cigarette_years_quit.value, 1, 80, 0, "Your cigarette years quit must be between 1 and 80.\n", "years quit");
    			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "Your cigarettes smoke a day must be between 1 and 80.\n", "cigarettes a day");
    		}
    		if(smokeStatus == "Still smoke"){
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
    		why += checkDropdown(theForm.general_exam.value, "You did not enter your general exam history.\n");
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
    if ( ( (theForm.page.value == 9) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 4) && (theForm.assessment.value == "GHA") && !noDrive) ){
    		
			theForm.miles_car.value = niceNum(theForm.miles_car.value);
  		    theForm.miles_motorcycle.value = niceNum(theForm.miles_motorcycle.value);			
			why += checkInt(theForm.miles_car.value,"Miles per year");
			why += checkInt(theForm.miles_motorcycle.value,"Miles per year");
    		why += checkDropdown(theForm.travel_mode.value, "You did not enter your travel mode.\n");
    		why += checkDropdown(theForm.seat_belt.value, "You did not enter your seat belt habits.\n");
    		why += checkDropdown(theForm.helmet.value, "You did not enter your helmet information.\n");
    		why += checkDropdown(theForm.speed.value, "You did not enter your driving speed habits.\n");
    }
    if ( ( (theForm.page.value == 9) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 4) && (theForm.assessment.value == "GHA") ) ){
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
       alert(why);
       return false;
    }
    return true;
  }
  else{
    return true; // submits without validation.
  }
}

/* Spanish check   */
function doCheckSpanish(theForm) {
  if(doValidate){
    var why = "";
		
    if ((theForm.page.value == 1) || (theForm.assessment.value == "FIT") || (theForm.assessment.value == "DRC")) {
    	why += isEmpty(theForm.first_name.value, "No ha introducido su nombre de pila\n");
    	why += isEmpty(theForm.last_name.value, "No ha introducido su apellido\n");
     	why += checkYear(theForm.birth_year.value);
     	why += checkthisdate(theForm.birth_month.value, theForm.birth_date.value, theForm.birth_year.value);
    	why += checkSEX(theForm.sex.value);
    	if (theForm.assessment.value != "GWB") {
			why += checkWeight(theForm.weight.value);
			why += checkDropdown(theForm.height.value, "No ha introducido su altura\n");			
    	}
		if (theForm.assessment.value == 'HRA') {
    		why += isEmpty(theForm.frame_size.value, "No ha introducido su tamaño coporal\n");
    	}
    	if (theForm.assessment.value != "GWB" && theForm.assessment.value != "FIT" && !noRace) {
    		why += checkDropdown(theForm.race.value, "No ha introducido su raza\n");
    	}
		
    	if ((theForm.assessment.value == "GHA")) {
			if(theForm.waist){
				why += checkWaist(theForm.waist.value);
			}
    		why += checkDropdown(theForm.smoke_status.value, "No ha introducido el uso de tabaco\n");
    	}
    }
    if (theForm.assessment.value == "FIT") {
    		why += checkWaist(theForm.waist.value);
    		why += checkFrame(theForm.elbow.value, theForm.wrist.value);
    		why += checkRange(theForm.flexibility.value, 1, 40, 0, "Su número de flexibilidad debe estar entre 1 y 40.\n", "flexibilidad");
    		why += checkRange(theForm.pulse_rate_30_seconds.value, 15, 200, 0, "Su puntaje de paso (pulso a 30 segundos)  debe estar entre 15 y 200.\n", "Puntuación del paso");
    		why += checkRange(theForm.sit_up.value, 0, 300, 1, "Sus sentadillas deben estar entre 0 y 300.\n", "Abdominales");
    		why += checkRange(theForm.push_ups.value, 0, 300, 1, "Tus flexiones deben estar entre 0 y 300.\n", "Lagartijas/flexiones");
    }
    if (theForm.assessment.value == "DRC") {
    		why += isEmpty(theForm.exercise.value, "No ha introducido su ejercicio\n");
    		if(!noGina){why += checkDropdown(theForm.siblings_have_diabetes.value, "No ha introducido la historia de su hermano/a\n");}
    		if(!noGina){why += checkDropdown(theForm.parents_have_diabetes.value, "No ha introducido la historia de sus padres.\n");}
    		if(theForm.sex.value == "Male"){
    			theForm.big_kid.value = 'No';
    			theForm.diabetes_gdm.value = 'No';
    		}
    		why += checkDropdown(theForm.big_kid.value, "No ha introducido la información de su nacimiento.\n");
    		why += checkDropdown(theForm.diabetes_gdm.value, "No ha introducido la información de su diabetes gestacional.\n");
    }
    if ( ( theForm.page.value == 2 && theForm.assessment.value == "HRA" ) || ( theForm.page.value == 5 && theForm.assessment.value == "GHA" ) ){
    	  
		if (theForm.sex.value == "Male"){
    		why += checkDropdown(theForm.rectal_male.value, "No ha introducido su información sobre el examen de próstata.\n");
    	}
    	if (theForm.sex.value == "Female"){
    		why += checkDropdown(theForm.menarche_female.value, "No ha introducido la información menstrual.\n");
    		why += checkDropdown(theForm.birth_age_female.value, "No ha introducido la información de su nacimiento.\n");
     		why += checkDropdown(theForm.pregnant_female.value, "No ha introducido la información sobre su estado de preñez.\n");
   		why += checkDropdown(theForm.mammogram_female.value, "No ha introducido la historia de su mamografía.\n");
  		if(!noGina){why += checkDropdown(theForm.fam_breast_cancer.value, "No ha introducido su historia familiar.\n");}
    		why += checkDropdown(theForm.self_breast_exam.value, "No ha introducido su información de auto examen de mama.\n");
    		why += checkDropdown(theForm.clinic_breast_exam.value, "No ha introducido información sobre su examen clínico de mama.\n");
    		why += checkDropdown(theForm.hyst_female.value, "No ha introducido su estatus de histerectomía.\n");
    		why += checkDropdown(theForm.pap_female.value, "No ha introducido su historia de examen de Papanicolaou.\n");
    		why += checkDropdown(theForm.rectal_female.value, "No ha introducido su información de examen rectal.\n");
    	}
    }
    if ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.diabetes.value, "No ha introducido el estado de su diabetes.\n");
    		if(!noGina){why += checkDropdown(theForm.family_diabetes.value, "No ha introducido sus antecedentes familiares de diabetes.\n");}
     		why += checkDropdown(theForm.heart_attack.value, "No ha introducido la historia de su corazón.\n");
    		if(!noGina){why += checkDropdown(theForm.family_heart_attack.value, "No ha introducido su historia familiar de infartos.\n");}
    		why += checkDropdown(theForm.bp_meds.value, "No ha introducido su estatus de medicamentos para la presión arterial.\n");
    }
    if ( ( (theForm.page.value == 4) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "CRC") ) || ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ) ) {
     	why += checkSys(theForm.bp_sys.value);
     	why += checkDias(theForm.bp_dias.value);
     	why += checkChol(theForm.cholesterol.value);
		why += checkLDL(theForm.ldl.value);
     	why += checkHDL(theForm.hdl.value);
    }
    
    
    if (  ( (theForm.page.value == 3) && (theForm.assessment.value == "CRC") ) || ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ) ) {
     	if(!noBio){why += checkLDL(theForm.ldl.value);}
     	if(!noBio){why += checkGlucose(theForm.glucose.value);}
     	if(!noBio){why += checkTri(theForm.triglycerides.value);}
    }
    if ( (theForm.page.value == 2) && (theForm.assessment.value == "CRC") ){
    		why += checkDropdown(theForm.diabetes.value, "No ha introducido su condición de diabetes.\n");
     		why += checkDropdown(theForm.heart_attack.value, "No ha introducido la historia de su corazón.\n");
    		if(!noGina){why += checkDropdown(theForm.family_heart_attack.value, "No ha introducido la historia de su familia.\n");}
    		why += checkDropdown(theForm.loss.value, "No ha introducido la información sobre la reciente pérdida de un familiar/amigo.\n");
    		why += checkDropdown(theForm.stress.value, "No ha introducido información sobre el estrés.\n");
    }
    if ( (theForm.page.value == 4) && (theForm.assessment.value == "CRC") ){
    		var smokeStatus = theForm.smoke_status.value;
			why += checkDropdown(theForm.smoke_status.value, "No ha introducido su uso de tabaco.\n");
			if(smokeStatus == "Used to smoke" || smokeStatus == "Still smoke"){
			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "La cantida de cigarrillos al día debe ser entre 1 y 80.\n", "Cigarrillos al día");
			}
    		why += isEmpty(theForm.exercise.value, "No ha introducido su ejercicio.\n");
    		why += checkDropdown(theForm.fiber.value, "No ha introducido su fibra.\n");
    		why += checkDropdown(theForm.fat.value, "No ha introducido información sobre su consumo de grasas.\n");
    }
    if ( ( (theForm.page.value == 5) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "GHA") ) ){
           var smokeStatus = theForm.smoke_status.value;
		if ( (theForm.assessment.value == "HRA") ){
			why += checkDropdown(theForm.smoke_status.value, "No ha introducido su uso de tabaco.\n");
    		}
    		if(smokeStatus != "Never smoked" ){
			why += checkDropdown(theForm.cigars_day.value, "No ha introducido al cantidad de cigarrillos que fuma.\n");
			why += checkDropdown(theForm.chews_day.value, "No ha especificado si utiliza el tabaco sin humo.\n");
			why += checkDropdown(theForm.pipes_day.value, "No ha especificado cuántas pipas fuma.\n");
		}
    		if(smokeStatus == "Never smoked"){
    			if(theForm.cigars_day.value == ''){ theForm.cigars_day.value = 'None'; }
    			if(theForm.chews_day.value == ''){ theForm.chews_day.value = 'None'; }
    			if(theForm.pipes_day.value == ''){ theForm.pipes_day.value = 'None'; }
    		}
    		if(smokeStatus == "Used to smoke"){
    			why += checkRange(theForm.cigarette_years_quit.value, 1, 80, 0, "La cantidad de años que dejó el cigarrillo debe estar entre 1 y 80.\n", "Los años sin fumar");
    			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "Los cigarrillos que fuma al día debe ser entre 1 y 80.\n", "Cigarrillos al día");
    		}
    		if(smokeStatus == "Still smoke"){
    			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "Los cigarrillos que fuma al día debe ser entre 1 y 80.\n", "Cigarrillos al día");
    		}
    }
    if ( (theForm.page.value == 3) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.fat.value, "No ha introducido la ingesta de grasas.\n");
    		why += checkDropdown(theForm.fiber.value, "No ha introducido la ingesta de fibra.\n");
    }
    if ( (theForm.page.value == 5) && (theForm.assessment.value == "GHA") ){
    		why += checkRange(theForm.drinks_week.value, 0, 100, 1, "Sus bebidas alcohólicas en una semana debe estar entre 0 y 100.\n", "Bebidas alcohólicas");
    		why += checkDropdown(theForm.exercise.value, "No ha introducido información sobre su ejercicio.\n");
    		why += checkDropdown(theForm.general_exam.value, "No ha introducido historia de su examen general.\n");
    }
    if ( (theForm.page.value == 6) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.overall_health.value, "No ha introducido su estado general de salud.\n");
    		why += checkDropdown(theForm.life_satisfaction.value, "No ha introducido su satisfacción con la vida.\n");
    		why += checkDropdown(theForm.loss.value, "No ha introducido información acerca de alguna pérdida por muerte.\n");
    		why += checkDropdown(theForm.violence.value, "No ha introducido información acerca de cualquier tipo de violencia.\n");
    }
    if ( (theForm.page.value == 7) && (theForm.assessment.value == "HRA") ){
    		why += checkDropdown(theForm.breads_check.value, "No ha introducido el consumo de pan.\n");
    		why += checkDropdown(theForm.fruits_check.value, "No ha introducido la ingesta de frutas.\n");
    		why += checkDropdown(theForm.vegetables_check.value, "No ha introducido ingesta de verduras.\n");
    		why += checkDropdown(theForm.meats_check.value, "No ha introducido el consumo de carnes.\n");
    		why += checkDropdown(theForm.fatty_meats_check.value, "No ha introducido su consumo de carnes grasosas.\n");
    		why += checkDropdown(theForm.rich_breads_check.value, "No ha introducido el consumo de panes ricos.\n");
    		why += checkDropdown(theForm.desserts_check.value, "No ha introducido el consumo de postres.\n");
    }
    if ( (theForm.page.value == 8) && (theForm.assessment.value == "HRA") ){
    		why += checkRange(theForm.drinks_week.value, 0, 100, 1, "Las bebidas alcohólicas en una semana deben ser de entre 0 y 100.\n", "Bebidas alcohólicas");
    }
    if ( ( (theForm.page.value == 9) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 4) && (theForm.assessment.value == "GHA") && !noDrive) ){
    		
			theForm.miles_car.value = niceNum(theForm.miles_car.value);
  		    theForm.miles_motorcycle.value = niceNum(theForm.miles_motorcycle.value);			
			why += checkInt(theForm.miles_car.value,"Millas por año");
			why += checkInt(theForm.miles_motorcycle.value,"Millas por año");
    		why += checkDropdown(theForm.travel_mode.value, "No ha introducido el modo de viaje.\n");
    		why += checkDropdown(theForm.seat_belt.value, "No ha introducido sus hábitos del cinturón de seguridad.\n");
    		why += checkDropdown(theForm.helmet.value, "No ha introducido la información de su casco.\n");
    		why += checkDropdown(theForm.speed.value, "No ha introducido sus hábitos de velocidad de conducción.\n");
    }
    if ( ( (theForm.page.value == 9) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 4) && (theForm.assessment.value == "GHA") ) ){
    		why += checkRange(theForm.drink_and_drive.value, 0, 25, 1, "Viajar con el número de conductores ebrios debe ser de entre 0 y 25.\n", "Viajar con conductores ebrios");
    }
    if ( (theForm.page.value == 10) && (theForm.assessment.value == "HRA") ){
    		why += checkDropdown(theForm.exercise.value, "No ha introducido información de su ejercicio.\n");
    }
    if ( (theForm.page.value == 12) && (theForm.assessment.value == "HRA") ){
    		why += checkDropdown(theForm.overall_health.value, "No ha introducido su estado general de salud.\n");
    		why += checkDropdown(theForm.life_satisfaction.value, "No ha introducido su satisfacción con la vida.\n");
    		why += checkDropdown(theForm.loss.value, "No ha introducido información acerca de alguna pérdida por muerte.\n");
    		why += checkDropdown(theForm.q3.value, "No ha introducido acerca de su sentimiento de depresión.\n");
    		why += checkDropdown(theForm.q5.value, "No ha introducido acerca de su sensación nerviosa.\n");
    		why += checkDropdown(theForm.q7.value, "No ha introducido acerca de su sentimiento de sentirse abatido.\n");
    		why += checkDropdown(theForm.q8.value, "No ha introducido acerca de su sensación tensa.\n");
    		why += checkDropdown(theForm.q11.value, "No ha introducido acerca de su sentimiento de tristeza.\n");
    		why += checkDropdown(theForm.q17.value, "No ha introducido acerca de su sensación de ansiedad.\n");
    		why += checkDropdown(theForm.q19.value, "No ha introducido acerca de su sensación de estar relajado.\n");
    		why += checkDropdown(theForm.q22.value, "No ha introducido acerca de sentirse presionado.\n");
    }
    if (why != "") {
       alert(why);
       return false;
    }
    return true;
  }
  else{
    return true; // submits without validation.
  }
}

/* Check Chinese*/
function doCheckChinese(theForm) {
  if(doValidate){
    var why = "";
		
    if ((theForm.page.value == 1) || (theForm.assessment.value == "FIT") || (theForm.assessment.value == "DRC")) {
    	why += isEmpty(theForm.first_name.value, "您未填写您的名字。\n");
    	why += isEmpty(theForm.last_name.value, "您未填写您的姓氏。\n");
     	why += checkYear(theForm.birth_year.value);
     	why += checkthisdate(theForm.birth_month.value, theForm.birth_date.value, theForm.birth_year.value);
    	why += checkSEX(theForm.sex.value);
    	if (theForm.assessment.value != "GWB") {
			why += checkWeight(theForm.weight.value);
			why += checkDropdown(theForm.height.value, "您未填写您的身高。\n");			
    	}
		if (theForm.assessment.value == 'HRA') {
    		why += isEmpty(theForm.frame_size.value, "您未填写您的骨架尺寸。\n");
    	}
    	if (theForm.assessment.value != "GWB" && theForm.assessment.value != "FIT" && !noRace) {
    		why += checkDropdown(theForm.race.value, "您未填写您的种族。\n");
    	}
		
    	if ((theForm.assessment.value == "GHA")) {
			if(theForm.waist){
				why += checkWaist(theForm.waist.value);
			}
    		why += checkDropdown(theForm.smoke_status.value, "您未填写您的烟草使用情况。\n");
    	}
    }
    if (theForm.assessment.value == "FIT") {
    		why += checkWaist(theForm.waist.value);
    		why += checkFrame(theForm.elbow.value, theForm.wrist.value);
    		why += checkRange(theForm.flexibility.value, 1, 40, 0, "您的灵活性必须在1-40之间。\n", "的灵活性");
    		why += checkRange(theForm.pulse_rate_30_seconds.value, 15, 200, 0, "您的台阶测试得分（30秒脉搏）必须在15-200之间。\n", "台阶测试得分");
    		why += checkRange(theForm.sit_up.value, 0, 300, 1, "您的仰卧起坐量必须在0-300之间。\n", "仰卧起坐");
    		why += checkRange(theForm.push_ups.value, 0, 300, 1, "您的俯卧撑量必须在0-300之间。\n", "俯卧撑");
    }
    if (theForm.assessment.value == "DRC") {
    		why += isEmpty(theForm.exercise.value, "您未填写您的锻炼信息。\n");
    		if(!noGina){why += checkDropdown(theForm.siblings_have_diabetes.value, "您未填写您的兄弟姐妹情况。\n");}
    		if(!noGina){why += checkDropdown(theForm.parents_have_diabetes.value, "您未填写您的双亲情况。\n");}
    		if(theForm.sex.value == "Male"){
    			theForm.big_kid.value = 'No';
    			theForm.diabetes_gdm.value = 'No';
    		}
    		why += checkDropdown(theForm.big_kid.value, "您未填写您的分娩信息。\n");
    		why += checkDropdown(theForm.diabetes_gdm.value, "您未填写您的孕期糖尿病信息。\n");
    }
    if ( ( theForm.page.value == 2 && theForm.assessment.value == "HRA" ) || ( theForm.page.value == 5 && theForm.assessment.value == "GHA" ) ){
    	  
		if (theForm.sex.value == "Male"){
    		why += checkDropdown(theForm.rectal_male.value, "您未填写您的前列腺检查信息。\n");
    	}
    	if (theForm.sex.value == "Female"){
    		why += checkDropdown(theForm.menarche_female.value, "您未填写您的月经信息。\n");
    		why += checkDropdown(theForm.birth_age_female.value, "您未填写您的分娩信息。\n");
     		why += checkDropdown(theForm.pregnant_female.value, "您未填写您是否受孕。\n");
   		why += checkDropdown(theForm.mammogram_female.value, "您未填写您的乳房X照片过往情况。\n");
  		if(!noGina){why += checkDropdown(theForm.fam_breast_cancer.value, "您未填写您的家族病史。\n");}
    		why += checkDropdown(theForm.self_breast_exam.value, "您未填写您的乳房自检情况。\n");
    		why += checkDropdown(theForm.clinic_breast_exam.value, "您未填写您的临床乳房检查情况。\n");
    		why += checkDropdown(theForm.hyst_female.value, "您未填写您子宫切除的情况。\n");
    		why += checkDropdown(theForm.pap_female.value, "您未填写您的宫颈检查历史。\n");
    		why += checkDropdown(theForm.rectal_female.value, "您未填写您的直肠检查历史。\n");
    	}
    }
    if ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.diabetes.value, "您未填写您的糖尿病情况。\n");
    		if(!noGina){why += checkDropdown(theForm.family_diabetes.value, "您未填写您的糖尿病家族史。\n");}
     		why += checkDropdown(theForm.heart_attack.value, "您未填写您的心脏病史。\n");
    		if(!noGina){why += checkDropdown(theForm.family_heart_attack.value, "您未填写您的心脏病家族史。\n");}
    		why += checkDropdown(theForm.bp_meds.value, "您未填写您血压的药物治疗情况。\n");
    }
    if ( ( (theForm.page.value == 4) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "CRC") ) || ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ) ) {
     	why += checkSys(theForm.bp_sys.value);
     	why += checkDias(theForm.bp_dias.value);
     	why += checkChol(theForm.cholesterol.value);
		why += checkLDL(theForm.ldl.value);
     	why += checkHDL(theForm.hdl.value);
    }
    
    
    if (  ( (theForm.page.value == 3) && (theForm.assessment.value == "CRC") ) || ( (theForm.page.value == 2) && (theForm.assessment.value == "GHA") ) ) {
     	if(!noBio){why += checkLDL(theForm.ldl.value);}
     	if(!noBio){why += checkGlucose(theForm.glucose.value);}
     	if(!noBio){why += checkTri(theForm.triglycerides.value);}
    }
    if ( (theForm.page.value == 2) && (theForm.assessment.value == "CRC") ){
    		why += checkDropdown(theForm.diabetes.value, "您未填写您的糖尿病情况。\n");
     		why += checkDropdown(theForm.heart_attack.value, "您未填写您的心脏病史。\n");
    		if(!noGina){why += checkDropdown(theForm.family_heart_attack.value, "您未填写您的家族病史。\n");}
    		why += checkDropdown(theForm.loss.value, "您未填写最近失去某人或某物的情况。\n");
    		why += checkDropdown(theForm.stress.value, "您未填写压力方面的信息。\n");
    }
    if ( (theForm.page.value == 4) && (theForm.assessment.value == "CRC") ){
    		var smokeStatus = theForm.smoke_status.value;
			why += checkDropdown(theForm.smoke_status.value, "您未填写您的烟草使用情况。\n");
			if(smokeStatus == "Used to smoke" || smokeStatus == "Still smoke"){
			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "您一天的吸烟量必须在1-80之间。\n", "一天的吸烟量");
			}
    		why += isEmpty(theForm.exercise.value, "您未填写您的锻炼信息。\n");
    		why += checkDropdown(theForm.fiber.value, "您未填写纤维素信息。\n");
    		why += checkDropdown(theForm.fat.value, "您未填写脂肪摄入量信息。\n");
    }
    if ( ( (theForm.page.value == 5) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 3) && (theForm.assessment.value == "GHA") ) ){
           var smokeStatus = theForm.smoke_status.value;
		if ( (theForm.assessment.value == "HRA") ){
			why += checkDropdown(theForm.smoke_status.value, "您未填写您的烟草使用情况。\n");
    		}
    		if(smokeStatus != "Never smoked" ){
			why += checkDropdown(theForm.cigars_day.value, "您未填写您吸烟的数量。\n");
			why += checkDropdown(theForm.chews_day.value, "您未填写您是否吸无烟烟草。\n");
			why += checkDropdown(theForm.pipes_day.value, "您未填写您抽烟斗的数量。\n");
		}
    		if(smokeStatus == "Never smoked"){
    			if(theForm.cigars_day.value == ''){ theForm.cigars_day.value = 'None'; }
    			if(theForm.chews_day.value == ''){ theForm.chews_day.value = 'None'; }
    			if(theForm.pipes_day.value == ''){ theForm.pipes_day.value = 'None'; }
    		}
    		if(smokeStatus == "Used to smoke"){
    			why += checkRange(theForm.cigarette_years_quit.value, 1, 80, 0, "您戒烟的年限必须在1-80之间。\n", "戒烟年限");
    			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "您一天的吸烟量必须在1-80之间。\n", "一天的吸烟量");
    		}
    		if(smokeStatus == "Still smoke"){
    			why += checkRange(theForm.cigs_a_day.value, 1, 80, 0, "您一天的吸烟量必须在1-80之间。\n", "一天的吸烟量");
    		}
    }
    if ( (theForm.page.value == 3) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.fat.value, "您未填写脂肪摄入量。\n");
    		why += checkDropdown(theForm.fiber.value, "您未填写纤维素摄入量。\n");
    }
    if ( (theForm.page.value == 5) && (theForm.assessment.value == "GHA") ){
    		why += checkRange(theForm.drinks_week.value, 0, 100, 1, "您一周内的饮酒量应在0-100之间。\n", "饮酒情况");
    		why += checkDropdown(theForm.exercise.value, "您未填写您的锻炼信息。\n");
    		why += checkDropdown(theForm.general_exam.value, "您未填写您的一般检查史。\n");
    }
    if ( (theForm.page.value == 6) && (theForm.assessment.value == "GHA") ){
    		why += checkDropdown(theForm.overall_health.value, "您未填写您的总体健康状况。\n");
    		why += checkDropdown(theForm.life_satisfaction.value, "您未填写您的生活满意度。\n");
    		why += checkDropdown(theForm.loss.value, "您未填写任何关于失去某人或某物的情况。\n");
    		why += checkDropdown(theForm.violence.value, "您未填写任何关于暴力的信息。\n");
    }
    if ( (theForm.page.value == 7) && (theForm.assessment.value == "HRA") ){
    		why += checkDropdown(theForm.breads_check.value, "您未填写面包摄入量。\n");
    		why += checkDropdown(theForm.fruits_check.value, "您未填写水果摄入量。\n");
    		why += checkDropdown(theForm.vegetables_check.value, "您未填写蔬菜摄入量。\n");
    		why += checkDropdown(theForm.meats_check.value, "您未填写肉类摄入量。\n");
    		why += checkDropdown(theForm.fatty_meats_check.value, "您未填写肥肉摄入量。\n");
    		why += checkDropdown(theForm.rich_breads_check.value, "您未填写高糖高油面包摄入量。\n");
    		why += checkDropdown(theForm.desserts_check.value, "您未填写甜食摄入量。\n");
    }
    if ( (theForm.page.value == 8) && (theForm.assessment.value == "HRA") ){
    		why += checkRange(theForm.drinks_week.value, 0, 100, 1, "您一周内的饮酒量应在0-100之间。\n", "饮酒情况");
    }
    if ( ( (theForm.page.value == 9) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 4) && (theForm.assessment.value == "GHA") && !noDrive) ){
    		
			theForm.miles_car.value = niceNum(theForm.miles_car.value);
  		    theForm.miles_motorcycle.value = niceNum(theForm.miles_motorcycle.value);			
			why += checkInt(theForm.miles_car.value,"每年的英里数");
			why += checkInt(theForm.miles_motorcycle.value,"每年的英里数");
    		why += checkDropdown(theForm.travel_mode.value, "您未填写您的旅行方式。\n");
    		why += checkDropdown(theForm.seat_belt.value, "您未填写您是否有系安全带的习惯。\n");
    		why += checkDropdown(theForm.helmet.value, "您未填写头盔信息。\n");
    		why += checkDropdown(theForm.speed.value, "您未填写您惯常的行车速度。\n");
    }
    if ( ( (theForm.page.value == 9) && (theForm.assessment.value == "HRA") ) || ( (theForm.page.value == 4) && (theForm.assessment.value == "GHA") ) ){
    		why += checkRange(theForm.drink_and_drive.value, 0, 25, 1, "您乘坐醉酒司机驾驶的车辆的次数应在0-25之间。\n", "乘坐醉酒司机驾驶的车辆");
    }
    if ( (theForm.page.value == 10) && (theForm.assessment.value == "HRA") ){
    		why += checkDropdown(theForm.exercise.value, "您未填写您的锻炼信息。\n");
    }
    if ( (theForm.page.value == 12) && (theForm.assessment.value == "HRA") ){
    		why += checkDropdown(theForm.overall_health.value, "您未填写您的总体健康状况。\n");
    		why += checkDropdown(theForm.life_satisfaction.value, "您未填写您的生活满意度。\n");
    		why += checkDropdown(theForm.loss.value, "您未填写关于任何失去某人或某物的情况。\n");
    		why += checkDropdown(theForm.q3.value, "您未填写您心情沮丧的情况。\n");
    		why += checkDropdown(theForm.q5.value, "您未填写您感到紧张的情况。\n");
    		why += checkDropdown(theForm.q7.value, "您未填写您无精打采的情况。\n");
    		why += checkDropdown(theForm.q8.value, "您未填写您感到紧张的情况。\n");
    		why += checkDropdown(theForm.q11.value, "您未填写您感到伤心的情况。\n");
    		why += checkDropdown(theForm.q17.value, "您未填写心情焦躁的情况。\n");
    		why += checkDropdown(theForm.q19.value, "您未填写心情放松的情况。\n");
    		why += checkDropdown(theForm.q22.value, "您未填写您感觉到压力的情况。\n");
    }
    if (why != "") {
       alert(why);
       return false;
    }
    return true;
  }
  else{
    return true; // submits without validation.
  }
}

function checkRange(entered, min, max, zero, msg, fldname) {
    var error = "";
    if (entered == "" && zero != '1') {
		if(theForm.language.value == 'espanol'){
    		error = "No ha introducido su " + fldname + ".\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的 " + fldname + ".\n";
		}else{
        	error = "You did not enter your " + fldname + ".\n";
		}
        //error = "You did not enter your " + fldname + ".\n";
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
		if(theForm.language.value == 'espanol'){
    		error = "No ha introducido su peso\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的体重。\n";
		}else{
        	error = "You did not enter your weight\n";
		}
       // error = "You did not enter your weight.\n";
    }
	var intRegex = /^\d+$/;
	if(!intRegex.test(weight) && weight != "") {
	    if(theForm.language.value == 'espanol'){
    		error += "El peso debe ser de un valor entero\n";
		}else if(theForm.language.value == 'chinese'){
			error += "体重必须是整数值。\n";
		}else{
        	error += "The weight must be an integer value.\n";
		}	
	  //error += "The weight must be an integer value.\n";   
	}
    num = niceNum(weight);
    if (num < 50 || num > 700) {
		if(theForm.language.value == 'espanol'){
    		error += "El peso debe ser de entre 50 y 700 para esta evaluación\n";
		}else if(theForm.language.value == 'chinese'){
			error += "本次评估中的体重必须在50-700之间。\n";
		}else{
        	error += "The weight must be between 50 and 700 for this assessment.\n";
		}
    	//error += "The weight must be between 50 and 700 for this assessment.\n";
	}
	
    return error;
}

function checkWaist(waist) {
    var error = "";
    if (waist == "") {
		if(theForm.language.value == 'espanol'){
    		error = "No ha entrado el tamaño de la cintura\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的腰围。\n";
		}else{
        	error = "You didn't enter your waist size.\n";
		}
        //error = "You didn't enter your waist size.\n";
    }
	var intRegex = /^\d+$/;
	if(!intRegex.test(waist) && waist != "") {
	   if(theForm.language.value == 'espanol'){
    		error += "La cintura debe ser de un valor entero\n";
		}else if(theForm.language.value == 'chinese'){
			error += "腰围必须是整数值。\n";
		}else{
        	error += "The waist must be an integer value.\n";
		}	
	   //error += "The waist must be an integer value.\n";	   
	}
    num = niceNum(waist);
    if (num < 10 || num > 90) {
		if(theForm.language.value == 'espanol'){
    		error += "El tamaño de la cintura debe ser de entre 10 y 90 para esta evaluación\n";
		}else if(theForm.language.value == 'chinese'){
			error += "本次评估中的腰围尺寸必须在10-90之间。\n";
		}else{
        	error += "The waist size must be between 10 and 90 for this assessment.\n";
		}	
    	//error += "The waist size must be between 10 and 90 for this assessment.\n";
	}
    return error;
}

function checkFrame(elbow, wrist) {
    var error = "";
    if ((wrist == "0") && (elbow == "0")){
		if(theForm.language.value == 'espanol'){
    		error = "No ha introducido el tamaño de la muñeca o del codo \n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的手腕或肘部尺寸。\n";
		}else{
        	error = "You did not enter your wrist or elbow size.\n";
		}
        //error = "You did not enter your wrist or elbow size.\n";
    }
    return error;
}

function checkYear(year) {
    var error = "";
    var d = new Date();
    var curr_year = d.getFullYear();
    var max_year = curr_year - 17;
    if (year == "") {
    	//error = "The year of birth must be between 1900 and ";
    	//error += max_year;
    	//error += " for this assessment.\n";
		if(theForm.language.value == 'espanol'){
    		error = "El año de nacimiento debe estar entre 1900 y\n";
			error += max_year;
			error += " para esta evaluación.\n";
		}else if(theForm.language.value == 'chinese'){
			error = "本次评估中的出生年份必须在1900-\n";
			error += max_year;
		}else{
        	error = "The year of birth must be between 1900 and ";
			error += max_year;
			error += " for this assessment.\n";
		}
    	document.theForm.birth_year.focus();
    }
    num = niceNum(year);
    num = parseInt(num);
    if (num < 1900 || num > max_year) {
    	//error = "The year of birth must be between 1900 and ";
    	//error += max_year;
    	//error += " for this assessment.\n";
		if(theForm.language.value == 'espanol'){
    		error = "El año de nacimiento debe estar entre 1900 y\n";
			error += max_year;
			error += " para esta evaluación.\n";
		}else if(theForm.language.value == 'chinese'){
			error = "本次评估中的出生年份必须在1900-\n";
			error += max_year;
		}else{
        	error = "The year of birth must be between 1900 and ";
			error += max_year;
			error += " for this assessment.\n";
		}
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
    	return error;
	}else{
		if(theForm.language.value == 'espanol'){
    		error = "No ha especificado una fecha válida\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写有效日期。\n";
		}else{
        	error = "You did not enter a valid date.\n";
		}
    	//error = "You did not enter a valid date.\n";
    	return error;
	}
}
    	

function checkSys(systolic) {
    var error = "";
    if (systolic == "" && (theForm.bp_check.value <= 0)) {
		if(theForm.language.value == 'espanol'){
    		error = "No ha entrado su valor de la presión arterial sistólica\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的收缩压值。\n";
		}else{
        	error = "You didn't enter your systolic blood pressure value.\n";
		}
        //error = "You didn't enter your systolic blood pressure value.\n";
    }
	var intRegex = /^\d+$/;
	if(!intRegex.test(systolic)) {
		if(theForm.language.value == 'espanol'){
    		error += "La presión arterial sistólica debe ser de un valor entero\n";
		}else if(theForm.language.value == 'chinese'){
			error += "收缩压值必须是整数值。\n";
		}else{
        	error += "The systolic blood pressure number must be an integer value.\n";
		}
	   //error += "The systolic blood pressure number must be an integer value.\n";	   
	}
    num = niceNum(systolic)
    num = parseInt(num);
  
    if ((num < 90 || num > 300) && (theForm.bp_check.value <= 0)) {
		if(theForm.language.value == 'espanol'){
    		error += "La presión arterial sistólica debe ser de entre 90 y 300 para esta evaluación\n";
		}else if(theForm.language.value == 'chinese'){
			error += "本次评估中的收缩压值必须在90-300之间。\n";
		}else{
        	error += "The systolic blood pressure number must be between 90 and 300 for this assessment.\n";
		}
    	//error += "The systolic blood pressure number must be between 90 and 300 for this assessment.\n";
    }
	
    return error;
}

function checkDias(diastolic) {
    var error = "";
    if (diastolic == "" && (theForm.bp_check.value <= 0)) {
		if(theForm.language.value == 'espanol'){
    		error = "No ha entrado su valor de la presión arterial diastólica\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的舒张压值。\n";
		}else{
        	error = "You did not enter your diastolic blood pressure value.\n";
		}
        //error = "You did not enter your diastolic blood pressure value.\n";
    }
	var intRegex = /^\d+$/;
	if(!intRegex.test(diastolic)) {
		if(theForm.language.value == 'espanol'){
    		error += "El número de la presión arterial diastólica debe ser de un valor entero\n";
		}else if(theForm.language.value == 'chinese'){
			error += "舒张压值必须是整数值。\n";
		}else{
        	error += "The diastolic blood pressure number must be an integer value.\n";
		}
	   //error += "The diastolic blood pressure number must be an integer value.\n";	   
	}
    num = parseInt(diastolic);
    if ((num < 50 || num > 150) && (theForm.bp_check.value <= 0)) {
		if(theForm.language.value == 'espanol'){
    		error += "El número de la presión arterial diastólica debe ser de entre 50 y 150 para esta evaluación\n";
		}else if(theForm.language.value == 'chinese'){
			error += "本次评估中的舒张压值必须在50-150之间。\n";
		}else{
        	error += "The diastolic blood pressure number must be between 50 and 150 for this assessment.\n";
		}
    	//error += "The diastolic blood pressure number must be between 50 and 150 for this assessment.\n";
    }
    return error;
}

function checkChol(cholesterol) {
    var error = "";
    if (cholesterol == "" && (theForm.cholesterol_check.value <= 0)) {
		if(theForm.language.value == 'espanol'){
    		error = "No ha entrado su valor de colesterol total\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的总胆固醇值。\n";
		}else{
        	error = "You did not enter your total cholesterol value.\n";
		}
        //error = "You did not enter your total cholesterol value.\n";
    }
	var intRegex = /^\d+$/;
	if(!intRegex.test(cholesterol) && cholesterol != "" ) {
		if(theForm.language.value == 'espanol'){
    		error += "El número total de colesterol debe ser de un valor entero\n";
		}else if(theForm.language.value == 'chinese'){
			error += "总胆固醇值必须是整数值。\n";
		}else{
        	error += "The total cholesterol number must be an integer value.\n";
		}
	   //error += "The total cholesterol number must be an integer value.\n";	   
	}
    num = niceNum(cholesterol);
    num = parseInt(num);
    if ((num < 80 || num > 450) && (theForm.cholesterol_check.value <= 0)){
		if(theForm.language.value == 'espanol'){
    		error += "El número total de colesterol debe ser de entre 80 y 450 para esta evaluación\n";
		}else if(theForm.language.value == 'chinese'){
			error += "本次评估中的总胆固醇值必须在80-450之间。\n";
		}else{
        	error += "The total cholesterol number must be between 80 and 450 for this assessment.\n";
		}
    	error += "The total cholesterol number must be between 80 and 450 for this assessment.\n";
    }
    return error;
}

function checkHDL(hdl) {
    var error = "";
    if (hdl == "" && (theForm.cholesterol_check.value <= 0)) {
		if(theForm.language.value == 'espanol'){
    		error = "No ha introducido su HDL  valor de colesterol (bueno) \n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的高密度脂蛋白（有益）胆固醇值。\n";
		}else{
        	error = "You did not enter your HDL (good) cholesterol value.\n";
		}
        //error = "You did not enter your HDL (good) cholesterol value.\n";
    }
	var intRegex = /^\d+$/;
	if(!intRegex.test(hdl) && hdl!= "" ) {
		if(theForm.language.value == 'espanol'){
    		error += "La cantidad de colesterol total debe ser de un valor entero\n";
		}else if(theForm.language.value == 'chinese'){
			error += "总胆固醇值必须是整数值。\n";
		}else{
        	error += "The total cholesterol number must be an integer value.\n";
		}
	   //error += "The total cholesterol number must be an integer value.\n";	   
	}
    num = niceNum(hdl);
    num = parseInt(num);
    if ((num < 5 || num > 150) && (theForm.cholesterol_check.value <= 0)){
		if(theForm.language.value == 'espanol'){
    		error += "El número de colesterol HDL debe ser de entre 5 y 150 para esta evaluación\n";
		}else if(theForm.language.value == 'chinese'){
			error += "本次评估中的高密度脂蛋白胆固醇值必须在5-150之间。\n";
		}else{
        	error += "The HDL cholesterol number must be between 5 and 150 for this assessment.\n";
		}
    	//error += "The HDL cholesterol number must be between 5 and 150 for this assessment.\n";
    }
    return error;
}

function checkLDL(ldl) {
    var error = "";
    if (ldl == "" && (theForm.cholesterol_check.value <= 0)) {
		if(theForm.language.value == 'espanol'){
    		error = "No ha introducido su colesterol LDL (malo) valor de colesterol\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的低密度脂蛋白（有害）胆固醇值。\n";
		}else{
        	error = "You did not enter your LDL (bad) cholesterol value.\n";
		}
        //error = "You did not enter your LDL (bad) cholesterol value.\n";
    }
	var intRegex = /^\d+$/;
	if(!intRegex.test(ldl) && ldl != "" ) {
		if(theForm.language.value == 'espanol'){
    		error += "El número de colesterol LDL debe ser de un valor entero\n";
		}else if(theForm.language.value == 'chinese'){
			error += "低密度脂蛋白胆固醇值必须是整数值。\n";
		}else{
        	error += "The LDL cholesterol number must be an integer value.\n";
		}
	   //error += "The LDL cholesterol number must be an integer value.\n";	   
	}
    num = niceNum(ldl);
    num = parseInt(num);
    if ((num < 5 || num > 450) && (theForm.cholesterol_check.value <= 0)){
		if(theForm.language.value == 'espanol'){
    		error += "El número de colesterol LDL debe ser de entre 5 y 450 para esta evaluación\n";
		}else if(theForm.language.value == 'chinese'){
			error += "本次评估中的低密度脂蛋白胆固醇值必须在5-450之间。\n";
		}else{
        	error += "The LDL cholesterol number must be between 5 and 450 for this assessment.\n";
		}
    	//error += "The LDL cholesterol number must be between 5 and 450 for this assessment.\n";
    }
    return error;
}

function checkGlucose(glucose) {
    var error = "";
	var intRegex = /^\d+$/;
	if(glucose != "" && !intRegex.test(glucose)) {
		if(theForm.language.value == 'espanol'){
    		error = "La glucosa debe tener un valor entero\n";
		}else if(theForm.language.value == 'chinese'){
			error = "葡萄糖值必须是整数值。\n";
		}else{
        	error = "The glucose must be an integer value.\n";
		}
	   //error = "The glucose must be an integer value.\n";	   
	}
    num = niceNum(glucose);
    num = parseInt(num);
    if ((num < 0 || num > 650)){
		if(theForm.language.value == 'espanol'){
    		error += "El número de glucosa debe ser de entre 1 y 650 para esta evaluación\n";
		}else if(theForm.language.value == 'chinese'){
			error += "本次评估中的葡萄糖值必须在1-650之间。\n";
		}else{
        	error += "The Glucose number must be between 1 and 650 for this assessment.\n";
		}
    	//error += "The Glucose number must be between 1 and 650 for this assessment.\n";
    }
    return error;
}

function checkTri(tri) {
    var error = "";
	var intRegex = /^\d+$/;
	if(tri != "" && !intRegex.test(tri)) {
		if(theForm.language.value == 'espanol'){
    		error = "El número de triglicéridos debe ser de un valor entero\n";
		}else if(theForm.language.value == 'chinese'){
			error = "甘油三酯值必须是整数值。\n";
		}else{
        	error = "The triglycerides number must be an integer value.\n";
		}
	   //error = "The triglycerides number must be an integer value.\n";	   
	}
    num = niceNum(tri);
    num = parseInt(num);
    if ((num < 0 || num > 650)){
		if(theForm.language.value == 'espanol'){
    		error += "El número de triglicéridos debe estar entre 1 y 650 para esta evaluación\n";
		}else if(theForm.language.value == 'chinese'){
			error += "本次评估中的甘油三酯值必须在1-650之间。\n";
		}else{
        	error += "The Triglycerides number must be between 1 and 650 for this assessment.\n";
		}
    	//error += "The Triglycerides number must be between 1 and 650 for this assessment.\n";
    }
    return error;
}

// Sex

function checkSEX (strng) {
var error = "";
if (strng == "") {
	if(theForm.language.value == 'espanol'){
    		error = "No has introducido tu sexo\n";
	}else if(theForm.language.value == 'chinese'){
		error = "您未填写您的性别。\n";
	}else{
		error = "You did not enter your gender.\n";
	}
    //error = "You did not enter your gender.\n";
}

    if (!(strng == "Male") && !(strng == "Female") ) {
		if(theForm.language.value == 'espanol'){
    		error = "No has introducido tu sexo\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写您的性别。\n";
		}else{
			error = "You did not enter your gender.\n";
		}
     //error = "You did not enter your gender.\n";
    }
return error;
}


function disable_smoke() {
		if(document.theForm.assessment.value == "CRC" && document.theForm.smoke_status.value == "Never smoked"){
		document.theForm.cigs_a_day.disabled = true;
		var notationS = document.getElementById("cigsdayStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
		document.theForm.exercise.focus();
	}
	if(document.theForm.assessment.value == "CRC" && document.theForm.smoke_status.value != "Never smoked"){
		document.theForm.cigs_a_day.disabled = false;
		var notationS = document.getElementById("cigsdayStatus")
		notationS.innerText = notationS.textContent = ''; 
		document.theForm.cigs_a_day.focus();
	}
}

function disable_smokeHRA() {
		if(document.theForm.assessment.value == "HRA" && document.theForm.smoke_status.value == "Never smoked"){
		document.theForm.cigarette_years_quit.disabled = true;
		document.theForm.cigs_a_day.disabled = true;
		var notationS = document.getElementById("cigyearsquitStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
		var notationS1 = document.getElementById("cigsdayStatus")
		notationS1.innerText = notationS1.textContent = '  (Does not apply)'; 
		document.theForm.exercise.focus();
	}
	if(document.theForm.assessment.value == "HRA" && document.theForm.smoke_status.value == "Still smoke"){
		document.theForm.cigarette_years_quit.disabled = true;
		document.theForm.cigs_a_day.disabled = false;
		var notationS = document.getElementById("cigyearsquitStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
		var notationS1 = document.getElementById("cigsdayStatus")
		notationS1.innerText = notationS1.textContent = ''; 
		document.theForm.cigs_a_day.focus();
	}
	if(document.theForm.assessment.value == "HRA" && document.theForm.smoke_status.value == "Used to smoke"){
		document.theForm.cigarette_years_quit.disabled = false;
		document.theForm.cigs_a_day.disabled = false;
		var notationS = document.getElementById("cigyearsquitStatus")
		notationS.innerText = notationS.textContent = ''; 
		var notationS1 = document.getElementById("cigsdayStatus")
		notationS1.innerText = notationS1.textContent = ''; 
		document.theForm.cigarette_years_quit.focus();
	}
}

function disable_sex() {
		if(document.theForm.assessment.value == "DRC" && document.theForm.sex.value == "Male"){
		document.getElementById('big_kid').style.display='none';
		document.getElementById('diabetes_gdm').style.display='none';
		// document.theForm.big_kid.disabled = true;
		// document.theForm.diabetes_gdm.disabled = true;
		var notationS = document.getElementById("gdmStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
		var notationS = document.getElementById("bigkidStatus")
		notationS.innerText = notationS.textContent = '  (Does not apply)'; 
	}
	if(document.theForm.assessment.value == "DRC" && document.theForm.sex.value != "Male"){
		document.getElementById('big_kid').style.display='';
		document.getElementById('diabetes_gdm').style.display='';
		// document.theForm.big_kid.disabled = false;
		// document.theForm.diabetes_gdm.disabled = false;
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
		document.theForm.siblings_have_diabetes.focus();
	}
	if(  document.theForm.assessment.value == "DRC" && document.theForm.exercise.value != "Yes") {
		document.theForm.r2c_exercise.disabled = false;
		var notationS = document.getElementById("r2c_exerciseStatus")
		notationS.innerText = notationS.textContent = ''; 
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
	if(theForm.language.value == 'espanol'){
    		alert("¡Este debe ser un número!. Sin comas, espacios o caracteres\n");
	}else if(theForm.language.value == 'chinese'){
		alert("必须是一个数字！没有逗号、空格或者字符。 \n");
	}else{
		alert("This must be a number! No commas, spaces or characters. \n");
	}
	//alert("This must be a number! No commas, spaces or characters. \n"); 
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
		if(theForm.language.value == 'espanol'){
				alert("Por favor, introduzca el número de cigarrillos fumados cada día.\n");
		}else if(theForm.language.value == 'chinese'){
			alert("请填写每天的吸烟量。 \n");
		}else{
			alert("Please enter the number of cigarettes smoked each day. \n");
		}
		//alert(" Please enter the number of cigarettes smoked each day.");
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
			if(theForm.language.value == 'espanol'){
				alert("Por favor, escriba correctamente los datos de BP\n");
			}else if(theForm.language.value == 'chinese'){
				alert("请正确输入血压详细信息\n");
			}else{
				alert("please type the BP details correctly. \n");
			}
			//alert ("please type the BP details correctly");
			eventCalled.bp_sys.focus();
			return false;
		}
	}
	if(eventCalled.bp_check.disabled)
	{
		if(eventCalled.bp_dias.value =="")
		{
		 if(theForm.language.value == 'espanol'){
			alert("Por favor, escriba correctamente los datos de BP\n");
		}else if(theForm.language.value == 'chinese'){
			alert("请正确输入血压详细信息\n");
		}else{
			alert("please type the BP details correctly. \n");
		 }
		//alert ("please type the BP details correctly");
		eventCalled.bp_dias.focus();
		return false;
		}
	}
	if((!(eventCalled.bp_check.disabled)) && (eventCalled.bp_check.value==""))
	{
		if(theForm.language.value == 'espanol'){
			alert("Por favor debe elegir correctamente los detalles de BP\n");
		}else if(theForm.language.value == 'chinese'){
			alert("请正确选择血压详细信息\n");
		}else{
			alert("please Choose the BP details correctly. \n");
		}
		//alert ("please Choose the BP details correctly");
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
	why += checkRegnumber(theForm.db_employer.value);
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

function checkRegFormCMOG(theForm) {
    var why = "";
    why += checkRegnum(theForm.db_employer.value);
    why += checkName(theForm.db_fullname.value);
    why += checkEmail(theForm.db_email.value);
    why += checkUsername(theForm.db_id.value);
    why += checkPassword(theForm.auth_password.value,theForm.auth_password_entry.value);
	if(theForm.language.value == 'espanol'){
		why += checkDropdown(theForm.db_relation.value, "No dió su estatus como empleado o estatus de empleado miembro del hogar \n");
	}else if(theForm.language.value == 'chinese'){
		why += checkDropdown(theForm.db_relation.value, "您未填写您是雇员，或您是雇员的家庭成员。\n");
	}else{
		why += checkDropdown(theForm.db_relation.value, "You did not enter your status as employee or household member of employee.\n");
	}
	if(theForm.language.value == 'espanol'){
		why += checkDropdown(theForm.client1.value, "No ha indicado si desea que se le pregunte preguntas sobre su historia familiar\n");
	}else if(theForm.language.value == 'chinese'){
		why += checkDropdown(theForm.client1.value, "您未说明您是否愿意被问及您的家族病史。\n");
	}else{
		why += checkDropdown(theForm.client1.value, "You did not indicate whether you want to be asked questions about your family history.\n");
	}
    
    
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
	if(theForm.language.value == 'espanol'){
		error = "No ha especificado una dirección de correo electrónico\n";
	}else if(theForm.language.value == 'chinese'){
		error = "您未填写邮箱地址。\n";
	}else{
		error = "You didn't enter an email address.\n";
	}
   //error = "You didn't enter an email address.\n";
}

    var emailFilter=/^.+@.+\..{2,3}$/;
    if (!(emailFilter.test(strng))) {
		if(theForm.language.value == 'espanol'){
		error = "Introduzca una dirección válida de correo electrónico\n";
		}else if(theForm.language.value == 'chinese'){
			error = "请填写有效的邮箱地址。\n";
		}else{
			error = "Please enter a valid email address.\n";
		}
        //error = "Please enter a valid email address.\n";
    }
    else {
//test email for illegal characters
       var illegalChars= /[\(\)\<\>\,\;\:\\\"\[\]]/
         if (strng.match(illegalChars)) {
		    if(theForm.language.value == 'espanol'){
				error = "La dirección de correo electrónico contiene caracteres no válidos\n";
			}else if(theForm.language.value == 'chinese'){
				error = "邮箱地址包含非法字符。\n";
			}else{
				error = "The email address contains illegal characters.\n";
			}
         // error = "The email address contains illegal characters.\n";
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
		if(theForm.language.value == 'espanol'){
			error = "El número de teléfono contiene caracteres no válidos\n";
		}else if(theForm.language.value == 'chinese'){
			error = "电话号码包含非法字符。\n";
		}else{
			error = "The phone number contains illegal characters.\n";
		}
      // error = "The phone number contains illegal characters.";
  
    }
    if (!(stripped.length == 10)) {
		if(theForm.language.value == 'espanol'){
			error = "El número de teléfono es de la longitud incorrecta. Asegúrese de incluir un código de área\n";
		}else if(theForm.language.value == 'chinese'){
			error = "电话号码长度有误，请确认您填写了电话区号。\n";
		}else{
			error = "The phone number is the wrong length. Make sure you included an area code.\n";
		}
		//error = "The phone number is the wrong length. Make sure you included an area code.\n";
    }
}
return error;
}


// password - between 6 chars min, uppercase, lowercase, and numeral

function checkPassword (strng,strng1) {
var error = "";
if (strng == "") {
	if(theForm.language.value == 'espanol'){
		error = "No ha introducido la contraseña\n";
	}else if(theForm.language.value == 'chinese'){
		error = "您未输入密码。\n";
	}else{
		error = "You didn't enter a password.\n";
	}
   //error = "You didn't enter a password.\n";
}

    var illegalChars = /[\W_]/; // allow only letters and numbers
    
    if ((strng.length < 6) || (strng.length > 25)) {
		if(theForm.language.value == 'espanol'){
			error = "La contraseña debe tener al menos 6 caracteres de largo y menos de 25\n";
		}else if(theForm.language.value == 'chinese'){
			error = "密码必须包含6-25个字符。\n";
		}else{
			error = "The password must be at least 6 characters long and less than 25.\n";
		}
       //error = "The password must be at least 6 characters long and less than 25.\n";
    }
    else if (illegalChars.test(strng)) {
		if(theForm.language.value == 'espanol'){
			error = "La contraseña contiene caracteres ilegales\n";
		}else if(theForm.language.value == 'chinese'){
			error = "密码包含非法字符。\n";
		}else{
			error = "The password contains illegal characters.\n";
		}
      //error = "The password contains illegal characters.\n";
    }
    if (!(strng==strng1)) {
		if(theForm.language.value == 'espanol'){
			error = "Las dos contraseñas que ha entrado, no coinciden\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您填写的两个密码不匹配。\n";
		}else{
			error = "The two passwords you entered, don't match.\n";
		}
    	//error += "The two passwords you entered, don't match.\n";
    }
return error;    
}    


function checkPassword_in (strng) {
var error = "";
if (strng == "") {
	if(theForm.language.value == 'espanol'){
		error = "No ha introducido la contraseña\n";
	}else if(theForm.language.value == 'chinese'){
		error = "您未输入密码。\n";
	}else{
		error = "You didn't enter a password.\n";
	}
   //error = "You didn't enter a password.\n";
}

    var illegalChars = /\W/; // allow only letters and numbers
    
    if ((strng.length < 6) || (strng.length > 24)) {
		if(theForm.language.value == 'espanol'){
			error = "La contraseña debe tener al menos 6 caracteres de largo y menos de 25\n";
		}else if(theForm.language.value == 'chinese'){
			error = "密码必须包含6-25个字符。\n";
		}else{
			error = "The password must be at least 6 characters long and less than 25.\n";
		}
       //error = "The password must be at least 6 characters long and less than 25.\n";
    }
    else if (illegalChars.test(strng)) {
		if(theForm.language.value == 'espanol'){
			error = "La contraseña contiene caracteres ilegales\n";
		}else if(theForm.language.value == 'chinese'){
			error = "密码包含非法字符。\n";
		}else{
			error = "The password contains illegal characters.\n";
		}
      //error = "The password contains illegal characters.\n";
    }
return error;    
}    
function checkRegnumber (strng) {
	var error = "";
	if (strng == "") {
		if(theForm.language.value == 'espanol'){
			error = "No ha introducido su número de registro\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写注册号码。\n";
		}else{
			error = "You didn't enter your registration number.\n";
		}
		//error = "You didn't enter your registration number.\n";
		return error;
		}	
return error;
}      

// username - 6 chars min, uc, lc, and underscore only.

function checkUsername (strng) {
	var error = "";
	if (strng == "") {
		
		if(theForm.language.value == 'espanol'){
			error = "No ha introducido un nombre de usuario\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写用户名。\n";
		}else{
			error = "You didn't enter a username.\n";
		}
		//error = "You didn't enter a username.\n";
		return error;
		}
	var illegalChars = /\w/; // allow letters, numbers, and underscores
	if ((strng.length < 6) || (strng.length > 24)) {
		if(theForm.language.value == 'espanol'){
			error = "El nombre de usuario debe tener al menos 6 caracteres de longitud y menos de 25\n";
		}else if(theForm.language.value == 'chinese'){
			error = "用户名必须包含6-25个字符。\n";
		}else{
			error = "The username must be at least 6 characters long and less than 25.\n";
		}
		//error = "The username must be at least 6 characters long and less than 25.\n";
		}
return error;
}       

// username - 6 chars min, uc, lc, and underscore only.

function checkRegnum (strng) {
	var error = "";
	if (strng == "") {
		if(theForm.language.value == 'espanol'){
			error = "No ha introducido un número de registro\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您未填写注册号码。\n";
		}else{
			error = "You didn't enter a registration number.\n";
		}
		//error = "You didn't enter a registration number.\n";
		return error;
		}
	var stripped = strng.replace(/[\(\)\.\-\ ]/g, '');
	//strip out acceptable non-numeric characters
	if (isNaN(parseInt(stripped))) {
		if(theForm.language.value == 'espanol'){
			error = "El código de registro contiene caracteres ilegales\n";
		}else if(theForm.language.value == 'chinese'){
			error = "注册码包含非法字符。\n";
		}else{
			error = "The registration code contains illegal characters.\n";
		}
   		//error = "The registration code contains illegal characters.";
	}
	if ((strng.length < 6) || (strng.length > 12)) {
		if(theForm.language.value == 'espanol'){
			error = "El código de registro debe tener al menos 6 caracteres de largo y menos de 12\n";
		}else if(theForm.language.value == 'chinese'){
			error = "注册码必须包含6-12个字符。\n";
		}else{
			error = "The registration code must be at least 6 characters long and less than 12.\n";
		}
		//error = "The registration code must be at least 6 characters long and less than 12.\n";
		}
return error;
}       


// name - 2 chars min.

function checkName (strng) {
var error = "";
if (strng == "") {
	if(theForm.language.value == 'espanol'){
		error = "No ha introducido su nombre completo\n";
	}else if(theForm.language.value == 'chinese'){
		error = "您未完整填写您的名字。\n";
	}else{
		error = "You didn't enter your complete name.\n";
	}
   //error = "You didn't enter your complete name.\n";
}


    var illegalChars = /\w/; // allow letters, numbers, and underscores
    if ((strng.length < 2) ) {
		if(theForm.language.value == 'espanol'){
			error = "Su nombre es más largo que\n";
		}else if(theForm.language.value == 'chinese'){
			error = "您的名字更长。\n";
		}else{
			error = "Your name is longer than that.\n";
		}
		//error = "Your name is longer than that.\n";
    }
return error;
}       


// ZIP 5 or 9 numeric.

function checkZIP (strng) {
var error = "";
if (strng == "") {
	if(theForm.language.value == 'espanol'){
		error = "No ha introducido un código postal\n";
	}else if(theForm.language.value == 'chinese'){
		error = "您未填写邮政编码。\n";
	}else{
		error = "You didn't enter a zip code.\n";
	}
	//error = "You didn't enter a zip code.\n";
	}
return error;
}       
function confirmDelete()
{
//var agree=confirm("Are you sure you wish to delete your account?");
var agree;
if(theForm.language.value == 'espanol'){
	agree=confirm("¿Está seguro de que desea eliminar su cuenta?");
}else if(theForm.language.value == 'chinese'){
	agree=confirm("您确定要删除您的账号吗？"); // but in that case confirm options(ok, yes, no, cancel etc.) will be in english
}else{
	agree=confirm("Are you sure you wish to delete your account?");
}
if (agree)
	return true ;
else
	return false ;
}

function Confirm_password() { 
	var pass1 = document.theForm.new1_password_entry.value; 
	var pass2 = document.theForm.new2_password_entry.value;

	if(pass1 == '' || pass2 == ''){
	    if(theForm.language.value == 'espanol'){
			alert("¡No ingresó/confirmó la contraseña!");
		}else if(theForm.language.value == 'chinese'){
			alert("您未输入密码/确认密码！");
		}else{
			alert("You did not enter password/confirm password!");
		}	
	  //alert("You did not enter password/confirm password!");
	  return false;
	}
	else if(pass1.length<6 || pass2.length<6){
		if(theForm.language.value == 'espanol'){
			alert("La contraseña debe tener al menos 6 caracteres de largo");
		}else if(theForm.language.value == 'chinese'){
			alert("密码必须至少包含6个字符。");
		}else{
			alert("The password must be at least 6 characters long");
		}
		//alert("The password must be at least 6 characters long.");
	  return false;
	} 
	if(pass1 == pass2){ 
	 return true; 
	} 
	else { 
		if(theForm.language.value == 'espanol'){
			alert("¡2 contraseñas no coinciden!");
		}else if(theForm.language.value == 'chinese'){
			alert("两个密码不匹配！");
		}else{
			alert("Two passwords do not match!");
		}
		//alert("Two passwords do not match!"); 
	 return false;
	}
} 

function CheckCheckboxes(){
     var c = document.getElementsByTagName('input');   
     for (var i = 0; i < c.length; i++) {   
		 if (c[i].type == 'checkbox' && c[i].checked == true) {   
		   // At least one checkbox IS checked       
			return true;   
		  }   
    }   
	// Nothing has been checked 	 
	//var agree=confirm("Are you sure you wish to continue without checking any option?");
	var agree;
	if(theForm.language.value == 'espanol'){
		agree=confirm("¿Está seguro de querer continuar sin la comprobación de alguna opción?");
	}else if(theForm.language.value == 'chinese'){
		agree=confirm("您确定不检查任何选项就继续吗？"); // but in that case js options(ok, yes, no, cancel etc.) will be in english
	}else{
		agree=confirm("Are you sure you wish to continue without checking any option?");
	}
    if (agree)
	  return true ;
    else
	  return false ;
}

function checkInt(val, field){

    var error = "";	    
	var intRegex = /^\d+$/;
	if(!intRegex.test(val)) {
	   error = " " + field + " must be an integer value.\n";	   
	}       
	return error;	
}
-->