#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

/*
 * Python Package Governance and Dependency Resolution Engine.
 * C++17 implementation.
 */

struct Version {
    int major;
    int minor;
    int patch;

    Version(int a, int b, int c)
        : major(a), minor(b), patch(c) {
        if (a < 0 || b < 0 || c < 0) {
            throw invalid_argument("Negative version component.");
        }
    }

    bool operator==(const Version& other) const {
        return tie() == other.tie();
    }

    bool operator!=(const Version& other) const {
        return !(*this == other);
    }

    bool operator<(const Version& other) const {
        return tie() < other.tie();
    }

    bool operator>(const Version& other) const {
        return other < *this;
    }

    bool operator<=(const Version& other) const {
        return !(other < *this);
    }

    bool operator>=(const Version& other) const {
        return !(*this < other);
    }

    auto tie() const {
        return make_tuple(major, minor, patch);
    }

    string toString() const {
        return to_string(major) + "." +
               to_string(minor) + "." +
               to_string(patch);
    }
};


struct Dependency {
    string name;
    string constraint;
};


enum class PackageStatus {
    AVAILABLE,
    BLOCKED,
    DEPRECATED
};


struct Package {
    string name;
    Version version;
    string description;
    vector<Dependency> dependencies;
    string license;
    string source;
    PackageStatus status;
};


string normalizeName(const string& name) {
    if (name.empty()) {
        throw invalid_argument("Empty package name.");
    }

    string result;

    for (char ch : name) {
        if (!isalnum(static_cast<unsigned char>(ch)) &&
            ch != '.' && ch != '-' && ch != '_') {
            throw invalid_argument("Invalid package name.");
        }

        result.push_back(
            (ch == '.' || ch == '_') ? '-' :
            static_cast<char>(
                tolower(static_cast<unsigned char>(ch))
            )
        );
    }

    if (result.front() == '-' || result.back() == '-') {
        throw invalid_argument("Invalid package name boundary.");
    }

    if (result.find("..") != string::npos) {
        throw invalid_argument("Consecutive dots are prohibited.");
    }

    return result;
}


bool satisfies(const Version& version, const string& constraint) {
    if (constraint == "*") {
        return true;
    }

    vector<string> operators = {
        "==", "!=", ">=", "<=", ">", "<"
    };

    for (const string& op : operators) {
        if (constraint.rfind(op, 0) == 0) {
            string value = constraint.substr(op.size());

            int major, minor, patch;
            char dot1, dot2;

            stringstream input(value);

            if (!(input >> major >> dot1 >> minor >> dot2 >> patch) ||
                dot1 != '.' || dot2 != '.' ||
                input.peek() != EOF) {
                throw invalid_argument("Invalid version constraint.");
            }

            Version required(major, minor, patch);

            if (op == "==") return version == required;
            if (op == "!=") return version != required;
            if (op == ">=") return version >= required;
            if (op == "<=") return version <= required;
            if (op == ">") return version > required;
            if (op == "<") return version < required;
        }
    }

    throw invalid_argument("Unsupported constraint: " + constraint);
}


class PackageRegistry {
private:
    map<string, vector<Package>> packages;

public:
    void publish(Package package) {
        package.name = normalizeName(package.name);

        if (package.description.empty()) {
            throw invalid_argument("Description is required.");
        }

        for (const auto& dependency : package.dependencies) {
            if (normalizeName(dependency.name) == package.name) {
                throw invalid_argument("Self-dependency prohibited.");
            }
        }

        auto& versions = packages[package.name];

        for (const auto& existing : versions) {
            if (existing.version == package.version) {
                throw invalid_argument("Duplicate package release.");
            }
        }

        versions.push_back(package);

        sort(
            versions.begin(),
            versions.end(),
            [](const Package& a, const Package& b) {
                return a.version > b.version;
            }
        );
    }

    Package find(
        const string& name,
        const string& constraint = "*"
    ) const {
        string key = normalizeName(name);

        auto it = packages.find(key);

        if (it == packages.end()) {
            throw runtime_error("Package not found: " + key);
        }

        for (const auto& package : it->second) {
            if (package.status == PackageStatus::AVAILABLE &&
                satisfies(package.version, constraint)) {
                return package;
            }
        }

        throw runtime_error(
            "No compatible release for " + key
        );
    }
};


class DependencyResolver {
private:
    const PackageRegistry& registry;

    set<string> visited;
    set<string> active;
    vector<Package> ordered;

    void visit(const string& name, const string& constraint) {
        string key = normalizeName(name);

        if (active.count(key)) {
            throw runtime_error(
                "Circular dependency detected: " + key
            );
        }

        Package package = registry.find(key, constraint);

        string identity =
            package.name + "@" + package.version.toString();

        if (visited.count(identity)) {
            return;
        }

        active.insert(key);

        vector<Dependency> dependencies = package.dependencies;

        sort(
            dependencies.begin(),
            dependencies.end(),
            [](const Dependency& a, const Dependency& b) {
                return a.name < b.name;
            }
        );

        for (const auto& dependency : dependencies) {
            visit(dependency.name, dependency.constraint);
        }

        active.erase(key);
        visited.insert(identity);
        ordered.push_back(package);
    }

public:
    explicit DependencyResolver(const PackageRegistry& value)
        : registry(value) {}

    vector<Package> resolve(
        const string& name,
        const string& constraint = "*"
    ) {
        visited.clear();
        active.clear();
        ordered.clear();

        visit(name, constraint);
        return ordered;
    }
};


class SecurityPolicy {
private:
    set<string> blocked;
    set<string> allowedLicenses;
    set<string> allowedSources;

public:
    SecurityPolicy() {
        allowedLicenses = {
            "MIT", "Apache-2.0", "BSD-3-Clause", "ISC"
        };

        allowedSources = {"pypi"};
    }

    void block(const string& name) {
        blocked.insert(normalizeName(name));
    }

    vector<string> evaluate(
        const vector<Package>& packages
    ) const {
        vector<string> violations;

        for (const auto& package : packages) {
            if (blocked.count(package.name)) {
                violations.push_back(
                    package.name + ": blocked"
                );
            }

            if (!allowedLicenses.count(package.license)) {
                violations.push_back(
                    package.name + ": unapproved license"
                );
            }

            if (!allowedSources.count(package.source)) {
                violations.push_back(
                    package.name + ": untrusted source"
                );
            }

            if (package.status != PackageStatus::AVAILABLE) {
                violations.push_back(
                    package.name + ": unavailable package"
                );
            }
        }

        return violations;
    }
};


class PackageEnvironment {
private:
    map<string, Package> installed;

public:
    void install(
        const vector<Package>& packages,
        const SecurityPolicy& policy
    ) {
        vector<string> violations = policy.evaluate(packages);

        if (!violations.empty()) {
            string message = "Installation rejected:";

            for (const auto& violation : violations) {
                message += "\n - " + violation;
            }

            throw runtime_error(message);
        }

        // Validate the complete transaction before changing state.
        map<string, Package> candidate = installed;

        for (const auto& package : packages) {
            auto it = candidate.find(package.name);

            if (it != candidate.end() &&
                it->second.version != package.version) {
                throw runtime_error(
                    "Version conflict: " + package.name
                );
            }

            candidate[package.name] = package;
        }

        installed.swap(candidate);
    }

    void uninstall(const string& name) {
        string key = normalizeName(name);

        if (!installed.count(key)) {
            throw runtime_error("Package is not installed.");
        }

        for (const auto& entry : installed) {
            for (const auto& dependency :
                 entry.second.dependencies) {
                if (normalizeName(dependency.name) == key) {
                    throw runtime_error(
                        key + " is required by " + entry.first
                    );
                }
            }
        }

        installed.erase(key);
    }

    void display() const {
        cout << "\nInstalled packages:\n";

        for (const auto& entry : installed) {
            cout << entry.first << "=="
                 << entry.second.version.toString()
                 << '\n';
        }
    }

    size_t size() const {
        return installed.size();
    }
};


Package makePackage(
    string name,
    Version version,
    string description,
    vector<Dependency> dependencies = {}
) {
    return {
        move(name),
        version,
        move(description),
        move(dependencies),
        "MIT",
        "pypi",
        PackageStatus::AVAILABLE
    };
}


int main() {
    try {
        PackageRegistry registry;

        registry.publish(
            makePackage(
                "numpy",
                Version(2, 1, 0),
                "Numerical computing."
            )
        );

        registry.publish(
            makePackage(
                "pandas",
                Version(2, 2, 0),
                "Data analysis.",
                {{"numpy", ">=2.0.0"}}
            )
        );

        registry.publish(
            makePackage(
                "requests",
                Version(2, 32, 0),
                "HTTP client."
            )
        );

        registry.publish(
            makePackage(
                "analytics-toolkit",
                Version(1, 0, 0),
                "Analytics application.",
                {
                    {"pandas", ">=2.2.0"},
                    {"requests", ">=2.30.0"}
                }
            )
        );

        cout << "1. Resolve package dependencies\n";

        DependencyResolver resolver(registry);

        vector<Package> packages =
            resolver.resolve("analytics-toolkit");

        for (const auto& package : packages) {
            cout << package.name << "=="
                 << package.version.toString() << '\n';
        }

        cout << "\n2. Security policy evaluation\n";

        SecurityPolicy policy;
        policy.block("malicious-library");

        vector<string> violations =
            policy.evaluate(packages);

        if (!violations.empty()) {
            throw runtime_error("Security policy rejected packages.");
        }

        cout << "Security policy passed.\n";

        cout << "\n3. Transactional installation\n";

        PackageEnvironment environment;
        environment.install(packages, policy);

        environment.display();

        cout << "\n4. Dependency version verification\n";

        if (!satisfies(Version(2, 1, 0), ">=2.0.0")) {
            throw runtime_error("Version validation failed.");
        }

        if (satisfies(Version(1, 0, 0), ">=2.0.0")) {
            throw runtime_error("Invalid version accepted.");
        }

        cout << "Version constraints passed.\n";

        cout << "\n5. Protected package removal\n";

        try {
            environment.uninstall("numpy");
        } catch (const exception& error) {
            cout << "Expected failure: "
                 << error.what() << '\n';
        }

        cout << "\n6. Final environment\n";
        environment.display();

        cout << "\nTotal installed packages: "
             << environment.size() << '\n';

    } catch (const exception& error) {
        cerr << "Package management error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
