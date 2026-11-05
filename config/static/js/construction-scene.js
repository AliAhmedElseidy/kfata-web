(() => {
  'use strict';
  const root=document.querySelector('[data-construction-scene]');
  if(!root)return;
  const video=root.querySelector('video'),player=root.querySelector('.scene-player');
  const controls=root.querySelector('.scene-controls'),toggle=root.querySelector('[data-scene-toggle]'),status=root.querySelector('[data-scene-state]');
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  const mobile=window.matchMedia('(max-width:800px)').matches;
  const ar=document.documentElement.lang==='ar',label=(a,b)=>ar?a:b;
  const masterOff=document.body.dataset.motion==='off';
  let phase='poster',generation=0,attempted=false;
  const setPhase=value=>{phase=value;root.dataset.state=value;};
  const completed=reason=>{
    ++generation;setPhase(reason);video.pause();player.dataset.playing='false';
    toggle.textContent=label('إعادة العرض','Replay');
    controls.hidden=reduced.matches||masterOff;
    status.textContent=reason==='reduced'?label('تقليل الحركة: المبنى المكتمل','Reduced motion: completed building'):label('المبنى المكتمل','Completed building');
  };
  const start=(reset=true)=>{
    if(reduced.matches||masterOff){completed(masterOff?'disabled':'reduced');return;}
    attempted=true;root.dataset.autoplayAttempted='true';
    const token=++generation;setPhase('loading');controls.hidden=false;
    video.muted=true;video.defaultMuted=true;video.playsInline=true;
    if(!video.getAttribute('src'))video.src=mobile?video.dataset.mobileUrl:video.dataset.desktopUrl;
    if(reset)video.currentTime=0;
    try{
      const result=video.play();
      if(result?.catch)result.catch(()=>{if(token===generation)completed('blocked');});
    }catch(_){if(token===generation)completed('blocked');}
  };
  video.addEventListener('playing',()=>{
    if(phase==='paused'){video.pause();return;}
    if(reduced.matches||masterOff){completed(masterOff?'disabled':'reduced');return;}
    setPhase('playing');player.dataset.playing='true';
    toggle.textContent=label('إيقاف مؤقت','Pause');status.textContent='';
  });
  video.addEventListener('pause',()=>{
    if(phase==='playing'&&!video.ended){setPhase('paused');toggle.textContent=label('متابعة','Resume');}
  });
  video.addEventListener('ended',()=>completed('finished'));
  video.addEventListener('error',()=>completed('error'));
  toggle.addEventListener('click',()=>{
    if(phase==='playing'||phase==='loading'){
      ++generation;setPhase('paused');video.autoplay=false;video.pause();
      toggle.textContent=label('متابعة','Resume');
    }else start(phase!=='paused');
  });
  reduced.addEventListener('change',()=>{
    if(reduced.matches){completed('reduced');video.removeAttribute('src');video.load();}
    else {controls.hidden=masterOff;if(!attempted&&!masterOff)start();}
  });
  // A fresh document always starts again. No session/cookie/storage playback gate.
  if(reduced.matches||masterOff)completed(masterOff?'disabled':'reduced');else start();
  window.addEventListener('pageshow',event=>{if(event.persisted&&!reduced.matches&&!masterOff)start();});
})();
