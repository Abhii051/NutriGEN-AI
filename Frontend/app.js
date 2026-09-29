/* ================================================================
   NutriGEN-AI — frontend logic
   This file does NOT calculate BMI, calories or macros.
   All of that happens on your backend. This file only:
     1. reads the form
     2. sends it to your API (once you connect fetchStats / askBackend)
     3. displays whatever comes back
   ================================================================ */


/* ---------------------------------------------------------------
   Small helper: shorthand for document.getElementById
   --------------------------------------------------------------- */
function $(id) {
  return document.getElementById(id);
}

/* ---------------------------------------------------------------
   S = shared app state (kept in one place so it's easy to find)
   --------------------------------------------------------------- */
const S = {
  act: 1.375,      // current activity multiplier, set by the activity tiles
  goal: 'maintain', // current goal, set by the goal switch
  done: false,      // true once results have loaded successfully
  target: null,     // last calorie target received from the backend
  profile: null     // last profile object sent to the backend
};

const sliderPairs = [
  ['age', 'ageV'],
  ['wt', 'wtV'],
  ['ht', 'htV']
];
sliderPairs.forEach(([sliderId, labelId]) => {
  $(sliderId).addEventListener('input', (e) => {
    $(labelId).textContent = e.target.value;
  });
});

// Name field: update the "Hi <name>" greeting live
$('name').addEventListener('input', (e) => {
  const typedName = e.target.value.trim();
  $('greet').textContent = typedName ? `Hi ${typedName}, let's get started` : 'Tell us about you';
});

// Activity tiles: clicking one selects it and stores its multiplier in S.act
$('act').addEventListener('click', (e) => {
  const clickedTile = e.target.closest('.tile');
  if (!clickedTile) return;

  document.querySelectorAll('#act .tile').forEach((tile) => {
    tile.setAttribute('aria-pressed', tile === clickedTile);
  });
  S.act = +clickedTile.dataset.v;
});

// Goal switch: Lose / Maintain / Gain, with a sliding highlight
const GOAL_ORDER = ['lose', 'maintain', 'gain'];

function setGoal(value) {
  S.goal = value;

  document.querySelectorAll('#goal button').forEach((button) => {
    button.setAttribute('aria-pressed', button.dataset.v === value);
  });

  const position = GOAL_ORDER.indexOf(value);
  document.querySelector('#goal .thumb').style.transform = `translateX(${position * 100}%)`;
}

$('goal').addEventListener('click', (e) => {
  const clickedButton = e.target.closest('button');
  if (clickedButton) setGoal(clickedButton.dataset.v);
});

setGoal('maintain'); // default selection on page load


/* ================================================================
   SECTION 2 — BMI GAUGE (drawing only, no math)
   Draws the four coloured arcs once. The needle rotation is set
   later, in renderStats(), based on the BMI value from the backend.
   ================================================================ */

// Each entry: [rangeStart, rangeEnd, CSS-variable-name-for-color]
const GAUGE_SEGMENTS = [
  [10, 18.5, '--under'],
  [18.5, 25, '--normal'],
  [25, 30, '--over'],
  [30, 40, '--obese']
];

// Convert a BMI value (10–40) into an angle for drawing the arc
function bmiToAngle(bmiValue) {
  return 180 - ((bmiValue - 10) / 30) * 180;
}

// Convert (radius, angle) into an (x, y) point on the gauge circle
function angleToPoint(radius, angleDegrees) {
  const angleRadians = (angleDegrees * Math.PI) / 180;
  return [
    150 + radius * Math.cos(angleRadians),
    150 - radius * Math.sin(angleRadians)
  ];
}

// Draw the four background arcs into the <g id="arcs"> element
$('arcs').innerHTML = GAUGE_SEGMENTS.map(([rangeStart, rangeEnd, colorVar]) => {
  const [x1, y1] = angleToPoint(120, bmiToAngle(rangeStart) - 0.6);
  const [x2, y2] = angleToPoint(120, bmiToAngle(rangeEnd) + 0.6);
  return `<path d="M${x1} ${y1}A120 120 0 0 1 ${x2} ${y2}" fill="none" stroke="var(${colorVar})" stroke-width="28"/>`;
}).join('');


/* ================================================================
   SECTION 3 — TALKING TO YOUR BACKEND (stats)
   This is the ONLY place BMI/calorie/macro numbers come from.
   ================================================================ */

// Maps a BMI category name to the matching gauge color variable
const CATEGORY_TO_COLOR = {
  Underweight: '--under',
  Healthy: '--normal',
  Overweight: '--over',
  Obese: '--obese'
};

/**
 * fetchStats(profile)
 * ---------------------------------------------------------------
 * TODO: connect this to your REST API.
 *
 * INPUT  (the "profile" object passed in):
 *   { name, age, weight, height, activity, goal, diet, allergies, otherAllergies }
 *
 * EXPECTED OUTPUT (what your API should return as JSON):
 *   {
 *     bmi: 22.5,
 *     category: "Healthy",   // one of: "Underweight" | "Healthy" | "Overweight" | "Obese"
 *     tdee: 2200,
 *     target: 1900,
 *     range_low: 55,
 *     range_high: 75,
 *     protein_g: 140,
 *     carbs_g: 180,
 *     fat_g: 55
 *   }
 *
 * Example of what to put here once you're ready:
 *
 *   const response = await fetch('https://your-api/api/stats', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify(profile)
 *   });
 *   if (!response.ok) throw new Error('stats API returned ' + response.status);
 *   return response.json();
 */
async function fetchStats(profile) {
  throw new Error('fetchStats() is not connected to a backend yet');
}

/**
 * renderStats(result)
 * ---------------------------------------------------------------
 * Takes the object returned by fetchStats() and paints it onto
 * the gauge, the calorie stats, and the macro bars.
 * You should NOT need to change this function — only fetchStats().
 */
function renderStats(result) {
  // BMI number + category tag
  $('bmiV').textContent = (+result.bmi).toFixed(1);
  $('bmiT').textContent = result.category;
  $('bmiT').style.background = `var(${CATEGORY_TO_COLOR[result.category] || '--normal'})`;

  // Needle rotation
  const clampedBmi = Math.min(Math.max(+result.bmi, 10), 40);
  const needleAngle = -90 + ((clampedBmi - 10) / 30) * 180;
  $('needle').style.transform = `rotate(${needleAngle}deg)`;

  // Calorie stats
  $('tdee').textContent = result.tdee + ' kcal';
  $('target').textContent = result.target + ' kcal';
  $('range').textContent = result.range_low + ' to ' + result.range_high + ' kg';

  // Macro bars — each bar's fill width is that macro's share of total calories
  const totalCalories = result.target;
  const macros = [
    ['mp', result.protein_g, 4], // protein: 4 kcal per gram
    ['mc', result.carbs_g, 4],   // carbs:   4 kcal per gram
    ['mf', result.fat_g, 9]      // fat:     9 kcal per gram
  ];
  macros.forEach(([elementId, grams, kcalPerGram]) => {
    const kcalFromThisMacro = grams * kcalPerGram;
    const widthPercent = Math.round((kcalFromThisMacro / totalCalories) * 100);
    $(elementId).style.width = widthPercent + '%';
    $(elementId + 'v').textContent = grams + ' g';
  });

  S.target = result.target;
}
async function show(scrollToResults) {
  const formData = readForm();

  S.profile = {
    name: formData.name,
    age: formData.age,
    weight: formData.wt,
    height: formData.ht,
    activity: S.act,
    goal: S.goal,
    diet: formData.diet,
    allergies: formData.allergies,
    otherAllergies: formData.other
  };

  $('results').classList.add('ready');
  $('bmiV').textContent = '...';
  $('bmiT').textContent = 'Calculating';
  $('tdee').textContent = '...';
  $('target').textContent = '...';
  $('range').textContent = '...';

  if (scrollToResults) {
    requestAnimationFrame(() => $('results').scrollIntoView({ behavior: 'smooth' }));
  }

  try {
    const result = await fetchStats(S.profile);
    renderStats(result);
    S.done = true;
  } catch (error) {
    $('bmiT').textContent = 'Could not reach backend';
    $('bmiT').style.background = 'var(--obese)';
    console.error(error);
  }
}

$('go').addEventListener('click', () => show(true));


/* ================================================================
   SECTION 4 — TALKING TO YOUR BACKEND (Ask-AI box)
   ================================================================ */

/**
 * askBackend(prompt, profile)
 * ---------------------------------------------------------------
 * TODO: connect this to your REST API / LLM.
 *
 * INPUT:
 *   prompt  — the text the user typed
 *   profile — the same profile object described above
 *
 * EXPECTED OUTPUT (what your API should return as JSON):
 *   {
 *     summary: "Three meal plans for about 1900 kcal a day.",
 *     plans: [
 *       {
 *         name: "Plan A: Balanced",
 *         kcal: 1900,
 *         meals: [
 *           { slot: "Breakfast", item: "Vegetable poha", kcal: 475 },
 *           { slot: "Lunch",     item: "Dal, rice, sabzi", kcal: 665 },
 *           ...
 *         ]
 *       },
 *       ...
 *     ],
 *     note: "optional extra text shown under the plans"
 *   }
 *
 * Example of what to put here once you're ready:
 *
 *   const response = await fetch('https://your-api/api/plan', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify({ prompt, profile })
 *   });
 *   if (!response.ok) throw new Error('plan API returned ' + response.status);
 *   return response.json();
 */
async function askBackend(prompt, profile) {
  throw new Error('askBackend() is not connected to a backend yet');
}

/**
 * ask(text)
 * ---------------------------------------------------------------
 * Called when the user presses "Generate". Shows a "thinking"
 * message, calls askBackend(), then renders the meal-plan cards.
 */
async function ask(text) {
  const outputBox = $('out');
  outputBox.innerHTML = '<div class="think">NutriGen AI is planning</div>';

  try {
    const result = await askBackend(text, S.profile);

    const planCards = result.plans.map((plan) => {
      const mealRows = plan.meals.map((meal) =>
        `<div class="meal"><b>${meal.slot}<span>${meal.kcal} kcal</span></b>${meal.item}</div>`
      ).join('');

      return `<div class="plan"><h3>${plan.name}</h3><div class="tot">${plan.kcal} kcal</div>${mealRows}</div>`;
    }).join('');

    const noteHtml = result.note ? `<p class="note">${result.note}</p>` : '';

    outputBox.innerHTML = `<p><b>${result.summary}</b></p><div class="plans">${planCards}</div>${noteHtml}`;

  } catch (error) {
    outputBox.innerHTML = '<p class="note">Could not reach the backend. Make sure your API is running and connected.</p>';
    console.error(error);
  }
}

$('send').addEventListener('click', () => {
  const promptText = $('q').value.trim();
  if (!promptText) {
    $('q').focus();
    return;
  }
  ask(promptText);
});

// Clicking a suggestion chip fills the textarea with that suggestion
$('chips').addEventListener('click', (e) => {
  if (e.target.classList.contains('chip')) {
    $('q').value = e.target.textContent;
    $('q').focus();
  }
});


/* ================================================================
   SECTION 5 — SAVED PROFILES (browser storage only)
   Saves the FORM INPUTS only — never any calculated results.
   This uses localStorage, so profiles are only available on this
   one browser/device. Swap this out for real accounts later if
   you want profiles to follow the user across devices.
   ================================================================ */

const STORAGE_KEY = 'nutrigen.profiles.v1';
let profileDB = { list: [], last: null }; // { list: [profileObject, ...], last: idOfLastUsed }
let currentProfileId = null;

// Load any previously saved profiles from this browser
try {
  profileDB = JSON.parse(localStorage.getItem(STORAGE_KEY)) || profileDB;
} catch (error) {
  // localStorage unavailable or corrupted — just start with an empty list
}

function saveProfileDB() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profileDB));
    return true;
  } catch (error) {
    return false;
  }
}

function makeId() {
  return Math.random().toString(36).slice(2, 9);
}

// Escapes text before inserting it into innerHTML, to avoid HTML injection
function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);
}

const allergyChips = [...document.querySelectorAll('#alg .chip')];

function setMessage(text) {
  $('msg').textContent = text;
}

// Clicking an allergy chip toggles its selected state
allergyChips.forEach((chip) => {
  chip.addEventListener('click', () => {
    const isSelected = chip.getAttribute('aria-pressed') === 'true';
    chip.setAttribute('aria-pressed', !isSelected);
  });
});

/**
 * readForm()
 * Reads every field on the form into one plain object.
 */
function readForm() {
  return {
    id: currentProfileId || makeId(),
    name: $('name').value.trim(),
    age: +$('age').value,
    wt: +$('wt').value,
    ht: +$('ht').value,
    act: S.act,
    goal: S.goal,
    diet: $('diet').value,
    allergies: allergyChips
      .filter((chip) => chip.getAttribute('aria-pressed') === 'true')
      .map((chip) => chip.textContent),
    other: $('otherAl').value.trim()
  };
}

/**
 * fillForm(profile)
 * Puts a saved profile object's values back into the form fields.
 */
function fillForm(profile) {
  currentProfileId = profile.id;

  $('name').value = profile.name || '';
  $('name').dispatchEvent(new Event('input')); // triggers the greeting update

  sliderPairs.forEach(([sliderId, labelId]) => {
    $(sliderId).value = profile[sliderId]; // sliderId is one of "age", "wt", "ht" — same keys used in readForm()
    $(labelId).textContent = $(sliderId).value;
  });

  S.act = profile.act;
  document.querySelectorAll('#act .tile').forEach((tile) => {
    tile.setAttribute('aria-pressed', +tile.dataset.v === profile.act);
  });

  setGoal(profile.goal);
  $('diet').value = profile.diet || '';

  allergyChips.forEach((chip) => {
    chip.setAttribute('aria-pressed', (profile.allergies || []).includes(chip.textContent));
  });
  $('otherAl').value = profile.other || '';
}

/**
 * blankForm()
 * Resets the form back to its default empty state, for "+ New profile".
 */
function blankForm() {
  currentProfileId = null;
  fillForm({
    id: null, name: '', age: 20, wt: 65, ht: 170,
    act: 1.375, goal: 'maintain', diet: '', allergies: [], other: ''
  });
  currentProfileId = null;
}

/**
 * renderSaved()
 * Redraws the row of saved-profile chips above the form.
 */
function renderSaved() {
  const profileChips = profileDB.list.map((profile) =>
    `<button type="button" class="chip pf" data-id="${escapeHtml(profile.id)}" aria-pressed="${profile.id === currentProfileId}">${escapeHtml(profile.name)}</button>`
  ).join('');

  const emptyHint = profileDB.list.length
    ? ''
    : '<span class="note">None yet. Fill in the form and press Save profile.</span>';

  $('saved').innerHTML = '<b>Saved profiles</b>' + profileChips +
    '<button type="button" class="chip" id="newP">+ New profile</button>' + emptyHint;

  $('del').style.display = (currentProfileId && profileDB.list.some((p) => p.id === currentProfileId)) ? '' : 'none';
}

// Clicking inside the saved-profiles bar: load a profile, or start a new one
$('saved').addEventListener('click', (e) => {
  const clickedButton = e.target.closest('button');
  if (!clickedButton) return;
  setMessage('');

  if (clickedButton.id === 'newP') {
    blankForm();
    profileDB.last = null;
    saveProfileDB();
    renderSaved();
    return;
  }

  const profile = profileDB.list.find((p) => p.id === clickedButton.dataset.id);
  if (!profile) return;

  fillForm(profile);
  profileDB.last = profile.id;
  saveProfileDB();
  show(false); // reload results for this profile without scrolling
  renderSaved();
});

// Save button: add a new profile, or update the currently loaded one
$('save').addEventListener('click', () => {
  const profile = readForm();

  if (!profile.name) {
    $('name').focus();
    setMessage('Add your name first, so this profile has a label.');
    return;
  }

  const existingIndex = profileDB.list.findIndex((p) => p.id === profile.id);
  if (existingIndex > -1) {
    profileDB.list[existingIndex] = profile;
  } else {
    profileDB.list.push(profile);
  }

  currentProfileId = profile.id;
  profileDB.last = profile.id;

  setMessage(saveProfileDB() ? 'Saved on this device.' : 'Could not save. Your browser may be blocking storage.');
  renderSaved();
});

// Delete button: remove the currently loaded profile
$('del').addEventListener('click', () => {
  profileDB.list = profileDB.list.filter((p) => p.id !== currentProfileId);
  profileDB.last = null;
  currentProfileId = null;
  saveProfileDB();
  setMessage('Profile deleted.');
  renderSaved();
});

// On page load: reopen the last-used profile, if there is one
{
  const lastUsedProfile = profileDB.list.find((p) => p.id === profileDB.last);
  if (lastUsedProfile) {
    fillForm(lastUsedProfile);
  }
  renderSaved();
}

const navLinks = [...document.querySelectorAll('nav ul a')];

const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      navLinks.forEach((link) => {
        link.classList.toggle('on', link.getAttribute('href') === '#' + entry.target.id);
      });
    }
  });
}, { rootMargin: '-45% 0px -50% 0px' });

document.querySelectorAll('section').forEach((section) => sectionObserver.observe(section));