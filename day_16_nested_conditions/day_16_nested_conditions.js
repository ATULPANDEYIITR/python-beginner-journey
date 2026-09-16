/*
 * Nested Conditions: a complete JavaScript study program.
 *
 * This file demonstrates:
 *   - if / else if / else
 *   - nested if statements
 *   - boolean operators
 *   - truthiness
 *   - validation
 *   - guard clauses
 *   - conditional expressions
 *   - object-oriented decision logic
 *   - arrays and nested decisions
 *   - switch as an alternative
 *   - asynchronous conditions
 *   - error handling
 *   - decision trees
 *   - testing
 *   - performance and maintainability
 *
 * Run with:
 *   node nested-conditions.js
 */

// ---------------------------------------------------------------------------
// 1. BASIC CONDITIONS
// ---------------------------------------------------------------------------

function demonstrateBasicCondition() {
    const age = 20;

    if (age >= 18) {
        console.log("Basic condition: adult");
    } else {
        console.log("Basic condition: minor");
    }
}

function demonstrateElseIf() {
    const score = 82;
    let grade;

    if (score >= 90) {
        grade = "A";
    } else if (score >= 80) {
        grade = "B";
    } else if (score >= 70) {
        grade = "C";
    } else if (score >= 60) {
        grade = "D";
    } else {
        grade = "F";
    }

    console.log(`else-if chain: score=${score}, grade=${grade}`);
}

function demonstrateBooleanOperators() {
    const age = 25;
    const hasId = true;
    const isStudent = false;

    if (age >= 18 && hasId) {
        console.log("AND: requirements satisfied");
    }

    if (isStudent || age >= 60) {
        console.log("OR: special pricing applies");
    } else {
        console.log("OR: regular pricing applies");
    }

    if (!isStudent) {
        console.log("NOT: person is not a student");
    }
}

// ---------------------------------------------------------------------------
// 2. SIMPLE NESTED CONDITIONS
// ---------------------------------------------------------------------------

function classifyAccess(age, hasIdentityDocument) {
    if (age >= 18) {
        if (hasIdentityDocument) {
            return "Access granted";
        } else {
            return "Access denied: identity document required";
        }
    } else {
        return "Access denied: minimum age requirement not met";
    }
}

function demonstrateNestedConditions() {
    const examples = [
        [25, true],
        [25, false],
        [16, true],
        [16, false],
    ];

    for (const [age, hasId] of examples) {
        console.log(
            `Nested condition: age=${age}, hasId=${hasId} -> ` +
            classifyAccess(age, hasId)
        );
    }
}

// ---------------------------------------------------------------------------
// 3. DEEP NESTING
// ---------------------------------------------------------------------------

function classifyExamResult(score, attendance, misconduct) {
    if (score >= 0 && score <= 100) {
        if (attendance >= 75) {
            if (misconduct) {
                return "Review required: misconduct record";
            } else {
                if (score >= 75) {
                    return "Distinction";
                } else {
                    if (score >= 40) {
                        return "Pass";
                    } else {
                        return "Fail";
                    }
                }
            }
        } else {
            return "Fail: attendance requirement not met";
        }
    } else {
        return "Invalid score";
    }
}

function demonstrateDeepNesting() {
    const cases = [
        [92, 95, false],
        [62, 80, false],
        [32, 90, false],
        [88, 90, true],
        [75, 60, false],
        [105, 90, false],
    ];

    for (const [score, attendance, misconduct] of cases) {
        console.log(
            `Exam: ${score}, attendance=${attendance}, ` +
            `misconduct=${misconduct} -> ` +
            classifyExamResult(score, attendance, misconduct)
        );
    }
}

// ---------------------------------------------------------------------------
// 4. VALIDATION
// ---------------------------------------------------------------------------

function validateAge(age) {
    if (!Number.isInteger(age)) {
        return {
            valid: false,
            message: "Age must be an integer.",
        };
    }

    if (age < 0 || age > 150) {
        return {
            valid: false,
            message: "Age must be between 0 and 150.",
        };
    }

    return {
        valid: true,
        message: "",
    };
}

function eligibilityDecision(age, employed, income) {
    const validation = validateAge(age);

    if (!validation.valid) {
        return `Invalid input: ${validation.message}`;
    }

    if (age >= 18) {
        if (employed) {
            if (income >= 30000) {
                return "Eligible: employed adult with sufficient income";
            } else {
                return "Condition not met: income below threshold";
            }
        } else {
            return "Condition not met: applicant is unemployed";
        }
    } else {
        return "Condition not met: applicant is under 18";
    }
}

// ---------------------------------------------------------------------------
// 5. TRUTHINESS AND EDGE CASES
// ---------------------------------------------------------------------------

function demonstrateTruthiness() {
    const values = [
        false,
        true,
        0,
        1,
        "",
        "JavaScript",
        null,
        undefined,
        [],
        {},
        NaN,
    ];

    for (const value of values) {
        if (value) {
            console.log("Truthy:", value);
        } else {
            console.log("Falsy:", value);
        }
    }

    // Empty arrays and objects are truthy in JavaScript.
    if ([]) {
        console.log("An empty array is truthy.");
    }

    if ({}) {
        console.log("An empty object is truthy.");
    }
}

// ---------------------------------------------------------------------------
// 6. COMPOUND VERSUS NESTED CONDITIONS
// ---------------------------------------------------------------------------

function accessCompound(age, hasId, activeAccount) {
    return age >= 18 && hasId && activeAccount;
}

function accessNested(age, hasId, activeAccount) {
    if (age >= 18) {
        if (hasId) {
            if (activeAccount) {
                return true;
            }
        }
    }

    return false;
}

function demonstrateEquivalentLogic() {
    const cases = [
        [20, true, true],
        [20, true, false],
        [20, false, true],
        [17, true, true],
    ];

    for (const testCase of cases) {
        const compound = accessCompound(...testCase);
        const nested = accessNested(...testCase);

        console.log(
            testCase,
            `-> compound=${compound}, nested=${nested}`
        );
    }
}

// ---------------------------------------------------------------------------
// 7. COLLECTIONS WITH NESTED CONDITIONS
// ---------------------------------------------------------------------------

function findUserPermission(users, username, requiredPermission) {
    for (const user of users) {
        if (user.username === username) {
            if (user.active === true) {
                if (Array.isArray(user.permissions)) {
                    if (user.permissions.includes(requiredPermission)) {
                        return "Permission granted";
                    } else {
                        return "Permission denied: missing permission";
                    }
                } else {
                    return "Invalid permission data";
                }
            } else {
                return "Permission denied: inactive account";
            }
        }
    }

    return "User not found";
}

function demonstrateCollectionNesting() {
    const users = [
        {
            username: "alice",
            active: true,
            permissions: ["read", "write"],
        },
        {
            username: "bob",
            active: false,
            permissions: ["read"],
        },
    ];

    for (const username of ["alice", "bob", "charlie"]) {
        console.log(
            username,
            "->",
            findUserPermission(users, username, "write")
        );
    }
}

// ---------------------------------------------------------------------------
// 8. CONDITIONAL OPERATOR
// ---------------------------------------------------------------------------

function demonstrateConditionalOperator() {
    const age = 21;
    const status = age >= 18 ? "adult" : "minor";

    console.log("Conditional operator:", status);

    // Nested ternaries are legal but can become difficult to maintain.
    const score = 85;
    const grade =
        score >= 90
            ? "A"
            : score >= 80
                ? "B"
                : score >= 70
                    ? "C"
                    : "F";

    console.log("Nested conditional operator:", grade);
}

// ---------------------------------------------------------------------------
// 9. GUARD CLAUSES
// ---------------------------------------------------------------------------

function calculateDiscount(customerActive, age, purchaseAmount) {
    if (!customerActive) {
        return 0;
    }

    if (age < 18) {
        return 0;
    }

    if (purchaseAmount <= 0) {
        return 0;
    }

    if (purchaseAmount >= 10000) {
        return 0.20;
    }

    if (purchaseAmount >= 5000) {
        return 0.10;
    }

    return 0.05;
}

// ---------------------------------------------------------------------------
// 10. SHIPPING DECISION LOGIC
// ---------------------------------------------------------------------------

function calculateShipping(destination, weightKg, express) {
    if (!["domestic", "international"].includes(destination)) {
        throw new Error("Unknown destination.");
    }

    if (!Number.isFinite(weightKg) || weightKg <= 0) {
        throw new Error("Weight must be positive.");
    }

    if (destination === "domestic") {
        let base;

        if (weightKg <= 1) {
            base = 60;
        } else if (weightKg <= 5) {
            base = 120;
        } else {
            base = 250;
        }

        if (express) {
            return base * 1.75;
        }

        return base;
    }

    let base;

    if (weightKg <= 1) {
        base = 1000;
    } else if (weightKg <= 5) {
        base = 2500;
    } else {
        base = 5000;
    }

    if (express) {
        return base * 1.50;
    }

    return base;
}

// ---------------------------------------------------------------------------
// 11. OBJECT-ORIENTED DECISION ENGINE
// ---------------------------------------------------------------------------

class Account {
    constructor(username, age, active, verified, role, balance) {
        this.username = username;
        this.age = age;
        this.active = active;
        this.verified = verified;
        this.role = role;
        this.balance = balance;
    }
}

class AccountDecisionEngine {
    constructor() {
        this.minimumRetainedBalance = 100;
    }

    evaluateTransfer(sender, recipient, amount) {
        if (amount <= 0) {
            return "Rejected: amount must be positive";
        }

        if (!sender.active) {
            return "Rejected: sender account is inactive";
        }

        if (!recipient.active) {
            return "Rejected: recipient account is inactive";
        }

        if (!sender.verified) {
            return "Rejected: sender is not verified";
        }

        if (!recipient.verified) {
            return "Rejected: recipient is not verified";
        }

        if (sender.age < 18) {
            return "Rejected: sender must be an adult";
        }

        if (sender.balance < amount) {
            return "Rejected: insufficient balance";
        }

        if (sender.balance - amount < this.minimumRetainedBalance) {
            return "Rejected: minimum retained balance violated";
        }

        return "Transfer approved";
    }
}

// ---------------------------------------------------------------------------
// 12. SWITCH AS AN ALTERNATIVE TO NESTED CATEGORICAL CONDITIONS
// ---------------------------------------------------------------------------

function classifyHttpStatus(statusCode) {
    switch (statusCode) {
        case 200:
            return "Success";

        case 201:
            return "Created";

        case 400:
            return "Bad request";

        case 401:
        case 403:
            return "Authentication or authorization failure";

        case 404:
            return "Not found";

        default:
            if (statusCode >= 500 && statusCode <= 599) {
                return "Server error";
            }

            return "Other status";
    }
}

// ---------------------------------------------------------------------------
// 13. AUTHORIZATION
// ---------------------------------------------------------------------------

function authorizationCheck(
    authenticated,
    role,
    requestedResource,
    resourceOwner,
    currentUser
) {
    if (!authenticated) {
        return "Denied: authentication required";
    }

    const normalizedRole = String(role).trim().toLowerCase();

    if (normalizedRole === "admin") {
        return "Allowed: administrator access";
    }

    if (normalizedRole === "user") {
        if (requestedResource === "profile") {
            if (resourceOwner === currentUser) {
                return "Allowed: own profile";
            }

            return "Denied: profile belongs to another user";
        }

        if (requestedResource === "public") {
            return "Allowed: public resource";
        }

        return "Denied: insufficient permission";
    }

    return "Denied: unknown role";
}

// ---------------------------------------------------------------------------
// 14. ASYNCHRONOUS CONDITIONS
// ---------------------------------------------------------------------------

function fetchAccountStatus(username) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (!username) {
                reject(new Error("Username is required."));
                return;
            }

            if (username === "alice") {
                resolve({
                    active: true,
                    verified: true,
                    role: "user",
                });
            } else {
                resolve({
                    active: false,
                    verified: false,
                    role: "guest",
                });
            }
        }, 20);
    });
}

async function asynchronousAuthorization(username) {
    try {
        const account = await fetchAccountStatus(username);

        if (account.active) {
            if (account.verified) {
                if (account.role === "user") {
                    return "Asynchronous decision: access granted";
                } else {
                    return "Asynchronous decision: role not permitted";
                }
            } else {
                return "Asynchronous decision: verification required";
            }
        } else {
            return "Asynchronous decision: account inactive";
        }
    } catch (error) {
        return `Asynchronous decision failed: ${error.message}`;
    }
}

// ---------------------------------------------------------------------------
// 15. DECISION TREE
// ---------------------------------------------------------------------------

class DecisionNode {
    constructor(question, yes = null, no = null, result = null) {
        this.question = question;
        this.yes = yes;
        this.no = no;
        this.result = result;
    }
}

function evaluateDecisionTree(root, answers) {
    let current = root;
    let answerIndex = 0;

    while (current.result === null) {
        if (answerIndex >= answers.length) {
            return "Insufficient answers";
        }

        const answer = answers[answerIndex++];

        if (answer) {
            if (current.yes === null) {
                return "Invalid tree: missing yes branch";
            }

            current = current.yes;
        } else {
            if (current.no === null) {
                return "Invalid tree: missing no branch";
            }

            current = current.no;
        }
    }

    return current.result;
}

function buildVehicleDecisionTree() {
    return new DecisionNode(
        "Does the vehicle have four wheels?",
        new DecisionNode(
            "Is it powered by an engine?",
            new DecisionNode(
                "Is it intended mainly for passengers?",
                null,
                null,
                "Car"
            ),
            null,
            "Utility vehicle"
        ),
        new DecisionNode(
            "Does it have two wheels?",
            null,
            null,
            "Other vehicle"
        ),
        null
    );
}

// ---------------------------------------------------------------------------
// 16. PERFORMANCE-AWARE CONDITIONS
// ---------------------------------------------------------------------------

function expensiveCheck() {
    let total = 0;

    for (let number = 1; number <= 10000; number += 1) {
        total += number * number;
    }

    return total > 0;
}

function performanceAwareDecision(age, active) {
    // Cheap rejection checks run before the expensive operation.
    if (age < 18) {
        return false;
    }

    if (!active) {
        return false;
    }

    if (expensiveCheck()) {
        return true;
    }

    return false;
}

// ---------------------------------------------------------------------------
// 17. INDUSTRY-STYLE LOAN CASE STUDY
// ---------------------------------------------------------------------------

class LoanApplication {
    constructor({
        applicantName,
        age,
        monthlyIncome,
        monthlyDebt,
        creditScore,
        employmentYears,
        verifiedIdentity,
        requestedAmount,
    }) {
        this.applicantName = applicantName;
        this.age = age;
        this.monthlyIncome = monthlyIncome;
        this.monthlyDebt = monthlyDebt;
        this.creditScore = creditScore;
        this.employmentYears = employmentYears;
        this.verifiedIdentity = verifiedIdentity;
        this.requestedAmount = requestedAmount;
    }
}

class LoanDecisionEngine {
    /*
     * Thresholds below are educational examples, not a real lender's policy.
     */
    evaluate(application) {
        if (application.age < 18) {
            return "Rejected: applicant is under 18";
        }

        if (!application.verifiedIdentity) {
            return "Rejected: identity verification failed";
        }

        if (application.monthlyIncome <= 0) {
            return "Rejected: income must be positive";
        }

        if (application.monthlyDebt < 0) {
            return "Rejected: debt cannot be negative";
        }

        if (
            application.creditScore < 300 ||
            application.creditScore > 900
        ) {
            return "Rejected: invalid credit score";
        }

        if (application.requestedAmount <= 0) {
            return "Rejected: requested amount must be positive";
        }

        const debtToIncome =
            application.monthlyDebt / application.monthlyIncome;

        if (application.creditScore >= 750) {
            if (debtToIncome <= 0.35) {
                if (application.employmentYears >= 2) {
                    return "Eligible: standard review";
                } else {
                    return "Manual review: limited employment history";
                }
            } else {
                return "Manual review: elevated debt-to-income ratio";
            }
        }

        if (application.creditScore >= 650) {
            if (debtToIncome <= 0.30) {
                if (application.employmentYears >= 3) {
                    return "Manual review: moderate credit profile";
                } else {
                    return "Manual review: employment history insufficient";
                }
            } else {
                return "Rejected: debt-to-income ratio too high";
            }
        }

        return "Rejected: credit score below example threshold";
    }
}

// ---------------------------------------------------------------------------
// 18. ASSERTION-BASED TESTING
// ---------------------------------------------------------------------------

function assertEqual(actual, expected, message) {
    if (actual !== expected) {
        throw new Error(
            `${message}: expected ${expected}, received ${actual}`
        );
    }
}

function runTests() {
    assertEqual(
        classifyAccess(18, true),
        "Access granted",
        "Age boundary"
    );

    assertEqual(
        classifyAccess(18, false),
        "Access denied: identity document required",
        "Missing ID"
    );

    assertEqual(
        classifyAccess(17, true),
        "Access denied: minimum age requirement not met",
        "Minor"
    );

    assertEqual(
        accessCompound(20, true, true),
        accessNested(20, true, true),
        "Equivalent access logic"
    );

    assertEqual(
        classifyHttpStatus(200),
        "Success",
        "HTTP 200"
    );

    assertEqual(
        classifyHttpStatus(503),
        "Server error",
        "HTTP 503"
    );

    assertEqual(
        calculateDiscount(true, 30, 12000),
        0.20,
        "Large purchase discount"
    );

    console.log("All JavaScript tests passed.");
}

// ---------------------------------------------------------------------------
// 19. MAIN DEMONSTRATION
// ---------------------------------------------------------------------------

async function main() {
    console.log("=".repeat(72));
    console.log("NESTED CONDITIONS: JAVASCRIPT STUDY PROGRAM");
    console.log("=".repeat(72));

    console.log("\n1. Basic condition");
    demonstrateBasicCondition();

    console.log("\n2. if / else if / else");
    demonstrateElseIf();

    console.log("\n3. Boolean operators");
    demonstrateBooleanOperators();

    console.log("\n4. Nested conditions");
    demonstrateNestedConditions();

    console.log("\n5. Deeper nesting");
    demonstrateDeepNesting();

    console.log("\n6. Validation");
    console.log(eligibilityDecision(25, true, 50000));
    console.log(eligibilityDecision(17, true, 50000));
    console.log(eligibilityDecision(-1, true, 50000));

    console.log("\n7. Truthiness");
    demonstrateTruthiness();

    console.log("\n8. Compound versus nested logic");
    demonstrateEquivalentLogic();

    console.log("\n9. Collection nesting");
    demonstrateCollectionNesting();

    console.log("\n10. Conditional operator");
    demonstrateConditionalOperator();

    console.log("\n11. Guard clauses");
    for (const amount of [0, 3000, 7000, 12000]) {
        console.log(
            `Purchase=${amount}, discount=${calculateDiscount(
                true,
                30,
                amount
            ) * 100}%`
        );
    }

    console.log("\n12. Shipping decisions");
    for (const [destination, weight, express] of [
        ["domestic", 0.5, false],
        ["domestic", 3, true],
        ["international", 2, false],
        ["international", 8, true],
    ]) {
        console.log(
            destination,
            weight,
            express,
            "->",
            calculateShipping(destination, weight, express)
        );
    }

    console.log("\n13. Object-oriented decision engine");
    const sender = new Account(
        "sender",
        30,
        true,
        true,
        "user",
        5000
    );

    const recipient = new Account(
        "recipient",
        30,
        true,
        true,
        "user",
        1000
    );

    const accountEngine = new AccountDecisionEngine();

    console.log(
        accountEngine.evaluateTransfer(sender, recipient, 1000)
    );

    console.log("\n14. Switch alternative");
    for (const code of [200, 201, 401, 404, 503, 418]) {
        console.log(code, "->", classifyHttpStatus(code));
    }

    console.log("\n15. Authorization");
    console.log(
        authorizationCheck(
            true,
            "user",
            "profile",
            "alice",
            "alice"
        )
    );

    console.log(
        authorizationCheck(
            true,
            "user",
            "profile",
            "bob",
            "alice"
        )
    );

    console.log("\n16. Asynchronous conditions");
    console.log(await asynchronousAuthorization("alice"));
    console.log(await asynchronousAuthorization("bob"));

    console.log("\n17. Decision tree");
    const tree = buildVehicleDecisionTree();
    console.log(evaluateDecisionTree(tree, [true, true, true]));
    console.log(evaluateDecisionTree(tree, [true, true, false]));
    console.log(evaluateDecisionTree(tree, [false]));

    console.log("\n18. Performance-aware condition");
    console.log(performanceAwareDecision(25, true));
    console.log(performanceAwareDecision(16, true));

    console.log("\n19. Loan case study");
    const applications = [
        new LoanApplication({
            applicantName: "Asha",
            age: 30,
            monthlyIncome: 100000,
            monthlyDebt: 20000,
            creditScore: 780,
            employmentYears: 5,
            verifiedIdentity: true,
            requestedAmount: 500000,
        }),
        new LoanApplication({
            applicantName: "Bharat",
            age: 28,
            monthlyIncome: 80000,
            monthlyDebt: 30000,
            creditScore: 680,
            employmentYears: 4,
            verifiedIdentity: true,
            requestedAmount: 300000,
        }),
        new LoanApplication({
            applicantName: "Chirag",
            age: 22,
            monthlyIncome: 50000,
            monthlyDebt: 20000,
            creditScore: 620,
            employmentYears: 1,
            verifiedIdentity: true,
            requestedAmount: 200000,
        }),
        new LoanApplication({
            applicantName: "Divya",
            age: 35,
            monthlyIncome: 90000,
            monthlyDebt: 10000,
            creditScore: 760,
            employmentYears: 7,
            verifiedIdentity: false,
            requestedAmount: 400000,
        }),
    ];

    const loanEngine = new LoanDecisionEngine();

    for (const application of applications) {
        console.log(
            application.applicantName,
            "->",
            loanEngine.evaluate(application)
        );
    }

    console.log("\n20. Tests");
    runTests();

    console.log("\nProgram completed.");
}

main().catch((error) => {
    console.error("Fatal error:", error.message);
    process.exitCode = 1;
});
