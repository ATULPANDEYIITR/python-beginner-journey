#include <algorithm>
#include <atomic>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

enum class Visibility {
    Public,
    Private,
    Internal
};

enum class RepositoryState {
    Active,
    Archived
};

enum class MergeStrategy {
    MergeCommit,
    Squash,
    Rebase
};

string toString(Visibility visibility) {
    switch (visibility) {
        case Visibility::Public: return "public";
        case Visibility::Private: return "private";
        case Visibility::Internal: return "internal";
    }
    throw invalid_argument("Unknown visibility");
}

struct RepositoryConfig {
    string name;
    string owner;
    Visibility visibility;
};

class Repository {
private:
    static atomic<int> totalRepositories;
    static constexpr int maximumRepositories = 100;
    static mutex registryMutex;
    static map<string, weak_ptr<Repository>> registry;

    string name;
    string owner;
    Visibility visibility;
    int commitCount = 0;
    RepositoryState state = RepositoryState::Active;

public:
    // Class attributes shared by every Repository instance.
    static const string organization;
    static const vector<string> supportedLanguages;
    static const MergeStrategy defaultMergeStrategy;

    Repository(
        const string& repositoryName,
        const string& repositoryOwner,
        Visibility repositoryVisibility
    )
        : name(repositoryName),
          owner(repositoryOwner),
          visibility(repositoryVisibility) {

        if (name.empty() || owner.empty()) {
            throw invalid_argument("Name and owner are required.");
        }
    }

    static shared_ptr<Repository> create(const RepositoryConfig& config) {
        lock_guard<mutex> guard(registryMutex);

        if (config.name.empty() || config.owner.empty()) {
            throw invalid_argument("Invalid repository configuration.");
        }

        auto existing = registry.find(config.name);

        if (existing != registry.end() && !existing->second.expired()) {
            throw invalid_argument("Repository already exists.");
        }

        if (totalRepositories.load() >= maximumRepositories) {
            throw runtime_error("Repository capacity reached.");
        }

        auto repository = shared_ptr<Repository>(
            new Repository(config.name, config.owner, config.visibility)
        );

        registry[config.name] = repository;
        totalRepositories.fetch_add(1);

        return repository;
    }

    static shared_ptr<Repository> find(const string& name) {
        lock_guard<mutex> guard(registryMutex);

        auto iterator = registry.find(name);

        if (iterator == registry.end()) {
            return nullptr;
        }

        return iterator->second.lock();
    }

    static int getTotalRepositories() {
        return totalRepositories.load();
    }

    static int getMaximumRepositories() {
        return maximumRepositories;
    }

    static const string& getOrganization() {
        return organization;
    }

    void addCommit() {
        if (state != RepositoryState::Active) {
            throw logic_error("Cannot commit to an archived repository.");
        }

        ++commitCount;
    }

    void archive() {
        state = RepositoryState::Archived;
    }

    string getName() const {
        return name;
    }

    int getCommitCount() const {
        return commitCount;
    }

    Visibility getVisibility() const {
        return visibility;
    }

    RepositoryState getState() const {
        return state;
    }

    void describe() const {
        cout << "Repository: " << name << '\n'
             << "Owner: " << owner << '\n'
             << "Visibility: " << toString(visibility) << '\n'
             << "Commits: " << commitCount << '\n'
             << "Organization: " << organization << '\n';
    }
};

// Static data member definitions.
atomic<int> Repository::totalRepositories{0};
mutex Repository::registryMutex;
map<string, weak_ptr<Repository>> Repository::registry;

const string Repository::organization = "OpenSystems";

const vector<string> Repository::supportedLanguages = {
    "C++", "Python", "JavaScript", "Java"
};

const MergeStrategy Repository::defaultMergeStrategy =
    MergeStrategy::Squash;

class EnterpriseRepository : public Repository {
public:
    // This static attribute hides the parent class attribute.
    static const string organization;
    static constexpr int maximumRepositories = 50;

    EnterpriseRepository(
        const string& name,
        const string& owner
    )
        : Repository(name, owner, Visibility::Internal) {}
};

const string EnterpriseRepository::organization = "EnterpriseSystems";

struct ReviewPolicy {
    int requiredApprovals = 2;
    bool requirePassingChecks = true;
    bool requireResolvedConversations = true;
    bool allowDirectPush = false;
    bool allowForcePush = false;
    bool requireLinearHistory = true;
};

struct Review {
    string reviewer;
    bool eligible;
    bool dismissed;
    int commitVersion;
    bool approved;
};

struct StatusCheck {
    string name;
    bool passed;
};

struct PullRequest {
    int id;
    string sourceBranch;
    string targetBranch;
    int proposedCommitVersion;
    bool draft = false;
    bool open = true;
    bool conflicts = false;
    bool conversationsResolved = true;
    bool linearHistory = true;

    vector<Review> reviews;
    vector<StatusCheck> checks;
};

struct EligibilityResult {
    bool eligible;
    vector<string> reasons;
};

class GovernanceEngine {
private:
    ReviewPolicy policy;

public:
    explicit GovernanceEngine(ReviewPolicy reviewPolicy)
        : policy(reviewPolicy) {

        if (policy.requiredApprovals < 0) {
            throw invalid_argument("Approval count cannot be negative.");
        }
    }

    EligibilityResult evaluate(const PullRequest& pr) const {
        vector<string> reasons;

        if (!pr.open) {
            reasons.push_back("Pull Request is closed.");
        }

        if (pr.draft) {
            reasons.push_back("Draft Pull Request cannot be merged.");
        }

        if (pr.sourceBranch.empty() || pr.targetBranch.empty()) {
            reasons.push_back("Source and target branches are required.");
        }

        if (pr.sourceBranch == pr.targetBranch) {
            reasons.push_back("Source and target branches must differ.");
        }

        if (pr.conflicts) {
            reasons.push_back("Merge conflicts must be resolved.");
        }

        if (policy.requireResolvedConversations &&
            !pr.conversationsResolved) {
            reasons.push_back("Review conversations remain unresolved.");
        }

        if (policy.requireLinearHistory && !pr.linearHistory) {
            reasons.push_back("Linear history is required.");
        }

        set<string> eligibleApprovers;

        for (const auto& review : pr.reviews) {
            if (!review.eligible || review.dismissed) {
                continue;
            }

            if (review.commitVersion != pr.proposedCommitVersion) {
                continue;
            }

            if (review.approved) {
                eligibleApprovers.insert(review.reviewer);
            }
        }

        if (static_cast<int>(eligibleApprovers.size()) <
            policy.requiredApprovals) {
            reasons.push_back("Required approvals are not satisfied.");
        }

        if (policy.requirePassingChecks) {
            if (pr.checks.empty()) {
                reasons.push_back("Required status checks are missing.");
            }

            for (const auto& check : pr.checks) {
                if (!check.passed) {
                    reasons.push_back(
                        "Status check failed: " + check.name
                    );
                }
            }
        }

        return {
            reasons.empty(),
            reasons
        };
    }

    void merge(PullRequest& pr) const {
        auto result = evaluate(pr);

        if (!result.eligible) {
            throw logic_error("Pull Request is not mergeable.");
        }

        // The repository's target branch is changed only after
        // every governance condition passes.
        pr.open = false;

        cout << "Pull Request #" << pr.id << " merged successfully.\n";
    }
};

void demonstrateClassAttributes() {
    cout << "\nCLASS ATTRIBUTE DEMONSTRATION\n";

    auto first = Repository::create({
        "payments",
        "finance-team",
        Visibility::Private
    });

    auto second = Repository::create({
        "analytics",
        "data-team",
        Visibility::Public
    });

    first->addCommit();
    first->addCommit();
    second->addCommit();

    first->describe();
    second->describe();

    cout << "\nShared repository count: "
         << Repository::getTotalRepositories() << '\n';

    cout << "Shared organization: "
         << Repository::getOrganization() << '\n';

    cout << "Parent organization: "
         << Repository::organization << '\n';

    cout << "Child organization: "
         << EnterpriseRepository::organization << '\n';

    cout << "Parent capacity: "
         << Repository::getMaximumRepositories() << '\n';

    cout << "Enterprise capacity: "
         << EnterpriseRepository::maximumRepositories << '\n';

    first->archive();

    try {
        first->addCommit();
    } catch (const logic_error& error) {
        cout << "State validation: " << error.what() << '\n';
    }
}

void demonstrateGovernance() {
    cout << "\nREPOSITORY GOVERNANCE ENGINE\n";

    ReviewPolicy policy;
    policy.requiredApprovals = 2;
    policy.requirePassingChecks = true;
    policy.requireResolvedConversations = true;
    policy.requireLinearHistory = true;

    GovernanceEngine engine(policy);

    PullRequest pr{
        101,
        "feature/payment-validation",
        "main",
        5
    };

    pr.reviews = {
        {"reviewer-a", true, false, 5, true},
        {"reviewer-b", true, false, 5, true},
        {"reviewer-c", false, false, 5, true},
        {"reviewer-d", true, false, 4, true}
    };

    pr.checks = {
        {"unit-tests", true},
        {"security-scan", true},
        {"build", true}
    };

    auto result = engine.evaluate(pr);

    if (!result.eligible) {
        cout << "Merge blocked:\n";

        for (const auto& reason : result.reasons) {
            cout << " - " << reason << '\n';
        }
    } else {
        engine.merge(pr);
    }

    PullRequest blocked{
        102,
        "feature/unsafe-change",
        "main",
        3
    };

    blocked.reviews = {
        {"reviewer-a", true, false, 3, true}
    };

    blocked.checks = {
        {"unit-tests", true},
        {"security-scan", false}
    };

    auto blockedResult = engine.evaluate(blocked);

    cout << "\nBlocked Pull Request:\n";

    for (const auto& reason : blockedResult.reasons) {
        cout << " - " << reason << '\n';
    }

    // A stale approval does not satisfy the current revision.
    blocked.reviews.push_back({
        "reviewer-b", true, false, 2, true
    });

    cout << "\nCurrent revision remains insufficient: "
         << boolalpha
         << engine.evaluate(blocked).eligible
         << '\n';

    // A dismissed approval cannot satisfy the policy.
    blocked.reviews.push_back({
        "reviewer-c", true, true, 3, true
    });

    cout << "Dismissed approval remains invalid: "
         << engine.evaluate(blocked).eligible
         << '\n';
}

int main() {
    try {
        cout << "CLASS ATTRIBUTES AND REPOSITORY GOVERNANCE\n";

        demonstrateClassAttributes();
        demonstrateGovernance();

        cout << "\nExecution completed successfully.\n";
    } catch (const exception& error) {
        cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
