var ggrloaded=0;

function page_1_load()

{

	if(ggrloaded){

		all_assessment_check();

		select_dates();

		if(document.frm.rpt_type[0].checked){disable_radio3();}

		if(document.frm.rpt_type[1].checked){disable_radio1();}

		if(document.frm.rpt_type[2].checked){disable_radio2();}

		if(document.frm.rpt_type[3].checked){disable_radio4();}

		if(!document.frm.rpt_type[1].checked && 

			!document.frm.rpt_type[2].checked &&

			!document.frm.rpt_type[3].checked &&

			!document.frm.rpt_type[0].checked){disable_radio1();document.frm.rpt_type[1].checked=true;}

	}	

}

function page_1_loadx()

{

	all_assessment_check();

	max_init();

	select_dates();

	if(document.frm.rpt_type[0].checked){disable_radio3();}

	if(document.frm.rpt_type[1].checked){disable_radio1();}

	if(document.frm.rpt_type[2].checked){disable_radio2();}

	if(document.frm.rpt_type[3].checked){disable_radio4();}

	if(!document.frm.rpt_type[1].checked && 

		!document.frm.rpt_type[2].checked &&

		!document.frm.rpt_type[3].checked &&

		!document.frm.rpt_type[0].checked){disable_radio1();document.frm.rpt_type[1].checked=true;}

}

function disable_radio1()

{

	document.frm.rpt_format[0].disabled=false;

	document.frm.rpt_format[1].disabled=false;

	document.frm.rpt_format[2].disabled=false;

	document.frm.rpt_format[3].disabled=true;

	

	document.frm.rpt_format[0].checked=true;

	var object=document.getElementById('selections');

		object.style.display = 'block';

	var object1=document.getElementById('accounting');

		object1.style.display = 'block';

}



function disable_radio2()

{

	document.frm.rpt_format[0].disabled=false;

	document.frm.rpt_format[1].disabled=false;

	document.frm.rpt_format[2].disabled=false;

	document.frm.rpt_format[3].disabled=false;

	

	document.frm.rpt_format[1].checked=true;

	var object=document.getElementById('selections');

		object.style.display = 'block';

	var object1=document.getElementById('accounting');

		object1.style.display = 'block';

}



function disable_radio3()

{

	document.frm.rpt_format[0].disabled=true;

	document.frm.rpt_format[1].disabled=false;

	document.frm.rpt_format[2].disabled=true;

	document.frm.rpt_format[3].disabled=true;

	

	document.frm.rpt_format[1].checked=true;

	var object=document.getElementById('selections');

		object.style.display = 'block';

	var object1=document.getElementById('accounting');

		object1.style.display = 'none';

}



function disable_radio4()

{

	document.frm.rpt_format[0].disabled=true;

	document.frm.rpt_format[1].disabled=false;

	document.frm.rpt_format[2].disabled=false;

	document.frm.rpt_format[3].disabled=false;

	

	document.frm.rpt_format[1].checked=true;

	var object=document.getElementById('selections');

		object.style.display = 'block';

	var object1=document.getElementById('accounting');

		object1.style.display = 'block';

}



function all_assessment_check()

{
     var chk = document.frm.assessment_list;
		
	 if (document.frm.all_assessment.checked){
	    for (i = 0; i < chk.length; i++){
		chk[i].checked = false ;
		}
	}
	 else if (document.frm.assessment_list[0].checked ||
		document.frm.assessment_list[1].checked ||
		document.frm.assessment_list[2].checked ||
		document.frm.assessment_list[3].checked ||
		document.frm.assessment_list[4].checked  ) 
	{
		document.frm.all_assessment.checked = false;
	}

    // if (document.frm.assessment_list){
	// if (document.frm.assessment_list[0].checked ||
		// document.frm.assessment_list[1].checked ||
		// document.frm.assessment_list[2].checked ||
		// document.frm.assessment_list[3].checked ||
		// document.frm.assessment_list[4].checked  ) 
		// {
		// document.frm.all_assessment.checked = false;}
	// else{	document.frm.all_assessment.checked = true;}

    // }
}



function select_dates()

{

	if(document.frm.date_range > ""){

		document.frm.date[0].checked=true;

		document.frm.date[1].checked=false;

		document.frm.date[2].checked=false;

		document.frm.date[3].checked=false;

		}

	else if(!document.frm.date[0].checked && !document.frm.date[1].checked && !document.frm.date[2].checked && !document.frm.date[3].checked)

		{

		document.frm.date[0].checked=true;

		document.frm.date[1].checked=false;		

		document.frm.date[2].checked=false;		

		document.frm.date[3].checked=false;		

		}

}



function setDateBox()

{

	if(document.frm.s_month > ""){

		document.frm.date[0].checked=false;

		document.frm.date[1].checked=true;

		document.frm.date[2].checked=false;

		document.frm.date[3].checked=false;

		}

}



function setDateBox1()

{

	if(document.frm.s_month1 > ""){

		document.frm.date[0].checked=false;

		document.frm.date[1].checked=false;

		document.frm.date[2].checked=true;

		document.frm.date[3].checked=false;

		}

}



function setDateBox2()

{

	if(document.frm.e_month1 > ""){

		document.frm.date[0].checked=false;

		document.frm.date[1].checked=false;

		document.frm.date[2].checked=false;

		document.frm.date[3].checked=true;

		}

}



function hideSelections()

{

	var object=document.getElementById('selections');

	var object1=document.getElementById('accounting');

	if(document.frm.use_saved.value == 0){ 

		object.style.display = 'block';

		object1.style.display = 'block';}

	else {

		object.style.display = 'none';

		object1.style.display = 'none';}

}



function open_records()

{

	document.frm.records.disabled=false;

}



function zero_records()

{

	document.frm.records.disabled=true;

}



function fill_drop_down(no)

{

	var select_name = 'gorup_id' + no;

	var comp = 'comp' + no;

	var choice = 'choice' + no;

	if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "sex" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

    

		var option10 = new Option("equal to", "equ");

		eval("document.frm."+comp+".options[0]=option10");

		

		var option20 = new Option("Male", "male");

		var option21 = new Option("Female", "female");		

		eval("document.frm."+choice+".options[0]=option20");

		eval("document.frm."+choice+".options[1]=option21");

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "age" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		var option11 = new Option("greater then", "gt");

		var option12 = new Option("less then", "lt");

		eval("document.frm."+comp+".options[0]=option10");

		eval("document.frm."+comp+".options[1]=option11");

		eval("document.frm."+comp+".options[2]=option12");

		

		var option20 = new Option("18", "18");

		eval("document.frm."+choice+".options[0]=option20");

		var j = 1;

		var i=20;

		while ( i<=80 ){

			option20 = new Option(i, i);

			eval("document.frm."+choice+".options["+j+"]=option20");

			i = i + 5;

			j = j + 1;

		}

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "bmi" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		eval("document.frm."+comp+".options[0]=option10");

		var j = 0;

		for ( i=18; i<=35; i++ ){

			option20 = new Option(i, i);

			eval("document.frm."+choice+".options["+j+"]=option20");

			j = j + 1;

		}

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "diabetes" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		eval("document.frm."+comp+".options[0]=option10");

		

		var option20 = new Option("Yes", "yes");

		var option21 = new Option("No", "no");		

		eval("document.frm."+choice+".options[0]=option20");

		eval("document.frm."+choice+".options[1]=option21");

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "bp" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		eval("document.frm."+comp+".options[0]=option10");

		

		var option20 = new Option("Low", "low");

		var option21 = new Option("Normal", "normal");

		var option22 = new Option("Prehypertension", "prehypertension");

		var option23 = new Option("High", "high");

		eval("document.frm."+choice+".options[0]=option20");

		eval("document.frm."+choice+".options[1]=option21");

		eval("document.frm."+choice+".options[2]=option22");

		eval("document.frm."+choice+".options[3]=option23");

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "cholesterol" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		eval("document.frm."+comp+".options[0]=option10");

		

		var option20 = new Option("Low", "low");

		var option21 = new Option("Normal", "normal");

		var option22 = new Option("Slightly High", "shigh");

		var option23 = new Option("High", "high");

		eval("document.frm."+choice+".options[0]=option20");

		eval("document.frm."+choice+".options[1]=option21");

		eval("document.frm."+choice+".options[2]=option22");

		eval("document.frm."+choice+".options[3]=option23");

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "race" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		eval("document.frm."+comp+".options[0]=option10");

		

		var option20 = new Option("African American", "africanamerican");

		var option21 = new Option("Aleutian, Eskimo or American Indian", "aleutian");

		var option22 = new Option("Asian", "asian");

		var option23 = new Option("Caucasian", "caucasian");

		var option24 = new Option("Hispanic/Latino", "hispanic");

		var option25 = new Option("Other", "other");

		var option26 = new Option("Don't know", "dknow");

		eval("document.frm."+choice+".options[0]=option20");

		eval("document.frm."+choice+".options[1]=option21");

		eval("document.frm."+choice+".options[2]=option22");

		eval("document.frm."+choice+".options[3]=option23");

		eval("document.frm."+choice+".options[4]=option24");

		eval("document.frm."+choice+".options[5]=option25");

		eval("document.frm."+choice+".options[6]=option26");

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "smoke" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		eval("document.frm."+comp+".options[0]=option10");

		

		var option20 = new Option("Never Smoked", "nsmoked");

		var option21 = new Option("Used to Smoke", "utsmoke");

		var option22 = new Option("Still Smoke", "ssmoke");

		eval("document.frm."+choice+".options[0]=option20");

		eval("document.frm."+choice+".options[1]=option21");

		eval("document.frm."+choice+".options[2]=option22");

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "drink" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		var option11 = new Option("greater then", "gt");

		var option12 = new Option("less then", "lt");

		eval("document.frm."+comp+".options[0]=option10");

		eval("document.frm."+comp+".options[1]=option11");

		eval("document.frm."+comp+".options[2]=option12");

		

		var option20 = new Option("No", "no");

		eval("document.frm."+choice+".options[0]=option20");

		var j = 1;

		for ( i=1; i<=100; i++ ){

			option20 = new Option(i, i);

			eval("document.frm."+choice+".options["+j+"]=option20");

			j = j + 1;

		}

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "exercise" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		eval("document.frm."+comp+".options[0]=option10");

		

		var option20 = new Option("None", "none");

		var option21 = new Option("1 or 2 per week", "perweek12");

		var option22 = new Option("3 or more per week", "perweek3m");

		eval("document.frm."+choice+".options[0]=option20");

		eval("document.frm."+choice+".options[1]=option21");

		eval("document.frm."+choice+".options[2]=option22");

	}else if ( eval("document.frm."+select_name+".options[document.frm."+select_name+".options.selectedIndex].value") == "risk" ) {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

		

		var option10 = new Option("equal to", "equ");

		eval("document.frm."+comp+".options[0]=option10");

		

		var option20 = new Option("Low", "low");

		var option21 = new Option("Normal", "normal");

		var option22 = new Option("Elevated", "elevated");

		var option23 = new Option("High", "high");

		eval("document.frm."+choice+".options[0]=option20");

		eval("document.frm."+choice+".options[1]=option21");

		eval("document.frm."+choice+".options[2]=option22");

		eval("document.frm."+choice+".options[3]=option23");

	}else {

		for(i=eval("frm."+comp+".options.length")-1; i>=0; i--) {

			eval("frm."+comp+".options["+i+"]=null");

		}

		

		for(i=eval("frm."+choice+".options.length")-1; i>=0; i--) {

			eval("frm."+choice+".options["+i+"]=null");

		}

	}

}

function enable_assessment_list()
{
	var length = document.frm.assessment_list.length;
	for(var i=0; i<length; i++) {
		document.frm.assessment_list[i].disabled=false;
	}
	document.getElementById('indv_fields').style.display='';
	document.getElementById('part_fields').style.display='none';
}
function disable_assessment_list()
{
	var length = document.frm.assessment_list.length;
	for(var i=0; i<length; i++) {
		document.frm.assessment_list[i].disabled=true;
	}
	document.getElementById('indv_fields').style.display='none';
	document.getElementById('part_fields').style.display='';
}
function check_new_report_form() 
{
	if(document.frm.new_report.checked == true ) {
		if (document.frm.rpt_name.value == '') {
			alert("You did not enter report name.\n");
			return false;
		} else {
			 var rpt_string = 	document.frm.rpt_friendly_string.value;
			 var array = rpt_string.split(',') ;
			 var name = trim(document.frm.rpt_name.value);
			 document.frm.rpt_name.value = name;
			 for (var i=0; i<array.length; i++) {
				if(trim(array[i]) == name) {				
					alert("Report name already exists.\n");
					return false;
				}
			 }
		}
	} else {
		return true;
	}

}

	function addField(objid,handler) {
		if(document.group_form.numberSubgroups.value == '' ) {
			alert("Please enter the numbers of subgroups.");
			return false;
		}
		var fieldbody = document.getElementById(objid);
		var ctr = document.group_form.numberSubgroups.value;
		var ctr_value = (fieldbody.getElementsByTagName("input").length/2) + 1;
		ctr = parseInt(ctr) + parseInt(ctr_value);
		for(i=ctr_value ; i< ctr; i++) {
			 add_row(objid,'input','subgroupNames',"text","","10","10","SubGroup name ",i);
			 add_row(objid,'input','subgroupDescriptions',"text","","255","50","SubGroup Description ",i);
		}	 
	}
	
	function add_row(objid,el,el_name,el_type, el_value, el_length,el_size,text,ctr) {
		var fieldbody = document.getElementById(objid);
		input_option = document.createElement(el);
		 input_option.name = el_name;
		 input_option.type = el_type;
		 input_option.value = el_value;
		 input_option.className = "maintext-n";
		 input_option.maxLength = el_length;
		 input_option.size = el_size;
		 if(el_name == "subgroupNames") {
			input_option.setAttribute("onblur", "return alphanumeric(this)");
		}
		var row = document.createElement('tr');
		var cell = document.createElement('td');
		cell.setAttribute("class", "maintext-b");
		cell.setAttribute("width", "180px");
		cell.appendChild(document.createTextNode(text + ctr+ ": "));
		row.appendChild(cell);
		var cell1 = document.createElement('td');
		cell1.appendChild(input_option);
		 row.appendChild(cell1);
		 fieldbody.appendChild(row);
	}
	function trim(str) {
		var string;
		string = str.replace(/^\s+/, '');
		string = string.replace(/\s+$/, '');
	    return string ;
	}
	function checkIntValue (obj) {
		var obj_value = obj.value;
		obj.value = trim(obj.value);
		if (isNaN(obj.value) || (obj.value<0) && (obj.value) ) {
			alert('Value "'+obj_value + '" is not a valid positive integer.');
			obj.value = 0;
			obj.focus();
			//alert(obj)
			return false;
		}
	}
function alphanumeric(obj)
{
	var numaric = obj.value;
	for(var j=0; j<numaric.length; j++)
		{
		  var alphaa = numaric.charAt(j);
		  var hh = alphaa.charCodeAt(0);
		  if((hh > 47 && hh<58) || (hh > 64 && hh<91) || (hh > 96 && hh<123))
		  {
		  }
		else	{
			 alert("Please enter the valid subgroup name. Only alphanumeric charaters are allowed.");
			 obj.value = '';
			 return false;
		  }
 		}
 return true;
}
function check_group_form() 
{   
	var regex =/\D/ ;
	if(document.group_form.groupID.value == '' ) {
		document.group_form.groupID.focus();
		alert("You did not enter group ID.");
		return false;
	} 
	// if(document.group_form.groupID.value != '' &&  document.group_form.groupID.value.match(regex)) {
		// document.group_form.groupID.focus();
		// alert("Please enter the valid group Id.");
		// return false;
	// }
	if(document.group_form.groupName.value == '' ) {
		document.group_form.groupName.focus();
		alert("You did not enter group name.");
		return false;
	}
	if( document.group_form.groupRestrict.value == '') {
	    alert("You did not select any assessment(s).");
		document.group_form.groupRestrict.focus();		
		return false;
	}
	if (document.group_form.subgroupNames){
		for (var i =0 ; i <document.group_form.subgroupNames.length ; i++) {
			if(document.group_form.subgroupNames[i].value == '' ) {
				document.group_form.subgroupNames[i].focus();
				alert("You did not enter subgroup name.");
				return false;
			}
		}
	}

	 if( document.group_form.groupAdminEmail.value != '') {
		var error = checkEmail(document.group_form.groupAdminEmail.value);
		if(error) {
			document.group_form.groupAdminEmail.focus();
			alert(error);
			return false;
		}
	}
	
	return true;
}
	

function checkEmail (strng) {
	var error="";
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

function check_Aggre_Rpt()
{
   var strng = document.frm_Ggr_Query.file_name.value;
     
   if ((strng.length < 6) || (strng.length > 12)) {
		alert("The file name must be at least 6 characters long and less than 12.");
		return false;
		}
}