(() => {
  'use strict';
  const video=document.querySelector('.scene-player video');
  if(!video)return;
  const player=video.parentElement,play=document.querySelector('[data-scene-play]'),skip=document.querySelector('[data-scene-skip]'),state=document.querySelector('[data-scene-state]');
  document.querySelector('.scene-controls').hidden=false;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)'),ar=document.documentElement.lang==='ar';
  const label=(arabic,english)=>ar?arabic:english;
  const finish=()=>{video.pause();player.dataset.playing='false';play.textContent=label('إعادة المشهد','Replay scene');state.textContent=label('المبنى المكتمل','Completed building');};
  const start=()=>{
    if(reduced.matches){finish();state.textContent=label('تقليل الحركة: صورة ثابتة','Reduced motion: still image');return;}
    if(!video.src)video.src=video.dataset.src;
    if(video.ended||player.dataset.playing!=='true')video.currentTime=0;
    video.play().catch(()=>{player.dataset.playing='false';state.textContent=label('اضغط لتشغيل الفيديو','Press to play video');});
  };
  play.addEventListener('click',()=>video.paused?start():video.pause());
  skip.addEventListener('click',finish);
  video.addEventListener('playing',()=>{player.dataset.playing='true';play.textContent=label('إيقاف مؤقت','Pause');state.textContent=label('تكوين المبنى','Building sequence');});
  video.addEventListener('pause',()=>{play.textContent=label('تشغيل المشهد','Play scene');});
  video.addEventListener('ended',finish);
  video.addEventListener('error',()=>{finish();state.textContent=label('الصورة الثابتة متاحة؛ تعذر تحميل الفيديو','Still image available; video could not load');});
  reduced.addEventListener('change',()=>{if(reduced.matches)finish();});
  try{if(!sessionStorage.getItem('kfata-construction-preview-v1')&&!reduced.matches){sessionStorage.setItem('kfata-construction-preview-v1','1');start();}}catch(_){/* Static poster and manual play stay available. */}
})();
