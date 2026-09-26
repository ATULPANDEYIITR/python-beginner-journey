/*
 * SET OPERATIONS: C++ INDUSTRY-STYLE CASE STUDY
 * ===============================================
 *
 * Scenario:
 * Build a permission and resource reconciliation service for an enterprise
 * application. The system receives users, required permissions, resource
 * memberships, and external resource records. It uses set operations to:
 *
 *   - validate authorization
 *   - calculate missing and excessive permissions
 *   - reconcile database/API resource IDs
 *   - identify common resources
 *   - track visited resources during traversal
 *   - produce deterministic reports
 *
 * Standard: C++17 or later
 *
 * Example compilation:
 *   g++ -std=c++17 -O2 -Wall -Wextra -pedantic set_operations.cpp -o set_operations
 */

#include <algorithm>
#include <cassert>
#include <chrono>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <limits>
#include <map>
#include <queue>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using std::cout;
using std::endl;
using std::size_t;
using std::string;

// ============================================================================
// 1. GENERIC SET OPERATION UTILITIES
// ============================================================================

template <typename T>
std::set<T> setUnion(const std::set<T>& first, const std::set<T>& second) {
    std::set<T> result;
    std::set_union(
        first.begin(), first.end(),
        second.begin(), second.end(),
        std::inserter(result, result.begin())
    );
    return result;
}

template <typename T>
std::set<T> setIntersection(
    const std::set<T>& first,
    const std::set<T>& second
) {
    std::set<T> result;
    std::set_intersection(
        first.begin(), first.end(),
        second.begin(), second.end(),
        std::inserter(result, result.begin())
    );
    return result;
}

template <typename T>
std::set<T> setDifference(
    const std::set<T>& first,
    const std::set<T>& second
) {
    std::set<T> result;
    std::set_difference(
        first.begin(), first.end(),
        second.begin(), second.end(),
        std::inserter(result, result.begin())
    );
    return result;
}

template <typename T>
std::set<T> symmetricDifference(
    const std::set<T>& first,
    const std::set<T>& second
) {
    std::set<T> result;
    std::set_symmetric_difference(
        first.begin(), first.end(),
        second.begin(), second.end(),
        std::inserter(result, result.begin())
    );
    return result;
}

template <typename T>
bool isSubset(const std::set<T>& subset, const std::set<T>& superset) {
    return std::includes(
        superset.begin(), superset.end(),
        subset.begin(), subset.end()
    );
}

template <typename T>
bool isDisjoint(const std::set<T>& first, const std::set<T>& second) {
    auto firstIterator = first.begin();
    auto secondIterator = second.begin();

    while (firstIterator != first.end() && secondIterator != second.end()) {
        if (*firstIterator < *secondIterator) {
            ++firstIterator;
        } else if (*secondIterator < *firstIterator) {
            ++secondIterator;
        } else {
            return false;
        }
    }

    return true;
}

// ============================================================================
// 2. FORMATTING HELPERS
// ============================================================================

template <typename T>
void printSet(const std::string& label, const std::set<T>& values) {
    cout << label << "{";

    bool first = true;
    for (const auto& value : values) {
        if (!first) {
            cout << ", ";
        }
        cout << value;
        first = false;
    }

    cout << "}" << endl;
}

void printHeader(const string& title) {
    cout << "\n" << string(78, '=') << "\n";
    cout << title << "\n";
    cout << string(78, '=') << "\n";
}

// ============================================================================
// 3. DOMAIN MODEL
// ============================================================================

struct User {
    string id;
    string name;
    std::set<string> permissions;
    std::set<int> resourceIds;
};

struct AuthorizationReport {
    bool authorized;
    std::set<string> missingPermissions;
    std::set<string> extraPermissions;
    std::set<int> accessibleResources;
    std::set<int> unauthorizedRequestedResources;
};

// ============================================================================
// 4. AUTHORIZATION SERVICE
// ============================================================================

class AuthorizationService {
public:
    static AuthorizationReport evaluate(
        const User& user,
        const std::set<string>& requiredPermissions,
        const std::set<int>& requestedResources
    ) {
        AuthorizationReport report{};

        report.missingPermissions =
            setDifference(requiredPermissions, user.permissions);

        report.extraPermissions =
            setDifference(user.permissions, requiredPermissions);

        report.accessibleResources =
            setIntersection(user.resourceIds, requestedResources);

        report.unauthorizedRequestedResources =
            setDifference(requestedResources, user.resourceIds);

        report.authorized = report.missingPermissions.empty();

        return report;
    }
};

// ============================================================================
// 5. RESOURCE RECONCILIATION
// ============================================================================

struct ReconciliationReport {
    std::set<int> common;
    std::set<int> onlyDatabase;
    std::set<int> onlyExternalSystem;
    std::set<int> all;
    std::set<int> changedMembership;
};

ReconciliationReport reconcileResources(
    const std::set<int>& databaseResources,
    const std::set<int>& externalResources
) {
    ReconciliationReport report;

    report.common =
        setIntersection(databaseResources, externalResources);

    report.onlyDatabase =
        setDifference(databaseResources, externalResources);

    report.onlyExternalSystem =
        setDifference(externalResources, databaseResources);

    report.all =
        setUnion(databaseResources, externalResources);

    report.changedMembership =
        symmetricDifference(databaseResources, externalResources);

    return report;
}

// ============================================================================
// 6. GRAPH RESOURCE DEPENDENCIES
// ============================================================================

class ResourceGraph {
private:
    std::map<int, std::set<int>> adjacency;

public:
    void addResource(int resourceId) {
        adjacency.try_emplace(resourceId);
    }

    void addDependency(int from, int to) {
        adjacency[from].insert(to);
        adjacency[to].insert(from);
    }

    std::set<int> neighbors(int resourceId) const {
        auto iterator = adjacency.find(resourceId);

        if (iterator == adjacency.end()) {
            return {};
        }

        return iterator->second;
    }

    std::set<int> reachableFrom(int start) const {
        std::set<int> visited;
        std::queue<int> pending;

        if (!adjacency.contains(start)) {
            return visited;
        }

        pending.push(start);

        while (!pending.empty()) {
            const int current = pending.front();
            pending.pop();

            if (visited.contains(current)) {
                continue;
            }

            visited.insert(current);

            auto iterator = adjacency.find(current);
            if (iterator == adjacency.end()) {
                continue;
            }

            for (const int neighbor : iterator->second) {
                if (!visited.contains(neighbor)) {
                    pending.push(neighbor);
                }
            }
        }

        return visited;
    }
};

// ============================================================================
// 7. INPUT VALIDATION
// ============================================================================

void validateUser(const User& user) {
    if (user.id.empty()) {
        throw std::invalid_argument("User ID cannot be empty.");
    }

    if (user.name.empty()) {
        throw std::invalid_argument("User name cannot be empty.");
    }

    for (const string& permission : user.permissions) {
        if (permission.empty()) {
            throw std::invalid_argument("Permission names cannot be empty.");
        }
    }

    for (const int resourceId : user.resourceIds) {
        if (resourceId <= 0) {
            throw std::invalid_argument(
                "Resource IDs must be positive."
            );
        }
    }
}

// ============================================================================
// 8. REPORT GENERATION
// ============================================================================

void printAuthorizationReport(const AuthorizationReport& report) {
    cout << "Authorized: "
         << (report.authorized ? "YES" : "NO") << endl;

    printSet("Missing permissions: ", report.missingPermissions);
    printSet("Extra permissions: ", report.extraPermissions);
    printSet("Accessible resources: ", report.accessibleResources);
    printSet(
        "Unauthorized requested resources: ",
        report.unauthorizedRequestedResources
    );
}

void printReconciliationReport(const ReconciliationReport& report) {
    printSet("Common resources: ", report.common);
    printSet("Only database: ", report.onlyDatabase);
    printSet("Only external system: ", report.onlyExternalSystem);
    printSet("All resources: ", report.all);
    printSet("Changed membership: ", report.changedMembership);
}

// ============================================================================
// 9. AUDIT LOG WITH UNIQUE EVENT IDENTIFIERS
// ============================================================================

class AuditLog {
private:
    std::unordered_set<string> processedEventIds;

public:
    bool recordEvent(const string& eventId) {
        if (eventId.empty()) {
            throw std::invalid_argument("Event ID cannot be empty.");
        }

        // insert().second is true only when the ID was not already present.
        return processedEventIds.insert(eventId).second;
    }

    size_t size() const {
        return processedEventIds.size();
    }
};

// ============================================================================
// 10. PERFORMANCE COMPARISON
// ============================================================================

void performanceComparison() {
    printHeader("10. ORDERED SET VS HASH SET MEMBERSHIP");

    constexpr int count = 200000;

    std::set<int> orderedSet;
    std::unordered_set<int> hashSet;

    for (int value = 0; value < count; ++value) {
        orderedSet.insert(value);
        hashSet.insert(value);
    }

    const int target = count - 1;

    auto start = std::chrono::high_resolution_clock::now();
    volatile bool orderedFound = orderedSet.contains(target);
    auto orderedEnd = std::chrono::high_resolution_clock::now();

    auto hashStart = std::chrono::high_resolution_clock::now();
    volatile bool hashFound = hashSet.contains(target);
    auto hashEnd = std::chrono::high_resolution_clock::now();

    const auto orderedMicroseconds =
        std::chrono::duration_cast<std::chrono::microseconds>(
            orderedEnd - start
        ).count();

    const auto hashMicroseconds =
        std::chrono::duration_cast<std::chrono::microseconds>(
            hashEnd - hashStart
        ).count();

    cout << "Ordered set found: " << std::boolalpha
         << orderedFound << endl;
    cout << "Hash set found: " << std::boolalpha
         << hashFound << endl;

    cout << "std::set lookup time: "
         << orderedMicroseconds << " microseconds" << endl;

    cout << "std::unordered_set lookup time: "
         << hashMicroseconds << " microseconds" << endl;

    cout << "std::set provides ordered O(log n) lookup." << endl;
    cout << "std::unordered_set provides average O(1) lookup." << endl;
    cout << "Worst-case unordered lookup can degrade because of hash collisions."
         << endl;
}

// ============================================================================
// 11. CASE STUDY
// ============================================================================

void runCaseStudy() {
    printHeader("SET OPERATIONS CASE STUDY: ENTERPRISE ACCESS CONTROL");

    User user{
        "USR-1001",
        "Atul",
        {"read", "write", "analytics"},
        {101, 102, 103, 105}
    };

    validateUser(user);

    const std::set<string> requiredPermissions{
        "read",
        "write"
    };

    const std::set<int> requestedResources{
        101,
        102,
        104,
        105
    };

    cout << "\nUSER\n";
    cout << "ID: " << user.id << endl;
    cout << "Name: " << user.name << endl;
    printSet("Permissions: ", user.permissions);
    printSet("Owned resources: ", user.resourceIds);

    cout << "\nAUTHORIZATION\n";

    const AuthorizationReport authorization =
        AuthorizationService::evaluate(
            user,
            requiredPermissions,
            requestedResources
        );

    printAuthorizationReport(authorization);

    cout << "\nRESOURCE RECONCILIATION\n";

    const std::set<int> databaseResources{
        101, 102, 103, 104, 105
    };

    const std::set<int> externalResources{
        103, 104, 105, 106, 107
    };

    const ReconciliationReport reconciliation =
        reconcileResources(
            databaseResources,
            externalResources
        );

    printReconciliationReport(reconciliation);

    cout << "\nRESOURCE DEPENDENCY GRAPH\n";

    ResourceGraph graph;

    graph.addDependency(101, 102);
    graph.addDependency(101, 103);
    graph.addDependency(102, 104);
    graph.addDependency(103, 105);
    graph.addDependency(104, 106);

    printSet("Neighbors of 101: ", graph.neighbors(101));
    printSet("Reachable from 101: ", graph.reachableFrom(101));

    cout << "\nAUDIT EVENT DEDUPLICATION\n";

    AuditLog auditLog;

    cout << "event-1 accepted: "
         << std::boolalpha
         << auditLog.recordEvent("event-1")
         << endl;

    cout << "event-1 duplicate accepted: "
         << std::boolalpha
         << auditLog.recordEvent("event-1")
         << endl;

    cout << "event-2 accepted: "
         << std::boolalpha
         << auditLog.recordEvent("event-2")
         << endl;

    cout << "Unique audit events: "
         << auditLog.size() << endl;
}

// ============================================================================
// 12. EDGE-CASE TESTS
// ============================================================================

void runTests() {
    printHeader("12. SELF-TESTS");

    const std::set<int> A{1, 2, 3};
    const std::set<int> B{3, 4, 5};

    assert(setUnion(A, B) == std::set<int>({1, 2, 3, 4, 5}));
    assert(setIntersection(A, B) == std::set<int>({3}));
    assert(setDifference(A, B) == std::set<int>({1, 2}));
    assert(
        symmetricDifference(A, B) ==
        std::set<int>({1, 2, 4, 5})
    );

    assert(isSubset(std::set<int>{1, 2}, A));
    assert(!isSubset(B, A));
    assert(isDisjoint(A, std::set<int>{7, 8}));
    assert(!isDisjoint(A, std::set<int>{3, 8}));

    const std::set<int> empty;
    assert(setUnion(A, empty) == A);
    assert(setIntersection(A, empty).empty());
    assert(setDifference(A, empty) == A);
    assert(symmetricDifference(A, empty) == A);

    User validUser{
        "U1",
        "Test User",
        {"read"},
        {1}
    };

    validateUser(validUser);

    bool exceptionCaught = false;

    try {
        User invalidUser{
            "",
            "Invalid",
            {"read"},
            {1}
        };

        validateUser(invalidUser);
    } catch (const std::invalid_argument&) {
        exceptionCaught = true;
    }

    assert(exceptionCaught);

    ResourceGraph graph;
    graph.addDependency(1, 2);

    assert(graph.reachableFrom(1) == std::set<int>({1, 2}));
    assert(graph.reachableFrom(999).empty());

    AuditLog audit;

    assert(audit.recordEvent("A"));
    assert(!audit.recordEvent("A"));
    assert(audit.recordEvent("B"));
    assert(audit.size() == 2);

    cout << "All tests passed." << endl;
}

// ============================================================================
// 13. MAIN
// ============================================================================

int main() {
    try {
        cout << string(78, '=') << endl;
        cout << "SET OPERATIONS IN C++: INDUSTRY-STYLE CASE STUDY" << endl;
        cout << string(78, '=') << endl;

        runCaseStudy();
        performanceComparison();
        runTests();

        printHeader("END OF SET OPERATIONS CASE STUDY");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal error: " << error.what() << endl;
        return 1;
    }
}
