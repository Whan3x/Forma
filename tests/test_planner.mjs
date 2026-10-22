import assert from 'node:assert/strict';
import planner from '../public/planner.js';

const { nextPriority, orderExercises, priorityLabel, priorityOptions } = planner;

const exercise = (id, name, plan) => ({ id, name, plan });

assert.deepEqual(priorityOptions('Upper'), ['back', 'chest', 'shoulders']);
assert.deepEqual(priorityOptions('Lower'), ['quads', 'posterior']);
assert.equal(priorityLabel('shoulders'), 'Ramena první');
assert.equal(nextPriority('Upper', []), 'back');
assert.equal(nextPriority('Upper', [{ name: 'Upper', priority: 'back', started: 10 }]), 'chest');
assert.equal(nextPriority('Upper', [
  { name: 'Upper', priority: 'back', started: 10 },
  { name: 'Upper', priority: 'chest', started: 20 },
]), 'shoulders');
assert.equal(nextPriority('Lower', [{ name: 'Lower', priority: 'posterior', started: 10 }]), 'quads');

const upper = [
  exercise('curl', 'Preacher curls', 'Upper'),
  exercise('row', 'Seated row', 'Upper'),
  exercise('bench', 'Bench press · osa', 'Upper'),
  exercise('lateral', 'Lateral raises', 'Upper'),
  exercise('pulldown', 'Lat pulldown', 'Upper'),
  exercise('triceps', 'Triceps extension', 'Upper'),
  exercise('press', 'Shoulder press', 'Upper'),
];
assert.deepEqual(orderExercises(upper, 'Upper', 'back').map(x => x.id), [
  'row', 'pulldown', 'bench', 'press', 'lateral', 'curl', 'triceps',
]);
assert.deepEqual(orderExercises(upper, 'Upper', 'chest').map(x => x.id).slice(0, 2), ['bench', 'row']);
assert.deepEqual(orderExercises(upper, 'Upper', 'original').map(x => x.id), upper.map(x => x.id));

const lower = [
  exercise('calves', 'Calf raises', 'Lower'),
  exercise('curl', 'Leg curl · hamstringy', 'Lower'),
  exercise('press', 'Leg press', 'Lower'),
  exercise('extension', 'Leg extension · kvadricepsy', 'Lower'),
];
assert.deepEqual(orderExercises(lower, 'Lower', 'posterior').map(x => x.id), [
  'curl', 'press', 'extension', 'calves',
]);

console.log('planner tests passed');
