// JavaScript Document
<!--
function MM_preloadImages() { //v3.0
  var d=document; if(d.images){ if(!d.MM_p) d.MM_p=new Array();
    var i,j=d.MM_p.length,a=MM_preloadImages.arguments; for(i=0; i<a.length; i++)
    if (a[i].indexOf("#")!=0){ d.MM_p[j]=new Image; d.MM_p[j++].src=a[i];}}
}

function MM_swapImgRestore() { //v3.0
  var i,x,a=document.MM_sr; for(i=0;a&&i<a.length&&(x=a[i])&&x.oSrc;i++) x.src=x.oSrc;
}

function MM_findObj(n, d) { //v4.01
  var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
    d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
  if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
  for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
  if(!x && d.getElementById) x=d.getElementById(n); return x;
}

function MM_swapImage() { //v3.0
  var i,j=0,x,a=MM_swapImage.arguments; document.MM_sr=new Array; for(i=0;i<(a.length-2);i+=3)
   if ((x=MM_findObj(a[i]))!=null){document.MM_sr[j++]=x; if(!x.oSrc) x.oSrc=x.src; x.src=a[i+2];}
}

function open_itAssessments(sel){
 var i = sel[sel.selectedIndex].value;
if(i == "0"){return false;}
else {subwin = window.open(i,'subwin','height=600,width=590,top=50,left=50,,toolbar=no,resizable=yes,status=no,menubar=no,scrollbars=yes'); subwin.focus();
}
}

function open_itCalculators(sel){
if(sel.selectedIndex>1) {
	if(sel.selectedIndex!=16) {subwin = window.open(sel[sel.selectedIndex].value,'subwin','height=410,width=410,top=50,left=50,,toolbar=no,resizable=yes,status=no,menubar=no,scrollbars=yes'); subwin.focus();
	}
	else if(sel.selectedIndex=16) {subwin = window.open(sel[sel.selectedIndex].value,'subwin','height=600,width=590,top=50,left=50,,toolbar=no,resizable=yes,status=no,menubar=no,scrollbars=yes'); subwin.focus();
	}
	}
}

function P7_Snap() { //v2.63 by PVII
 var x,y,ox,bx,oy,p,tx,a,b,k,d,da,e,el,tw,q0,xx,yy,w1,pa='px',args=P7_Snap.arguments;a=parseInt(a);
 if(document.layers||window.opera){pa='';}for(k=0;k<(args.length);k+=4){
 if((g=MM_findObj(args[k]))!=null){if((el=MM_findObj(args[k+1]))!=null){
 a=parseInt(args[k+2]);b=parseInt(args[k+3]);x=0;y=0;ox=0;oy=0;p="";tx=1;
 da="document.all['"+args[k]+"']";if(document.getElementById){
 d="document.getElementsByName('"+args[k]+"')[0]";if(!eval(d)){
 d="document.getElementById('"+args[k]+"')";if(!eval(d)){d=da;}}
 }else if(document.all){d=da;}if(document.all||document.getElementById){while(tx==1){
 p+=".offsetParent";if(eval(d+p)){x+=parseInt(eval(d+p+".offsetLeft"));y+=parseInt(eval(d+p+".offsetTop"));
 }else{tx=0;}}ox=parseInt(g.offsetLeft);oy=parseInt(g.offsetTop);tw=x+ox+y+oy;
 if(tw==0||(navigator.appVersion.indexOf("MSIE 4")>-1&&navigator.appVersion.indexOf("Mac")>-1)){
  ox=0;oy=0;if(g.style.left){x=parseInt(g.style.left);y=parseInt(g.style.top);}else{
  w1=parseInt(el.style.width);bx=(a<0)?-5-w1:-10;a=(Math.abs(a)<1000)?0:a;b=(Math.abs(b)<1000)?0:b;
  x=document.body.scrollLeft+event.clientX+bx;y=document.body.scrollTop+event.clientY;}}
 }else if(document.layers){x=g.x;y=g.y;q0=document.layers,dd="";for(var s=0;s<q0.length;s++){
  dd='document.'+q0[s].name;if(eval(dd+'.document.'+args[k])){x+=eval(dd+'.left');y+=eval(dd+'.top');
  break;}}}e=(document.layers)?el:el.style;xx=parseInt(x+ox+a),yy=parseInt(y+oy+b);
 if(navigator.appVersion.indexOf("MSIE 5")>-1 && navigator.appVersion.indexOf("Mac")>-1){
  xx+=parseInt(document.body.leftMargin);yy+=parseInt(document.body.topMargin);}
 e.left=xx+pa;e.top=yy+pa;}}}
}

function P7_moveScroll(co,md,op,dy,cy) { //v2.9 by PVII
 var g,d,dd,x,y,h,w,tt,ff,m=false,pa="";
 op=parseInt(op);cy=parseInt(cy);dy=parseInt(dy);
 if((parseInt(navigator.appVersion)>4 || navigator.userAgent.indexOf("MSIE")>-1)&& navigator.userAgent.indexOf("Opera")==-1){pa="px";}
 if((g=MM_findObj(co))==null){return;}
 if((d=MM_findObj(g.p7Scroll))==null){return;}
 var sp=parseInt(sp=g.P7Ssp),fr=parseInt(g.P7Sfr),ff=fr;
 if(op==2){g.p7sCycle=0;g.p7sCycDy=(dy>0)?dy:g.p7sCycDy;dy=0;op=3;}
 if(op==3){g.p7sCycle+=sp;ff=fr;if(parseInt(g.p7sCycle)>cy){
  op=2;g.p7sCycle=0;ff=g.p7sCycDy;}}g.P7Sop=op;if(dy>0){ff=dy;}
 var ti="g.p7Magic=setTimeout(\"P7_moveScroll('"+co+"','"+md+"',"+op+",0,"+cy+")\","+ff+")";
 if(op==2 || dy>0){clearTimeout(g.p7Magic);eval(ti);return;}
 dd=(document.layers)?d:d.style;x=parseInt(dd.left);y=parseInt(dd.top);
 if(document.all || document.getElementById){
  h=parseInt(d.offsetHeight);w=parseInt(d.offsetWidth);
  if(!h){h=parseInt(d.style.pixelHeight);w=parseInt(d.style.pixelWidth);}
 }else if(document.layers){h=parseInt(d.clip.height);w=parseInt(d.clip.width);}
 var st=0,rStart=parseInt(g.p7sStartLeft),tStart=parseInt(g.p7sStartTop);g.p7sH=h;g.p7sW=w;
 if(md=="Down"){tt=y-sp;st=parseInt(g.p7sBot)-h-tStart;
  if(tStart<0 && tt<tStart){dd.top=tStart+pa;
  }else if(tStart>=0 && tt<st){dd.top=st+pa;}else{dd.top=tt+pa;m=true;}}
 if(md=="Up"){tt=sp+y;var rEnd=tStart+h;if(tStart<0 && tt>rEnd){dd.top=rEnd+pa;
  }else if(tStart>=0 && tt>tStart){dd.top=tStart+pa;}else{dd.top=tt+pa;m=true;}}
 if(md=="Right"){tt=x-sp;st=parseInt(g.p7sRight)-w-rStart;
  if(rStart<0 && tt<rStart){dd.left=rStart+pa;
  }else if (rStart>=0 && tt<st){dd.left=st+pa;}else{dd.left=tt+pa;m=true;}}
 if(md=="Left"){tt=x+sp;var rEnd=rStart+w;if(rStart<0 && tt>rEnd){dd.left=rEnd+pa;
  }else if (rStart>=0 && tt>rStart){dd.left=rStart+pa;}else{dd.left=tt+pa;m=true;}}
 if(m && g.toMove){eval(ti);}else{if(g.P7Sflip==1){clearTimeout(g.p7Magic);var tj=0;
  eval("g.p7Magic=setTimeout(\"P7_runScroller('"+co+"','Reverse','Medium',0,0,0,1)\","+tj+")");
 }else{if(op>0 && g.toMove){
  g.p7sCycle=0;dd.top=g.p7sStartTop+pa;dd.left=g.p7sStartLeft+pa;eval(ti);}}}
}

function P7_runScroller(co,md,spd,op,dy,cy,flp) { //v2.9 by PVII
 var g,d,dd,rl=0;rt=0;pa='',sp=2,fr=10,slw=true,kl=true;
 if((parseInt(navigator.appVersion)>4 || navigator.userAgent.indexOf("MSIE")>-1)&& navigator.userAgent.indexOf("Opera")==-1){pa="px";}
 if(navigator.userAgent.indexOf("NT")>-1 || navigator.userAgent.indexOf("Windows 2000")>-1 ){slw=false;}
 if((g=MM_findObj(co))!=null){if(g.p7Scroll){
 if((d=MM_findObj(g.p7Scroll))!=null){dd=(document.layers)?d:d.style;
 if(md=="Resume" && g.P7Sspd){spd=g.P7Sspd;md=g.P7Smd;op=g.P7Sop;dy=0;cy=g.P7Scy;flp=g.P7Sflip;kl=false;}
 if(md=="Reverse" && g.P7Sspd){spd=g.P7Sspd;md=g.P7Smd;op=g.P7Sop;flp=g.P7Sflip;dy=0;cy=g.P7Scy;kl=false;g.p7sCycle=0;
  if(g.P7Smd == "Down"){md="Up";if(g.P7Sop>0){g.p7sStartTop=g.p7sStartTop-g.p7sH;}}
  if(g.P7Smd == "Up"){md="Down";if(g.P7Sop>0){g.p7sStartTop=g.p7sStartTop+g.p7sH;}}
  if(g.P7Smd == "Left"){md="Right";if(g.P7Sop>0){g.p7sStartLeft=g.p7sStartLeft+g.p7sW;}}
  if(g.P7Smd == "Right"){md="Left";if(g.P7Sop>0){g.p7sStartLeft=g.p7sStartLeft-g.p7sW;}}}
 if(spd=="Slow"){sp=(slw)?2:1;fr=(slw)?40:30;
 }else if(spd=="Medium"){sp=(slw)?4:1;fr=(slw)?40:10;
 }else{sp=(slw)?8:4;fr=(slw)?40:10;}
 if(md=="Stop"){g.toMove=false;clearTimeout(g.p7Magic);}else if(md=="Reset"){
  g.toMove=false;dd.top=g.p7sStartTop+pa;dd.left=g.p7sStartLeft+pa;
 }else{if(kl){g.P7Ssp=sp;g.P7Sfr=fr;}if(md=="Speed"){return;}
  g.toMove=true;clearTimeout(g.p7Magic);
  g.P7Smd=md;g.P7Sspd=spd;g.P7Sop=op;g.P7Sdy=dy;g.P7Scy=cy;g.P7Sflip=flp;
  eval("P7_moveScroll('"+co+"','"+md+"',"+op+","+dy+","+cy+")");}}}}
}

function P7_setScroller(a,b,x,y) { //v2.9 by PVII
 var g,d,dd,w,ww,pa="";
 if((parseInt(navigator.appVersion)>4 || navigator.userAgent.indexOf("MSIE")>-1)&& navigator.userAgent.indexOf("Opera")==-1){pa="px";}
 if((g=MM_findObj(a))!=null && (d=MM_findObj(b))!=null){
  if(g.p7Scroll){if((w=MM_findObj(g.p7Scroll))!=null){
   ww=(document.layers)?w:w.style;ww.visibility="hidden";}}
 g.p7Scroll=b;dd=(document.layers)?d:d.style;dd.left=parseInt(x)+pa;
 dd.top=parseInt(y)+pa;dd.visibility="visible";g.p7sCycle=0;
 if(document.layers){g.p7sTop=g.clip.top;g.p7sBot=g.clip.bottom;
  g.p7sRight=g.clip.right;g.p7sLeft=g.clip.left;g.p7sStartTop=parseInt(y);g.p7sStartLeft=parseInt(x);
 }else if(g.style.clip){var tc=g.style.clip;var j=tc.indexOf("(");
  tc=tc.substring(j+1,tc.length-1);var tr=tc.split(" ");
  if(tc.length < 1){tr[0]=0;tr[3]=0;tr[2]=g.style.pixelHeight;tr[1]=g.style.pixelWidth;}
  g.p7sTop=parseInt(tr[0]);g.p7sRight=parseInt(tr[1]);g.p7sBot=parseInt(tr[2]);
  g.p7sLeft=parseInt(tr[3]);g.p7sStartTop=parseInt(y);g.p7sStartLeft=parseInt(x);
 }else{g.p7sTop=0;g.p7sRight=g.offsetWidth;g.p7sBot=g.offsetHeight;
  g.p7sLeft=0;g.p7sStartTop=parseInt(y);g.p7sStartLeft=parseInt(x);}}
  g.toMove=true;
}
function MM_reloadPage(init) {  //Updated by PVII. Reloads the window if Nav4 resized
  if (init==true) with (navigator) {if ((appName=="Netscape")&&(parseInt(appVersion)==4)) {
    document.MM_pgW=innerWidth; document.MM_pgH=innerHeight; onresize=MM_reloadPage; }}
  else if (innerWidth!=document.MM_pgW || innerHeight!=document.MM_pgH) location.reload();
}

MM_reloadPage(true);



  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-3560878-1']);
  _gaq.push(['_setDomainName', 'none']);
  _gaq.push(['_setAllowLinker', true]);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

function isEmpty(strng, msg) {
	var error = "";
	  if (strng.length == 0) {
		 error = msg;
	  }
	return error;
}
function checkMailForm(theForm) {
    var why = "";
    why += isEmpty(theForm.name.value, "You did not enter your name.\n");
    why += isEmpty(theForm.company.value, "You did not enter your company.\n");
    why += isEmpty(theForm.phone.value, "You did not enter your phone number.\n");
    why += isEmpty(theForm.email.value, "You did not enter your email.\n");
    if (why != "") {
       alert(why);
       return false;
    }
	var chkd = theForm.files1.checked || theForm.files2.checked|| theForm.demo.checked;

    if (chkd) {
      return true; //Submit the form
    } else {
      alert ("You did not check any checkbox");
      return false; //Prevent it from being submitted
    }
return true;
}

//-->