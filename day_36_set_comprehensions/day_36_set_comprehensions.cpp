#include <algorithm>
#include <chrono>
#include <cctype>
#include <iostream>
#include <set>
#include <string>
#include <unordered_set>
#include <vector>
#include <map>
#include <stdexcept>

using namespace std;

void heading(const string& title) {
    cout << "\n" << string(72, '=') << "\n";
    cout << title << "\n";
    cout << string(72, '=') << "\n";
}

template <typename T>
void printSet(const set<T>& values) {
    cout << "{ ";
    for (const auto& value : values) {
        cout << value << " ";
    }
    cout << "}\n";
}

void basicSetConstruction() {
    heading("Basic Set Construction");

    vector<int> numbers{1, 2, 2, 3, 4, 4, 5};
    set<int> squares;
    set<int> evens;

    for (int number : numbers) {
        squares.insert(number * number);

        if (number % 2 == 0) {
            evens.insert(number);
        }
    }

    cout << "Squares: ";
    printSet(squares);

    cout << "Even numbers: ";
    printSet(evens);

    // std::set maintains uniqueness automatically, so repeated input
    // values do not create repeated output elements.
}

void transformationAndFiltering() {
    heading("Transformation and Filtering");

    struct Transaction {
        string account;
        int amount;
    };

    vector<Transaction> transactions{
        {"A100", 2500},
        {"A101", 750},
        {"A100", 1250},
        {"A102", 4000},
        {"A103", -50}
    };

    set<string> highValueAccounts;
    set<int> positiveAmounts;

    for (const auto& transaction : transactions) {
        if (transaction.amount >= 2000) {
            highValueAccounts.insert(transaction.account);
        }

        if (transaction.amount > 0) {
            positiveAmounts.insert(transaction.amount);
        }
    }

    cout << "High-value accounts: ";
    printSet(highValueAccounts);

    cout << "Positive amounts: ";
    printSet(positiveAmounts);
}

void nestedIteration() {
    heading("Nested Iteration");

    set<string> combinations;

    vector<char> letters{'A', 'B'};
    vector<int> numbers{1, 2, 3};

    // This explicitly models the nested iteration represented by multiple
    // for clauses in a Python set comprehension.
    for (char letter : letters) {
        for (int number : numbers) {
            combinations.insert(string(1, letter) + to_string(number));
        }
    }

    cout << "Cartesian combinations: ";
    printSet(combinations);

    set<pair<int, int>> coordinates;

    for (int x = 0; x < 3; ++x) {
        for (int y = 0; y < 3; ++y) {
            if (x != y) {
                coordinates.emplace(x, y);
            }
        }
    }

    cout << "Coordinate count: " << coordinates.size() << "\n";
}

bool isPrime(int number) {
    if (number < 2) {
        return false;
    }

    if (number == 2) {
        return true;
    }

    if (number % 2 == 0) {
        return false;
    }

    for (int divisor = 3; divisor * divisor <= number; divisor += 2) {
        if (number % divisor == 0) {
            return false;
        }
    }

    return true;
}

void algorithmicSetConstruction() {
    heading("Algorithmic Set Construction");

    set<int> primes;

    for (int number = 2; number <= 100; ++number) {
        if (isPrime(number)) {
            primes.insert(number);
        }
    }

    cout << "Primes through 100: ";
    printSet(primes);
}

void setRelationships() {
    heading("Set Relationships");

    set<string> requested{
        "read", "write", "delete", "audit"
    };

    set<string> granted{
        "read", "write", "audit"
    };

    set<string> missing;
    set<string> intersection;

    set_difference(
        requested.begin(), requested.end(),
        granted.begin(), granted.end(),
        inserter(missing, missing.begin())
    );

    set_intersection(
        requested.begin(), requested.end(),
        granted.begin(), granted.end(),
        inserter(intersection, intersection.begin())
    );

    cout << "Missing permissions: ";
    printSet(missing);

    cout << "Intersection: ";
    printSet(intersection);
}

void structuredData() {
    heading("Structured Data");

    struct User {
        string username;
        set<string> roles;
        bool active;
    };

    vector<User> users{
        {"anita", {"reader", "analyst"}, true},
        {"rahul", {"admin", "reader"}, true},
        {"meera", {"reader"}, false},
        {"vikas", {"analyst", "auditor"}, true}
    };

    set<string> activeUsers;
    set<string> activeRoles;
    set<string> analysts;

    for (const auto& user : users) {
        if (!user.active) {
            continue;
        }

        activeUsers.insert(user.username);

        if (user.roles.contains("analyst")) {
            analysts.insert(user.username);
        }

        for (const auto& role : user.roles) {
            activeRoles.insert(role);
        }
    }

    cout << "Active users: ";
    printSet(activeUsers);

    cout << "Active analysts: ";
    printSet(analysts);

    cout << "Active roles: ";
    printSet(activeRoles);
}

void stringNormalization() {
    heading("String Normalization");

    vector<string> raw{
        " Python ",
        "python",
        "SQL",
        "sql",
        " Java "
    };

    set<string> normalized;

    for (string value : raw) {
        value.erase(
            remove_if(
                value.begin(),
                value.end(),
                [](unsigned char character) {
                    return isspace(character);
                }
            ),
            value.end()
        );

        transform(
            value.begin(),
            value.end(),
            value.begin(),
            [](unsigned char character) {
                return static_cast<char>(tolower(character));
            }
        );

        normalized.insert(value);
    }

    cout << "Normalized unique values: ";
    printSet(normalized);
}

void validationAndFailure() {
    heading("Validation and Failure Conditions");

    vector<int> values{10, 20, 30, 10};

    set<int> validPositiveValues;

    for (int value : values) {
        if (value <= 0) {
            continue;
        }

        validPositiveValues.insert(value);
    }

    cout << "Validated values: ";
    printSet(validPositiveValues);

    try {
        int divisor = 0;

        if (divisor == 0) {
            throw invalid_argument(
                "Division cannot use zero as a divisor."
            );
        }

        cout << 100 / divisor << "\n";
    }
    catch (const invalid_argument& error) {
        cout << "Expected validation failure: "
             << error.what() << "\n";
    }
}

void permissionPolicyCaseStudy() {
    heading("Permission Policy Case Study");

    map<string, set<string>> accounts{
        {"finance", {"read", "write", "approve"}},
        {"analytics", {"read", "export"}},
        {"support", {"read", "comment"}},
        {"guest", {"read"}}
    };

    set<string> approvalEligibleRoles;
    set<string> elevatedPermissions;

    for (const auto& [role, permissions] : accounts) {
        if (
            permissions.contains("read") &&
            permissions.contains("approve")
        ) {
            approvalEligibleRoles.insert(role);
        }

        for (const auto& permission : permissions) {
            if (
                permission == "write" ||
                permission == "approve" ||
                permission == "export"
            ) {
                elevatedPermissions.insert(permission);
            }
        }
    }

    cout << "Approval-eligible roles: ";
    printSet(approvalEligibleRoles);

    cout << "Elevated permissions: ";
    printSet(elevatedPermissions);
}

void performanceCaseStudy() {
    heading("Performance Characteristics");

    vector<int> values;
    values.reserve(100000);

    for (int number = 0; number < 100000; ++number) {
        values.push_back(number);
    }

    auto start = chrono::high_resolution_clock::now();

    unordered_set<int> transformed;

    for (int number : values) {
        if (number % 3 == 0) {
            transformed.insert(number * 2);
        }
    }

    auto finish = chrono::high_resolution_clock::now();

    chrono::duration<double, milli> elapsed = finish - start;

    cout << "Unique transformed values: "
         << transformed.size() << "\n";

    cout << "Hash-set construction time: "
         << elapsed.count() << " ms\n";

    // A set provides uniqueness but introduces storage overhead.
    // unordered_set provides average O(1) lookup while std::set provides
    // ordered elements with O(log n) insertion and lookup.
}

void compareOrderedAndHashSets() {
    heading("Ordered Set versus Hash Set");

    set<int> ordered{5, 1, 4, 2, 3};
    unordered_set<int> hashed{5, 1, 4, 2, 3};

    cout << "Ordered set: ";
    printSet(ordered);

    cout << "Hash-set membership for 4: "
         << (hashed.contains(4) ? "present" : "missing") << "\n";

    // Use std::set when ordering and logarithmic operations matter.
    // Use std::unordered_set when fast average-case membership matters and
    // iteration order is not part of the application contract.
}

int main() {
    basicSetConstruction();
    transformationAndFiltering();
    nestedIteration();
    algorithmicSetConstruction();
    setRelationships();
    structuredData();
    stringNormalization();
    validationAndFailure();
    permissionPolicyCaseStudy();
    performanceCaseStudy();
    compareOrderedAndHashSets();

    return 0;
}
