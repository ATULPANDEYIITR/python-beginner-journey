#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class EnvironmentState {
    CREATED,
    CONFIGURING,
    READY,
    FAILED,
    RETIRED
};

enum class Runtime {
    PYTHON,
    NODE,
    JAVA
};

enum class IsolationLevel {
    STRICT,
    STANDARD,
    SHARED
};

string toString(EnvironmentState state) {
    switch (state) {
        case EnvironmentState::CREATED: return "CREATED";
        case EnvironmentState::CONFIGURING: return "CONFIGURING";
        case EnvironmentState::READY: return "READY";
        case EnvironmentState::FAILED: return "FAILED";
        case EnvironmentState::RETIRED: return "RETIRED";
    }

    throw runtime_error("Unknown environment state.");
}

string toString(Runtime runtime) {
    switch (runtime) {
        case Runtime::PYTHON: return "PYTHON";
        case Runtime::NODE: return "NODE";
        case Runtime::JAVA: return "JAVA";
    }

    throw runtime_error("Unknown runtime.");
}

string toString(IsolationLevel level) {
    switch (level) {
        case IsolationLevel::STRICT: return "STRICT";
        case IsolationLevel::STANDARD: return "STANDARD";
        case IsolationLevel::SHARED: return "SHARED";
    }

    throw runtime_error("Unknown isolation level.");
}

struct Dependency {
    string name;
    string version;
    bool direct = true;
};

struct Environment {
    int id;
    string name;
    string project;
    Runtime runtime;
    string runtimeVersion;
    IsolationLevel isolation;
    EnvironmentState state;
    int diskSpaceMB;
    bool lockfilePresent;
    bool systemPackagesEnabled;
    map<string, Dependency> dependencies;
};

struct Policy {
    set<Runtime> allowedRuntimes;
    int minimumDiskSpaceMB = 100;
    int maximumDependencies = 100;
    bool requireLockfile = true;
    bool prohibitSystemPackages = true;
    bool requireStrictIsolation = false;
};

struct Evaluation {
    bool eligible;
    vector<string> violations;
};

class EnvironmentValidator {

public:

    static void validateName(const string& name) {

        if (name.empty() || name.size() > 50) {
            throw invalid_argument("Invalid environment name length.");
        }

        for (unsigned char c : name) {
            if (
                !isalnum(c) &&
                c != '_' &&
                c != '-' &&
                c != '.'
            ) {
                throw invalid_argument(
                    "Environment name contains invalid characters."
                );
            }
        }

        if (name == "." || name == "..") {
            throw invalid_argument("Invalid environment name.");
        }
    }

    static void validateDependency(const Dependency& dependency) {

        if (dependency.name.empty() || dependency.version.empty()) {
            throw invalid_argument("Dependency name and version are required.");
        }

        for (unsigned char c : dependency.name) {
            if (
                !isalnum(c) &&
                c != '_' &&
                c != '-' &&
                c != '.'
            ) {
                throw invalid_argument("Invalid dependency name.");
            }
        }
    }
};

class EnvironmentPolicyEngine {

private:
    Policy policy;

public:

    explicit EnvironmentPolicyEngine(Policy configuredPolicy)
        : policy(std::move(configuredPolicy)) {

        if (policy.allowedRuntimes.empty()) {
            throw invalid_argument("No runtime is permitted.");
        }

        if (
            policy.minimumDiskSpaceMB < 0 ||
            policy.maximumDependencies < 0
        ) {
            throw invalid_argument("Invalid policy limits.");
        }
    }

    Evaluation evaluate(const Environment& environment) const {

        vector<string> violations;

        if (!policy.allowedRuntimes.count(environment.runtime)) {
            violations.push_back("Runtime is not approved.");
        }

        if (environment.diskSpaceMB < policy.minimumDiskSpaceMB) {
            violations.push_back("Insufficient disk allocation.");
        }

        if (
            static_cast<int>(environment.dependencies.size()) >
            policy.maximumDependencies
        ) {
            violations.push_back("Dependency limit exceeded.");
        }

        if (
            policy.requireLockfile &&
            !environment.lockfilePresent
        ) {
            violations.push_back("Dependency lockfile is missing.");
        }

        if (
            policy.prohibitSystemPackages &&
            environment.systemPackagesEnabled
        ) {
            violations.push_back("System packages are prohibited.");
        }

        if (
            policy.requireStrictIsolation &&
            environment.isolation != IsolationLevel::STRICT
        ) {
            violations.push_back("Strict isolation is required.");
        }

        return {
            violations.empty(),
            violations
        };
    }
};

class VirtualEnvironmentManager {

private:

    map<int, Environment> environments;
    map<string, int> names;
    map<string, set<int>> projects;

    EnvironmentPolicyEngine policyEngine;

    int nextId = 1;

    static bool validTransition(
        EnvironmentState current,
        EnvironmentState next
    ) {

        switch (current) {

            case EnvironmentState::CREATED:
                return next == EnvironmentState::CONFIGURING ||
                       next == EnvironmentState::RETIRED;

            case EnvironmentState::CONFIGURING:
                return next == EnvironmentState::READY ||
                       next == EnvironmentState::FAILED ||
                       next == EnvironmentState::RETIRED;

            case EnvironmentState::READY:
                return next == EnvironmentState::CONFIGURING ||
                       next == EnvironmentState::FAILED ||
                       next == EnvironmentState::RETIRED;

            case EnvironmentState::FAILED:
                return next == EnvironmentState::CONFIGURING ||
                       next == EnvironmentState::RETIRED;

            case EnvironmentState::RETIRED:
                return false;
        }

        return false;
    }

    Environment& find(int id) {

        auto iterator = environments.find(id);

        if (iterator == environments.end()) {
            throw out_of_range("Environment does not exist.");
        }

        return iterator->second;
    }

    const Environment& find(int id) const {

        auto iterator = environments.find(id);

        if (iterator == environments.end()) {
            throw out_of_range("Environment does not exist.");
        }

        return iterator->second;
    }

public:

    explicit VirtualEnvironmentManager(Policy policy)
        : policyEngine(std::move(policy)) {}

    int create(
        const string& name,
        const string& project,
        Runtime runtime,
        const string& version,
        IsolationLevel isolation,
        int diskSpaceMB,
        bool lockfile,
        bool systemPackages
    ) {

        EnvironmentValidator::validateName(name);

        if (project.empty() || version.empty()) {
            throw invalid_argument("Project and runtime version are required.");
        }

        if (diskSpaceMB < 0) {
            throw invalid_argument("Disk allocation cannot be negative.");
        }

        if (names.count(name)) {
            throw runtime_error("Environment name already exists.");
        }

        Environment environment{
            nextId,
            name,
            project,
            runtime,
            version,
            isolation,
            EnvironmentState::CREATED,
            diskSpaceMB,
            lockfile,
            systemPackages,
            {}
        };

        Evaluation evaluation = policyEngine.evaluate(environment);

        if (!evaluation.eligible) {

            ostringstream message;

            message << "Policy rejection:";

            for (const string& violation : evaluation.violations) {
                message << "\n - " << violation;
            }

            throw runtime_error(message.str());
        }

        int id = nextId++;

        environments.emplace(id, std::move(environment));
        names.emplace(name, id);
        projects[project].insert(id);

        return id;
    }

    void addDependency(
        int id,
        const Dependency& dependency
    ) {

        Environment& environment = find(id);

        if (environment.state == EnvironmentState::RETIRED) {
            throw runtime_error("Cannot modify retired environment.");
        }

        EnvironmentValidator::validateDependency(dependency);

        string normalized = dependency.name;

        transform(
            normalized.begin(),
            normalized.end(),
            normalized.begin(),
            [](unsigned char c) {
                return static_cast<char>(tolower(c));
            }
        );

        if (environment.dependencies.count(normalized)) {
            throw runtime_error("Dependency already exists.");
        }

        environment.dependencies.emplace(
            normalized,
            dependency
        );

        Evaluation evaluation = policyEngine.evaluate(environment);

        if (!evaluation.eligible) {
            environment.dependencies.erase(normalized);
            throw runtime_error("Dependency violates environment policy.");
        }
    }

    void transition(
        int id,
        EnvironmentState next
    ) {

        Environment& environment = find(id);

        if (!validTransition(environment.state, next)) {
            throw runtime_error(
                "Invalid transition: " +
                toString(environment.state) +
                " -> " +
                toString(next)
            );
        }

        environment.state = next;
    }

    Evaluation checkEligibility(int id) const {

        const Environment& environment = find(id);

        Evaluation evaluation = policyEngine.evaluate(environment);

        if (environment.state != EnvironmentState::READY) {
            evaluation.eligible = false;
            evaluation.violations.push_back(
                "Environment must be READY."
            );
        }

        return evaluation;
    }

    void retire(int id) {
        transition(id, EnvironmentState::RETIRED);
    }

    vector<Environment> listByProject(
        const string& project
    ) const {

        vector<Environment> result;

        auto iterator = projects.find(project);

        if (iterator == projects.end()) {
            return result;
        }

        for (int id : iterator->second) {
            result.push_back(find(id));
        }

        return result;
    }

    void printReport(int id) const {

        const Environment& environment = find(id);

        cout << "\nENVIRONMENT REPORT\n";
        cout << "------------------------------\n";

        cout << "ID: " << environment.id << '\n';
        cout << "Name: " << environment.name << '\n';
        cout << "Project: " << environment.project << '\n';
        cout << "Runtime: " << toString(environment.runtime) << '\n';
        cout << "Version: " << environment.runtimeVersion << '\n';
        cout << "Isolation: " << toString(environment.isolation) << '\n';
        cout << "State: " << toString(environment.state) << '\n';
        cout << "Disk: " << environment.diskSpaceMB << " MB\n";

        cout << "\nDEPENDENCIES\n";

        for (const auto& [name, dependency] :
             environment.dependencies) {

            cout << "  "
                 << dependency.name
                 << " == "
                 << dependency.version
                 << '\n';
        }

        Evaluation evaluation = checkEligibility(id);

        cout << "\nPOLICY EVALUATION\n";
        cout << "Eligible: "
             << (evaluation.eligible ? "YES" : "NO")
             << '\n';

        for (const string& violation : evaluation.violations) {
            cout << "Violation: " << violation << '\n';
        }
    }
};

int main() {

    try {

        Policy policy;

        policy.allowedRuntimes = {
            Runtime::PYTHON,
            Runtime::NODE,
            Runtime::JAVA
        };

        policy.minimumDiskSpaceMB = 100;
        policy.maximumDependencies = 20;
        policy.requireLockfile = true;
        policy.prohibitSystemPackages = true;
        policy.requireStrictIsolation = true;

        VirtualEnvironmentManager manager(policy);

        cout << "VIRTUAL ENVIRONMENT GOVERNANCE ENGINE\n";

        int environmentId = manager.create(
            "analytics-dev",
            "analytics-platform",
            Runtime::PYTHON,
            "3.13",
            IsolationLevel::STRICT,
            2048,
            true,
            false
        );

        manager.addDependency(
            environmentId,
            {"numpy", "2.3.0", true}
        );

        manager.addDependency(
            environmentId,
            {"pandas", "2.3.0", true}
        );

        manager.addDependency(
            environmentId,
            {"pytest", "8.4.0", true}
        );

        manager.transition(
            environmentId,
            EnvironmentState::CONFIGURING
        );

        manager.transition(
            environmentId,
            EnvironmentState::READY
        );

        manager.printReport(environmentId);

        cout << "\nPROJECT ENVIRONMENT INVENTORY\n";

        for (const Environment& environment :
             manager.listByProject("analytics-platform")) {

            cout << environment.name
                 << " | "
                 << toString(environment.state)
                 << '\n';
        }

        cout << "\nTESTING INVALID POLICY\n";

        try {

            manager.create(
                "shared-dev",
                "analytics-platform",
                Runtime::PYTHON,
                "3.13",
                IsolationLevel::SHARED,
                1024,
                true,
                false
            );

        } catch (const exception& error) {
            cout << "Rejected: " << error.what() << '\n';
        }

        cout << "\nRETIRING ENVIRONMENT\n";

        manager.retire(environmentId);

        cout << "Final state: "
             << toString(EnvironmentState::RETIRED)
             << '\n';

    } catch (const exception& error) {

        cerr << "ERROR: " << error.what() << '\n';

        return 1;
    }

    return 0;
}
