// NutriGEN-AI Frontend Logic

// Change this URL if your backend uses a different endpoint.
const API_URL = "http://127.0.0.1:8000/generate-meal-plan";

const form = document.getElementById("nutritionForm");
const generateBtn = document.getElementById("generateBtn");
const mealResults = document.getElementById("mealResults");


// Calculate BMI and estimated calories
function calculateHealthStats(data) {

    const height = data.height / 100;
    const bmi = data.weight / (height * height);

    let bmiStatus = "Normal weight";

    if (bmi < 18.5) bmiStatus = "Underweight";
    else if (bmi >= 25 && bmi < 30) bmiStatus = "Overweight";
    else if (bmi >= 30) bmiStatus = "Obesity range";

    // Mifflin-St Jeor estimation
    let bmr = 10 * data.weight + 6.25 * data.height - 5 * data.age;

    if (data.gender === "male") {
        bmr += 5;
    } else if (data.gender === "female") {
        bmr -= 161;
    } else {
        bmr -= 78;
    }

    const activityFactors = {
        sedentary: 1.2,
        light: 1.375,
        moderate: 1.55,
        active: 1.725,
        very_active: 1.9
    };

    let calories = bmr * activityFactors[data.activity];

    if (data.goal === "weight_loss") calories -= 300;
    if (data.goal === "weight_gain") calories += 300;

    document.getElementById("bmiValue").textContent = bmi.toFixed(1);
    document.getElementById("bmiStatus").textContent = bmiStatus;

    document.getElementById("calorieValue").innerHTML =
        `${Math.round(calories)} <small>kcal</small>`;

    const goalNames = {
        weight_loss: "Weight Loss",
        weight_gain: "Weight Gain",
        maintenance: "Maintenance"
    };

    document.getElementById("goalValue").textContent =
        goalNames[data.goal];

    return Math.round(calories);
}


// Collect user information
function getFormData() {

    return {
        name: document.getElementById("name").value.trim(),
        age: Number(document.getElementById("age").value),
        gender: document.getElementById("gender").value,
        weight: Number(document.getElementById("weight").value),
        height: Number(document.getElementById("height").value),
        activity: document.getElementById("activity").value,
        goal: document.getElementById("goal").value,
        diet: document.getElementById("diet").value,
        allergies: document.getElementById("allergies").value.trim() || "None",
        meals: Number(document.getElementById("meals").value)
    };
}


// Safely display text returned by the backend
function createTextElement(tag, className, value) {
    const element = document.createElement(tag);
    element.className = className;
    element.textContent = value;
    return element;
}


// Display generated meal plan
function displayMealPlan(response, calories) {

    mealResults.replaceChildren();

    const summary = document.createElement("div");
    summary.className = "nutrition-summary";

    summary.appendChild(
        createTextElement("h3", "", "Your Nutrition Overview")
    );

    summary.appendChild(
        createTextElement(
            "p",
            "",
            `Estimated daily calorie target: ${calories} kcal`
        )
    );

    mealResults.appendChild(summary);

    // Support common backend response formats
    let meals = response.meal_plan ??
                response.meals ??
                response.plan ??
                response.recommendations ??
                response;

    if (typeof meals === "string") {
        mealResults.appendChild(
            createTextElement("p", "", meals)
        );
        return;
    }

    if (!Array.isArray(meals)) {
        if (meals && typeof meals === "object") {
            meals = Object.entries(meals)
                .filter(([key, value]) =>
                    Array.isArray(value) ||
                    (value && typeof value === "object")
                )
                .flatMap(([key, value]) =>
                    Array.isArray(value)
                        ? value.map(item => ({
                            meal_type: key,
                            ...item
                        }))
                        : [{
                            meal_type: key,
                            ...value
                        }]
                );
        }
    }

    if (!Array.isArray(meals) || meals.length === 0) {
        mealResults.appendChild(
            createTextElement(
                "p",
                "",
                "The backend returned a response, but no meal list was found. Check the API response format."
            )
        );
        return;
    }

    const grid = document.createElement("div");
    grid.className = "meal-grid";

    meals.forEach((meal, index) => {

        const card = document.createElement("div");
        card.className = "meal-card";

        if (typeof meal === "string") {
            card.appendChild(
                createTextElement("span", "", `Meal ${index + 1}`)
            );

            card.appendChild(
                createTextElement("h3", "", meal)
            );

        } else {

            const mealName =
                meal.meal_type ||
                meal.meal ||
                meal.category ||
                `Meal ${index + 1}`;

            const food =
                meal.food_name ||
                meal.name ||
                meal.dish ||
                meal.recipe ||
                meal.food ||
                "See meal recommendation";

            const description =
                meal.description ||
                meal.details ||
                meal.ingredients ||
                "";

            const caloriesValue =
                meal.calories ??
                meal.calorie ??
                null;

            card.appendChild(
                createTextElement("span", "", mealName)
            );

            card.appendChild(
                createTextElement("h3", "", food)
            );

            if (description) {
                card.appendChild(
                    createTextElement("p", "", String(description))
                );
            }

            if (caloriesValue !== null) {
                card.appendChild(
                    createTextElement(
                        "p",
                        "",
                        `Calories: ${caloriesValue} kcal`
                    )
                );
            }
        }

        grid.appendChild(card);
    });

    mealResults.appendChild(grid);
}


// Form submission
form.addEventListener("submit", async function(event) {

    event.preventDefault();

    const data = getFormData();

    if (
        !Number.isFinite(data.age) ||
        !Number.isFinite(data.weight) ||
        !Number.isFinite(data.height) ||
        data.age <= 0 ||
        data.weight <= 0 ||
        data.height <= 0
    ) {
        alert("Please enter valid health details.");
        return;
    }

    const calories = calculateHealthStats(data);

    generateBtn.disabled = true;
    generateBtn.textContent = "Generating your meal plan...";

    mealResults.replaceChildren();

    const loading = createTextElement(
        "p",
        "",
        "Analysing your profile and requesting personalised meal recommendations..."
    );

    mealResults.appendChild(loading);

    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                ...data,
                daily_calories: calories
            })

        });

        if (!response.ok) {
            throw new Error(
                `Backend error: ${response.status} ${response.statusText}`
            );
        }

        const result = await response.json();

        displayMealPlan(result, calories);

        document.getElementById("meal-section").scrollIntoView({
            behavior: "smooth"
        });

    } catch (error) {

        console.error("Meal plan generation error:", error);

        mealResults.replaceChildren();

        const errorBox = createTextElement(
            "p",
            "error-message",
            "Unable to generate your meal plan. Please check whether your backend is running and whether the API endpoint is correct."
        );

        mealResults.appendChild(errorBox);

    } finally {

        generateBtn.disabled = false;
        generateBtn.innerHTML =
            'Generate My Meal Plan <span>→</span>';

    }

});