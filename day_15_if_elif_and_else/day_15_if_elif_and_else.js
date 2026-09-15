/*
 * Comprehensive study of if, else if, and else in JavaScript.
 *
 * This file progresses from basic conditional statements to Boolean logic,
 * truthiness, nested decisions, guard clauses, conditional expressions,
 * functions, validation, asynchronous decisions, object-oriented design,
 * rule engines, security-oriented authorization, testing, and performance.
 *
 * Run with:
 *     node conditionals.js
 */

// =============================================================================
// 1. FUNDAMENTALS
// =============================================================================

function section(title) {
    console.log("\n" + "=".repeat(78));
    console.log(title);
    console.log("=".repeat(78));
}

function example01BasicIf() {
    section("1. Basic if statement");

    const age = 20;

    // The block executes only when the condition evaluates to true.
    if (age >= 18) {
        console.log("The person is an adult.");
    }
}

function example02IfElse() {
    section("2. if and else");

    const age = 16;

    if (age >= 18) {
        console.log("Adult");
    } else {
        console.log("Minor");
    }
}

function example03IfElseIfElse() {
    section("3. if, else if, and else");

    const marks = 76;
    let grade;

    // JavaScript evaluates this chain from top to bottom.
    if (marks >= 90) {
        grade = "A+";
    } else if (marks >= 80) {
        grade = "A";
    } else if (marks >= 70) {
        grade = "B";
    } else if (marks >= 60) {
        grade = "C";
    } else if (marks >= 50) {
        grade = "D";
    } else {
        grade = "F";
    }

    console.log("Grade:", grade);
}

function example04ComparisonOperators() {
    section("4. Comparison operators");

    const a = 10;
    const b = 20;

    console.log("a === b:", a === b);
    console.log("a !== b:", a !== b);
    console.log("a < b:", a < b);
    console.log("a <= b:", a <= b);
    console.log("a > b:", a > b);
    console.log("a >= b:", a >= b);

    // Prefer strict equality === in normal application code.
    if (a < b) {
        console.log("a is smaller than b.");
    }
}

// =============================================================================
// 2. BOOLEAN LOGIC
// =============================================================================

function example05BooleanOperators() {
    section("5. Boolean operators");

    const age = 25;
    const hasId = true;

    if (age >= 18 && hasId) {
        console.log("Entry permitted.");
    }

    const temperature = 39;
    const raining = false;

    if (temperature > 40 || raining) {
        console.log("Carry appropriate protection.");
    }

    const accountLocked = false;

    if (!accountLocked) {
        console.log("Account is available.");
    }
}

function example06Truthiness() {
    section("6. JavaScript truthiness");

    const values = [
        true,
        false,
        0,
        1,
        "",
        "JavaScript",
        null,
        undefined,
        NaN,
        [],
        {}
    ];

    for (const value of values) {
        if (value) {
            console.log(String(value), "-> truthy");
        } else {
            console.log(String(value), "-> falsy");
        }
    }

    // Important JavaScript detail:
    // [] and {} are truthy even though they are empty.
    if ([]) {
        console.log("An empty array is truthy in JavaScript.");
    }

    if ({}) {
        console.log("An empty object is truthy in JavaScript.");
    }
}

function example07StrictEquality() {
    section("7. Strict versus loose equality");

    console.log("5 === '5':", 5 === "5");
    console.log("5 == '5':", 5 == "5");

    // Strict equality avoids implicit type conversion.
    if (5 === 5) {
        console.log("Strict equality matched.");
    }
}

// =============================================================================
// 3. INPUT VALIDATION
// =============================================================================

function parsePositiveInteger(value) {
    const number = Number(value);

    if (!Number.isInteger(number)) {
        throw new TypeError("Value must be an integer.");
    }

    if (number <= 0) {
        throw new RangeError("Value must be greater than zero.");
    }

    return number;
}

function example08InputValidation() {
    section("8. Input validation");

    const inputs = ["42", "0", "-5", "hello"];

    for (const value of inputs) {
        try {
            console.log(value, "->", parsePositiveInteger(value));
        } catch (error) {
            console.log(value, "-> rejected:", error.message);
        }
    }
}

// =============================================================================
// 4. NESTING AND GUARD CLAUSES
// =============================================================================

function canEnterEvent(age, hasTicket, isBanned) {
    if (age < 18) {
        return false;
    }

    if (!hasTicket) {
        return false;
    }

    if (isBanned) {
        return false;
    }

    return true;
}

function example09GuardClauses() {
    section("9. Guard clauses");

    console.log(canEnterEvent(25, true, false));
    console.log(canEnterEvent(16, true, false));

    // Early returns reduce unnecessary nesting and make failure conditions
    // explicit before the successful path.
}

// =============================================================================
// 5. CONDITIONAL EXPRESSIONS
// =============================================================================

function example10ConditionalOperator() {
    section("10. Conditional operator");

    const age = 21;
    const status = age >= 18 ? "adult" : "minor";

    console.log(status);

    const score = 85;

    const result =
        score >= 90
            ? "excellent"
            : score >= 70
                ? "good"
                : "needs improvement";

    console.log(result);

    // Nested ternary expressions can become difficult to read.
    // For complex decisions, use if/else if/else.
}

// =============================================================================
// 6. FUNCTIONS AND BUSINESS RULES
// =============================================================================

function classifyTemperature(celsius) {
    if (celsius < 0) {
        return "freezing";
    } else if (celsius < 15) {
        return "cold";
    } else if (celsius < 25) {
        return "mild";
    } else if (celsius < 35) {
        return "warm";
    } else {
        return "hot";
    }
}

function calculateDiscount(customerType, purchaseAmount) {
    if (!Number.isFinite(purchaseAmount) || purchaseAmount < 0) {
        throw new RangeError("Purchase amount must be a non-negative number.");
    }

    let rate = 0;

    if (customerType === "premium") {
        if (purchaseAmount >= 10000) {
            rate = 0.20;
        } else if (purchaseAmount >= 5000) {
            rate = 0.15;
        } else {
            rate = 0.10;
        }
    } else if (customerType === "regular") {
        if (purchaseAmount >= 10000) {
            rate = 0.10;
        } else if (purchaseAmount >= 5000) {
            rate = 0.05;
        }
    }

    return purchaseAmount * rate;
}

function example11BusinessRules() {
    section("11. Functions containing conditional rules");

    for (const temperature of [-10, 8, 20, 30, 40]) {
        console.log(temperature, "->", classifyTemperature(temperature));
    }

    console.log(
        "Premium discount:",
        calculateDiscount("premium", 7000)
    );

    console.log(
        "Regular discount:",
        calculateDiscount("regular", 7000)
    );
}

// =============================================================================
// 7. BOUNDARIES AND EDGE CASES
// =============================================================================

function grade(marks) {
    if (!Number.isFinite(marks)) {
        throw new TypeError("Marks must be a finite number.");
    }

    if (marks < 0 || marks > 100) {
        throw new RangeError("Marks must be between 0 and 100.");
    }

    if (marks >= 90) {
        return "A+";
    } else if (marks >= 80) {
        return "A";
    } else if (marks >= 70) {
        return "B";
    } else if (marks >= 60) {
        return "C";
    } else if (marks >= 50) {
        return "D";
    } else {
        return "F";
    }
}

function example12BoundaryTesting() {
    section("12. Boundary testing");

    const testMarks = [
        0,
        49.99,
        50,
        59.99,
        60,
        69.99,
        70,
        79.99,
        80,
        89.99,
        90,
        100
    ];

    for (const marks of testMarks) {
        console.log(marks, "->", grade(marks));
    }

    for (const invalidMarks of [-1, 101]) {
        try {
            console.log(grade(invalidMarks));
        } catch (error) {
            console.log("Rejected:", error.message);
        }
    }
}

// =============================================================================
// 8. SHORT-CIRCUIT EVALUATION
// =============================================================================

function safeDivision(numerator, denominator) {
    if (denominator === 0) {
        return null;
    }

    return numerator / denominator;
}

function example13ShortCircuit() {
    section("13. Short-circuit evaluation");

    const username = "";
    const isAdmin = false;

    // The second expression is evaluated only when the first expression
    // is truthy.
    if (username && isAdmin) {
        console.log("Admin access.");
    }

    const numbers = [10, 20, 30];

    if (numbers.length > 0 && numbers[0] > 5) {
        console.log("First number is greater than five.");
    }

    console.log("10 / 0 guarded:", safeDivision(10, 0));
}

// =============================================================================
// 9. INDEPENDENT IF VERSUS ELSE IF
// =============================================================================

function example14IndependentIf() {
    section("14. Independent if versus else if");

    const number = 8;

    // Both independent conditions can execute.
    if (number % 2 === 0) {
        console.log("The number is even.");
    }

    if (number > 0) {
        console.log("The number is positive.");
    }

    // Only one branch in this chain can execute.
    if (number < 0) {
        console.log("Negative");
    } else if (number === 0) {
        console.log("Zero");
    } else {
        console.log("Positive");
    }
}

// =============================================================================
// 10. OBJECT-ORIENTED DECISION LOGIC
// =============================================================================

class Employee {
    constructor(name, performanceScore, yearsOfService, disciplinaryAction = false) {
        this.name = name;
        this.performanceScore = performanceScore;
        this.yearsOfService = yearsOfService;
        this.disciplinaryAction = disciplinaryAction;
    }
}

function determineBonus(employee) {
    if (
        !Number.isFinite(employee.performanceScore) ||
        employee.performanceScore < 0 ||
        employee.performanceScore > 100
    ) {
        throw new RangeError("Performance score must be between 0 and 100.");
    }

    if (employee.disciplinaryAction) {
        return 0;
    }

    let baseRate;

    if (employee.performanceScore >= 90) {
        baseRate = 0.20;
    } else if (employee.performanceScore >= 75) {
        baseRate = 0.12;
    } else if (employee.performanceScore >= 60) {
        baseRate = 0.05;
    } else {
        baseRate = 0;
    }

    if (employee.yearsOfService >= 10) {
        baseRate += 0.05;
    } else if (employee.yearsOfService >= 5) {
        baseRate += 0.02;
    }

    return baseRate;
}

function example15ObjectOrientedDecisions() {
    section("15. Object-oriented conditional logic");

    const employees = [
        new Employee("Asha", 94, 11),
        new Employee("Ravi", 80, 6),
        new Employee("Meera", 55, 3),
        new Employee("Kabir", 95, 8, true)
    ];

    for (const employee of employees) {
        console.log(
            employee.name,
            "->",
            `${determineBonus(employee) * 100}% bonus`
        );
    }
}

// =============================================================================
// 11. OBJECTIVE DECISION RULES
// =============================================================================

function assessTransaction(amount, suspicious, verified) {
    if (!Number.isFinite(amount) || amount <= 0) {
        throw new RangeError("Transaction amount must be positive.");
    }

    if (suspicious) {
        return "high";
    } else if (amount >= 100000 && !verified) {
        return "high";
    } else if (amount >= 10000) {
        return "medium";
    } else {
        return "low";
    }
}

function example16RuleEngine() {
    section("16. Rule-based transaction decisions");

    const transactions = [
        { amount: 500, suspicious: false, verified: true },
        { amount: 15000, suspicious: false, verified: true },
        { amount: 150000, suspicious: false, verified: false },
        { amount: 2000, suspicious: true, verified: true }
    ];

    for (const transaction of transactions) {
        console.log(
            transaction,
            "->",
            assessTransaction(
                transaction.amount,
                transaction.suspicious,
                transaction.verified
            )
        );
    }
}

// =============================================================================
// 12. NULLISH VALUES VERSUS GENERAL FALSINESS
// =============================================================================

function example17NullishLogic() {
    section("17. Nullish values and conditional decisions");

    const values = [null, undefined, 0, "", false, "hello"];

    for (const value of values) {
        if (value == null) {
            console.log(String(value), "is nullish.");
        } else if (!value) {
            console.log(String(value), "is present but falsy.");
        } else {
            console.log(String(value), "is truthy.");
        }
    }

    const configuredLimit = 0;

    // ?? preserves zero because zero is not null or undefined.
    const limit = configuredLimit ?? 100;

    console.log("Limit:", limit);
}

// =============================================================================
// 13. ASYNCHRONOUS CONDITIONAL LOGIC
// =============================================================================

function fetchUserStatus() {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                authenticated: true,
                active: true,
                role: "admin"
            });
        }, 10);
    });
}

async function example18AsyncDecision() {
    section("18. Conditions after asynchronous operations");

    try {
        const user = await fetchUserStatus();

        if (!user.authenticated) {
            console.log("Authentication required.");
        } else if (!user.active) {
            console.log("Account is inactive.");
        } else if (user.role === "admin") {
            console.log("Administrative access granted.");
        } else {
            console.log("Standard access granted.");
        }
    } catch (error) {
        console.log("Could not obtain user status:", error.message);
    }
}

// =============================================================================
// 14. SECURITY-ORIENTED AUTHORIZATION
// =============================================================================

function authorizeRequest({
    authenticated,
    role,
    resourceOwner,
    resourcePublic
}) {
    if (!authenticated) {
        return false;
    }

    if (resourcePublic) {
        return true;
    }

    if (role === "admin") {
        return true;
    }

    if (role === "owner" && resourceOwner) {
        return true;
    }

    return false;
}

function example19Authorization() {
    section("19. Security-oriented authorization");

    const requests = [
        {
            authenticated: false,
            role: "admin",
            resourceOwner: false,
            resourcePublic: false
        },
        {
            authenticated: true,
            role: "user",
            resourceOwner: false,
            resourcePublic: true
        },
        {
            authenticated: true,
            role: "admin",
            resourceOwner: false,
            resourcePublic: false
        },
        {
            authenticated: true,
            role: "owner",
            resourceOwner: true,
            resourcePublic: false
        },
        {
            authenticated: true,
            role: "owner",
            resourceOwner: false,
            resourcePublic: false
        }
    ];

    for (const request of requests) {
        console.log(request, "->", authorizeRequest(request));
    }

    // Unknown or missing permissions should normally fail closed.
}

// =============================================================================
// 15. ADVANCED RULE ENGINE
// =============================================================================

class Order {
    constructor(customerType, amount, country, verified) {
        this.customerType = customerType;
        this.amount = amount;
        this.country = country;
        this.verified = verified;
    }
}

function evaluateOrder(order) {
    if (!Number.isFinite(order.amount) || order.amount <= 0) {
        return "REJECTED: invalid amount";
    }

    const supportedCountries = new Set(["IN", "US", "GB", "SG"]);

    if (!supportedCountries.has(order.country)) {
        return "REJECTED: unsupported country";
    }

    if (order.amount >= 500000 && !order.verified) {
        return "REJECTED: verification required";
    }

    if (order.customerType === "enterprise") {
        if (order.amount >= 100000) {
            return "APPROVED: enterprise-high-priority";
        } else if (order.amount >= 10000) {
            return "APPROVED: enterprise-priority";
        } else {
            return "APPROVED: enterprise-standard";
        }
    } else if (order.customerType === "premium") {
        if (order.amount >= 100000) {
            return "APPROVED: premium-high-priority";
        } else {
            return "APPROVED: premium-standard";
        }
    } else if (order.customerType === "regular") {
        if (order.amount >= 100000) {
            return "APPROVED: regular-review";
        } else {
            return "APPROVED: regular-standard";
        }
    } else {
        return "REJECTED: unknown customer type";
    }
}

function example20CompleteDecisionEngine() {
    section("20. Complete order decision engine");

    const orders = [
        new Order("enterprise", 250000, "IN", true),
        new Order("premium", 15000, "US", true),
        new Order("regular", 8000, "GB", true),
        new Order("regular", 600000, "IN", false),
        new Order("regular", 1000, "XX", true),
        new Order("unknown", 1000, "IN", true),
        new Order("regular", -50, "IN", true)
    ];

    for (const order of orders) {
        console.log(order, "->", evaluateOrder(order));
    }
}

// =============================================================================
// 16. PERFORMANCE
// =============================================================================

function linearSearchWithIf(values, target) {
    for (const value of values) {
        if (value === target) {
            return true;
        }
    }

    return false;
}

function example21Performance() {
    section("21. Performance considerations");

    const values = Array.from({ length: 100000 }, (_, index) => index);

    console.log(linearSearchWithIf(values, 99999));
    console.log(values.includes(99999));

    // Array membership is O(n).
    // Set membership is approximately O(1) average case.
    const valueSet = new Set(values);

    if (valueSet.has(99999)) {
        console.log("Set membership found the target efficiently.");
    }
}

// =============================================================================
// 17. COMMON MISTAKES
// =============================================================================

function example22CommonMistakes() {
    section("22. Common mistakes");

    const age = 18;

    // Prefer === instead of = for comparison.
    if (age === 18) {
        console.log("Correct equality comparison.");
    }

    // Avoid accidentally writing:
    // if (age = 18) { ... }
    //
    // Assignment changes the variable and does not express a comparison.

    const score = 95;

    // Correct ordering from highest threshold to lowest.
    if (score >= 90) {
        console.log("Excellent");
    } else if (score >= 70) {
        console.log("Good");
    } else {
        console.log("Needs improvement");
    }

    const verified = true;

    // Prefer:
    if (verified) {
        console.log("Account verified.");
    }

    // Rather than:
    // if (verified === true) { ... }
}

// =============================================================================
// 18. TESTING
// =============================================================================

function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function runTests() {
    section("23. Lightweight executable tests");

    assert(grade(100) === "A+", "100 should be A+");
    assert(grade(90) === "A+", "90 should be A+");
    assert(grade(89.99) === "A", "89.99 should be A");
    assert(grade(80) === "A", "80 should be A");
    assert(grade(79.99) === "B", "79.99 should be B");
    assert(grade(70) === "B", "70 should be B");
    assert(grade(60) === "C", "60 should be C");
    assert(grade(50) === "D", "50 should be D");
    assert(grade(49.99) === "F", "49.99 should be F");

    for (const invalid of [-1, 101]) {
        let rejected = false;

        try {
            grade(invalid);
        } catch {
            rejected = true;
        }

        assert(rejected, `Invalid mark ${invalid} should be rejected`);
    }

    assert(
        authorizeRequest({
            authenticated: false,
            role: "admin",
            resourceOwner: false,
            resourcePublic: false
        }) === false,
        "Unauthenticated users must be denied"
    );

    assert(
        authorizeRequest({
            authenticated: true,
            role: "admin",
            resourceOwner: false,
            resourcePublic: false
        }) === true,
        "Admins should be authorized"
    );

    console.log("All tests passed.");
}

// =============================================================================
// 19. BROWSER-ORIENTED CONDITIONAL EXAMPLE
// =============================================================================

function browserDecisionExample() {
    section("24. Browser-oriented conditional logic");

    // typeof is useful when checking whether a browser global exists.
    if (typeof window !== "undefined") {
        console.log("This code is running in a browser environment.");
    } else {
        console.log("This code is running outside a browser.");
    }

    if (typeof document !== "undefined") {
        console.log("The DOM is available.");
    } else {
        console.log("The DOM is not available.");
    }
}

// =============================================================================
// 20. MAIN PROGRAM
// =============================================================================

async function main() {
    const examples = [
        example01BasicIf,
        example02IfElse,
        example03IfElseIfElse,
        example04ComparisonOperators,
        example05BooleanOperators,
        example06Truthiness,
        example07StrictEquality,
        example08InputValidation,
        example09GuardClauses,
        example10ConditionalOperator,
        example11BusinessRules,
        example12BoundaryTesting,
        example13ShortCircuit,
        example14IndependentIf,
        example15ObjectOrientedDecisions,
        example16RuleEngine,
        example17NullishLogic,
        example18AsyncDecision,
        example19Authorization,
        example20CompleteDecisionEngine,
        example21Performance,
        example22CommonMistakes,
        runTests,
        browserDecisionExample
    ];

    for (const example of examples) {
        const result = example();

        // Support both synchronous and asynchronous examples.
        if (result instanceof Promise) {
            await result;
        }
    }
}

main().catch((error) => {
    console.error("Program failed:", error.message);
    process.exitCode = 1;
});
