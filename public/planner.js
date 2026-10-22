(function attachPlanner(root, factory) {
  const planner = factory();
  if (typeof module === 'object' && module.exports) module.exports = planner;
  else root.FormaPlanner = planner;
}(typeof globalThis === 'undefined' ? this : globalThis, function createPlanner() {
  'use strict';

  const cycles = {
    upper: ['back', 'chest', 'shoulders'],
    lower: ['quads', 'posterior'],
  };

  const labels = {
    original: 'Vlastní pořadí',
    back: 'Záda první',
    chest: 'Hrudník první',
    shoulders: 'Ramena první',
    quads: 'Kvadricepsy první',
    posterior: 'Zadní řetězec první',
  };

  const normalize = value => String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();

  function priorityOptions(plan) {
    return [...(cycles[normalize(plan)] || [])];
  }

  function priorityLabel(priority) {
    return labels[priority] || labels.original;
  }

  function nextPriority(plan, workouts) {
    const options = priorityOptions(plan);
    if (!options.length) return 'original';
    const latest = [...(workouts || [])]
      .filter(workout => normalize(workout.name) === normalize(plan))
      .sort((a, b) => Number(b.started || 0) - Number(a.started || 0))[0];
    const index = latest ? options.indexOf(latest.priority) : -1;
    return options[(index + 1) % options.length];
  }

  function muscleGroup(exercise) {
    const name = normalize(exercise && exercise.name);
    if (/leg curl|hamstring|deadlift|hip hinge|glute|zakop/.test(name)) return 'posterior';
    if (/preacher|biceps|triceps|biceps curl/.test(name)) return 'arms';
    if (/lat |pulldown|row|pritah|z[áa]d|trap|shrug/.test(name)) return 'back';
    if (/bench|chest|pec|hrud|dips/.test(name)) return 'chest';
    if (/shoulder|lateral|rear delt|ramen/.test(name)) return 'shoulders';
    if (/leg press|leg extension|squat|drep|quad/.test(name)) return 'quads';
    if (/calf|l[ýy]tk/.test(name)) return 'calves';
    if (/abdominal|crunch|core|b[řr]ich/.test(name)) return 'core';
    return 'other';
  }

  function isCompound(exercise) {
    return /bench|chest press|shoulder press|leg press|squat|drep|deadlift|pulldown|row|dips|shyb/.test(normalize(exercise && exercise.name));
  }

  function orderExercises(exercises, plan, priority = 'original') {
    const selected = (exercises || []).filter(exercise => exercise.plan === plan);
    if (priority === 'original') return [...selected];
    return selected
      .map((exercise, index) => ({ exercise, index, group: muscleGroup(exercise) }))
      .sort((a, b) => {
        const rank = item => item.group === priority ? 0 : isCompound(item.exercise) ? 1 : ['arms', 'calves', 'core'].includes(item.group) ? 3 : 2;
        const focusCompound = item => item.group === priority && isCompound(item.exercise) ? 0 : 1;
        return rank(a) - rank(b) || focusCompound(a) - focusCompound(b) || a.index - b.index;
      })
      .map(item => item.exercise);
  }

  function orderedForWorkout(exercises, workout) {
    if (!workout) return [];
    const byId = new Map((exercises || []).map(exercise => [exercise.id, exercise]));
    const saved = Array.isArray(workout.exercise_order) ? workout.exercise_order : [];
    const ordered = saved.map(id => byId.get(id)).filter(Boolean);
    const seen = new Set(ordered.map(exercise => exercise.id));
    return [...ordered, ...orderExercises(exercises, workout.name, workout.priority).filter(exercise => !seen.has(exercise.id))];
  }

  return { muscleGroup, nextPriority, orderExercises, orderedForWorkout, priorityLabel, priorityOptions };
}));
