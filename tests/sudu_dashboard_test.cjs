const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const source=fs.readFileSync('sudu/dashboard.js','utf8');
const sample=[
{id:'p01',year:'自編',subject:'會計學',topic:'企業個體假設',question:'私人購物可以算商店支出嗎？',answer:1,options:['可以','不可以','不確定','都可以'],explanation:'老闆的錢和商店的錢分開。',steps:'分清個人與公司。',extension:'企業個體假設',source:'自編示範',verified:false},
{id:'p02',year:'自編',subject:'經濟學',topic:'需求',question:'價格變化',answer:2,options:['甲','乙','丙','丁'],explanation:'價格上升，需求量通常下降。',steps:'觀察價格變化',extension:'需求法則',source:'自編示範'},
{id:'official-1',year:114,subject:'會計學',topic:'概念',question:'未經核對不得計算',answer:0,options:['甲','乙','丙','丁'],explanation:'不顯示',verified:false}
];
const records=new Map();
const store={getItem:k=>records.has(k)?records.get(k):null,setItem:(k,v)=>records.set(k,String(v)),removeItem:k=>records.delete(k)};
const basicState=()=>({attempts:{},reviewAnswers:{},reviewHistory:{},extended:{}});
function start(state=basicState()){
  const ctx=vm.createContext({
    ALL:{practice:sample.slice(0,2),officialQuestions:sample.slice(2),archive:[{year:114},{year:113}],books:{}},
    state,crypto:crypto.webcrypto,localStorage:store,
    esc:x=>String(x??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'),
    keyHtml:x=>String(x??''),indexedDB:undefined,console,
    navigator:{},document:{getElementById:()=>null},
    window:{},Blob,Date,Number,Object,Array,JSON,Math,Set,Intl
  });
  vm.runInContext(source,ctx);
  vm.runInContext('suduBoot()',ctx);
  return ctx;
}
const one=start();
const code=vm.runInContext('suduDevice.id',one);
assert(/^SUDU-[A-F0-9]{24}$/.test(code),'secure unique code format');
const a=one.state.attempts;
a.p01=[{choice:0,correct:false,at:'2026-01-01'},{choice:1,correct:true,at:'2026-01-02'}];
one.state.reviewHistory.p01=[{choice:0,correct:false,at:'2026-01-03'}];
let stats=vm.runInContext("suduStats('自編','全部科目')",one);
assert.equal(stats.total,2);assert.equal(stats.done,1);assert.equal(stats.completed,50);assert.equal(stats.unfinished,50);
assert.equal(vm.runInContext("suduWrongCount(ALL.practice[0])",one),2);
let missing=vm.runInContext("suduStats('114','全部科目')",one);
assert.equal(missing.total,0);assert.equal(missing.completed,null);
let markup=vm.runInContext('dashboard()',one);
assert(markup.includes('完成比例')&&markup.includes('科目篩選')&&markup.includes('答錯 2 次'),'dashboard expected elements');
assert(markup.includes('尚未收錄核實題目'),'uncatalogued years must not get percentages');
assert(markup.includes('企業個體假設'),'concept must appear');
store.setItem('sudu_sites_state',JSON.stringify(one.state));
const two=start(JSON.parse(store.getItem('sudu_sites_state')));
assert.equal(vm.runInContext('suduDevice.id',two),code,'reopening browser must retain profile');
assert.equal(vm.runInContext("suduStats('自編','全部科目').completed",two),50,'reopening browser must retain answers');
assert.equal(vm.runInContext("suduWrongCount(ALL.practice[0])",two),2,'reopening browser must retain error history');
console.log('PASS: browser profile restores, annual progress accurate, missing official years show unavailable, wrong ranking consistent.');
