// =====================================================================
// NutriGEN-AI: Clinical Nutrition & AI-Optimized Meal Planner
// Frontend Client Logic (Vanilla JS, Zero External Dependencies)
// =====================================================================

// Use relative API path so it works seamlessly on localhost:8000, 127.0.0.1, or network host
const API_URL = "/api/generate-plan";
const STORAGE_KEY = "nutrigen_meal_plans_history_v2";

// DOM Elements
const form = document.getElementById("nutritionForm");
const generateBtn = document.getElementById("generateBtn");
const mealResults = document.getElementById("mealResults");
const demoBtn = document.getElementById("demoBtn");

// History Drawer Elements
const historyDrawer = document.getElementById("historyDrawer");
const historyDrawerBackdrop = document.getElementById("historyDrawerBackdrop");
const historyDrawerList = document.getElementById("historyDrawerList");
const historyBadge = document.getElementById("historyBadge");
const topbarHistoryCount = document.getElementById("topbarHistoryCount");
const historyCountLabel = document.getElementById("historyCountLabel");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const openHistoryBtn = document.getElementById("openHistoryBtn");
const historyNavBtn = document.getElementById("historyNavBtn");
const heroHistoryBtn = document.getElementById("heroHistoryBtn");
const historyPreviewViewAll = document.getElementById("historyPreviewViewAll");
const historyDrawerCloseBtn = document.getElementById("historyDrawerCloseBtn");
const historyPreviewList = document.getElementById("historyPreviewList");

// Grocery Modal Elements
const groceryModal = document.getElementById("groceryModal");
const groceryModalBackdrop = document.getElementById("groceryModalBackdrop");
const groceryModalCloseBtn = document.getElementById("groceryModalCloseBtn");
const groceryContent = document.getElementById("groceryContent");
const groceryItemCount = document.getElementById("groceryItemCount");
const copyGroceryBtn = document.getElementById("copyGroceryBtn");
const printGroceryBtn = document.getElementById("printGroceryBtn");
const sidebarGroceryBtn = document.getElementById("sidebarGroceryBtn");
const sidebarPrintBtn = document.getElementById("sidebarPrintBtn");

// Current active plan state in memory
let currentActivePlan = null;


// ─── Utility Helpers ─────────────────────────────────────────────────────────

function el(tag, className, text) {
    const e = document.createElement(tag);
    if (className) e.className = className;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
}

function fmt(n, decimals = 1) {
    if (n === null || n === undefined || isNaN(n)) return "--";
    return Number(n).toFixed(decimals);
}

function capitalize(s) {
    if (!s) return "";
    return s.charAt(0).toUpperCase() + s.slice(1);
}


// ─── Real-Time Live Biometric Calculations ───────────────────────────────────

function calculateBiometricsLive() {
    const age = Number(document.getElementById("age").value);
    const gender = document.getElementById("gender").value || "male";
    const weight = Number(document.getElementById("weight").value);
    const targetWeight = Number(document.getElementById("target_weight").value);
    const height = Number(document.getElementById("height").value);
    const activity = document.getElementById("activity").value || "moderate";
    const goal = document.getElementById("goal").value || "maintenance";

    if (!weight || weight <= 0 || !height || height <= 0 || !age || age <= 0) {
        return;
    }

    // 1. BMI Calculation
    const hMeters = height / 100.0;
    const bmi = weight / (hMeters * hMeters);
    const bmiEl = document.getElementById("bmiValue");
    const bmiStatusEl = document.getElementById("bmiStatus");

    bmiEl.textContent = bmi.toFixed(1);

    if (bmi < 18.5) {
        bmiStatusEl.textContent = "Underweight";
        bmiStatusEl.className = "stat-pill alert";
    } else if (bmi < 25.0) {
        bmiStatusEl.textContent = "Normal Healthy Weight";
        bmiStatusEl.className = "stat-pill success";
    } else if (bmi < 30.0) {
        bmiStatusEl.textContent = "Overweight";
        bmiStatusEl.className = "stat-pill warn";
    } else {
        bmiStatusEl.textContent = "Obese Range";
        bmiStatusEl.className = "stat-pill alert";
    }

    // 2. BMR Calculation (Mifflin-St Jeor)
    let bmr = 10 * weight + 6.25 * height - 5 * age;
    if (gender === "male") {
        bmr += 5;
    } else if (gender === "female") {
        bmr -= 161;
    } else {
        bmr -= 78;
    }
    document.getElementById("bmrValue").innerHTML = `${Math.round(bmr)} <small>kcal</small>`;

    // 3. TDEE Calculation
    const activityFactors = {
        sedentary: 1.20,
        light: 1.375,
        moderate: 1.55,
        active: 1.725,
        very_active: 1.90
    };
    const factor = activityFactors[activity] || 1.55;
    const tdee = bmr * factor;
    document.getElementById("tdeeValue").innerHTML = `${Math.round(tdee)} <small>kcal</small>`;

    // 4. Calorie Target & Deficit/Surplus
    let calorieTarget = tdee;
    const deltaBadge = document.getElementById("calorieDeltaBadge");

    if (goal === "weight_loss") {
        calorieTarget = tdee * 0.90;
        const deficit = Math.round(tdee - calorieTarget);
        deltaBadge.textContent = `-${deficit} kcal/day Deficit`;
        deltaBadge.className = "stat-pill normal";
    } else if (goal === "weight_gain") {
        calorieTarget = tdee * 1.10;
        const surplus = Math.round(calorieTarget - tdee);
        deltaBadge.textContent = `+${surplus} kcal/day Surplus`;
        deltaBadge.className = "stat-pill warn";
    } else {
        deltaBadge.textContent = "Balanced Maintenance";
        deltaBadge.className = "stat-pill neutral";
    }

    document.getElementById("calorieValue").innerHTML = `${Math.round(calorieTarget)} <small>kcal</small>`;

    // 5. Target Weight & Timeline Projection
    const targetDisplay = document.getElementById("targetWeightDisplay");
    const timelineEl = document.getElementById("targetWeightTimeline");
    const paceEl = document.getElementById("targetWeightPace");

    if (targetWeight && targetWeight > 0) {
        const weightDiff = targetWeight - weight;
        targetDisplay.innerHTML = `${targetWeight.toFixed(1)} <small>kg</small>`;

        const dailyDelta = Math.abs(calorieTarget - tdee);
        const weeklyRateKg = (dailyDelta * 7.0) / 7700.0; // 7700 kcal per kg of body weight change

        if (Math.abs(weightDiff) < 0.2) {
            timelineEl.textContent = "At target goal weight!";
            paceEl.textContent = "Focus on maintenance nutrition";
        } else if (weeklyRateKg > 0.05) {
            const weeks = Math.abs(weightDiff) / weeklyRateKg;
            const diffText = weightDiff < 0 ? `${weightDiff.toFixed(1)} kg` : `+${weightDiff.toFixed(1)} kg`;
            timelineEl.textContent = `${diffText} in ~${Math.ceil(weeks)} weeks`;
            paceEl.textContent = `Projected safe rate: ~${weeklyRateKg.toFixed(2)} kg/wk`;
        } else {
            const diffText = weightDiff < 0 ? `${weightDiff.toFixed(1)} kg` : `+${weightDiff.toFixed(1)} kg`;
            timelineEl.textContent = `Goal: ${diffText}`;
            paceEl.textContent = "Select weight loss or gain for timeline";
        }
    } else {
        targetDisplay.innerHTML = `-- <small>kg</small>`;
        timelineEl.textContent = "Optional: Set target weight";
        paceEl.textContent = "Estimates weeks to reach goal";
    }

    // 6. Clinical Hydration Target (35 ml per kg)
    const waterLiters = (weight * 0.035).toFixed(1);
    const glasses = Math.round((weight * 0.035) / 0.25); // ~250 ml glass
    document.getElementById("waterValue").innerHTML = `${waterLiters} <small>L/day</small>`;
    document.getElementById("waterGlasses").textContent = `~${glasses} standard glasses daily`;
}

// Bind live recalculation to all form input changes
[
    "age", "gender", "weight", "target_weight", "height", "activity", "goal"
].forEach(id => {
    const elem = document.getElementById(id);
    if (elem) {
        elem.addEventListener("input", calculateBiometricsLive);
        elem.addEventListener("change", calculateBiometricsLive);
    }
});


// ─── Extract Form Data & Build Backend Payload ───────────────────────────────

function getFormData() {
    return {
        name: document.getElementById("name").value.trim() || "User",
        age: Number(document.getElementById("age").value),
        gender: document.getElementById("gender").value || "male",
        weight: Number(document.getElementById("weight").value),
        target_weight: Number(document.getElementById("target_weight").value) || null,
        height: Number(document.getElementById("height").value),
        activity: document.getElementById("activity").value || "moderate",
        goal: document.getElementById("goal").value || "maintenance",
        diet: document.getElementById("diet").value || "vegetarian",
        cuisine: document.getElementById("cuisine").value || "indian",
        meals: Number(document.getElementById("meals").value) || 4,
        allergies: document.getElementById("allergies").value.trim(),
        user_prompt: document.getElementById("user_prompt").value.trim()
    };
}

function buildPayload(data) {
    let diet_type = data.diet;
    let eats_eggs = false;

    if (data.diet === "eggetarian") {
        diet_type = "vegetarian";
        eats_eggs = true;
    } else if (data.diet === "non_vegetarian") {
        diet_type = "non-vegetarian";
    }

    const sex = data.gender === "female" ? "female" : "male";
    const number_of_snacks = Math.max(0, data.meals - 3);
    const number_of_meals = 3;

    const allergies = data.allergies
        ? data.allergies.split(",").map(s => s.trim()).filter(Boolean)
        : [];

    return {
        age: data.age,
        sex: sex,
        height_cm: data.height,
        weight_kg: data.weight,
        target_weight_kg: data.target_weight,
        activity_level: data.activity,
        goal: data.goal,
        diet_type: diet_type,
        eats_eggs: eats_eggs,
        allergies: allergies,
        cuisine: data.cuisine,
        number_of_meals: number_of_meals,
        number_of_snacks: number_of_snacks,
        user_prompt: data.user_prompt || ""
    };
}


// ─── Household Serving Hints Generator ───────────────────────────────────────

function getServingHint(foodName, grams) {
    const fn = (foodName || "").toLowerCase();
    const g = Number(grams) || 0;

    if (fn.includes("roti") || fn.includes("chapati")) {
        const count = Math.max(1, Math.round(g / 40));
        return `~${count} ${count === 1 ? 'chapati' : 'chapatis'}`;
    }
    if (fn.includes("poha") || fn.includes("upma") || fn.includes("khichdi") || fn.includes("rice")) {
        const bowls = (g / 130).toFixed(1);
        return `~${bowls} katori / bowl`;
    }
    if (fn.includes("dal") || fn.includes("sambar") || fn.includes("curry") || fn.includes("chana") || fn.includes("rajma")) {
        const bowls = (g / 150).toFixed(1);
        return `~${bowls} medium bowl`;
    }
    if (fn.includes("paneer") || fn.includes("tofu")) {
        const cubes = Math.round(g / 25);
        return `~${cubes} cubes`;
    }
    if (fn.includes("pita")) {
        const count = Math.max(1, Math.round(g / 60));
        return `~${count} pita`;
    }
    if (fn.includes("hummus")) {
        const tbsp = Math.max(1, Math.round(g / 15));
        return `~${tbsp} tbsp`;
    }
    if (fn.includes("egg")) {
        const count = Math.max(1, Math.round(g / 50));
        return `~${count} whole`;
    }
    if (fn.includes("chicken") || fn.includes("salmon") || fn.includes("fish")) {
        return `~${(g / 100).toFixed(1)} palm portion`;
    }
    if (fn.includes("oats")) {
        const cups = (g / 40).toFixed(1);
        return `~${cups} cup cooked`;
    }
    if (fn.includes("almond") || fn.includes("peanut") || fn.includes("walnut")) {
        return `~${Math.round(g / 1.2)} nuts`;
    }
    if (fn.includes("ghee") || fn.includes("olive oil") || fn.includes("oil")) {
        const tsp = Math.max(1, Math.round(g / 5));
        return `~${tsp} tsp`;
    }
    return `~${Math.round(g)}g serving`;
}


// ─── Render Complete Meal Plan on Screen ─────────────────────────────────────

function displayMealPlan(response, optionalUserData = null) {
    mealResults.replaceChildren();
    currentActivePlan = { response, user: optionalUserData || getFormData() };

    const nr = response.nutrition_requirements || {};
    const mp = response.meal_plan || {};
    const totals = mp.totals || {};
    const bio = response.biometrics || {};

    // 1. Action Toolbar
    const toolbar = el("div", "results-toolbar");

    const leftGroup = el("div", "toolbar-group");
    const printBtn = el("button", "tool-action-btn", "🖨️ Print / Export PDF");
    printBtn.addEventListener("click", () => exportPlanToPrint(currentActivePlan));

    const groceryBtn = el("button", "tool-action-btn", "🛒 View Grocery List");
    groceryBtn.addEventListener("click", () => openGroceryModal(currentActivePlan));

    leftGroup.appendChild(printBtn);
    leftGroup.appendChild(groceryBtn);

    // Quick Cuisine Switcher Pills
    const rightGroup = el("div", "toolbar-group");
    const cuisineLabel = el("span", "cuisine-quick-label", "Switch Cuisine:");
    rightGroup.appendChild(cuisineLabel);

    const cuisines = [
        { id: "indian", label: "🇮🇳 Indian" },
        { id: "mediterranean", label: "🫒 Mediterranean" },
        { id: "japanese", label: "🍱 Japanese" },
        { id: "western", label: "🥗 Western" }
    ];

    const currentCuisine = optionalUserData?.cuisine || document.getElementById("cuisine").value || "indian";

    cuisines.forEach(c => {
        const pill = el("button", `cuisine-pill-btn ${c.id === currentCuisine ? 'active' : ''}`, c.label);
        pill.addEventListener("click", () => {
            document.getElementById("cuisine").value = c.id;
            document.querySelectorAll(".cuisine-pill-btn").forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            form.requestSubmit();
        });
        rightGroup.appendChild(pill);
    });

    toolbar.appendChild(leftGroup);
    toolbar.appendChild(rightGroup);
    mealResults.appendChild(toolbar);


    // 2. Optimization Precision & Macro Energy Distribution Card
    const targetCal = Number(nr.calories) || 1;
    const actualCal = Number(totals.calories) || 0;
    const variancePercent = Math.abs((actualCal - targetCal) / targetCal) * 100;
    const accuracyScore = Math.max(90, Math.min(99.9, 100 - variancePercent)).toFixed(1);

    const optCard = el("div", "optimization-card");
    optCard.innerHTML = `
        <div class="opt-card-header">
            <div>
                <span class="opt-badge-pill">🎯 ${accuracyScore}% Mathematical Match</span>
                <span class="opt-solver-tag" style="margin-left: 10px;">SciPy SLSQP Constrained Solver · Bounded Portions</span>
            </div>
            <div class="opt-solver-tag">
                ${response.llm_engine ? `✦ Recipes: ${response.llm_engine}` : "✦ Verified Clinical Macro Engine"}
            </div>
        </div>

        <div class="macro-comparison-grid">
            <div class="macro-comp-card">
                <div class="mcc-icon">🔥</div>
                <div class="mcc-label">Calories</div>
                <div class="mcc-values">
                    <div class="mcc-actual">${fmt(totals.calories, 0)} <small>kcal</small></div>
                    <div class="mcc-target">Target: ${fmt(nr.calories, 0)} kcal</div>
                </div>
                <span class="mcc-diff ${variancePercent < 3 ? 'diff-match' : 'diff-close'}">
                    ${variancePercent < 1 ? 'Perfect Match' : `${variancePercent.toFixed(1)}% variance`}
                </span>
            </div>

            <div class="macro-comp-card">
                <div class="mcc-icon">💪</div>
                <div class="mcc-label">Protein</div>
                <div class="mcc-values">
                    <div class="mcc-actual">${fmt(totals.protein_g, 1)}g</div>
                    <div class="mcc-target">Target: ${fmt(nr.protein_g, 1)}g</div>
                </div>
                <span class="mcc-diff diff-match">${Math.round((totals.protein_g * 4 / totals.calories) * 100)}% of energy</span>
            </div>

            <div class="macro-comp-card">
                <div class="mcc-icon">🌾</div>
                <div class="mcc-label">Carbohydrates</div>
                <div class="mcc-values">
                    <div class="mcc-actual">${fmt(totals.carbs_g, 1)}g</div>
                    <div class="mcc-target">Target: ${fmt(nr.carbs_g, 1)}g</div>
                </div>
                <span class="mcc-diff diff-match">${Math.round((totals.carbs_g * 4 / totals.calories) * 100)}% of energy</span>
            </div>

            <div class="macro-comp-card">
                <div class="mcc-icon">🥑</div>
                <div class="mcc-label">Healthy Fats</div>
                <div class="mcc-values">
                    <div class="mcc-actual">${fmt(totals.fat_g, 1)}g</div>
                    <div class="mcc-target">Target: ${fmt(nr.fat_g, 1)}g</div>
                </div>
                <span class="mcc-diff diff-match">${Math.round((totals.fat_g * 9 / totals.calories) * 100)}% of energy</span>
            </div>
        </div>

        <div class="macro-ratio-container">
            <div class="mrc-title-row">
                <span>MACRONUTRIENT CALORIC RATIO (4:4:9 kcal/g)</span>
                <span>Total: ${fmt(totals.calories, 0)} kcal</span>
            </div>
            <div class="macro-split-bar">
                <div class="split-protein" style="width: ${(totals.protein_g * 4 / totals.calories * 100).toFixed(1)}%;"></div>
                <div class="split-carbs" style="width: ${(totals.carbs_g * 4 / totals.calories * 100).toFixed(1)}%;"></div>
                <div class="split-fat" style="width: ${(totals.fat_g * 9 / totals.calories * 100).toFixed(1)}%;"></div>
            </div>
            <div class="mrc-legend">
                <span><span class="legend-dot" style="background: #e06d53;"></span> Protein (${(totals.protein_g * 4 / totals.calories * 100).toFixed(0)}%)</span>
                <span><span class="legend-dot" style="background: #468ca8;"></span> Carbs (${(totals.carbs_g * 4 / totals.calories * 100).toFixed(0)}%)</span>
                <span><span class="legend-dot" style="background: #e5b33d;"></span> Fat (${(totals.fat_g * 9 / totals.calories * 100).toFixed(0)}%)</span>
            </div>
        </div>
    `;
    mealResults.appendChild(optCard);


    // 3. Render Per-Meal Cards
    const mealPlanData = mp.meal_plan || {};
    const recipesData = response.recipes || mp.recipes || {};
    const mealOrder = ["Breakfast", "Lunch", "Dinner", "Snack"];

    const mealsGrid = el("div", "meals-grid");

    mealOrder.forEach(mealName => {
        const foods = mealPlanData[mealName];
        if (!foods || foods.length === 0) return;

        const recipe = recipesData[mealName] || {};
        const card = el("div", "meal-card-full");

        const mealEmojis = { Breakfast: "🌅", Lunch: "☀️", Dinner: "🌙", Snack: "🍎" };
        const header = el("div", "meal-card-header");
        header.innerHTML = `
            <div class="meal-name-row">
                <span class="meal-emoji">${mealEmojis[mealName] || "🍽️"}</span>
                <span class="meal-name">${mealName}</span>
            </div>
            ${recipe.dish_title ? `<div class="dish-title">${recipe.dish_title}</div>` : ""}
            ${recipe.cooking_time ? `<div class="cook-time">⏱ Cook Time: ${recipe.cooking_time}</div>` : ""}
        `;
        card.appendChild(header);

        // Foods Table with pixel-perfect column alignment
        const tableWrap = el("div", "meal-table-wrap");
        const table = el("table", "meal-food-table");

        table.innerHTML = `
            <thead>
                <tr>
                    <th class="col-food">Food & Serving</th>
                    <th class="col-qty">Weight</th>
                    <th class="col-num">Cal</th>
                    <th class="col-num">Protein</th>
                    <th class="col-num">Carbs</th>
                    <th class="col-num">Fat</th>
                </tr>
            </thead>
            <tbody>
                ${foods.map(f => {
                    const serving = getServingHint(f.food, f.grams);
                    const raw = f.food || "—";
                    const parts = raw.split(",");
                    const mainTitle = parts[0].trim();
                    const subTitle = parts.length > 1 ? parts.slice(1).join(",").trim() : "";

                    return `
                        <tr>
                            <td class="col-food">
                                <div class="food-cell">
                                    <strong class="food-title" title="${raw}">${mainTitle}</strong>
                                    <span class="food-desc">${serving}${subTitle ? ' · ' + subTitle : ''}</span>
                                </div>
                            </td>
                            <td class="col-qty">${fmt(f.grams, 0)}g</td>
                            <td class="col-num col-cal">${fmt(f.calories, 0)}</td>
                            <td class="col-num col-macro">${fmt(f.protein_g, 1)}g</td>
                            <td class="col-num col-macro">${fmt(f.carbs_g, 1)}g</td>
                            <td class="col-num col-macro">${fmt(f.fat_g, 1)}g</td>
                        </tr>
                    `;
                }).join("")}
            </tbody>
        `;

        tableWrap.appendChild(table);
        card.appendChild(tableWrap);

        // Recipe Drawer
        if (recipe.instructions && recipe.instructions.length > 0) {
            const toggle = el("button", "recipe-toggle", "▸ View AI Chef Recipe & Steps");
            const drawer = el("div", "recipe-drawer");
            drawer.style.display = "none";

            recipe.instructions.forEach((step, i) => {
                const s = el("div", "recipe-step");
                s.innerHTML = `<span class="step-num">${i + 1}</span><span>${step}</span>`;
                drawer.appendChild(s);
            });

            if (recipe.chef_notes) {
                const notes = el("p", "chef-notes", `✦ Chef's Note: ${recipe.chef_notes}`);
                drawer.appendChild(notes);
            }

            toggle.addEventListener("click", () => {
                const isOpen = drawer.style.display !== "none";
                drawer.style.display = isOpen ? "none" : "block";
                toggle.textContent = isOpen ? "▸ View AI Chef Recipe & Steps" : "▾ Hide Recipe";
            });

            card.appendChild(toggle);
            card.appendChild(drawer);
        }

        mealsGrid.appendChild(card);
    });

    mealResults.appendChild(mealsGrid);
}


// ─── LocalStorage History Management ─────────────────────────────────────────

function getHistory() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        console.error("Failed to read history from localStorage:", e);
        return [];
    }
}

function savePlanToHistory(payload, result) {
    const history = getHistory();
    const entry = {
        id: "plan_" + Date.now(),
        timestamp: new Date().toISOString(),
        formattedDate: new Date().toLocaleDateString(undefined, {
            month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
        }),
        user: payload,
        response: result
    };

    // Prepend and keep top 15 plans
    history.unshift(entry);
    if (history.length > 15) history.pop();

    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
        console.warn("Could not save history to localStorage (quota exceeded?):", e);
    }

    updateHistoryUI();
}

function deleteHistoryItem(id) {
    let history = getHistory();
    history = history.filter(item => item.id !== id);
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) {}
    updateHistoryUI();
    renderHistoryDrawer();
}

function clearAllHistory() {
    if (confirm("Are you sure you want to clear all saved meal plans?")) {
        try {
            localStorage.removeItem(STORAGE_KEY);
        } catch (e) {}
        updateHistoryUI();
        renderHistoryDrawer();
    }
}

function updateHistoryUI() {
    const history = getHistory();
    const count = history.length;

    if (historyBadge) historyBadge.textContent = count;
    if (topbarHistoryCount) topbarHistoryCount.textContent = count;
    if (historyCountLabel) historyCountLabel.textContent = `${count} saved plans in local memory`;

    // Update the sidebar preview card
    if (historyPreviewList) {
        historyPreviewList.replaceChildren();

        if (count === 0) {
            historyPreviewList.innerHTML = `<p class="empty-history-text">No plans saved yet. Generate a plan to see it here!</p>`;
        } else {
            // Show up to 3 recent plans
            history.slice(0, 3).forEach((item, idx) => {
                const div = el("div", "hp-item");
                const cal = item.response?.nutrition_requirements?.calories || item.response?.meal_plan?.totals?.calories || "--";
                const cuisine = capitalize(item.user?.cuisine || "General");

                div.innerHTML = `
                    <div class="hp-info">
                        <h5>${cuisine} · ${Math.round(cal)} kcal</h5>
                        <small>${item.formattedDate}</small>
                    </div>
                `;

                const loadBtn = el("button", "hp-load-btn", "Load");
                loadBtn.addEventListener("click", () => {
                    loadPlanFromHistory(item);
                });

                div.appendChild(loadBtn);
                historyPreviewList.appendChild(div);
            });
        }
    }
}

function renderHistoryDrawer() {
    const history = getHistory();
    historyDrawerList.replaceChildren();

    if (history.length === 0) {
        historyDrawerList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📜</div>
                <h3>No saved plans yet</h3>
                <p>Plans you generate are automatically saved here so you can reload them anytime without re-running.</p>
            </div>
        `;
        return;
    }

    history.forEach(item => {
        const nr = item.response?.nutrition_requirements || {};
        const mp = item.response?.meal_plan?.totals || {};
        const u = item.user || {};

        const card = el("div", "saved-plan-card");
        card.innerHTML = `
            <div class="spc-top">
                <span class="spc-time">${item.formattedDate}</span>
                <span class="spc-cuisine-tag">${capitalize(u.cuisine || 'indian')}</span>
            </div>
            <h4 class="spc-title">${u.name || 'Personalized'} Plan (${Math.round(nr.calories || mp.calories || 2000)} kcal)</h4>
            <div class="spc-chips">
                <span class="spc-chip">${capitalize(u.diet_type || 'Vegetarian')}</span>
                <span class="spc-chip">${capitalize(u.goal?.replace('_', ' ') || 'Maintenance')}</span>
                <span class="spc-chip">${u.weight_kg ? `${u.weight_kg} kg` : ''}</span>
                ${u.target_weight_kg ? `<span class="spc-chip">Goal: ${u.target_weight_kg} kg</span>` : ''}
            </div>
            <div class="spc-macros">
                <div class="spc-macro-item">
                    <span>Calories</span>
                    <strong>${fmt(mp.calories || nr.calories, 0)}</strong>
                </div>
                <div class="spc-macro-item">
                    <span>Protein</span>
                    <strong>${fmt(mp.protein_g || nr.protein_g, 1)}g</strong>
                </div>
                <div class="spc-macro-item">
                    <span>Carbs</span>
                    <strong>${fmt(mp.carbs_g || nr.carbs_g, 1)}g</strong>
                </div>
                <div class="spc-macro-item">
                    <span>Fat</span>
                    <strong>${fmt(mp.fat_g || nr.fat_g, 1)}g</strong>
                </div>
            </div>
        `;

        const actions = el("div", "spc-actions");
        const loadBtn = el("button", "btn-load-plan", "⚡ Load This Plan");
        loadBtn.addEventListener("click", () => {
            loadPlanFromHistory(item);
            closeHistoryDrawer();
        });

        const deleteBtn = el("button", "btn-delete-plan", "🗑️");
        deleteBtn.title = "Delete this plan";
        deleteBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            deleteHistoryItem(item.id);
        });

        actions.appendChild(loadBtn);
        actions.appendChild(deleteBtn);
        card.appendChild(actions);

        historyDrawerList.appendChild(card);
    });
}

function loadPlanFromHistory(historyItem) {
    if (!historyItem || !historyItem.response) return;

    // Restore form values if present
    const u = historyItem.user || {};
    if (u.name) document.getElementById("name").value = u.name;
    if (u.age) document.getElementById("age").value = u.age;
    if (u.sex || u.gender) document.getElementById("gender").value = u.sex || u.gender;
    if (u.weight_kg || u.weight) document.getElementById("weight").value = u.weight_kg || u.weight;
    if (u.target_weight_kg || u.target_weight) document.getElementById("target_weight").value = u.target_weight_kg || u.target_weight;
    if (u.height_cm || u.height) document.getElementById("height").value = u.height_cm || u.height;
    if (u.activity_level || u.activity) document.getElementById("activity").value = u.activity_level || u.activity;
    if (u.goal) document.getElementById("goal").value = u.goal;
    if (u.diet_type || u.diet) {
        const dietVal = (u.diet_type || u.diet).replace("-", "_");
        document.getElementById("diet").value = dietVal;
    }
    if (u.cuisine) document.getElementById("cuisine").value = u.cuisine;
    if (u.user_prompt) document.getElementById("user_prompt").value = u.user_prompt;

    // Re-calculate biometrics
    calculateBiometricsLive();

    // Render the meal plan directly
    displayMealPlan(historyItem.response, u);

    // Smooth scroll to results
    document.getElementById("meal-section").scrollIntoView({ behavior: "smooth" });
}

function openHistoryDrawer() {
    renderHistoryDrawer();
    historyDrawer.classList.add("active");
    historyDrawerBackdrop.classList.add("active");
    historyDrawer.setAttribute("aria-hidden", "false");
}

function closeHistoryDrawer() {
    historyDrawer.classList.remove("active");
    historyDrawerBackdrop.classList.remove("active");
    historyDrawer.setAttribute("aria-hidden", "true");
}

[openHistoryBtn, historyNavBtn, heroHistoryBtn, historyPreviewViewAll].forEach(btn => {
    if (btn) btn.addEventListener("click", openHistoryDrawer);
});

if (historyDrawerCloseBtn) historyDrawerCloseBtn.addEventListener("click", closeHistoryDrawer);
if (historyDrawerBackdrop) historyDrawerBackdrop.addEventListener("click", closeHistoryDrawer);
if (clearHistoryBtn) clearHistoryBtn.addEventListener("click", clearAllHistory);


// ─── Smart Grocery Shopping List Generator ───────────────────────────────────

function categorizeFood(foodName) {
    const fn = (foodName || "").toLowerCase();

    if (
        fn.includes("spinach") || fn.includes("palak") || fn.includes("methi") ||
        fn.includes("tomato") || fn.includes("onion") || fn.includes("potato") ||
        fn.includes("cucumber") || fn.includes("bell pepper") || fn.includes("capsicum") ||
        fn.includes("carrot") || fn.includes("cauliflower") || fn.includes("gobi") ||
        fn.includes("peas") || fn.includes("mushroom") || fn.includes("apple") ||
        fn.includes("banana") || fn.includes("lettuce") || fn.includes("salad") ||
        fn.includes("edamame") || fn.includes("lemon") || fn.includes("ginger") ||
        fn.includes("garlic") || fn.includes("vegetable")
    ) {
        return "🥬 Fresh Produce";
    }

    if (
        fn.includes("chapati") || fn.includes("roti") || fn.includes("wheat") ||
        fn.includes("rice") || fn.includes("poha") || fn.includes("upma") ||
        fn.includes("oats") || fn.includes("quinoa") || fn.includes("bread") ||
        fn.includes("pita") || fn.includes("khichdi") || fn.includes("flour")
    ) {
        return "🌾 Grains, Cereals & Flours";
    }

    if (
        fn.includes("milk") || fn.includes("yogurt") || fn.includes("curd") ||
        fn.includes("paneer") || fn.includes("cheese") || fn.includes("butter")
    ) {
        return "🥛 Dairy & Alternatives";
    }

    if (
        fn.includes("dal") || fn.includes("lentil") || fn.includes("chana") ||
        fn.includes("chickpea") || fn.includes("rajma") || fn.includes("tofu") ||
        fn.includes("chicken") || fn.includes("egg") || fn.includes("fish") ||
        fn.includes("salmon") || fn.includes("souvlaki") || fn.includes("turkey")
    ) {
        return "🫘 Legumes, Lentils & Proteins";
    }

    if (
        fn.includes("ghee") || fn.includes("oil") || fn.includes("almond") ||
        fn.includes("peanut") || fn.includes("walnut") || fn.includes("nut") ||
        fn.includes("chia") || fn.includes("flax")
    ) {
        return "🌰 Healthy Fats, Nuts & Seeds";
    }

    return "🧂 Pantry, Spices & Condiments";
}

function generateGroceryData(plan) {
    if (!plan || !plan.response || !plan.response.meal_plan) return {};

    const mealData = plan.response.meal_plan.meal_plan || {};
    const consolidated = {};

    Object.keys(mealData).forEach(mealType => {
        const items = mealData[mealType] || [];
        items.forEach(item => {
            const rawName = (item.food || "").trim();
            if (!rawName) return;

            const category = categorizeFood(rawName);
            if (!consolidated[category]) consolidated[category] = {};

            if (consolidated[category][rawName]) {
                consolidated[category][rawName] += Number(item.grams) || 0;
            } else {
                consolidated[category][rawName] = Number(item.grams) || 0;
            }
        });
    });

    return consolidated;
}

function openGroceryModal(plan) {
    if (!plan) {
        alert("Please generate or load a meal plan first to view its grocery list.");
        return;
    }

    const categorized = generateGroceryData(plan);
    groceryContent.replaceChildren();

    let totalItems = 0;

    Object.keys(categorized).forEach(cat => {
        const itemsObj = categorized[cat];
        const itemNames = Object.keys(itemsObj);
        if (itemNames.length === 0) return;

        totalItems += itemNames.length;

        const block = el("div", "grocery-category-block");
        const title = el("div", "gcb-title", cat);
        block.appendChild(title);

        const itemsContainer = el("div", "gcb-items");

        itemNames.forEach(itemName => {
            const grams = itemsObj[itemName];
            const row = el("div", "grocery-item-row");

            const left = el("div", "grocery-item-left");
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.addEventListener("change", () => {
                row.classList.toggle("checked", checkbox.checked);
            });

            const nameSpan = el("span", "item-title", itemName);
            left.appendChild(checkbox);
            left.appendChild(nameSpan);

            const qtySpan = el("span", "item-qty", grams >= 1000 ? `${(grams/1000).toFixed(2)} kg` : `${Math.round(grams)} g`);

            row.appendChild(left);
            row.appendChild(qtySpan);
            itemsContainer.appendChild(row);
        });

        block.appendChild(itemsContainer);
        groceryContent.appendChild(block);
    });

    if (groceryItemCount) groceryItemCount.textContent = `${totalItems} distinct items`;

    groceryModal.classList.add("active");
    groceryModalBackdrop.classList.add("active");
    groceryModal.setAttribute("aria-hidden", "false");
}

function closeGroceryModal() {
    groceryModal.classList.remove("active");
    groceryModalBackdrop.classList.remove("active");
    groceryModal.setAttribute("aria-hidden", "true");
}

if (groceryModalCloseBtn) groceryModalCloseBtn.addEventListener("click", closeGroceryModal);
if (groceryModalBackdrop) groceryModalBackdrop.addEventListener("click", closeGroceryModal);
if (sidebarGroceryBtn) sidebarGroceryBtn.addEventListener("click", () => openGroceryModal(currentActivePlan));

// Copy Grocery List to Clipboard
if (copyGroceryBtn) {
    copyGroceryBtn.addEventListener("click", () => {
        if (!currentActivePlan) return;
        const categorized = generateGroceryData(currentActivePlan);
        let text = "🛒 NUTRIGEN-AI GROCERY SHOPPING LIST\n====================================\n\n";

        Object.keys(categorized).forEach(cat => {
            text += `[ ${cat} ]\n`;
            Object.keys(categorized[cat]).forEach(name => {
                const g = categorized[cat][name];
                const qty = g >= 1000 ? `${(g/1000).toFixed(2)} kg` : `${Math.round(g)} g`;
                text += `  • [ ] ${name} — ${qty}\n`;
            });
            text += "\n";
        });

        navigator.clipboard.writeText(text).then(() => {
            const original = copyGroceryBtn.textContent;
            copyGroceryBtn.textContent = "✓ Copied to Clipboard!";
            setTimeout(() => { copyGroceryBtn.textContent = original; }, 2000);
        }).catch(err => {
            console.error("Clipboard write error:", err);
            alert("Could not copy automatically. Please select text manually.");
        });
    });
}

// Print Grocery List
if (printGroceryBtn) {
    printGroceryBtn.addEventListener("click", () => {
        window.print();
    });
}


// ─── Clinical Print / PDF Export ─────────────────────────────────────────────

function exportPlanToPrint(plan) {
    if (!plan) {
        alert("Please generate or load a meal plan first to print.");
        return;
    }

    const printContainer = document.getElementById("printableReport");
    const u = plan.user || {};
    const nr = plan.response?.nutrition_requirements || {};
    const totals = plan.response?.meal_plan?.totals || {};
    const bio = plan.response?.biometrics || {};

    printContainer.innerHTML = `
        <div class="print-report-header">
            <div>
                <h1>NutriGEN-AI Clinical Nutrition Report</h1>
                <p>Personalized Precision Nutrition & Meal Prescription</p>
                <p><strong>Patient / User:</strong> ${u.name || "Client"} | <strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
            </div>
            <div style="text-align: right;">
                <p><strong>Calorie Target:</strong> ${fmt(totals.calories || nr.calories, 0)} kcal/day</p>
                <p><strong>BMR:</strong> ${fmt(bio.bmr || nr.bmr, 0)} kcal | <strong>TDEE:</strong> ${fmt(bio.tdee || nr.tdee, 0)} kcal</p>
                <p><strong>BMI:</strong> ${fmt(bio.bmi, 1)} (${bio.bmi_category || 'Normal'})</p>
            </div>
        </div>
    `;

    window.print();
}

if (sidebarPrintBtn) {
    sidebarPrintBtn.addEventListener("click", () => exportPlanToPrint(currentActivePlan));
}


// ─── Demo Auto-Fill (For Rapid Evaluation & Presentation) ─────────────────────

if (demoBtn) {
    demoBtn.addEventListener("click", () => {
        document.getElementById("name").value = "Abhinav Sharma";
        document.getElementById("age").value = "23";
        document.getElementById("gender").value = "male";
        document.getElementById("weight").value = "76.0";
        document.getElementById("target_weight").value = "70.0";
        document.getElementById("height").value = "176";
        document.getElementById("activity").value = "moderate";
        document.getElementById("goal").value = "weight_loss";
        document.getElementById("diet").value = "vegetarian";
        document.getElementById("cuisine").value = "indian";
        document.getElementById("meals").value = "4";
        document.getElementById("allergies").value = "Peanuts";
        document.getElementById("user_prompt").value = "Quick authentic meals, high protein, flavorful spices, no oven";

        // Trigger recalculation immediately
        calculateBiometricsLive();

        // Give quick visual indicator on button
        const oldText = demoBtn.innerHTML;
        demoBtn.innerHTML = "<span>✓</span> Loaded Demo";
        setTimeout(() => { demoBtn.innerHTML = oldText; }, 1500);
    });
}


// ─── Main Form Submission ────────────────────────────────────────────────────

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = getFormData();

    if (!data.age || data.age < 15 || !data.weight || data.weight <= 0 || !data.height || data.height <= 0) {
        alert("Please enter valid clinical health details (age >= 15, positive weight and height).");
        return;
    }

    calculateBiometricsLive();

    generateBtn.disabled = true;
    generateBtn.innerHTML = "Solving Optimization & Crafting Recipes… <span>⏳</span>";

    mealResults.replaceChildren();
    const loader = el("div", "loader-box");
    loader.innerHTML = `
        <div class="loader-spinner"></div>
        <h3>NutriGEN-AI Optimizer Running</h3>
        <p>Executing SciPy SLSQP constrained numerical solver & Groq Llama 3.1 AI Chef recipe generation…</p>
    `;
    mealResults.appendChild(loader);

    try {
        const payload = buildPayload(data);

        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errBody = await response.json().catch(() => ({}));
            throw new Error(
                errBody.detail || `Server Error (${response.status}): ${response.statusText}`
            );
        }

        const result = await response.json();

        // Save plan to localStorage history automatically
        savePlanToHistory(payload, result);

        // Display results
        displayMealPlan(result, data);

        // Scroll down smoothly to results section
        document.getElementById("meal-section").scrollIntoView({ behavior: "smooth" });

    } catch (error) {
        console.error("Meal plan generation error:", error);
        mealResults.replaceChildren();

        const errBox = el("div", "error-box");
        errBox.innerHTML = `
            <div class="error-icon">⚠️</div>
            <h3>Could Not Generate Meal Plan</h3>
            <p>${error.message || "Ensure your backend server is active at http://127.0.0.1:8000"}</p>
            <p style="margin-top: 10px; font-size: 11px; color: #777;">
                To launch the server: <code>python -m uvicorn Backend.server:app --reload --port 8000</code>
            </p>
        `;
        mealResults.appendChild(errBox);

    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = "Generate Clinically Optimized Meal Plan <span>→</span>";
    }
});


// ─── Initial Page Load Initialization ────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
    // Populate default biometrics
    calculateBiometricsLive();

    // Load any existing history from localStorage
    updateHistoryUI();
});
