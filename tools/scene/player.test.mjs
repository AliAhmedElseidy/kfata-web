import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../../config/static/js/construction-scene.js',import.meta.url),'utf8');
class Element {
  dataset={};hidden=false;textContent='';listeners={};
  addEventListener(type,fn){(this.listeners[type]??=[]).push(fn);}
  emit(type,event={}){for(const fn of this.listeners[type]??[])fn(event);}
}
function mount({reduced=false,mobile=false,blocked=false,masterOff=false,pending=false,lang='en'}={}){
  const preference=new Element();preference.matches=reduced;
  const root=new Element(),player=new Element(),controls=new Element(),toggle=new Element(),status=new Element(),video=new Element();
  video.dataset={desktopUrl:'/scene-media/1/',mobileUrl:'/scene-media/2/'};
  video.paused=true;video.currentTime=0;video.ended=false;video.playCalls=0;video.src=null;
  video.getAttribute=()=>video.src;
  video.removeAttribute=()=>{video.src=null;};
  video.load=()=>{};
  video.play=()=>{video.playCalls++;if(pending)return new Promise(()=>{});if(blocked)return Promise.reject(new Error('NotAllowedError'));video.paused=false;video.ended=false;video.emit('playing');return Promise.resolve();};
  video.pause=()=>{if(!video.paused){video.paused=true;video.emit('pause');}};
  root.querySelector=selector=>({'video':video,'.scene-player':player,'.scene-controls':controls,'[data-scene-toggle]':toggle,'[data-scene-state]':status})[selector];
  const window=new Element();window.matchMedia=query=>query.includes('reduced')?preference:{matches:mobile};
  Object.defineProperty(window,'sessionStorage',{get(){throw Error('Playback must not depend on session storage');}});
  const document={documentElement:{lang},body:{dataset:{motion:masterOff?'off':'on'}},querySelector:()=>root};
  vm.runInNewContext(source,{window,document});
  return {root,player,controls,toggle,status,video,preference,window};
}
test('every fresh document autoplays without consulting persistent/session storage',()=>{
  for(let i=0;i<2;i++){const v=mount();assert.equal(v.video.playCalls,1);assert.equal(v.root.dataset.state,'playing');assert.equal(v.video.muted,true);assert.equal(v.video.playsInline,true);}
});
test('small-screen load selects the lighter video once',()=>{const v=mount({mobile:true});assert.equal(v.video.src,'/scene-media/2/');});
test('autoplay rejection leaves the completed poster and a small replay control',async()=>{
  const v=mount({blocked:true});await new Promise(resolve=>setImmediate(resolve));
  assert.equal(v.root.dataset.state,'blocked');assert.equal(v.player.dataset.playing,'false');assert.equal(v.toggle.textContent,'Replay');assert.equal(v.controls.hidden,false);
});
test('reduced motion and master off never assign/download a video source',()=>{
  for(const option of [{reduced:true},{masterOff:true}]){const v=mount(option);assert.equal(v.video.src,null);assert.equal(v.video.playCalls,0);assert.equal(v.controls.hidden,true);}
});
test('end holds the final poster without looping; replay is explicit',()=>{
  const v=mount();v.video.ended=true;v.video.emit('ended');assert.equal(v.root.dataset.state,'finished');assert.equal(v.player.dataset.playing,'false');assert.equal(v.video.playCalls,1);
  v.toggle.emit('click');assert.equal(v.video.playCalls,2);assert.equal(v.video.currentTime,0);
});
test('pause/resume preserves position and changing reduced-motion stops playback',()=>{
  const v=mount();v.video.currentTime=3;v.toggle.emit('click');assert.equal(v.root.dataset.state,'paused');v.toggle.emit('click');assert.equal(v.video.currentTime,3);
  v.preference.matches=true;v.preference.emit('change');assert.equal(v.video.src,null);assert.equal(v.root.dataset.state,'reduced');assert.equal(v.video.paused,true);
});

test('pause during initial loading cancels the attempt and suppresses a late playing event',()=>{
  const v=mount({pending:true});assert.equal(v.root.dataset.state,'loading');v.toggle.emit('click');assert.equal(v.root.dataset.state,'paused');assert.equal(v.video.autoplay,false);
  v.video.emit('playing');assert.equal(v.root.dataset.state,'paused');assert.notEqual(v.player.dataset.playing,'true');
});
test('Arabic pause and resume labels remain correctly encoded',()=>{
  const v=mount({lang:'ar'});assert.equal(v.toggle.textContent,'إيقاف مؤقت');v.toggle.emit('click');assert.equal(v.toggle.textContent,'متابعة');v.toggle.emit('click');assert.equal(v.toggle.textContent,'إيقاف مؤقت');
});
