const assert=require('node:assert/strict'),timer=require('../sudu/exam_countdown.js'),data=require('../sudu/data/exam-schedule.json');
assert.equal(timer.state(null).status,'unconfirmed');
assert.equal(timer.state(data,new Date('2027-04-23T15:59:00Z')).status,'date-countdown');
assert.equal(timer.state(data,new Date('2027-04-23T16:00:00Z')).status,'exam-days');
assert.equal(timer.state(data,new Date('2027-04-25T16:00:00Z')).status,'ended');
assert(!timer.state(data,new Date('2030-01-01')).label.includes('-'));
assert.equal(timer.state(data,new Date('2027-04-22T16:00:00Z')).label,'116 統測倒數 1 天');
console.log('PASS: verified calendar dates, Taipei midnight boundary, unknown and expired countdown states');
