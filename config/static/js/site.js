(() => {
  const language = document.documentElement.lang === 'ar' ? 'ar' : 'en';
  // These measurements stay in this document. No analytics or network reporting.
  if ('PerformanceObserver' in window) {
    try {
      new PerformanceObserver(list => { const entries = list.getEntries(); document.documentElement.dataset.lcpMs = Math.round(entries[entries.length - 1].startTime); }).observe({type:'largest-contentful-paint',buffered:true});
      let maximum=0,total=0,start=0,previous=0;
      new PerformanceObserver(list => list.getEntries().forEach(entry => {if(entry.hadRecentInput)return;if(entry.startTime-previous>1000||entry.startTime-start>5000){start=entry.startTime;total=0;}total+=entry.value;previous=entry.startTime;maximum=Math.max(maximum,total);document.documentElement.dataset.cls=maximum.toFixed(4);})).observe({type:'layout-shift',buffered:true});
      let longest=0;
      new PerformanceObserver(list => list.getEntries().forEach(entry => {if(entry.interactionId){longest=Math.max(longest,entry.duration);document.documentElement.dataset.maxInteractionMs=longest;}})).observe({type:'event',buffered:true,durationThreshold:16});
    } catch (_) { /* Unsupported observations never affect content. */ }
  }
  const menu=document.querySelector('.mobile-menu');
  const compact=window.matchMedia('(max-width:1000px)');
  if(menu){menu.open=!compact.matches;compact.addEventListener('change',e=>{menu.open=!e.matches;});}
  // Progressive enhancement: ordinary image links continue to work without JS.
  document.querySelectorAll('[data-gallery]').forEach(gallery => {
    const links=[...gallery.querySelectorAll('[data-gallery-image]')];
    let dialog,index=0,opener;
    const create=()=>{
      dialog=document.createElement('dialog');dialog.className='lightbox';dialog.setAttribute('aria-label',language==='ar'?'معرض الصور':'Image gallery');
      const controls=document.createElement('div');controls.className='lightbox-controls';
      const prev=document.createElement('button'),next=document.createElement('button'),close=document.createElement('button');
      prev.type=next.type=close.type='button';prev.textContent=language==='ar'?'السابق':'Previous';next.textContent=language==='ar'?'التالي':'Next';close.textContent=language==='ar'?'إغلاق ×':'Close ×';
      const image=document.createElement('img'),caption=document.createElement('p');caption.setAttribute('aria-live','polite');
      const show=()=>{const link=links[index];image.src=link.href;image.alt=link.dataset.caption||'';caption.textContent=(index+1)+' / '+links.length+' — '+image.alt;prev.disabled=next.disabled=links.length<2;};
      prev.addEventListener('click',()=>{index=(index+links.length-1)%links.length;show();});next.addEventListener('click',()=>{index=(index+1)%links.length;show();});close.addEventListener('click',()=>dialog.close());
      dialog.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'){e.preventDefault();prev.click();}if(e.key==='ArrowRight'){e.preventDefault();next.click();}});
      dialog.addEventListener('close',()=>{document.body.classList.remove('gallery-open');image.removeAttribute('src');if(opener)opener.focus();});
      controls.append(prev,next,close);dialog.append(controls,image,caption);document.body.append(dialog);
      return {show,close};
    };
    let controller;
    links.forEach((link,i)=>link.addEventListener('click',e=>{
      if(!window.HTMLDialogElement||!HTMLDialogElement.prototype.showModal||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;
      e.preventDefault();opener=link;index=i;if(!dialog)controller=create();controller.show();dialog.showModal();document.body.classList.add('gallery-open');controller.close.focus();
    }));
  });
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  if(reduced.matches||document.body.dataset.motion!=='on')return;
  if('IntersectionObserver' in window){
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target);}}),{threshold:.04});
    document.querySelectorAll('.reveal').forEach(element=>observer.observe(element));document.body.classList.add('motion-ready');
    setTimeout(()=>document.querySelectorAll('.reveal').forEach(el=>el.classList.add('visible')),4000);
    reduced.addEventListener('change',e=>{if(e.matches){document.body.classList.remove('motion-ready');document.querySelector('.opening-mark')?.remove();observer.disconnect();}});
  }
  try{
    if(document.body.dataset.opening==='on'&&!sessionStorage.getItem('kfata-intro-v2')){
      sessionStorage.setItem('kfata-intro-v2','1');
      const opening=document.createElement('div');opening.className='opening-mark';opening.setAttribute('aria-hidden','true');
      const original=document.querySelector('.brand img');if(original){opening.append(original.cloneNode(true));document.body.append(opening);setTimeout(()=>opening.remove(),1300);}
    }
  }catch(_){/* Storage access must never block the site. */}
})();
