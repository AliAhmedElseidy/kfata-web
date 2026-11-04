(() => {
  'use strict';
  const root=document.documentElement;
  const rtl=root.dir==='rtl';
  const ar=root.lang==='ar';
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  const active=new Set();
  const enabled=()=>document.body.dataset.motion==='on'&&!reduced.matches;
  const quiet=()=>document.body.dataset.intensity!=='full';
  const animate=(element,frames,options={})=>{
    if(!element||!enabled()||!element.animate)return null;
    const animation=element.animate(frames,{duration:quiet()?360:560,easing:'cubic-bezier(.2,.65,.3,1)',...options});
    active.add(animation);
    animation.finished.then(()=>active.delete(animation),()=>active.delete(animation));
    return animation;
  };
  const settle=element=>animate(element,[{opacity:.96,transform:`translate3d(0,${quiet()?6:12}px,0)`},{opacity:1,transform:'none'}]);
  // Local diagnostics only; no analytics, cookies or network reporting.
  if('PerformanceObserver' in window){
    try{new PerformanceObserver(list=>{const entries=list.getEntries();root.dataset.lcpMs=Math.round(entries[entries.length-1].startTime);}).observe({type:'largest-contentful-paint',buffered:true});}catch(_){}
    try{
      let maximum=0,total=0,start=0,previous=0;
      new PerformanceObserver(list=>list.getEntries().forEach(entry=>{if(entry.hadRecentInput)return;if(entry.startTime-previous>1000||entry.startTime-start>5000){start=entry.startTime;total=0;}total+=entry.value;previous=entry.startTime;maximum=Math.max(maximum,total);root.dataset.cls=maximum.toFixed(4);})).observe({type:'layout-shift',buffered:true});
      root.dataset.cls='0.0000';
    }catch(_){}
    try{let longest=0;new PerformanceObserver(list=>list.getEntries().forEach(entry=>{if(entry.interactionId){longest=Math.max(longest,entry.duration);root.dataset.maxInteractionMs=longest;}})).observe({type:'event',buffered:true,durationThreshold:16});}catch(_){}
  }

  // Native disclosure remains available when scripts are disabled.
  const menu=document.querySelector('.mobile-menu');
  const compact=window.matchMedia('(max-width:1000px)');
  if(menu){
    const summary=menu.querySelector('summary');
    const nav=menu.querySelector('nav');
    const close=(restore=false)=>{menu.open=false;if(restore)summary.focus();};
    const resize=()=>{
      const focus=document.activeElement;
      menu.open=!compact.matches;
      if(compact.matches&&nav.contains(focus))summary.focus();
      if(!compact.matches&&focus===summary)nav.querySelector('a')?.focus();
    };
    resize();compact.addEventListener('change',resize);
    menu.addEventListener('keydown',event=>{if(event.key==='Escape'&&compact.matches&&menu.open){event.preventDefault();close(true);}});
    nav.addEventListener('click',event=>{if(compact.matches&&event.target.closest('a'))close();});
    document.addEventListener('click',event=>{if(compact.matches&&menu.open&&!menu.contains(event.target))close(nav.contains(document.activeElement));});
    document.body.classList.add('navigation-ready');
    const header=document.querySelector('.site-header');
    const offset=()=>root.style.setProperty('--header-height',Math.ceil(header.getBoundingClientRect().height)+'px');
    offset();
    if('ResizeObserver' in window)new ResizeObserver(offset).observe(header);
  }

  // Full renditions are fetched only when selected. Cached thumbnail stays
  // visible during decoding; failed high-resolution loads retain the preview.
  document.querySelectorAll('[data-gallery]').forEach(gallery=>{
    const links=[...gallery.querySelectorAll('[data-gallery-image]')];
    let dialog,index=0,opener,controller,loadToken=0,closing=false;
    const create=()=>{
      dialog=document.createElement('dialog');dialog.className='lightbox';dialog.setAttribute('aria-label',ar?'معرض الصور':'Image gallery');
      const controls=document.createElement('div');controls.className='lightbox-controls';
      const prev=document.createElement('button'),next=document.createElement('button'),close=document.createElement('button');
      prev.type=next.type=close.type='button';
      prev.textContent=ar?'السابق':'Previous';next.textContent=ar?'التالي':'Next';close.textContent=ar?'إغلاق ×':'Close ×';
      prev.setAttribute('aria-keyshortcuts',rtl?'ArrowRight':'ArrowLeft');next.setAttribute('aria-keyshortcuts',rtl?'ArrowLeft':'ArrowRight');
      const figure=document.createElement('figure'),image=document.createElement('img'),caption=document.createElement('figcaption');
      caption.setAttribute('aria-live','polite');
      const show=()=>{
        const token=++loadToken,link=links[index];
        const preview=link.querySelector('img');
        image.src=preview?.currentSrc||preview?.src||link.href;
        image.alt=link.dataset.caption||'';
        caption.textContent=(index+1)+' / '+links.length+' — '+image.alt;
        figure.setAttribute('aria-busy','true');prev.disabled=next.disabled=links.length<2;
        const full=new Image();full.src=link.href;
        const loaded=()=>{
          if(token!==loadToken||!dialog.open)return;
          image.src=link.href;figure.removeAttribute('aria-busy');
          animate(image,[{opacity:.86,transform:'translate3d(0,4px,0)'},{opacity:1,transform:'none'}],{duration:quiet()?160:240});
        };
        if(full.decode)full.decode().then(loaded,()=>{if(token===loadToken)figure.removeAttribute('aria-busy');});
        else{full.onload=loaded;full.onerror=()=>figure.removeAttribute('aria-busy');}
      };
      const move=step=>{index=(index+links.length+step)%links.length;show();};
      const dismiss=()=>{
        if(closing||!dialog.open)return;
        closing=true;
        const exit=animate(dialog,[{opacity:1,transform:'none'},{opacity:0,transform:'translate3d(0,5px,0)'}],{duration:130});
        if(exit)exit.finished.then(()=>dialog.close(),()=>dialog.close());else dialog.close();
      };
      prev.addEventListener('click',()=>move(-1));next.addEventListener('click',()=>move(1));close.addEventListener('click',dismiss);
      dialog.addEventListener('cancel',event=>{event.preventDefault();dismiss();});
      dialog.addEventListener('keydown',event=>{
        if(event.key==='ArrowLeft'||event.key==='ArrowRight'){
          event.preventDefault();if(links.length>1)move((event.key==='ArrowRight'?1:-1)*(rtl?-1:1));
        }
        if(event.key==='Tab'){
          const buttons=[prev,next,close].filter(button=>!button.disabled);
          const first=buttons[0],last=buttons[buttons.length-1];
          if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
          else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
        }
      });
      dialog.addEventListener('close',()=>{loadToken++;closing=false;document.body.classList.remove('gallery-open');image.removeAttribute('src');if(opener?.isConnected)opener.focus({preventScroll:true});});
      controls.append(prev,next,close);figure.append(image,caption);dialog.append(controls,figure);document.body.append(dialog);
      return{show,close};
    };
    links.forEach((link,i)=>link.addEventListener('click',event=>{
      if(!window.HTMLDialogElement||!HTMLDialogElement.prototype.showModal||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
      event.preventDefault();opener=link;index=i;if(!dialog)controller=create();
      dialog.showModal();document.body.classList.add('gallery-open');controller.show();controller.close.focus();
      animate(dialog,[{opacity:.8,transform:'translate3d(0,8px,0)'},{opacity:1,transform:'none'}],{duration:quiet()?170:240});
    }));
  });

  let observer;
  const stop=()=>{active.forEach(animation=>animation.cancel());active.clear();document.querySelector('.opening-mark')?.remove();observer?.disconnect();root.dataset.motionState=reduced.matches?'reduced':'off';};
  reduced.addEventListener('change',event=>{if(event.matches)stop();});
  root.dataset.motionState=enabled()?'enabled':reduced.matches?'reduced':'off';
  if(!enabled())return;

  // Content starts visible. Effects never depend on a hidden/reveal-ready class.
  const hero=document.querySelector('.hero');
  if(hero){
    hero.querySelectorAll('.hero-copy>.eyebrow,.hero-copy>h1,.hero-intro,.hero-actions').forEach((element,i)=>{
      animate(element,[{opacity:.82,transform:`translate3d(0,${quiet()?6:12}px,0)`},{opacity:1,transform:'none'}],{delay:i*(quiet()?40:65),fill:'backwards'});
    });
    if(!quiet())animate(hero.querySelector('.hero-image'),[{transform:'scale(1.025)'},{transform:'scale(1)'}],{duration:950});
  }
  if('IntersectionObserver' in window){
    try{
      observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
        if(!entry.isIntersecting)return;
        observer.unobserve(entry.target);
        settle(entry.target);
        const children=entry.target.querySelectorAll('.project-grid>.project-card,.service-list>.project-card,.sector-list>.project-card,.process-steps>li');
        children.forEach((element,i)=>animate(element,[{opacity:.96,transform:`translate3d(0,${quiet()?5:10}px,0)`},{opacity:1,transform:'none'}],{delay:Math.min(i,3)*(quiet()?35:60)}));
      }),{threshold:.06});
      document.querySelectorAll('.reveal,.gallery-section,.project-facts,.page-heading,.footer-callout').forEach(element=>observer.observe(element));
    }catch(_){/* No observer means ordinary, visible content. */}
  }
  try{
    const original=document.querySelector('.brand img');
    if(hero&&original&&document.body.dataset.opening==='on'&&!sessionStorage.getItem('kfata-intro-v2')){
      sessionStorage.setItem('kfata-intro-v2','1');root.dataset.introPlayed='true';
      const opening=document.createElement('div');opening.className='opening-mark';opening.setAttribute('aria-hidden','true');
      const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 300 130');svg.setAttribute('focusable','false');
      ['M16 106H284','M40 18V116','M260 18V116','M78 96L150 24L222 96','M96 96L150 42L204 96','M114 96L150 60L186 96'].forEach((d,i)=>{
        const path=document.createElementNS(svg.namespaceURI,'path');path.setAttribute('d',d);path.setAttribute('pathLength','1');path.style.setProperty('--trace-delay',i*35+'ms');svg.append(path);
      });
      opening.append(svg,original.cloneNode(true));hero.append(opening);setTimeout(()=>opening.remove(),1320);
    }else root.dataset.introPlayed='false';
  }catch(_){root.dataset.introPlayed='false';/* Blocked storage never blocks content. */}
})();
