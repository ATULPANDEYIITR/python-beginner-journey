#include <algorithm>
#include <chrono>
#include <cstddef>
#include <functional>
#include <iomanip>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

/*
    C++17 CASE STUDY: ACCESS CONTROL AND FEATURE-COMPATIBILITY ENGINE

    This program demonstrates set-oriented thinking in an industry-style
    authorization and capability-management system.

    The implementation progresses from basic unordered_set usage to:
      - uniqueness
      - membership
      - insertion and deletion
      - set union/intersection/difference
      - subset testing
      - data validation
      - user permissions
      - feature compatibility
      - audit reporting
      - duplicate detection
      - performance measurement
      - edge cases
      - modular class design

    Compile:
        g++ -std=c++17 -O2 sets_case_study.cpp -o sets_case_study

    The C++ standard library's unordered_set is used because it provides
    average constant-time lookup and is a natural implementation for
    membership-oriented sets.
*/

using StringSet = std::unordered_set<std::string>;


// ============================================================================
// 1. OUTPUT UTILITIES
// ============================================================================

void printSection(const std::string& title) {
    std::cout << "\n" << std::string(78, '=') << "\n";
    std::cout << title << "\n";
    std::cout << std::string(78, '=') << "\n";
}

void printSet(const StringSet& values, const std::string& label) {
    std::vector<std::string> sortedValues(values.begin(), values.end());
    std::sort(sortedValues.begin(), sortedValues.end());

    std::cout << label << " {";

    bool first = true;
    for (const auto& value : sortedValues) {
        if (!first) {
            std::cout << ", ";
        }

        std::cout << value;
        first = false;
    }

    std::cout << "}\n";
}


// ============================================================================
// 2. BASIC SET OPERATIONS
// ============================================================================

StringSet setUnion(
    const StringSet& first,
    const StringSet& second
) {
    StringSet result = first;

    result.insert(second.begin(), second.end());

    return result;
}

StringSet setIntersection(
    const StringSet& first,
    const StringSet& second
) {
    const StringSet* smaller = &first;
    const StringSet* larger = &second;

    if (first.size() > second.size()) {
        smaller = &second;
        larger = &first;
    }

    StringSet result;

    for (const auto& value : *smaller) {
        if (larger->find(value) != larger->end()) {
            result.insert(value);
        }
    }

    return result;
}

StringSet setDifference(
    const StringSet& first,
    const StringSet& second
) {
    StringSet result;

    for (const auto& value : first) {
        if (second.find(value) == second.end()) {
            result.insert(value);
        }
    }

    return result;
}

StringSet symmetricDifference(
    const StringSet& first,
    const StringSet& second
) {
    StringSet result = setDifference(first, second);

    StringSet secondOnly = setDifference(second, first);

    result.insert(secondOnly.begin(), secondOnly.end());

    return result;
}

bool isSubset(
    const StringSet& subset,
    const StringSet& superset
) {
    if (subset.size() > superset.size()) {
        return false;
    }

    for (const auto& value : subset) {
        if (superset.find(value) == superset.end()) {
            return false;
        }
    }

    return true;
}

bool isDisjoint(
    const StringSet& first,
    const StringSet& second
) {
    const StringSet* smaller = &first;
    const StringSet* larger = &second;

    if (first.size() > second.size()) {
        smaller = &second;
        larger = &first;
    }

    for (const auto& value : *smaller) {
        if (larger->find(value) != larger->end()) {
            return false;
        }
    }

    return true;
}


// ============================================================================
// 3. USER MODEL
// ============================================================================

struct User {
    int id;
    std::string username;
    StringSet permissions;
    StringSet features;
};


// ============================================================================
// 4. AUTHORIZATION ENGINE
// ============================================================================

class AuthorizationEngine {
private:
    std::unordered_map<int, User> users;

public:
    void addUser(const User& user) {
        if (user.id <= 0) {
            throw std::invalid_argument("User ID must be positive.");
        }

        if (users.find(user.id) != users.end()) {
            throw std::invalid_argument("Duplicate user ID.");
        }

        users.emplace(user.id, user);
    }

    const User& getUser(int userId) const {
        auto iterator = users.find(userId);

        if (iterator == users.end()) {
            throw std::out_of_range("User does not exist.");
        }

        return iterator->second;
    }

    bool hasPermission(
        int userId,
        const std::string& permission
    ) const {
        const User& user = getUser(userId);

        return user.permissions.find(permission)
            != user.permissions.end();
    }

    bool hasAllPermissions(
        int userId,
        const StringSet& required
    ) const {
        const User& user = getUser(userId);

        return isSubset(required, user.permissions);
    }

    StringSet missingPermissions(
        int userId,
        const StringSet& required
    ) const {
        const User& user = getUser(userId);

        return setDifference(required, user.permissions);
    }

    StringSet commonFeatures(
        int firstUserId,
        int secondUserId
    ) const {
        const User& first = getUser(firstUserId);
        const User& second = getUser(secondUserId);

        return setIntersection(first.features, second.features);
    }

    void printUser(int userId) const {
        const User& user = getUser(userId);

        std::cout << "User " << user.id
                  << " (" << user.username << ")\n";

        printSet(user.permissions, "  Permissions");
        printSet(user.features, "  Features");
    }
};


// ============================================================================
// 5. FEATURE COMPATIBILITY
// ============================================================================

struct CompatibilityReport {
    bool compatible;
    StringSet missing;
    StringSet unused;
};

CompatibilityReport evaluateCompatibility(
    const StringSet& requested,
    const StringSet& supported
) {
    StringSet missing = setDifference(requested, supported);
    StringSet unused = setDifference(supported, requested);

    return {
        missing.empty(),
        std::move(missing),
        std::move(unused)
    };
}


// ============================================================================
// 6. DUPLICATE DETECTION
// ============================================================================

std::unordered_set<int> findDuplicates(
    const std::vector<int>& values
) {
    std::unordered_set<int> seen;
    std::unordered_set<int> duplicates;

    for (int value : values) {
        auto [iterator, inserted] = seen.insert(value);

        if (!inserted) {
            duplicates.insert(value);
        }
    }

    return duplicates;
}


// ============================================================================
// 7. REQUIRED-FIELD VALIDATION
// ============================================================================

using Record = std::unordered_map<std::string, std::string>;

std::vector<std::pair<std::size_t, StringSet>> validateRecords(
    const std::vector<Record>& records,
    const StringSet& requiredFields
) {
    std::vector<std::pair<std::size_t, StringSet>> failures;

    for (std::size_t index = 0; index < records.size(); ++index) {
        StringSet presentFields;

        for (const auto& [field, value] : records[index]) {
            static_cast<void>(value);
            presentFields.insert(field);
        }

        StringSet missing = setDifference(
            requiredFields,
            presentFields
        );

        if (!missing.empty()) {
            failures.emplace_back(index, std::move(missing));
        }
    }

    return failures;
}


// ============================================================================
// 8. AUDIT REPORT
// ============================================================================

class AuditReporter {
public:
    static void printAuthorizationResult(
        const AuthorizationEngine& engine,
        int userId,
        const StringSet& requiredPermissions
    ) {
        std::cout << "\nAuthorization request for user "
                  << userId << "\n";

        try {
            if (engine.hasAllPermissions(
                    userId,
                    requiredPermissions)) {
                std::cout << "  Result: GRANTED\n";
            } else {
                std::cout << "  Result: DENIED\n";

                StringSet missing =
                    engine.missingPermissions(
                        userId,
                        requiredPermissions
                    );

                printSet(missing, "  Missing");
            }
        } catch (const std::exception& error) {
            std::cout << "  Error: "
                      << error.what()
                      << "\n";
        }
    }
};


// ============================================================================
// 9. PERFORMANCE CASE STUDY
// ============================================================================

void performanceStudy() {
    printSection("9. PERFORMANCE STUDY");

    constexpr std::size_t elementCount = 500000;

    std::vector<int> values;
    values.reserve(elementCount);

    for (std::size_t i = 0; i < elementCount; ++i) {
        values.push_back(static_cast<int>(i));
    }

    std::unordered_set<int> valueSet(
        values.begin(),
        values.end()
    );

    const int target = static_cast<int>(elementCount - 1);

    auto vectorStart = std::chrono::high_resolution_clock::now();

    bool vectorFound =
        std::find(
            values.begin(),
            values.end(),
            target
        ) != values.end();

    auto vectorEnd = std::chrono::high_resolution_clock::now();

    auto setStart = std::chrono::high_resolution_clock::now();

    bool setFound =
        valueSet.find(target)
        != valueSet.end();

    auto setEnd = std::chrono::high_resolution_clock::now();

    const auto vectorDuration =
        std::chrono::duration<double, std::micro>(
            vectorEnd - vectorStart
        ).count();

    const auto setDuration =
        std::chrono::duration<double, std::micro>(
            setEnd - setStart
        ).count();

    std::cout << std::boolalpha;
    std::cout << "Vector found target: " << vectorFound << "\n";
    std::cout << "Set found target:    " << setFound << "\n";
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Vector search: "
              << vectorDuration
              << " microseconds\n";

    std::cout << "Set lookup:    "
              << setDuration
              << " microseconds\n";

    std::cout
        << "unordered_set provides average O(1) lookup, "
        << "while linear vector search is O(n).\n";

    std::cout
        << "The measured times are environment-dependent and "
        << "must not be treated as universal benchmarks.\n";
}


// ============================================================================
// 10. HASH-TABLE TRADE-OFFS
// ============================================================================

void hashTableTradeoffs() {
    printSection("10. HASH-TABLE TRADE-OFFS");

    std::unordered_set<std::string> permissions = {
        "read",
        "write",
        "download",
        "audit"
    };

    std::cout
        << "Element count: "
        << permissions.size()
        << "\n";

    std::cout
        << "Bucket count: "
        << permissions.bucket_count()
        << "\n";

    std::cout
        << "Load factor: "
        << permissions.load_factor()
        << "\n";

    std::cout
        << "Max load factor: "
        << permissions.max_load_factor()
        << "\n";

    std::cout
        << "Hash tables consume extra memory to obtain fast average "
        << "membership operations.\n";
}


// ============================================================================
// 11. EXCEPTION AND EDGE CASE HANDLING
// ============================================================================

void edgeCases(const AuthorizationEngine& engine) {
    printSection("11. EDGE CASES AND FAILURE CONDITIONS");

    try {
        static_cast<void>(engine.getUser(9999));
    } catch (const std::out_of_range& error) {
        std::cout
            << "Unknown user handled: "
            << error.what()
            << "\n";
    }

    StringSet empty;

    std::cout
        << "Empty set is subset of empty set: "
        << std::boolalpha
        << isSubset(empty, empty)
        << "\n";

    StringSet values = {"read", "write"};

    std::cout
        << "Set is subset of itself: "
        << isSubset(values, values)
        << "\n";

    std::cout
        << "Disjoint with {delete}: "
        << isDisjoint(values, {"delete"})
        << "\n";
}


// ============================================================================
// 12. COMPLETE BUSINESS SCENARIO
// ============================================================================

void runAuthorizationScenario() {
    printSection(
        "12. INDUSTRY-STYLE CASE STUDY: ACCESS CONTROL"
    );

    AuthorizationEngine engine;

    engine.addUser({
        1,
        "alice",
        {"read", "write", "download"},
        {"analytics", "reporting", "export"}
    });

    engine.addUser({
        2,
        "bob",
        {"read", "download"},
        {"analytics", "reporting"}
    });

    engine.addUser({
        3,
        "carol",
        {"read"},
        {"reporting", "audit"}
    });

    engine.printUser(1);
    engine.printUser(2);
    engine.printUser(3);

    StringSet reportingPermissions = {
        "read",
        "download"
    };

    StringSet administrationPermissions = {
        "read",
        "write",
        "delete"
    };

    AuditReporter::printAuthorizationResult(
        engine,
        1,
        reportingPermissions
    );

    AuditReporter::printAuthorizationResult(
        engine,
        2,
        administrationPermissions
    );

    AuditReporter::printAuthorizationResult(
        engine,
        9999,
        reportingPermissions
    );

    StringSet common =
        engine.commonFeatures(1, 2);

    printSet(
        common,
        "Common features of Alice and Bob"
    );

    StringSet requestedFeatures = {
        "analytics",
        "reporting",
        "export"
    };

    StringSet platformFeatures = {
        "analytics",
        "reporting",
        "audit",
        "monitoring"
    };

    CompatibilityReport report =
        evaluateCompatibility(
            requestedFeatures,
            platformFeatures
        );

    std::cout
        << "\nPlatform compatibility: "
        << report.compatible
        << "\n";

    printSet(report.missing, "Missing features");
    printSet(report.unused, "Unused platform features");
}


// ============================================================================
// 13. DATA QUALITY SCENARIO
// ============================================================================

void runDataQualityScenario() {
    printSection("13. DATA QUALITY WITH SET DIFFERENCE");

    std::vector<Record> records = {
        {
            {"id", "1001"},
            {"name", "Alice"},
            {"email", "alice@example.com"}
        },
        {
            {"id", "1002"},
            {"name", "Bob"}
        },
        {
            {"id", "1003"},
            {"email", "carol@example.com"}
        }
    };

    StringSet required = {
        "id",
        "name",
        "email"
    };

    auto failures =
        validateRecords(records, required);

    for (const auto& [index, missing] : failures) {
        std::cout
            << "Record "
            << index
            << " has missing fields:\n";

        printSet(missing, "  Missing");
    }

    if (failures.empty()) {
        std::cout << "All records passed validation.\n";
    }
}


// ============================================================================
// 14. DUPLICATE DATA SCENARIO
// ============================================================================

void runDuplicateScenario() {
    printSection("14. DUPLICATE DETECTION");

    std::vector<int> transactionIds = {
        1001,
        1002,
        1003,
        1002,
        1004,
        1005,
        1001,
        1006
    };

    auto duplicates =
        findDuplicates(transactionIds);

    std::cout
        << "Duplicate transaction IDs: ";

    for (int value : duplicates) {
        std::cout << value << " ";
    }

    std::cout << "\n";
}


// ============================================================================
// 15. SET ALGEBRA DEMONSTRATION
// ============================================================================

void runSetAlgebraDemo() {
    printSection("15. SET ALGEBRA");

    StringSet first = {
        "read",
        "write",
        "download"
    };

    StringSet second = {
        "download",
        "delete",
        "audit"
    };

    printSet(first, "First");
    printSet(second, "Second");

    printSet(
        setUnion(first, second),
        "Union"
    );

    printSet(
        setIntersection(first, second),
        "Intersection"
    );

    printSet(
        setDifference(first, second),
        "First - Second"
    );

    printSet(
        setDifference(second, first),
        "Second - First"
    );

    printSet(
        symmetricDifference(first, second),
        "Symmetric difference"
    );

    std::cout
        << "First subset of union: "
        << isSubset(
            first,
            setUnion(first, second)
        )
        << "\n";
}


// ============================================================================
// 16. TEST SUITE
// ============================================================================

void runTests() {
    printSection("16. ASSERTION-BASED TESTS");

    StringSet a = {"A", "B", "C"};
    StringSet b = {"B", "C", "D"};

    StringSet unionResult = setUnion(a, b);
    StringSet intersectionResult = setIntersection(a, b);
    StringSet differenceResult = setDifference(a, b);
    StringSet symmetricResult =
        symmetricDifference(a, b);

    if (unionResult.size() != 4) {
        throw std::runtime_error("Union test failed.");
    }

    if (intersectionResult.size() != 2) {
        throw std::runtime_error("Intersection test failed.");
    }

    if (differenceResult != StringSet{"A"}) {
        throw std::runtime_error("Difference test failed.");
    }

    if (symmetricResult != StringSet{"A", "D"}) {
        throw std::runtime_error(
            "Symmetric difference test failed."
        );
    }

    if (!isSubset({"A", "B"}, a)) {
        throw std::runtime_error("Subset test failed.");
    }

    if (!isDisjoint({"A", "B"}, {"X", "Y"})) {
        throw std::runtime_error("Disjoint test failed.");
    }

    auto duplicates =
        findDuplicates({1, 2, 2, 3, 3});

    if (duplicates != std::unordered_set<int>{2, 3}) {
        throw std::runtime_error(
            "Duplicate detection test failed."
        );
    }

    std::cout << "All tests passed.\n";
}


// ============================================================================
// 17. DESIGN AND COMPLEXITY REFERENCE
// ============================================================================

void printComplexityReference() {
    printSection("17. COMPLEXITY REFERENCE");

    std::cout
        << "unordered_set lookup:       average O(1)\n"
        << "unordered_set insertion:    average O(1)\n"
        << "unordered_set deletion:     average O(1)\n"
        << "Union:                       O(n + m)\n"
        << "Intersection:               O(min(n, m)) average\n"
        << "Difference:                 O(n) average\n"
        << "Subset test:                O(n) average\n"
        << "Iteration:                  O(n)\n"
        << "Sorting a set for display:  O(n log n)\n"
        << "Vector linear search:       O(n)\n";

    std::cout
        << "\nWorst-case unordered_set operations can degrade because "
        << "of hash collisions. Hash quality and load factor matter.\n";
}


// ============================================================================
// 18. MAIN
// ============================================================================

int main() {
    try {
        runSetAlgebraDemo();
        runAuthorizationScenario();
        runDataQualityScenario();
        runDuplicateScenario();
        edgeCases(
            [] {
                AuthorizationEngine engine;

                engine.addUser({
                    1,
                    "temporary-user",
                    {"read"},
                    {"basic"}
                });

                return engine;
            }()
        );
        hashTableTradeoffs();
        performanceStudy();
        printComplexityReference();
        runTests();

        printSection("END OF C++ SET CASE STUDY");
        std::cout
            << "Program completed successfully.\n";

        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "Fatal error: "
            << error.what()
            << "\n";

        return 1;
    }
}
