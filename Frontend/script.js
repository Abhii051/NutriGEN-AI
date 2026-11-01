
const form = document.getElementById("nutritionForm");

form.addEventListener("submit", function(event) {
    event.preventDefault();

    // Get user details
    const name = document.getElementById("name").value.trim();
    const age = Number(document.getElementById("age").value);
    const gender = document.getElementById("gender").value;
    const weight = Number(document.getElementById("weight").value);
    const height = Number(document.getElementById("height").value);
    const activity = Number(document.getElementById("activity").value);
    const goal = document.getElementById("goal").value;
    const diet = document.getElementById("diet").value;

    // Basic validation
    if (
        !name ||
        !Number.isFinite(age) || age < 18 || age > 100 ||
        !Number.isFinite(weight) || weight <= 0 ||
        !Number.isFinite(height) || height <= 0 ||
        !Number.isFinite(activity)
    ) {
        alert("Please enter valid details.");
        return;
    }

    // Step 1: Calculate BMR using Mifflin-St Jeor equation
    let bmr;

    if (gender === "male") {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
    } else {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
    }

    // Step 2: Calculate TDEE
    const tdee = bmr * activity;

    // Step 3: Goal-based calorie estimate
    let target;

    if (goal === "loss") {
        target = tdee - 300;
    } else if (goal === "gain") {
        target = tdee + 300;
    } else {
        target = tdee;
    }

    // Step 4: Display results
    document.getElementById("resultGreeting").textContent =
        "Hello, " + name + "!";

    document.getElementById("bmrResult").textContent =
        Math.round(bmr).toLocaleString("en-IN");

    document.getElementById("tdeeResult").textContent =
        Math.round(tdee).toLocaleString("en-IN");

    document.getElementById("targetResult").textContent =
        Math.round(target).toLocaleString("en-IN");

    document.getElementById("dietResult").textContent =
        "Dietary Preference: " + diet.charAt(0).toUpperCase() + diet.slice(1);

    document.getElementById("goalResult").textContent =
        "Nutrition Goal: " + {
            loss: "Weight Loss",
            maintain: "Weight Maintenance",
            gain: "Weight Gain"
        }[goal];

    // Show results
    const results = document.getElementById("results");
    results.hidden = false;

    results.scrollIntoView({
        behavior: "smooth"
    });
});
