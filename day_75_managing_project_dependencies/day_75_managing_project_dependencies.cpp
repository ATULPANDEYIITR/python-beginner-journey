#include <algorithm>
#include <cctype>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using namespace std;

class ValidationError : public runtime_error {
public:
    using runtime_error::runtime_error;
};

class GovernanceError : public runtime_error {
public:
    using runtime_error::runtime_error;
};

struct Version {
    int major = 0;
    int minor = 0;
    int patch = 0;

    static Version parse(const string& value) {
        Version result;
        char first, second;

        stringstream stream(value);

        if (!(stream >> result.major >> first
                     >> result.minor >> second >> result.patch)
            || first != '.' || second != '.'
            || !stream.eof()
            || result.major < 0
            || result.minor < 0
            || result.patch < 0) {
            throw ValidationError("Invalid semantic version: " + value);
        }

        string canonical =
            to_string(result.major) + "." +
            to_string(result.minor) + "." +
            to_string(result.patch);

        if (canonical != value) {
            throw ValidationError("Noncanonical version: " + value);
        }

        return result;
    }

    bool operator<(const Version& other) const {
        if (major != other.major) return major < other.major;
        if (minor != other.minor) return minor < other.minor;
        return patch < other.patch;
    }

    bool operator==(const Version& other) const {
        return major == other.major &&
               minor == other.minor &&
               patch == other.patch;
    }

    bool operator>(const Version& other) const {
        return other < *this;
    }

    bool operator<=(const Version& other) const {
        return !(other < *this);
    }

    string str() const {
        return to_string(major) + "." +
               to_string(minor) + "." +
               to_string(patch);
    }
};

enum class ReviewState {
    Approved,
    ChangesRequested,
    Commented,
    Dismissed
};

enum class CheckState {
    Pending,
    Passed,
    Failed
};

enum class PRState {
    Draft,
    Open,
    Merged,
    Closed
};

enum class MergeStrategy {
    MergeCommit,
    Squash,
    Rebase
};

struct Dependency {
    string name;
    Version current;
    Version minimum;
    Version maximum;
    bool hasMaximum = false;
    bool direct = true;
    string license = "MIT";
    int vulnerabilities = 0;
    vector<string> prerequisites;
};

struct Review {
    string reviewer;
    ReviewState state;
    string commit;
};

struct PullRequest {
    int id;
    string source;
    string target;
    map<string, Version> changes;
    PRState state = PRState::Open;
    bool draft = false;
    bool synchronized = true;
    bool conflicts = false;
    string headCommit = "initial";
    map<string, Review> reviews;
    map<string, CheckState> checks;
    map<string, bool> conversations;
};

struct ProtectionPolicy {
    set<string> allowedLicenses = {
        "MIT", "Apache-2.0", "BSD-3-Clause"
    };

    int maximumVulnerabilities = 0;
    int requiredApprovals = 2;
    bool requireChecks = true;
    bool requireResolvedConversations = true;
    bool requireLockfile = true;
    bool dismissStaleApprovals = true;
    bool rejectDirectPush = true;
    bool rejectForcePush = true;
    bool rejectBranchDeletion = true;
    bool requireLinearHistory = true;
    bool administratorBypass = false;
};

class GovernanceEngine {
private:
    map<string, Dependency> dependencies;
    map<int, PullRequest> pullRequests;
    set<string> protectedBranches = {"main"};
    ProtectionPolicy policy;
    int nextPR = 1;

    static bool validName(const string& name) {
        if (name.empty() || name.size() > 100) return false;

        return all_of(name.begin(), name.end(), [](unsigned char c) {
            return isalnum(c) || c == '-' || c == '_' || c == '.';
        });
    }

    static string createCommit(const PullRequest& pr) {
        // Stable simulation identifier, not a cryptographic Git object.
        ostringstream out;
        out << pr.id << ":" << pr.source << ":" << pr.target << ":";
        for (const auto& [name, version] : pr.changes) {
            out << name << "=" << version.str() << ";";
        }
        return out.str();
    }

public:
    explicit GovernanceEngine(ProtectionPolicy configured = {})
        : policy(std::move(configured)) {}

    void addDependency(const Dependency& dependency) {
        if (!validName(dependency.name)) {
            throw ValidationError("Invalid dependency name");
        }

        if (dependencies.count(dependency.name)) {
            throw ValidationError("Duplicate dependency");
        }

        if (dependency.vulnerabilities < 0) {
            throw ValidationError("Negative vulnerability count");
        }

        if (dependency.current < dependency.minimum) {
            throw ValidationError("Minimum version violation");
        }

        if (dependency.hasMaximum &&
            dependency.maximum < dependency.current) {
            throw ValidationError("Maximum version violation");
        }

        dependencies.emplace(dependency.name, dependency);
    }

    vector<string> resolveGraph() const {
        map<string, int> color;
        vector<string> result;

        function<void(const string&)> visit =
            [&](const string& name) {
                int state = color[name];

                if (state == 1) {
                    throw GovernanceError(
                        "Circular dependency: " + name
                    );
                }

                if (state == 2) return;

                auto found = dependencies.find(name);
                if (found == dependencies.end()) {
                    throw ValidationError(
                        "Missing dependency: " + name
                    );
                }

                color[name] = 1;

                auto children = found->second.prerequisites;
                sort(children.begin(), children.end());

                for (const auto& child : children) {
                    visit(child);
                }

                color[name] = 2;
                result.push_back(name);
            };

        for (const auto& [name, dependency] : dependencies) {
            visit(name);
        }

        return result;
    }

    vector<string> audit() const {
        vector<string> failures;

        for (const auto& [name, dependency] : dependencies) {
            if (!policy.allowedLicenses.count(dependency.license)) {
                failures.push_back(
                    name + ": prohibited license"
                );
            }

            if (dependency.vulnerabilities >
                policy.maximumVulnerabilities) {
                failures.push_back(
                    name + ": vulnerability threshold exceeded"
                );
            }
        }

        try {
            resolveGraph();
        } catch (const exception& error) {
            failures.push_back(error.what());
        }

        return failures;
    }

    map<string, Version> planUpdates(
        const map<string, string>& available
    ) const {
        map<string, Version> result;

        for (const auto& [name, rawVersion] : available) {
            auto found = dependencies.find(name);

            if (found == dependencies.end()) {
                throw ValidationError(
                    "Unknown dependency: " + name
                );
            }

            Version candidate = Version::parse(rawVersion);
            const Dependency& current = found->second;

            if (candidate <= current.current) continue;

            if (candidate < current.minimum) continue;

            if (current.hasMaximum &&
                current.maximum < candidate) {
                continue;
            }

            result[name] = candidate;
        }

        return result;
    }

    PullRequest& createPR(
        const string& source,
        const string& target,
        const map<string, Version>& changes,
        bool draft = false
    ) {
        if (source.empty() || target.empty() || source == target) {
            throw ValidationError("Invalid branch relationship");
        }

        if (!protectedBranches.count(target)) {
            throw GovernanceError("Target branch is not protected");
        }

        if (changes.empty()) {
            throw ValidationError("Empty dependency changeset");
        }

        for (const auto& [name, candidate] : changes) {
            auto found = dependencies.find(name);

            if (found == dependencies.end()) {
                throw ValidationError("Unknown package: " + name);
            }

            const auto& current = found->second;

            if (candidate <= current.current) {
                throw ValidationError("Update is not an upgrade");
            }

            if (current.hasMaximum &&
                current.maximum < candidate) {
                throw ValidationError("Version exceeds permitted range");
            }
        }

        PullRequest pr;
        pr.id = nextPR++;
        pr.source = source;
        pr.target = target;
        pr.changes = changes;
        pr.draft = draft;
        pr.state = draft ? PRState::Draft : PRState::Open;
        pr.headCommit = createCommit(pr);

        auto inserted = pullRequests.emplace(pr.id, std::move(pr));
        return inserted.first->second;
    }

    void configureCheck(
        PullRequest& pr,
        const string& name,
        CheckState state
    ) {
        if (pr.state != PRState::Open || pr.draft) {
            throw GovernanceError("PR is not ready for checks");
        }

        pr.checks[name] = state;
    }

    void submitReview(
        PullRequest& pr,
        const string& reviewer,
        ReviewState state
    ) {
        if (pr.state != PRState::Open || pr.draft) {
            throw GovernanceError("PR is not reviewable");
        }

        if (reviewer.empty()) {
            throw ValidationError("Reviewer identity is required");
        }

        pr.reviews[reviewer] = {
            reviewer, state, pr.headCommit
        };
    }

    void updateCommit(
        PullRequest& pr,
        const map<string, Version>& changes
    ) {
        if (pr.state != PRState::Open) {
            throw GovernanceError("PR is not open");
        }

        for (const auto& [name, version] : changes) {
            if (!pr.changes.count(name)) {
                throw ValidationError("Unexpected package update");
            }

            pr.changes[name] = version;
        }

        pr.headCommit = createCommit(pr);

        if (policy.dismissStaleApprovals) {
            for (auto& [reviewer, review] : pr.reviews) {
                if (review.state == ReviewState::Approved) {
                    review.state = ReviewState::Dismissed;
                }
            }
        }

        for (auto& [name, state] : pr.checks) {
            state = CheckState::Pending;
        }
    }

    vector<string> evaluateMerge(const PullRequest& pr) const {
        vector<string> failures;

        if (pr.state != PRState::Open) {
            failures.push_back("PR is not open");
        }

        if (pr.draft) {
            failures.push_back("Draft PR cannot be merged");
        }

        if (pr.conflicts) {
            failures.push_back("Merge conflicts exist");
        }

        if (!pr.synchronized) {
            failures.push_back("Base branch synchronization required");
        }

        if (policy.requireResolvedConversations) {
            for (const auto& [id, resolved] : pr.conversations) {
                if (!resolved) {
                    failures.push_back("Unresolved conversation: " + id);
                }
            }
        }

        if (policy.requireChecks) {
            if (pr.checks.empty()) {
                failures.push_back("No status checks configured");
            }

            for (const auto& [name, state] : pr.checks) {
                if (state != CheckState::Passed) {
                    failures.push_back("Check not passed: " + name);
                }
            }
        }

        set<string> approvals;

        for (const auto& [reviewer, review] : pr.reviews) {
            if (review.state == ReviewState::ChangesRequested &&
                review.commit == pr.headCommit) {
                failures.push_back("Changes requested");
            }

            if (review.state == ReviewState::Approved &&
                review.commit == pr.headCommit) {
                approvals.insert(reviewer);
            }
        }

        if (static_cast<int>(approvals.size()) <
            policy.requiredApprovals) {
            failures.push_back("Insufficient current approvals");
        }

        auto policyFailures = audit();
        failures.insert(
            failures.end(),
            policyFailures.begin(),
            policyFailures.end()
        );

        if (policy.requireLockfile && dependencies.empty()) {
            failures.push_back("Dependency inventory is empty");
        }

        return failures;
    }

    void merge(
        PullRequest& pr,
        MergeStrategy strategy
    ) {
        auto failures = evaluateMerge(pr);

        if (!failures.empty()) {
            string message = "Merge denied: ";
            for (const auto& failure : failures) {
                message += failure + "; ";
            }
            throw GovernanceError(message);
        }

        // Validate every update before mutating repository state.
        for (const auto& [name, version] : pr.changes) {
            const auto& dependency = dependencies.at(name);

            if (dependency.hasMaximum &&
                dependency.maximum < version) {
                throw GovernanceError("Invalid final dependency version");
            }
        }

        for (const auto& [name, version] : pr.changes) {
            dependencies.at(name).current = version;
        }

        pr.state = PRState::Merged;

        string strategyName;
        switch (strategy) {
            case MergeStrategy::MergeCommit:
                strategyName = "merge";
                break;
            case MergeStrategy::Squash:
                strategyName = "squash";
                break;
            case MergeStrategy::Rebase:
                strategyName = "rebase";
                break;
        }

        cout << "Merged PR #" << pr.id
             << " using " << strategyName << "\n";
    }

    void printInventory() const {
        cout << "\nDEPENDENCY INVENTORY\n";

        for (const auto& [name, dependency] : dependencies) {
            cout << left << setw(18) << name
                 << dependency.current.str()
                 << " | " << dependency.license
                 << " | vulnerabilities="
                 << dependency.vulnerabilities << "\n";
        }
    }
};

int main() {
    try {
        ProtectionPolicy policy;
        policy.requiredApprovals = 2;

        GovernanceEngine engine(policy);

        engine.addDependency({
            "httpx",
            Version::parse("0.27.0"),
            Version::parse("0.25.0"),
            Version{},
            false,
            true,
            "BSD-3-Clause",
            0,
            {}
        });

        engine.addDependency({
            "pydantic",
            Version::parse("2.8.2"),
            Version::parse("2.5.0"),
            Version{},
            false,
            true,
            "MIT",
            0,
            {}
        });

        engine.addDependency({
            "fastapi",
            Version::parse("0.112.0"),
            Version::parse("0.100.0"),
            Version{},
            false,
            true,
            "MIT",
            0,
            {"httpx", "pydantic"}
        });

        engine.addDependency({
            "cryptography",
            Version::parse("43.0.0"),
            Version::parse("42.0.0"),
            Version{},
            false,
            true,
            "Apache-2.0",
            0,
            {}
        });

        engine.printInventory();

        cout << "\nDEPENDENCY RESOLUTION ORDER\n";
        for (const auto& name : engine.resolveGraph()) {
            cout << name << " ";
        }
        cout << "\n";

        cout << "\nPOLICY AUDIT\n";
        auto audit = engine.audit();

        if (audit.empty()) {
            cout << "All dependencies satisfy policy\n";
        } else {
            for (const auto& issue : audit) {
                cout << issue << "\n";
            }
        }

        auto updates = engine.planUpdates({
            {"httpx", "0.28.1"},
            {"pydantic", "2.9.2"},
            {"fastapi", "0.115.0"}
        });

        cout << "\nUPDATE PLAN\n";
        for (const auto& [name, version] : updates) {
            cout << name << " -> " << version.str() << "\n";
        }

        auto& pr = engine.createPR(
            "dependency/quarterly-update",
            "main",
            updates
        );

        engine.configureCheck(
            pr, "unit-tests", CheckState::Passed
        );
        engine.configureCheck(
            pr, "security-scan", CheckState::Passed
        );
        engine.configureCheck(
            pr, "license-audit", CheckState::Passed
        );

        pr.conversations["compatibility"] = true;
        pr.conversations["migration-impact"] = true;

        engine.submitReview(
            pr, "security-reviewer", ReviewState::Approved
        );
        engine.submitReview(
            pr, "platform-reviewer", ReviewState::Approved
        );

        cout << "\nMERGE ELIGIBILITY\n";
        auto failures = engine.evaluateMerge(pr);

        if (failures.empty()) {
            cout << "ELIGIBLE\n";
            engine.merge(pr, MergeStrategy::Squash);
        } else {
            for (const auto& failure : failures) {
                cout << "BLOCKED: " << failure << "\n";
            }
        }

        engine.printInventory();

        // Demonstrate malformed version rejection.
        try {
            Version::parse("2.4");
        } catch (const ValidationError& error) {
            cout << "\nEXPECTED VALIDATION ERROR: "
                 << error.what() << "\n";
        }

        cout << "\nExecution completed.\n";

    } catch (const exception& error) {
        cerr << "FATAL ERROR: " << error.what() << "\n";
        return 1;
    }

    return 0;
}
