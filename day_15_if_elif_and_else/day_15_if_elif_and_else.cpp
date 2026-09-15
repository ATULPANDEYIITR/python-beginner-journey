/*
 * C++17 case study: conditional decision-making with if, else if, and else.
 *
 * Scenario:
 * A financial order-processing service evaluates customer orders before
 * approving, reviewing, or rejecting them.
 *
 * The program progressively demonstrates:
 * - basic conditional decisions
 * - validation
 * - Boolean expressions
 * - nested conditions
 * - guard clauses
 * - classes and structs
 * - rule evaluation
 * - authorization
 * - order prioritization
 * - edge cases
 * - complexity considerations
 * - lightweight testing
 *
 * Compile:
 *     g++ -std=c++17 -Wall -Wextra -pedantic -O2 main.cpp -o decision_engine
 *
 * Run:
 *     ./decision_engine
 */

#include <algorithm>
#include <cassert>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

// =============================================================================
// 1. BASIC CONDITIONAL EXAMPLES
// =============================================================================

void printSection(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

void basicIfExample() {
    printSection("1. Basic if statement");

    int age = 20;

    // The body executes only when the expression evaluates to true.
    if (age >= 18) {
        cout << "The person is an adult.\n";
    }
}

void ifElseExample() {
    printSection("2. if and else");

    int age = 16;

    if (age >= 18) {
        cout << "Adult\n";
    } else {
        cout << "Minor\n";
    }
}

void ifElseIfElseExample() {
    printSection("3. if, else if, and else");

    int marks = 76;
    string grade;

    // Conditions are evaluated from top to bottom.
    // The first matching branch is executed.
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

    cout << "Grade: " << grade << "\n";
}

// =============================================================================
// 2. BOOLEAN CONDITIONS
// =============================================================================

void booleanExample() {
    printSection("4. Boolean conditions");

    int age = 25;
    bool hasId = true;

    // && means logical AND.
    if (age >= 18 && hasId) {
        cout << "Entry permitted.\n";
    }

    int temperature = 39;
    bool raining = false;

    // || means logical OR.
    if (temperature > 40 || raining) {
        cout << "Carry appropriate protection.\n";
    }

    bool accountLocked = false;

    // ! means logical NOT.
    if (!accountLocked) {
        cout << "Account is available.\n";
    }
}

// =============================================================================
// 3. FUNCTIONS AND VALIDATION
// =============================================================================

string classifyTemperature(double celsius) {
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

string gradeMarks(double marks) {
    if (marks < 0.0 || marks > 100.0) {
        throw invalid_argument("Marks must be between 0 and 100.");
    }

    if (marks >= 90.0) {
        return "A+";
    } else if (marks >= 80.0) {
        return "A";
    } else if (marks >= 70.0) {
        return "B";
    } else if (marks >= 60.0) {
        return "C";
    } else if (marks >= 50.0) {
        return "D";
    } else {
        return "F";
    }
}

void validationExample() {
    printSection("5. Validation and boundary conditions");

    vector<double> values{
        0.0, 49.99, 50.0, 59.99, 60.0,
        69.99, 70.0, 79.99, 80.0, 89.99, 90.0, 100.0
    };

    for (double marks : values) {
        cout << fixed << setprecision(2)
             << marks << " -> " << gradeMarks(marks) << "\n";
    }

    for (double invalidMarks : {-1.0, 101.0}) {
        try {
            cout << gradeMarks(invalidMarks) << "\n";
        } catch (const invalid_argument& error) {
            cout << "Rejected: " << error.what() << "\n";
        }
    }
}

// =============================================================================
// 4. GUARD CLAUSES
// =============================================================================

bool canEnterEvent(int age, bool hasTicket, bool isBanned) {
    // Guard clauses reject failure conditions immediately.
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

void guardClauseExample() {
    printSection("6. Guard clauses");

    cout << boolalpha;
    cout << "25, ticket, not banned -> "
         << canEnterEvent(25, true, false) << "\n";

    cout << "16, ticket, not banned -> "
         << canEnterEvent(16, true, false) << "\n";
}

// =============================================================================
// 5. ORDER PROCESSING DOMAIN MODEL
// =============================================================================

enum class CustomerType {
    Regular,
    Premium,
    Enterprise,
    Unknown
};

string customerTypeToString(CustomerType type) {
    if (type == CustomerType::Regular) {
        return "regular";
    } else if (type == CustomerType::Premium) {
        return "premium";
    } else if (type == CustomerType::Enterprise) {
        return "enterprise";
    } else {
        return "unknown";
    }
}

struct Order {
    int id;
    CustomerType customerType;
    double amount;
    string country;
    bool verified;
};

enum class DecisionStatus {
    Approved,
    Review,
    Rejected
};

struct Decision {
    DecisionStatus status;
    string reason;
    int priority;
};

string decisionStatusToString(DecisionStatus status) {
    if (status == DecisionStatus::Approved) {
        return "APPROVED";
    } else if (status == DecisionStatus::Review) {
        return "REVIEW";
    } else {
        return "REJECTED";
    }
}

// =============================================================================
// 6. ORDER VALIDATION
// =============================================================================

optional<string> validateOrder(const Order& order) {
    if (order.id <= 0) {
        return "order ID must be positive";
    }

    if (order.amount <= 0.0) {
        return "amount must be positive";
    }

    if (order.country.empty()) {
        return "country is required";
    }

    return nullopt;
}

// =============================================================================
// 7. COUNTRY VALIDATION
// =============================================================================

bool isSupportedCountry(const string& country) {
    // A set provides efficient average-case lookup and expresses the
    // membership rule more directly than a long if/else chain.
    static const set<string> supportedCountries{
        "IN", "US", "GB", "SG"
    };

    return supportedCountries.find(country) != supportedCountries.end();
}

// =============================================================================
// 8. ORDER DECISION ENGINE
// =============================================================================

Decision evaluateOrder(const Order& order) {
    // Step 1: validate the order before making business decisions.
    if (auto validationError = validateOrder(order)) {
        return {
            DecisionStatus::Rejected,
            *validationError,
            0
        };
    }

    // Step 2: reject unsupported geographic regions.
    if (!isSupportedCountry(order.country)) {
        return {
            DecisionStatus::Rejected,
            "unsupported country",
            0
        };
    }

    // Step 3: high-value transactions require verification.
    if (order.amount >= 500000.0 && !order.verified) {
        return {
            DecisionStatus::Rejected,
            "verification required for high-value order",
            0
        };
    }

    // Step 4: classify enterprise customers.
    if (order.customerType == CustomerType::Enterprise) {
        if (order.amount >= 100000.0) {
            return {
                DecisionStatus::Approved,
                "enterprise high priority",
                3
            };
        } else if (order.amount >= 10000.0) {
            return {
                DecisionStatus::Approved,
                "enterprise priority",
                2
            };
        } else {
            return {
                DecisionStatus::Approved,
                "enterprise standard",
                1
            };
        }
    }

    // Step 5: classify premium customers.
    if (order.customerType == CustomerType::Premium) {
        if (order.amount >= 100000.0) {
            return {
                DecisionStatus::Approved,
                "premium high priority",
                3
            };
        } else {
            return {
                DecisionStatus::Approved,
                "premium standard",
                1
            };
        }
    }

    // Step 6: classify regular customers.
    if (order.customerType == CustomerType::Regular) {
        if (order.amount >= 100000.0) {
            return {
                DecisionStatus::Review,
                "large regular order requires manual review",
                2
            };
        } else {
            return {
                DecisionStatus::Approved,
                "regular standard",
                1
            };
        }
    }

    // Unknown classifications fail closed.
    return {
        DecisionStatus::Rejected,
        "unknown customer type",
        0
    };
}

// =============================================================================
// 9. ORDER REPORTING
// =============================================================================

void printOrderDecision(const Order& order, const Decision& decision) {
    cout << "Order #" << order.id
         << " | customer=" << customerTypeToString(order.customerType)
         << " | amount=" << fixed << setprecision(2) << order.amount
         << " | country=" << order.country
         << " | verified=" << boolalpha << order.verified
         << " -> "
         << decisionStatusToString(decision.status)
         << " | " << decision.reason
         << " | priority=" << decision.priority
         << "\n";
}

// =============================================================================
// 10. AUTHORIZATION SYSTEM
// =============================================================================

enum class Role {
    User,
    Owner,
    Admin,
    Unknown
};

struct AccessRequest {
    bool authenticated;
    Role role;
    bool resourceOwner;
    bool resourcePublic;
};

bool authorize(const AccessRequest& request) {
    // Authentication must be established first.
    if (!request.authenticated) {
        return false;
    }

    // Public resources can be accessed by authenticated users.
    if (request.resourcePublic) {
        return true;
    }

    // Administrators have access to protected resources.
    if (request.role == Role::Admin) {
        return true;
    }

    // Owners may access resources they own.
    if (request.role == Role::Owner && request.resourceOwner) {
        return true;
    }

    // Default deny is safer than default allow.
    return false;
}

void authorizationExample() {
    printSection("7. Authorization decisions");

    vector<AccessRequest> requests{
        {false, Role::Admin, false, false},
        {true, Role::User, false, true},
        {true, Role::Admin, false, false},
        {true, Role::Owner, true, false},
        {true, Role::Owner, false, false},
        {true, Role::Unknown, true, false}
    };

    for (const auto& request : requests) {
        cout << "authenticated=" << request.authenticated
             << ", public=" << request.resourcePublic
             << ", owner=" << request.resourceOwner
             << " -> allowed=" << authorize(request)
             << "\n";
    }
}

// =============================================================================
// 11. INTERACTIVE INPUT
// =============================================================================

optional<int> parseInteger(const string& text) {
    if (text.empty()) {
        return nullopt;
    }

    size_t position = 0;

    try {
        int value = stoi(text, &position);

        // If not all characters were consumed, input was not a pure integer.
        if (position != text.size()) {
            return nullopt;
        }

        return value;
    } catch (const exception&) {
        return nullopt;
    }
}

void inputProcessingExample() {
    printSection("8. Safe input processing");

    vector<string> inputs{
        "42",
        "0",
        "-10",
        "abc",
        "42abc",
        ""
    };

    for (const string& input : inputs) {
        auto parsed = parseInteger(input);

        if (!parsed.has_value()) {
            cout << "'" << input << "' -> invalid integer\n";
        } else if (*parsed > 0) {
            cout << "'" << input << "' -> positive integer: "
                 << *parsed << "\n";
        } else if (*parsed < 0) {
            cout << "'" << input << "' -> negative integer: "
                 << *parsed << "\n";
        } else {
            cout << "'" << input << "' -> zero\n";
        }
    }
}

// =============================================================================
// 12. PERFORMANCE-RELATED CONDITIONAL LOGIC
// =============================================================================

bool linearSearch(const vector<int>& values, int target) {
    for (int value : values) {
        if (value == target) {
            return true;
        }
    }

    return false;
}

void performanceExample() {
    printSection("9. Performance considerations");

    vector<int> values;
    values.reserve(100000);

    for (int i = 0; i < 100000; ++i) {
        values.push_back(i);
    }

    cout << "Linear search result: "
         << linearSearch(values, 99999) << "\n";

    // The if condition itself is normally inexpensive.
    // Performance depends more heavily on:
    // - how many times the condition is evaluated
    // - expensive functions called inside conditions
    // - data structures used for membership checks
    // - branch predictability in very performance-sensitive code
    //
    // Linear search is O(n).
}

// =============================================================================
// 13. BUSINESS REPORTING
// =============================================================================

struct OrderStatistics {
    int approved = 0;
    int review = 0;
    int rejected = 0;
    double approvedValue = 0.0;
};

OrderStatistics calculateStatistics(const vector<Order>& orders) {
    OrderStatistics statistics;

    for (const auto& order : orders) {
        Decision decision = evaluateOrder(order);

        if (decision.status == DecisionStatus::Approved) {
            ++statistics.approved;
            statistics.approvedValue += order.amount;
        } else if (decision.status == DecisionStatus::Review) {
            ++statistics.review;
        } else {
            ++statistics.rejected;
        }
    }

    return statistics;
}

void reportingExample(const vector<Order>& orders) {
    printSection("10. Processing multiple orders");

    OrderStatistics statistics = calculateStatistics(orders);

    cout << "Approved: " << statistics.approved << "\n";
    cout << "Review: " << statistics.review << "\n";
    cout << "Rejected: " << statistics.rejected << "\n";
    cout << "Approved value: "
         << fixed << setprecision(2)
         << statistics.approvedValue << "\n";
}

// =============================================================================
// 14. LIGHTWEIGHT TESTING
// =============================================================================

void runTests() {
    printSection("11. Executable tests");

    assert(gradeMarks(100.0) == "A+");
    assert(gradeMarks(90.0) == "A+");
    assert(gradeMarks(89.99) == "A");
    assert(gradeMarks(80.0) == "A");
    assert(gradeMarks(79.99) == "B");
    assert(gradeMarks(70.0) == "B");
    assert(gradeMarks(60.0) == "C");
    assert(gradeMarks(50.0) == "D");
    assert(gradeMarks(49.99) == "F");

    bool rejectedInvalidMarks = false;

    try {
        gradeMarks(101.0);
    } catch (const invalid_argument&) {
        rejectedInvalidMarks = true;
    }

    assert(rejectedInvalidMarks);

    assert(canEnterEvent(25, true, false));
    assert(!canEnterEvent(16, true, false));
    assert(!canEnterEvent(25, false, false));
    assert(!canEnterEvent(25, true, true));

    assert(authorize({
        true,
        Role::Admin,
        false,
        false
    }));

    assert(!authorize({
        false,
        Role::Admin,
        false,
        false
    }));

    cout << "All tests passed.\n";
}

// =============================================================================
// 15. MAIN CASE STUDY
// =============================================================================

int main() {
    basicIfExample();
    ifElseExample();
    ifElseIfElseExample();
    booleanExample();
    validationExample();
    guardClauseExample();
    authorizationExample();
    inputProcessingExample();
    performanceExample();

    vector<Order> orders{
        {1001, CustomerType::Enterprise, 250000.0, "IN", true},
        {1002, CustomerType::Premium, 15000.0, "US", true},
        {1003, CustomerType::Regular, 8000.0, "GB", true},
        {1004, CustomerType::Regular, 600000.0, "IN", false},
        {1005, CustomerType::Regular, 1000.0, "XX", true},
        {1006, CustomerType::Unknown, 1000.0, "IN", true},
        {1007, CustomerType::Regular, -50.0, "IN", true}
    };

    printSection("12. Industry-style order decision engine");

    for (const auto& order : orders) {
        Decision decision = evaluateOrder(order);
        printOrderDecision(order, decision);
    }

    reportingExample(orders);
    runTests();

    printSection("13. Case study completed");

    cout << "The system used if, else if, and else to implement ordered "
         << "business rules, validation, authorization, classification, "
         << "error handling, and reporting.\n";

    return 0;
}
