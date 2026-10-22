import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const publicDir = new URL('../public/', import.meta.url);
const planner = fs.readFileSync(new URL('planner.js', publicDir), 'utf8');
const app = fs.readFileSync(new URL('app.js', publicDir), 'utf8');
const source = app.slice(0, app.lastIndexOf('(async()=>{'));
const storage = new Map();
const fakeNode = { innerHTML: '', textContent: '', classList: { add() {}, remove() {} }, querySelector() { return null; } };
const context = vm.createContext({
  console,
  Intl,
  Map,
  Set,
  Date,
  JSON,
  Math,
  Number,
  String,
  URL,
  crypto: globalThis.crypto,
  document: { querySelector() { return fakeNode; }, querySelectorAll() { return []; }, addEventListener() {} },
  window: { addEventListener() {} },
  navigator: {},
  location: { origin: 'https://forma.example', href: 'https://forma.example/', pathname: '/' },
  history: { replaceState() {} },
  localStorage: { getItem: key => storage.get(key) ?? null, setItem: (key, value) => storage.set(key, value), removeItem: key => storage.delete(key) },
  setInterval() { return 0; },
  setTimeout() { return 0; },
  clearTimeout() {},
  confirm() { return true; },
});

vm.runInContext(`${planner}\n${source}`, context, { filename: 'forma-frontend.js' });

const fixture = {
  user: { id: 'user-a', name: '<Karel>', email: 'karel@example.cz', code: 'invite', settings: { kcal: 2350, protein: 170, carbs: 260, fat: 70, water: 2500, weekly: 3, rest: 120, gamification: true, share: false } },
  workouts: [],
  exercises: [
    { id: 'row', name: 'Seated row', plan: 'Upper', weight: 92, extra: 0, reps: 8, mode: 'machine', note: '', step: 5 },
    { id: 'bench', name: 'Bench press', plan: 'Upper', weight: 105, extra: 0, reps: 8, mode: 'bar', note: '', step: 2.5 },
    { id: 'curl', name: 'Preacher curls', plan: 'Upper', weight: 56, extra: 0, reps: 8, mode: 'machine', note: '', step: 2 },
    { id: 'leg', name: 'Leg press', plan: 'Lower', weight: 210, extra: 0, reps: 10, mode: 'machine', note: '', step: 10 },
  ],
  sets: [], meals: [], water: [], metrics: [],
};

vm.runInContext(`state=${JSON.stringify(fixture)}; community={friends:[],feed:[],challenges:[]};`, context);
const result = vm.runInContext(`JSON.stringify({
  home: renderHome(),
  plans: renderPlans(),
  train: renderTrain(),
  profile: renderProfile()
})`, context);
const pages = JSON.parse(result);

assert.match(pages.plans, /Plán, který drží tvar/);
assert.match(pages.plans, /Záda první/);
assert.ok(pages.plans.indexOf('Seated row') < pages.plans.indexOf('Bench press'));
assert.match(pages.train, /exercise-order/);
assert.ok(!pages.home.includes('<Karel>'));
assert.ok(!pages.profile.includes('<Karel>'));
console.log('frontend render tests passed');
