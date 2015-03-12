var horizontal_offset="5px" //horizontal offset of hint box from anchor link
var vertical_offset="0" //horizontal offset of hint box from anchor link. No need to change.
var ie=document.all
var ns6=document.getElementById&&!document.all
var tipmenuobj;

function getposOffset_tip(what, offsettype){
var totaloffset=(offsettype=="left")? what.offsetLeft : what.offsetTop;
var parentEl=what.offsetParent;
while (parentEl!=null){
totaloffset=(offsettype=="left")? totaloffset+parentEl.offsetLeft : totaloffset+parentEl.offsetTop;
parentEl=parentEl.offsetParent;
}
return totaloffset;
}

function iecompattest_tip(){
return (document.compatMode && document.compatMode!="BackCompat")? document.documentElement : document.body
}

function clearbrowseredge_tip(obj, whichedge){
var edgeoffset=(whichedge=="rightedge")? parseInt(horizontal_offset)*-1 : parseInt(vertical_offset)*-1
if (whichedge=="rightedge"){
var windowedge=ie && !window.opera? iecompattest_tip().scrollLeft+iecompattest_tip().clientWidth-30 : window.pageXOffset+window.innerWidth-40
tipmenuobj.contentmeasure=tipmenuobj.offsetWidth
if (windowedge-tipmenuobj.x < tipmenuobj.contentmeasure)
edgeoffset=tipmenuobj.contentmeasure+obj.offsetWidth+parseInt(horizontal_offset)
}
else{
var windowedge=ie && !window.opera? iecompattest_tip().scrollTop+iecompattest_tip().clientHeight-15 : window.pageYOffset+window.innerHeight-18
tipmenuobj.contentmeasure=tipmenuobj.offsetHeight
if (windowedge-tipmenuobj.y < tipmenuobj.contentmeasure)
edgeoffset=tipmenuobj.contentmeasure-obj.offsetHeight
}
return edgeoffset
}

function showhint(menucontents, obj, e, tipwidth)
{
if(wload==1)
{
createhintbox();
if ($("hintbox"))
{
if ((ie||ns6) && document.getElementById("hintbox")){
tipmenuobj=document.getElementById("hintbox")

var tipwidth1=tipwidth-7;

tipmenuobj.innerHTML="<div style='z-index:9999;width:"+tipwidth+"'><div style='float:left;position:relative;left:1px;width:7px;'><img src='images/trans.gif' width='1' height='10'><br><img src='images/htip_arrow.gif' width='7' height='13'></div><div style='float:left;z-index:2'><div style='width:"+tipwidth1+"px;float:left'><div style='float:left;'><img src='images/htip_top_left.gif' width='10' height='10'></div><div style='float:left;background-image: url(images/htip_top_line.gif);width:"+parseInt(tipwidth1-20)+"px;height:10px'><img src='images/trans.gif' width='"+parseInt(tipwidth1-20)+"' height='10'></div><div style='float:left;'><img src='images/htip_top_right.gif' width='10' height='10'></div></div><div style='clear:both'></div><div style='float:left;border-left:1px solid #CFCFCF;border-right:1px solid #CFCFCF;width:"+parseInt(tipwidth1-2)+"px !important; width:"+ eval(tipwidth1 - 2) +"px;'><div style='background-color:#ffffff;padding-left:10px;padding-right:10px' class='smalltxt'>"+menucontents+"</div></div><div style='clear:both'></div><div style='"+tipwidth1+"px;float:left'><div style='float:left;width:10px'><img src='images/htip_bottom_left.gif' width='10' height='10'></div><div style='float:left;background-image: url(images/htip_bottom_line.gif);width:"+parseInt(tipwidth1-20)+"px;height:10px'><img src='images/trans.gif' width='"+parseInt(tipwidth1-20)+"' height='10'></div><div style='float:left;width:10px'><img src='images/htip_bottom_right.gif' width='10' height='10'></div></div></div></div>";
tipmenuobj.style.left=tipmenuobj.style.top=-500
if (tipwidth!=""){
tipmenuobj.widthobj=tipmenuobj.style
tipmenuobj.widthobj.width=tipwidth;
}
tipmenuobj.x=getposOffset_tip(obj, "left")
tipmenuobj.y=getposOffset_tip(obj, "top")
tipmenuobj.style.left=tipmenuobj.x-clearbrowseredge_tip(obj, "rightedge")+obj.offsetWidth+"px"
tipmenuobj.style.top=tipmenuobj.y-clearbrowseredge_tip(obj, "bottomedge")+"px"
tipmenuobj.style.visibility="visible"
//obj.onblur=hidetip
}
}
}
}

function showhintother(menucontents, obj, e, tipwidth,left){
if(wload==1)
{
createhintbox();
if ($("hintbox"))
{
if ((ie||ns6) && document.getElementById("hintbox")){
tipmenuobj=document.getElementById("hintbox")
var tipwidth1=tipwidth-7;
tipmenuobj.innerHTML="<div style='width:"+tipwidth+"'><div style='float:left;z-index:2'><div style='width:"+tipwidth1+"px;float:left'><div style='float:left;'><img src='images/htip_top_left.gif' width='10' height='10'></div><div style='float:left;background-image: url(images/htip_top_line.gif);width:"+parseInt(tipwidth1-20)+"px;height:10px'><img src='images/trans.gif' width='"+parseInt(tipwidth1-20)+"' height='10'></div><div style='float:left;'><img src='images/htip_top_right.gif' width='10' height='10'></div></div><div style='clear:both'></div><div style='float:left;border-left:1px solid #CFCFCF;border-right:1px solid #CFCFCF;width:"+parseInt(tipwidth1-2)+"px !important; width:"+tipwidth1+"px;'><div style='background-color:#ffffff;padding-left:10px;padding-right:10px' class='smalltxt'>"+menucontents+"</div></div><div style='clear:both'></div><div style='"+tipwidth1+"px;float:left'><div style='float:left;width:10px'><img src='images/htip_bottom_left.gif' width='10' height='10'></div><div style='float:left;background-image: url(images/htip_bottom_line.gif);width:"+parseInt(tipwidth1-20)+"px;height:10px'><img src='images/trans.gif' width='"+parseInt(tipwidth1-20)+"' height='10'></div><div style='float:left;width:10px'><img src='images/htip_bottom_right.gif' width='10' height='10'></div></div></div><div style='float:left;position:relative;left:-1px;width:7px;'><img src='images/trans.gif' width='1' height='10'><br><img src='images/htipr_arrow.gif' width='7' height='13'></div></div>";

tipmenuobj.style.left=tipmenuobj.style.top=-500
if (tipwidth!=""){
tipmenuobj.widthobj=tipmenuobj.style
tipmenuobj.widthobj.width=tipwidth
}
tipmenuobj.x=left;
tipmenuobj.y=getposOffset_tip(obj, "top")
tipmenuobj.style.left=tipmenuobj.x-clearbrowseredge_tip(obj, "rightedge")+obj.offsetWidth+"px"
tipmenuobj.style.top=tipmenuobj.y-clearbrowseredge_tip(obj, "bottomedge")+"px"
tipmenuobj.style.visibility="visible"
//obj.onblur=hidetip
}}}}

function hidetip(){if ($("hintbox")){tipmenuobj.style.visibility="hidden";tipmenuobj.style.left="-500px"}}
function createhintbox(){var divblock=document.createElement("div");divblock.setAttribute("id", "hintbox");document.body.appendChild(divblock)}

/*if (window.addEventListener)
window.addEventListener("load", createhintbox, false)
else if (window.attachEvent)
window.attachEvent("onload", createhintbox)
else if (document.getElementById)
window.onload=createhintbox;*/