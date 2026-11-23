'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../sudu/v4-115-multisubject-review-demo.html'), 'utf8');
const start = html.indexOf('function guideEntries(q){');
const end = html.indexOf('\nfunction renderGuide(){', start);
assert.ok(start > 0 && end > start, 'extract actual production guideEntries');
const source = html.slice(start, end);
const mockConfig = {examCalculations: {}};
const context = {
  window: {DEMO_LEARNING_CONFIG: mockConfig},
  subjectEntries: (q) => q.extraRows || [],
  sourceText: () => '',
  hasStudyValue: (v) => v != null && String(v).trim() && !String(v).startsWith('N/A'),
  normalizeStudyText: (v) => String(v ?? '').normalize('NFKC').toLowerCase().replace(/\s+/g, ''),
};
vm.createContext(context);
vm.runInContext(source, context);
const names = (q) => Array.from(context.guideEntries(q), ([name]) => name);
const chinese = {subject:'國文',id:9,concept:'閱讀銜接',formula:'排序檢查：指示詞＋因果＋時間順序。',memory:'',extraRows:[]};
assert.ok(names(chinese).includes('解題線索'), '國文 Q9 reasoning is preserved');
assert.ok(!names(chinese).includes('公式／分錄'), '國文 Q9 has no calculation card');
assert.ok(!names(chinese).includes('考題計算式'), 'no exam steps for non calculation');
assert.equal(context.guideEntries(chinese).find(x=>x[0]==='解題線索')[1],chinese.formula);
const math={subject:'數學 B',id:9,formula:'m1*m2=-1',concept:'垂直',memory:'',extraRows:[]};
mockConfig.examCalculations['數學 B|9']={hasExamCalculation:true,lines:['用途：求斜率','代入 m1=-2','m2=1/2','驗算 (-2)*(1/2)=-1']};
math.extraRows=[['考題計算式',mockConfig.examCalculations['數學 B|9'].lines.join('\n')]];
assert.ok(names(math).includes('公式／分錄'), 'real math formula remains');
assert.ok(names(math).includes('考題計算式'), 'real math steps remain');
for (const subject of ['會計學','經濟學']) {
 const q={subject,id:22,formula:'計算所需之公式',memory:'',extraRows:[['考題計算式','公式用途\n代入\n答案\n驗算']]};
 mockConfig.examCalculations[subject+'|22']={hasExamCalculation:true,lines:['公式用途','代入','答案','驗算']};
 assert.ok(names(q).includes('公式／分錄') && names(q).includes('考題計算式'), subject+' real calculation preserved');
}
mockConfig.examCalculations['國文|9']={hasExamCalculation:false,lines:['stale steps']};
assert.ok(!names(chinese).includes('公式／分錄'), 'false flag cannot show calculation label');
mockConfig.examCalculations['國文|9']={hasExamCalculation:true,lines:[]};
assert.ok(!names(chinese).includes('公式／分錄'), 'empty steps cannot show calculation label');
console.log('PASS 7 V4 noncalculation/real calculation regression assertions');
