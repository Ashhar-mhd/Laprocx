(function(){
  var AR=document.documentElement.lang==='ar';
  var WA='971543368567';
  function waLink(t){return 'https://wa.me/'+WA+'?text='+encodeURIComponent(t)}
  function $(id){return document.getElementById(id)}

  // homepage tabs
  var tabs=[['tab-biz','grid-biz'],['tab-ind','grid-ind']];
  function showTab(id){tabs.forEach(function(p){var on=p[0]===id;var t=$(p[0]),g=$(p[1]);if(t&&g){t.setAttribute('aria-selected',on);g.hidden=!on}})}
  tabs.forEach(function(p){var t=$(p[0]);if(t)t.onclick=function(){showTab(p[0])}});

  // homepage finder
  var finder=$('finder');
  if(finder){
    var q=$('q'),out=$('results'),cards=[].slice.call(document.querySelectorAll('.svc'));
    var find=function(term){
      term=(term||'').trim().toLowerCase();
      if(!term){out.textContent='';return}
      var hit=cards.filter(function(c){return ((c.dataset.k||'')+' '+c.textContent).toLowerCase().indexOf(term)>-1})[0];
      if(!hit){out.innerHTML=(AR?'لم نجدها في القائمة. أرسلها لنا على ':'Not in the list yet. Send it to us on ')+'<a href="'+waLink(term)+'">'+(AR?'واتساب':'WhatsApp')+'</a>.';return}
      var grid=hit.closest('.svc-grid');if(grid)showTab(grid.id==='grid-biz'?'tab-biz':'tab-ind');
      out.innerHTML=(AR?'وجدنا: ':'Found: ')+'<a href="'+hit.getAttribute('href')+'">'+hit.querySelector('h3').textContent+(AR?' ←':' →')+'</a>';
    };
    finder.addEventListener('submit',function(e){e.preventDefault();find(q.value)});
    [].forEach.call(document.querySelectorAll('.chip'),function(c){c.onclick=function(){q.value=c.textContent;find(c.dataset.q)}});
  }

  // homepage estimate teaser
  var docsCount={g:7,f:6,c:9,r:5};
  var es=$('e-svc');
  if(es){
    var upd=function(){var n=docsCount[es.value];$('e-docs').textContent=AR?n+' مستندات':n+' documents';
      var em=$('e-em');var t=(AR?'مرحباً لابروكس، أريد تقدير رسوم: ':'Hello Laprocx, I would like a fee estimate for: ')+es.options[es.selectedIndex].text+' – '+em.options[em.selectedIndex].text;
      var b=es.closest('.est').querySelector('a.btn-wa');if(b)b.href=waLink(t)};
    es.onchange=upd;$('e-em').onchange=upd;upd();
  }

  // estimate page
  if(window.LPX_EST&&$('est-svc')){
    var D=window.LPX_EST.data,sv=$('est-svc'),em2=$('est-em'),nn=$('est-n');
    try{var pre=new URLSearchParams(location.search).get('s');if(pre&&D[pre])sv.value=pre}catch(e){}
    var draw=function(){
      var d=D[sv.value];$('est-name').textContent=d.name;$('est-time').textContent=d.time;
      var ul=$('est-docs');ul.innerHTML='';d.docs.forEach(function(x){var li=document.createElement('li');li.textContent=x;ul.appendChild(li)});
      $('est-more').href=d.url;
      var t=AR?('مرحباً لابروكس، أريد عرض سعر لخدمة: '+d.name+'\nالإمارة: '+em2.value+'\nالعدد: '+nn.value):('Hello Laprocx, I would like a quote for: '+d.name+'\nEmirate: '+em2.value+'\nPeople/documents: '+nn.value);
      $('est-wa').href=waLink(t);
    };
    [sv,em2,nn].forEach(function(x){x.onchange=draw});draw();
  }

  // brief filters
  var fb=[].slice.call(document.querySelectorAll('.filters button'));
  fb.forEach(function(b){b.onclick=function(){fb.forEach(function(x){x.setAttribute('aria-pressed',x===b)});var t=b.dataset.t;
    [].forEach.call(document.querySelectorAll('.card'),function(c){c.hidden=!(t==='all'||c.dataset.t===t)})}});

  // contact form -> WhatsApp
  var cf=$('contact-form');
  if(cf){cf.addEventListener('submit',function(e){e.preventDefault();
    var t=AR?('مرحباً لابروكس، أنا '+$('cf-name').value+'.\nالخدمة: '+$('cf-svc').value+'\n'+$('cf-msg').value):('Hello Laprocx, I am '+$('cf-name').value+'.\nService: '+$('cf-svc').value+'\n'+$('cf-msg').value);
    window.location.href=waLink(t)})}
})();
