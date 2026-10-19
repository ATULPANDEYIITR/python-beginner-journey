#include <algorithm>
#include <functional>
#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

/*
 * Technical case study: a dependency analyzer for a software build.
 *
 * A dependency graph is naturally recursive when represented as a tree or
 * as a depth-first traversal of a directed acyclic graph. The program
 * demonstrates both forms and explicitly detects cycles, because naive
 * recursive graph traversal would otherwise recurse indefinitely.
 */

struct Package {
    string name;
    vector<string> dependencies;
};

class DependencyAnalyzer {
private:
    unordered_map<string, Package> packages;
    unordered_map<string, int> state;
    vector<string> traversal;

    // 0 = unseen, 1 = currently exploring, 2 = completely explored.
    void depthFirst(const string& packageName) {
        int currentState = state[packageName];

        if (currentState == 2) {
            return;
        }

        if (currentState == 1) {
            throw runtime_error(
                "dependency cycle detected at package: " + packageName
            );
        }

        state[packageName] = 1;
        traversal.push_back(packageName);

        const auto it = packages.find(packageName);
        if (it == packages.end()) {
            throw runtime_error("unknown dependency: " + packageName);
        }

        for (const string& dependency : it->second.dependencies) {
            depthFirst(dependency);
        }

        state[packageName] = 2;
    }

public:
    void addPackage(string name, vector<string> dependencies) {
        if (name.empty()) {
            throw invalid_argument("package name cannot be empty");
        }

        if (packages.contains(name)) {
            throw invalid_argument("package already exists: " + name);
        }

        packages.emplace(
            name,
            Package{move(name), move(dependencies)}
        );
    }

    vector<string> resolveBuildOrder(const string& root) {
        state.clear();
        traversal.clear();
        depthFirst(root);

        reverse(traversal.begin(), traversal.end());
        return traversal;
    }
};

struct TreeNode {
    int value;
    unique_ptr<TreeNode> left;
    unique_ptr<TreeNode> right;

    explicit TreeNode(int value) : value(value) {}
};

class BinarySearchTree {
private:
    unique_ptr<TreeNode> root;

    static void insertRecursive(unique_ptr<TreeNode>& node, int value) {
        if (!node) {
            node = make_unique<TreeNode>(value);
            return;
        }

        if (value < node->value) {
            insertRecursive(node->left, value);
        } else if (value > node->value) {
            insertRecursive(node->right, value);
        }
    }

    static bool containsRecursive(const TreeNode* node, int target) {
        if (!node) {
            return false;
        }

        if (node->value == target) {
            return true;
        }

        return target < node->value
            ? containsRecursive(node->left.get(), target)
            : containsRecursive(node->right.get(), target);
    }

    static void inorderRecursive(
        const TreeNode* node,
        vector<int>& result
    ) {
        if (!node) {
            return;
        }

        inorderRecursive(node->left.get(), result);
        result.push_back(node->value);
        inorderRecursive(node->right.get(), result);
    }

    static int heightRecursive(const TreeNode* node) {
        if (!node) {
            return 0;
        }

        return 1 + max(
            heightRecursive(node->left.get()),
            heightRecursive(node->right.get())
        );
    }

public:
    void insert(int value) {
        insertRecursive(root, value);
    }

    bool contains(int value) const {
        return containsRecursive(root.get(), value);
    }

    vector<int> inorder() const {
        vector<int> result;
        inorderRecursive(root.get(), result);
        return result;
    }

    int height() const {
        return heightRecursive(root.get());
    }
};

long long factorialRecursive(int n) {
    if (n < 0) {
        throw invalid_argument("factorial requires n >= 0");
    }

    if (n <= 1) {
        return 1;
    }

    return n * factorialRecursive(n - 1);
}

long long fibonacciMemoized(
    int n,
    unordered_map<int, long long>& memo
) {
    if (n < 0) {
        throw invalid_argument("Fibonacci requires n >= 0");
    }

    if (n <= 1) {
        return n;
    }

    const auto found = memo.find(n);
    if (found != memo.end()) {
        return found->second;
    }

    const long long result =
        fibonacciMemoized(n - 1, memo) +
        fibonacciMemoized(n - 2, memo);

    memo[n] = result;
    return result;
}

double powerBySquaring(double base, long long exponent) {
    if (exponent == 0) {
        return 1.0;
    }

    if (exponent < 0) {
        if (base == 0.0) {
            throw domain_error("zero cannot have a negative exponent");
        }

        // Avoid -LLONG_MIN overflow by changing the base first.
        return powerBySquaring(1.0 / base, -(exponent + 1))
            * (1.0 / base);
    }

    const double half = powerBySquaring(base, exponent / 2);
    const double squared = half * half;

    return exponent % 2 == 0 ? squared : squared * base;
}

int main() {
    try {
        cout << "=== Recursive mathematical computation ===\n";
        cout << "7! = " << factorialRecursive(7) << '\n';

        unordered_map<int, long long> fibonacciCache{
            {0, 0},
            {1, 1}
        };
        cout << "F(40) = "
             << fibonacciMemoized(40, fibonacciCache)
             << '\n';

        cout << fixed << setprecision(2);
        cout << "3^15 = " << powerBySquaring(3.0, 15) << '\n';

        cout << "\n=== Repository dependency case study ===\n";

        DependencyAnalyzer analyzer;

        analyzer.addPackage("application", {
            "api",
            "database"
        });

        analyzer.addPackage("api", {
            "validation",
            "logging"
        });

        analyzer.addPackage("database", {
            "logging"
        });

        analyzer.addPackage("validation", {
            "logging"
        });

        analyzer.addPackage("logging", {});

        const vector<string> buildOrder =
            analyzer.resolveBuildOrder("application");

        cout << "Dependency resolution order:\n";
        for (const string& package : buildOrder) {
            cout << "  " << package << '\n';
        }

        cout << "\n=== Binary search tree case study ===\n";

        BinarySearchTree tree;

        for (int value : {50, 30, 70, 20, 40, 60, 80, 65}) {
            tree.insert(value);
        }

        cout << "Inorder traversal: ";
        for (int value : tree.inorder()) {
            cout << value << ' ';
        }
        cout << '\n';

        cout << "Contains 65: "
             << boolalpha
             << tree.contains(65)
             << '\n';

        cout << "Contains 99: "
             << tree.contains(99)
             << '\n';

        cout << "Tree height: " << tree.height() << '\n';

        cout << "\n=== Cycle detection failure ===\n";

        DependencyAnalyzer invalidAnalyzer;

        invalidAnalyzer.addPackage("service-a", {"service-b"});
        invalidAnalyzer.addPackage("service-b", {"service-c"});
        invalidAnalyzer.addPackage("service-c", {"service-a"});

        try {
            invalidAnalyzer.resolveBuildOrder("service-a");
        } catch (const runtime_error& error) {
            cout << "Rejected invalid graph: "
                 << error.what()
                 << '\n';
        }

        cout << "\n=== Complexity characteristics ===\n";
        cout << "Factorial recursion uses O(n) stack depth.\n";
        cout << "Memoized Fibonacci performs O(n) recursive states.\n";
        cout << "Exponentiation by squaring uses O(log n) recursive depth.\n";
        cout << "BST search is O(h), where h is tree height.\n";
        cout << "Depth-first dependency traversal is O(V + E) for V packages and E dependencies.\n";
        cout << "Cycle detection prevents unbounded recursion in cyclic dependency graphs.\n";
        cout << "A recursive implementation should impose depth or graph-size limits when input is externally controlled.\n";

    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
