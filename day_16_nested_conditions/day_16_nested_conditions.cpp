#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

/*
 * Nested Conditions: C++ industry-style case study.
 *
 * Scenario:
 * A financial service receives loan applications. The program validates
 * applications and evaluates them through progressively more detailed
 * conditional rules.
 *
 * The implementation demonstrates:
 *   - basic if / else
 *   - nested conditions
 *   - compound conditions
 *   - guard clauses
 *   - validation
 *   - enums
 *   - structs/classes
 *   - collections
 *   - decision trees
 *   - error handling
 *   - complexity
 *   - maintainability
 *
 * Compile:
 *   g++ -std=c++17 -Wall -Wextra -pedantic nested_conditions.cpp -o nested_conditions
 */

enum class EmploymentType {
    Unemployed,
    Salaried,
    SelfEmployed
};

enum class DecisionStatus {
    Approved,
    ManualReview,
    Rejected
};

struct LoanApplication {
    std::string applicantName;
    int age;
    double monthlyIncome;
    double monthlyDebt;
    int creditScore;
    double employmentYears;
    bool verifiedIdentity;
    double requestedAmount;
    EmploymentType employmentType;
};

struct DecisionResult {
    DecisionStatus status;
    std::string reason;
};

std::string decisionStatusToString(DecisionStatus status) {
    switch (status) {
        case DecisionStatus::Approved:
            return "Approved";
        case DecisionStatus::ManualReview:
            return "Manual review";
        case DecisionStatus::Rejected:
            return "Rejected";
    }

    return "Unknown";
}

// ---------------------------------------------------------------------------
// Basic nested condition
// ---------------------------------------------------------------------------

std::string classifyAccess(int age, bool hasIdentityDocument) {
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

// ---------------------------------------------------------------------------
// Multi-level nested condition
// ---------------------------------------------------------------------------

std::string classifyExamResult(
    double score,
    double attendance,
    bool misconduct
) {
    if (score >= 0.0 && score <= 100.0) {
        if (attendance >= 75.0) {
            if (misconduct) {
                return "Review required: misconduct record";
            } else {
                if (score >= 75.0) {
                    return "Distinction";
                } else {
                    if (score >= 40.0) {
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

// ---------------------------------------------------------------------------
// Guard-clause alternative
// ---------------------------------------------------------------------------

double calculateDiscount(
    bool customerActive,
    int age,
    double purchaseAmount
) {
    /*
     * Guard clauses reduce indentation. Each invalid condition returns
     * immediately, leaving the main business logic at the bottom.
     */
    if (!customerActive) {
        return 0.0;
    }

    if (age < 18) {
        return 0.0;
    }

    if (purchaseAmount <= 0.0) {
        return 0.0;
    }

    if (purchaseAmount >= 10000.0) {
        return 0.20;
    }

    if (purchaseAmount >= 5000.0) {
        return 0.10;
    }

    return 0.05;
}

// ---------------------------------------------------------------------------
// Collection lookup with nested conditions
// ---------------------------------------------------------------------------

struct User {
    std::string username;
    bool active;
    std::unordered_set<std::string> permissions;
};

std::string findUserPermission(
    const std::vector<User>& users,
    const std::string& username,
    const std::string& requiredPermission
) {
    for (const User& user : users) {
        if (user.username == username) {
            if (user.active) {
                if (user.permissions.find(requiredPermission) !=
                    user.permissions.end()) {
                    return "Permission granted";
                } else {
                    return "Permission denied: missing permission";
                }
            } else {
                return "Permission denied: inactive account";
            }
        }
    }

    return "User not found";
}

// ---------------------------------------------------------------------------
// Decision tree data structure
// ---------------------------------------------------------------------------

struct DecisionNode {
    std::string question;
    std::optional<std::size_t> yesChild;
    std::optional<std::size_t> noChild;
    std::optional<std::string> result;
};

class DecisionTree {
private:
    std::vector<DecisionNode> nodes;
    std::size_t rootIndex{0};

public:
    void addNode(
        const std::string& question,
        std::optional<std::size_t> yesChild,
        std::optional<std::size_t> noChild,
        std::optional<std::string> result
    ) {
        nodes.push_back(
            DecisionNode{
                question,
                yesChild,
                noChild,
                result
            }
        );
    }

    void setRoot(std::size_t index) {
        if (index >= nodes.size()) {
            throw std::out_of_range("Root index is outside the tree.");
        }

        rootIndex = index;
    }

    std::string evaluate(const std::vector<bool>& answers) const {
        if (nodes.empty()) {
            return "Invalid tree: no nodes";
        }

        std::size_t currentIndex = rootIndex;
        std::size_t answerIndex = 0;

        while (true) {
            if (currentIndex >= nodes.size()) {
                return "Invalid tree: child index outside tree";
            }

            const DecisionNode& node = nodes[currentIndex];

            if (node.result.has_value()) {
                return node.result.value();
            }

            if (answerIndex >= answers.size()) {
                return "Insufficient answers";
            }

            const bool answer = answers[answerIndex++];

            if (answer) {
                if (!node.yesChild.has_value()) {
                    return "Invalid tree: missing yes branch";
                }

                currentIndex = node.yesChild.value();
            } else {
                if (!node.noChild.has_value()) {
                    return "Invalid tree: missing no branch";
                }

                currentIndex = node.noChild.value();
            }
        }
    }
};

// ---------------------------------------------------------------------------
// Loan decision engine
// ---------------------------------------------------------------------------

class LoanDecisionEngine {
private:
    static constexpr double MAX_STANDARD_DTI = 0.35;
    static constexpr double MAX_MODERATE_DTI = 0.30;

    bool validate(const LoanApplication& application, std::string& reason) const {
        /*
         * Validation happens before business decisions. This prevents invalid
         * data from being interpreted as a legitimate decision.
         */
        if (application.applicantName.empty()) {
            reason = "Applicant name is required";
            return false;
        }

        if (application.age < 18 || application.age > 150) {
            reason = "Age must be between 18 and 150";
            return false;
        }

        if (application.monthlyIncome <= 0.0) {
            reason = "Monthly income must be positive";
            return false;
        }

        if (application.monthlyDebt < 0.0) {
            reason = "Monthly debt cannot be negative";
            return false;
        }

        if (application.creditScore < 300 ||
            application.creditScore > 900) {
            reason = "Credit score must be between 300 and 900";
            return false;
        }

        if (application.employmentYears < 0.0) {
            reason = "Employment history cannot be negative";
            return false;
        }

        if (application.requestedAmount <= 0.0) {
            reason = "Requested amount must be positive";
            return false;
        }

        return true;
    }

public:
    DecisionResult evaluate(const LoanApplication& application) const {
        std::string validationError;

        if (!validate(application, validationError)) {
            return {
                DecisionStatus::Rejected,
                validationError
            };
        }

        if (!application.verifiedIdentity) {
            return {
                DecisionStatus::Rejected,
                "Identity verification failed"
            };
        }

        /*
         * A nested decision tree follows:
         *
         * credit score
         *     |
         *     +-- high score
         *     |      |
         *     |      +-- acceptable DTI
         *     |             |
         *     |             +-- sufficient employment history
         *     |
         *     +-- moderate score
         *            |
         *            +-- lower DTI requirement
         *                   |
         *                   +-- longer employment history
         *
         * The exact thresholds are educational examples and do not represent
         * an actual lender's underwriting policy.
         */
        const double debtToIncome =
            application.monthlyDebt / application.monthlyIncome;

        if (application.creditScore >= 750) {
            if (debtToIncome <= MAX_STANDARD_DTI) {
                if (application.employmentYears >= 2.0) {
                    return {
                        DecisionStatus::Approved,
                        "Example rules satisfied for standard review"
                    };
                } else {
                    return {
                        DecisionStatus::ManualReview,
                        "Limited employment history"
                    };
                }
            } else {
                return {
                    DecisionStatus::ManualReview,
                    "Debt-to-income ratio exceeds standard threshold"
                };
            }
        }

        if (application.creditScore >= 650) {
            if (debtToIncome <= MAX_MODERATE_DTI) {
                if (application.employmentYears >= 3.0) {
                    return {
                        DecisionStatus::ManualReview,
                        "Moderate credit profile requires manual review"
                    };
                } else {
                    return {
                        DecisionStatus::ManualReview,
                        "Employment history below example requirement"
                    };
                }
            } else {
                return {
                    DecisionStatus::Rejected,
                    "Debt-to-income ratio exceeds moderate threshold"
                };
            }
        }

        return {
            DecisionStatus::Rejected,
            "Credit score below example threshold"
        };
    }
};

// ---------------------------------------------------------------------------
// Input validation helper
// ---------------------------------------------------------------------------

int readInteger(const std::string& prompt) {
    int value{};

    while (true) {
        std::cout << prompt;

        if (std::cin >> value) {
            return value;
        }

        std::cout << "Invalid integer. Try again.\n";
        std::cin.clear();
        std::cin.ignore(
            std::numeric_limits<std::streamsize>::max(),
            '\n'
        );
    }
}

bool readBoolean(const std::string& prompt) {
    int value{};

    while (true) {
        std::cout << prompt << " (1=yes, 0=no): ";

        if (std::cin >> value && (value == 0 || value == 1)) {
            return value == 1;
        }

        std::cout << "Enter 1 or 0.\n";
        std::cin.clear();
        std::cin.ignore(
            std::numeric_limits<std::streamsize>::max(),
            '\n'
        );
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void assertEqual(
    const std::string& actual,
    const std::string& expected,
    const std::string& testName
) {
    if (actual != expected) {
        throw std::runtime_error(
            "Test failed: " + testName +
            " | expected='" + expected +
            "', actual='" + actual + "'"
        );
    }
}

void assertDouble(
    double actual,
    double expected,
    const std::string& testName
) {
    constexpr double epsilon = 1e-9;

    if (std::abs(actual - expected) > epsilon) {
        throw std::runtime_error(
            "Floating-point test failed: " + testName
        );
    }
}

void runTests() {
    assertEqual(
        classifyAccess(18, true),
        "Access granted",
        "adult with ID"
    );

    assertEqual(
        classifyAccess(18, false),
        "Access denied: identity document required",
        "adult without ID"
    );

    assertEqual(
        classifyAccess(17, true),
        "Access denied: minimum age requirement not met",
        "minor"
    );

    assertEqual(
        classifyExamResult(75, 75, false),
        "Distinction",
        "score and attendance boundaries"
    );

    assertEqual(
        classifyExamResult(40, 75, false),
        "Pass",
        "passing boundary"
    );

    assertEqual(
        classifyExamResult(39.99, 75, false),
        "Fail",
        "failing boundary"
    );

    assertEqual(
        classifyExamResult(80, 74.99, false),
        "Fail: attendance requirement not met",
        "attendance boundary"
    );

    assertDouble(
        calculateDiscount(true, 30, 12000),
        0.20,
        "highest discount"
    );

    assertDouble(
        calculateDiscount(true, 30, 5000),
        0.10,
        "medium discount"
    );

    assertDouble(
        calculateDiscount(false, 30, 12000),
        0.0,
        "inactive customer"
    );

    std::cout << "All C++ tests passed.\n";
}

// ---------------------------------------------------------------------------
// Decision tree construction
// ---------------------------------------------------------------------------

DecisionTree buildVehicleDecisionTree() {
    DecisionTree tree;

    /*
     * Nodes:
     * 0: four wheels?
     * 1: powered?
     * 2: passenger focused?
     * 3: car
     * 4: utility vehicle
     * 5: non-powered four-wheel vehicle
     * 6: two wheels?
     * 7: two-wheel vehicle
     * 8: other vehicle
     */

    tree.addNode(
        "Does the vehicle have four wheels?",
        1,
        6,
        std::nullopt
    );

    tree.addNode(
        "Is it powered by an engine?",
        2,
        5,
        std::nullopt
    );

    tree.addNode(
        "Is it intended mainly for passengers?",
        3,
        4,
        std::nullopt
    );

    tree.addNode(
        "",
        std::nullopt,
        std::nullopt,
        "Car"
    );

    tree.addNode(
        "",
        std::nullopt,
        std::nullopt,
        "Utility vehicle"
    );

    tree.addNode(
        "",
        std::nullopt,
        std::nullopt,
        "Non-powered four-wheel vehicle"
    );

    tree.addNode(
        "Does it have two wheels?",
        7,
        8,
        std::nullopt
    );

    tree.addNode(
        "",
        std::nullopt,
        std::nullopt,
        "Two-wheel vehicle"
    );

    tree.addNode(
        "",
        std::nullopt,
        std::nullopt,
        "Other vehicle"
    );

    tree.setRoot(0);

    return tree;
}

// ---------------------------------------------------------------------------
// Demonstration
// ---------------------------------------------------------------------------

void demonstrateFundamentals() {
    std::cout << "\n=== FUNDAMENTALS ===\n";

    int age = 20;

    if (age >= 18) {
        std::cout << "Adult\n";
    } else {
        std::cout << "Minor\n";
    }

    const int score = 82;
    std::string grade;

    if (score >= 90) {
        grade = "A";
    } else if (score >= 80) {
        grade = "B";
    } else if (score >= 70) {
        grade = "C";
    } else {
        grade = "F";
    }

    std::cout << "Grade: " << grade << '\n';

    bool hasId = true;
    bool active = true;

    if (age >= 18 && hasId && active) {
        std::cout << "Compound condition passed\n";
    }
}

void demonstrateNestedConditions() {
    std::cout << "\n=== NESTED CONDITIONS ===\n";

    const std::vector<std::pair<int, bool>> cases = {
        {25, true},
        {25, false},
        {17, true},
        {17, false}
    };

    for (const auto& [age, hasId] : cases) {
        std::cout
            << "age=" << age
            << ", hasId=" << std::boolalpha << hasId
            << " -> "
            << classifyAccess(age, hasId)
            << '\n';
    }

    std::cout << "\nDeep decision examples:\n";

    struct ExamCase {
        double score;
        double attendance;
        bool misconduct;
    };

    const std::vector<ExamCase> exams = {
        {92, 95, false},
        {62, 80, false},
        {32, 90, false},
        {88, 90, true},
        {75, 60, false},
        {105, 90, false}
    };

    for (const ExamCase& exam : exams) {
        std::cout
            << "score=" << exam.score
            << ", attendance=" << exam.attendance
            << ", misconduct=" << std::boolalpha << exam.misconduct
            << " -> "
            << classifyExamResult(
                exam.score,
                exam.attendance,
                exam.misconduct
            )
            << '\n';
    }
}

void demonstrateCollections() {
    std::cout << "\n=== COLLECTIONS ===\n";

    std::vector<User> users = {
        {
            "alice",
            true,
            {"read", "write"}
        },
        {
            "bob",
            false,
            {"read"}
        }
    };

    for (const std::string& username : {"alice", "bob", "charlie"}) {
        std::cout
            << username
            << " -> "
            << findUserPermission(
                users,
                username,
                "write"
            )
            << '\n';
    }
}

void demonstrateDecisionTree() {
    std::cout << "\n=== DECISION TREE ===\n";

    const DecisionTree tree = buildVehicleDecisionTree();

    std::cout
        << "Four wheels -> powered -> passenger: "
        << tree.evaluate({true, true, true})
        << '\n';

    std::cout
        << "Four wheels -> powered -> utility: "
        << tree.evaluate({true, true, false})
        << '\n';

    std::cout
        << "Not four wheels -> two wheels: "
        << tree.evaluate({false, true})
        << '\n';

    std::cout
        << "Not four wheels -> not two wheels: "
        << tree.evaluate({false, false})
        << '\n';

    std::cout
        << "Missing answer: "
        << tree.evaluate({true})
        << '\n';
}

void demonstrateLoanSystem() {
    std::cout << "\n=== LOAN CASE STUDY ===\n";

    const std::vector<LoanApplication> applications = {
        {
            "Asha",
            30,
            100000.0,
            20000.0,
            780,
            5.0,
            true,
            500000.0,
            EmploymentType::Salaried
        },
        {
            "Bharat",
            28,
            80000.0,
            30000.0,
            680,
            4.0,
            true,
            300000.0,
            EmploymentType::Salaried
        },
        {
            "Chirag",
            22,
            50000.0,
            20000.0,
            620,
            1.0,
            true,
            200000.0,
            EmploymentType::SelfEmployed
        },
        {
            "Divya",
            35,
            90000.0,
            10000.0,
            760,
            7.0,
            false,
            400000.0,
            EmploymentType::Salaried
        },
        {
            "Invalid",
            17,
            50000.0,
            10000.0,
            760,
            5.0,
            true,
            200000.0,
            EmploymentType::Salaried
        }
    };

    LoanDecisionEngine engine;

    for (const LoanApplication& application : applications) {
        const DecisionResult result = engine.evaluate(application);

        const double dti =
            application.monthlyIncome > 0.0
                ? application.monthlyDebt / application.monthlyIncome
                : std::numeric_limits<double>::infinity();

        std::cout
            << std::fixed
            << std::setprecision(2)
            << application.applicantName
            << " | DTI=" << dti
            << " | "
            << decisionStatusToString(result.status)
            << " | "
            << result.reason
            << '\n';
    }
}

void demonstrateInteractiveInput() {
    std::cout << "\n=== OPTIONAL INTERACTIVE EXAMPLE ===\n";

    std::cout
        << "Enter an age to see a nested classification.\n"
        << "Enter -1 to skip.\n";

    const int age = readInteger("Age: ");

    if (age == -1) {
        std::cout << "Interactive example skipped.\n";
        return;
    }

    if (age < 0 || age > 150) {
        std::cout << "Invalid age.\n";
        return;
    }

    if (age < 13) {
        std::cout << "Child\n";
    } else {
        if (age < 18) {
            std::cout << "Teenager\n";
        } else {
            if (age < 65) {
                std::cout << "Adult\n";
            } else {
                std::cout << "Senior adult\n";
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main() {
    try {
        std::cout
            << "============================================================\n"
            << "NESTED CONDITIONS: C++ TECHNICAL CASE STUDY\n"
            << "============================================================\n";

        demonstrateFundamentals();
        demonstrateNestedConditions();

        std::cout << "\n=== GUARD CLAUSES ===\n";

        for (double purchaseAmount : {0.0, 3000.0, 5000.0, 7000.0, 12000.0}) {
            std::cout
                << "Purchase=" << purchaseAmount
                << " -> discount="
                << calculateDiscount(true, 30, purchaseAmount) * 100.0
                << "%\n";
        }

        demonstrateCollections();
        demonstrateDecisionTree();
        demonstrateLoanSystem();

        std::cout << "\n=== TESTS ===\n";
        runTests();

        std::cout
            << "\nNested conditions have been demonstrated from simple "
            << "branches to a data-driven decision tree and a complete "
            << "validation and decision engine.\n";

        /*
         * The interactive function is intentionally not called by default.
         * The rest of the program is deterministic and suitable for automated
         * execution. To interact manually, call demonstrateInteractiveInput()
         * from main.
         */

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "Program error: "
            << error.what()
            << '\n';

        return 1;
    }
}
