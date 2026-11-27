/*
 * POLYMORPHISM IN C++17
 *
 * Repository governance and merge-eligibility engine.
 *
 * Demonstrates:
 * 1. Runtime polymorphism through virtual functions
 * 2. Abstract base classes
 * 3. Method overriding
 * 4. Smart pointers
 * 5. STL containers and algorithms
 * 6. Strategy-based policy evaluation
 * 7. Immutable review decisions
 * 8. Status-check evaluation
 * 9. Branch protection
 * 10. Merge eligibility
 * 11. Exception safety
 *
 * Compile:
 * g++ -std=c++17 -Wall -Wextra -pedantic polymorphism.cpp -o polymorphism
 *
 * Run:
 * ./polymorphism
 */

#include <algorithm>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;


/* ============================================================
   1. DOMAIN TYPES
   ============================================================ */

enum class ReviewState {
    Approved,
    ChangesRequested,
    Commented,
    Dismissed
};

enum class CheckState {
    Passed,
    Failed,
    Pending
};

enum class PullRequestState {
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


struct Commit {
    string hash;
    string author;
    string message;
};

struct Review {
    string reviewer;
    ReviewState state;
    string commitHash;
    bool eligible;
    bool discussionResolved;
};

struct StatusCheck {
    string name;
    CheckState state;
    string commitHash;
};

struct Branch {
    string name;
    string headCommit;
    bool protectedBranch;
};

struct PullRequest {
    int id;
    string title;
    string sourceBranch;
    string targetBranch;
    string baseCommit;
    string headCommit;
    PullRequestState state;
    bool draft;
    bool conversationsResolved;
    vector<Commit> commits;
    vector<Review> reviews;
    vector<StatusCheck> checks;
};


/* ============================================================
   2. ABSTRACT POLICY INTERFACE
   ============================================================ */

class GovernanceRule {
public:
    virtual ~GovernanceRule() = default;

    virtual bool evaluate(
        const PullRequest& pr,
        const Branch& target,
        vector<string>& violations
    ) const = 0;

    virtual string name() const = 0;
};


/* ============================================================
   3. APPROVAL POLICY
   ============================================================ */

class ApprovalRule : public GovernanceRule {
private:
    size_t requiredApprovals;

public:
    explicit ApprovalRule(size_t required)
        : requiredApprovals(required) {}

    bool evaluate(
        const PullRequest& pr,
        const Branch&,
        vector<string>& violations
    ) const override {

        set<string> approvedReviewers;

        for (const auto& review : pr.reviews) {
            if (
                review.eligible &&
                review.state == ReviewState::Approved &&
                review.commitHash == pr.headCommit
            ) {
                approvedReviewers.insert(review.reviewer);
            }
        }

        if (approvedReviewers.size() < requiredApprovals) {
            violations.push_back(
                "Insufficient current eligible approvals."
            );

            return false;
        }

        return true;
    }

    string name() const override {
        return "ApprovalRule";
    }
};


/* ============================================================
   4. STATUS CHECK POLICY
   ============================================================ */

class StatusCheckRule : public GovernanceRule {
private:
    set<string> requiredChecks;

public:
    explicit StatusCheckRule(set<string> checks)
        : requiredChecks(move(checks)) {}

    bool evaluate(
        const PullRequest& pr,
        const Branch&,
        vector<string>& violations
    ) const override {

        map<string, CheckState> results;

        for (const auto& check : pr.checks) {
            if (check.commitHash == pr.headCommit) {
                results[check.name] = check.state;
            }
        }

        bool valid = true;

        for (const auto& required : requiredChecks) {
            auto it = results.find(required);

            if (it == results.end()) {
                violations.push_back(
                    "Missing status check: " + required
                );

                valid = false;
            } else if (it->second != CheckState::Passed) {
                violations.push_back(
                    "Status check not passed: " + required
                );

                valid = false;
            }
        }

        return valid;
    }

    string name() const override {
        return "StatusCheckRule";
    }
};


/* ============================================================
   5. CONVERSATION POLICY
   ============================================================ */

class ConversationRule : public GovernanceRule {
public:
    bool evaluate(
        const PullRequest& pr,
        const Branch&,
        vector<string>& violations
    ) const override {

        if (!pr.conversationsResolved) {
            violations.push_back(
                "Unresolved review conversations."
            );

            return false;
        }

        return true;
    }

    string name() const override {
        return "ConversationRule";
    }
};


/* ============================================================
   6. BRANCH PROTECTION POLICY
   ============================================================ */

class BranchProtectionRule : public GovernanceRule {
public:
    bool evaluate(
        const PullRequest& pr,
        const Branch& target,
        vector<string>& violations
    ) const override {

        if (!target.protectedBranch) {
            return true;
        }

        if (pr.sourceBranch == pr.targetBranch) {
            violations.push_back(
                "Source and target branches must differ."
            );

            return false;
        }

        if (pr.baseCommit.empty() || pr.headCommit.empty()) {
            violations.push_back(
                "Branch commit references are missing."
            );

            return false;
        }

        return true;
    }

    string name() const override {
        return "BranchProtectionRule";
    }
};


/* ============================================================
   7. LINEAR HISTORY POLICY
   ============================================================ */

class LinearHistoryRule : public GovernanceRule {
private:
    MergeStrategy strategy;

public:
    explicit LinearHistoryRule(MergeStrategy selected)
        : strategy(selected) {}

    bool evaluate(
        const PullRequest&,
        const Branch& target,
        vector<string>& violations
    ) const override {

        if (
            target.protectedBranch &&
            strategy == MergeStrategy::MergeCommit
        ) {
            violations.push_back(
                "Merge commits are prohibited by linear-history policy."
            );

            return false;
        }

        return true;
    }

    string name() const override {
        return "LinearHistoryRule";
    }
};


/* ============================================================
   8. PULL REQUEST VALIDATION
   ============================================================ */

class PullRequestValidator {
public:
    static void validate(const PullRequest& pr) {

        if (pr.id <= 0) {
            throw invalid_argument("Invalid Pull Request ID.");
        }

        if (pr.title.empty()) {
            throw invalid_argument("Pull Request title is required.");
        }

        if (
            pr.sourceBranch.empty() ||
            pr.targetBranch.empty()
        ) {
            throw invalid_argument("Branch names are required.");
        }

        if (pr.sourceBranch == pr.targetBranch) {
            throw invalid_argument(
                "Source and target branches cannot be identical."
            );
        }

        if (pr.commits.empty()) {
            throw invalid_argument(
                "Pull Request must contain at least one commit."
            );
        }

        if (pr.headCommit.empty() || pr.baseCommit.empty()) {
            throw invalid_argument(
                "Base and head commit references are required."
            );
        }
    }
};


/* ============================================================
   9. GOVERNANCE ENGINE
   ============================================================ */

struct EligibilityResult {
    bool eligible;
    vector<string> violations;
};

class GovernanceEngine {
private:
    vector<shared_ptr<const GovernanceRule>> rules;

public:
    void addRule(shared_ptr<const GovernanceRule> rule) {

        if (!rule) {
            throw invalid_argument("Governance rule cannot be null.");
        }

        rules.push_back(move(rule));
    }

    EligibilityResult evaluate(
        const PullRequest& pr,
        const Branch& target
    ) const {

        PullRequestValidator::validate(pr);

        EligibilityResult result{true, {}};

        if (pr.state != PullRequestState::Open) {
            result.violations.push_back(
                "Pull Request is not open."
            );

            result.eligible = false;
            return result;
        }

        if (pr.draft) {
            result.violations.push_back(
                "Draft Pull Requests cannot be merged."
            );

            result.eligible = false;
            return result;
        }

        for (const auto& rule : rules) {
            if (!rule->evaluate(
                    pr,
                    target,
                    result.violations
                )) {
                result.eligible = false;
            }
        }

        return result;
    }
};


/* ============================================================
   10. MERGE SERVICE
   ============================================================ */

class MergeService {
public:
    static void merge(
        PullRequest& pr,
        Branch& target,
        MergeStrategy strategy,
        const GovernanceEngine& engine
    ) {

        const auto eligibility = engine.evaluate(pr, target);

        if (!eligibility.eligible) {
            throw runtime_error(
                "Merge rejected: governance conditions failed."
            );
        }

        if (pr.baseCommit != target.headCommit) {
            throw runtime_error(
                "Target branch changed. Synchronize the Pull Request."
            );
        }

        if (strategy == MergeStrategy::Rebase) {
            // A production rebase must also verify conflicts and
            // recreate the commit chain before changing branch state.
            if (pr.commits.empty()) {
                throw runtime_error("No commits available for rebase.");
            }
        }

        const string mergedCommit =
            "merge-" + to_string(pr.id) + "-" + pr.headCommit;

        target.headCommit = mergedCommit;
        pr.state = PullRequestState::Merged;
    }
};


/* ============================================================
   11. REPORTING
   ============================================================ */

void printEligibility(
    const EligibilityResult& result
) {

    cout << "Merge eligible: "
         << (result.eligible ? "YES" : "NO")
         << '\n';

    for (const auto& violation : result.violations) {
        cout << " - " << violation << '\n';
    }
}


/* ============================================================
   12. TEST SCENARIO
   ============================================================ */

int main() {

    try {

        Branch mainBranch{
            "main",
            "commit-100",
            true
        };

        PullRequest pr{
            101,
            "Add secure inventory processing",
            "feature/inventory",
            "main",
            "commit-100",
            "commit-105",
            PullRequestState::Open,
            false,
            true,
            {
                {"commit-104", "developer1", "Add inventory model"},
                {"commit-105", "developer1", "Add validation"}
            },
            {
                {
                    "reviewer1",
                    ReviewState::Approved,
                    "commit-105",
                    true,
                    true
                },
                {
                    "reviewer2",
                    ReviewState::Approved,
                    "commit-105",
                    true,
                    true
                }
            },
            {
                {
                    "unit-tests",
                    CheckState::Passed,
                    "commit-105"
                },
                {
                    "security-scan",
                    CheckState::Passed,
                    "commit-105"
                },
                {
                    "build",
                    CheckState::Passed,
                    "commit-105"
                }
            }
        };

        GovernanceEngine engine;

        engine.addRule(
            make_shared<ApprovalRule>(2)
        );

        engine.addRule(
            make_shared<StatusCheckRule>(
                set<string>{
                    "unit-tests",
                    "security-scan",
                    "build"
                }
            )
        );

        engine.addRule(
            make_shared<ConversationRule>()
        );

        engine.addRule(
            make_shared<BranchProtectionRule>()
        );

        engine.addRule(
            make_shared<LinearHistoryRule>(
                MergeStrategy::Squash
            )
        );

        cout << "\n1. SUCCESSFUL GOVERNANCE EVALUATION\n";

        auto result = engine.evaluate(pr, mainBranch);
        printEligibility(result);

        cout << "\n2. MERGE PROCESSING\n";

        MergeService::merge(
            pr,
            mainBranch,
            MergeStrategy::Squash,
            engine
        );

        cout << "Pull Request state: Merged\n";
        cout << "New main commit: "
             << mainBranch.headCommit << '\n';

        cout << "\n3. STALE APPROVAL TEST\n";

        PullRequest stalePR = pr;

        stalePR.id = 102;
        stalePR.state = PullRequestState::Open;
        stalePR.headCommit = "commit-200";
        stalePR.baseCommit = mainBranch.headCommit;
        stalePR.draft = false;

        auto staleResult = engine.evaluate(
            stalePR,
            mainBranch
        );

        printEligibility(staleResult);

        cout << "\n4. FAILED STATUS CHECK TEST\n";

        PullRequest failedPR = stalePR;

        failedPR.reviews = {
            {
                "reviewer1",
                ReviewState::Approved,
                "commit-200",
                true,
                true
            },
            {
                "reviewer2",
                ReviewState::Approved,
                "commit-200",
                true,
                true
            }
        };

        failedPR.checks = {
            {
                "unit-tests",
                CheckState::Passed,
                "commit-200"
            },
            {
                "security-scan",
                CheckState::Failed,
                "commit-200"
            },
            {
                "build",
                CheckState::Passed,
                "commit-200"
            }
        };

        printEligibility(
            engine.evaluate(failedPR, mainBranch)
        );

        cout << "\n5. UNRESOLVED CONVERSATION TEST\n";

        PullRequest discussionPR = failedPR;

        discussionPR.conversationsResolved = false;

        printEligibility(
            engine.evaluate(discussionPR, mainBranch)
        );

        cout << "\n6. DRAFT PULL REQUEST TEST\n";

        PullRequest draftPR = failedPR;

        draftPR.draft = true;

        printEligibility(
            engine.evaluate(draftPR, mainBranch)
        );

        cout << "\n7. VALIDATION FAILURE TEST\n";

        try {
            PullRequest invalidPR = failedPR;
            invalidPR.id = -1;

            engine.evaluate(invalidPR, mainBranch);

        } catch (const invalid_argument& error) {
            cout << "Validation rejected input: "
                 << error.what() << '\n';
        }

        cout << "\n8. MERGE STRATEGY TEST\n";

        PullRequest strategyPR = failedPR;

        strategyPR.reviews = {
            {
                "reviewer1",
                ReviewState::Approved,
                "commit-200",
                true,
                true
            },
            {
                "reviewer2",
                ReviewState::Approved,
                "commit-200",
                true,
                true
            }
        };

        strategyPR.checks = {
            {"unit-tests", CheckState::Passed, "commit-200"},
            {"security-scan", CheckState::Passed, "commit-200"},
            {"build", CheckState::Passed, "commit-200"}
        };

        GovernanceEngine mergeCommitEngine;

        mergeCommitEngine.addRule(
            make_shared<LinearHistoryRule>(
                MergeStrategy::MergeCommit
            )
        );

        printEligibility(
            mergeCommitEngine.evaluate(
                strategyPR,
                mainBranch
            )
        );

        cout << "\nAll governance scenarios completed.\n";

    } catch (const exception& error) {

        cerr << "Execution error: "
             << error.what() << '\n';

        return 1;
    }

    return 0;
}
