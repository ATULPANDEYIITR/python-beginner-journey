#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <optional>
#include <queue>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

enum class JobStatus {
    Pending,
    Running,
    Completed,
    Failed
};

enum class Priority : int {
    Low = 1,
    Normal = 2,
    High = 3,
    Critical = 4
};

string toString(JobStatus status) {
    switch (status) {
        case JobStatus::Pending: return "PENDING";
        case JobStatus::Running: return "RUNNING";
        case JobStatus::Completed: return "COMPLETED";
        case JobStatus::Failed: return "FAILED";
    }
    throw logic_error("Unknown status");
}

struct Job {
    int id;
    string name;
    Priority priority;
    JobStatus status = JobStatus::Pending;
    int attempts = 0;
};

struct JobComparator {
    bool operator()(const Job& a, const Job& b) const {
        if (a.priority != b.priority) {
            return static_cast<int>(a.priority) <
                   static_cast<int>(b.priority);
        }
        return a.id > b.id;
    }
};

class JobEngine {
private:
    unordered_map<int, Job> jobs;

    const map<JobStatus, set<JobStatus>> transitions = {
        {JobStatus::Pending, {JobStatus::Running}},
        {JobStatus::Running,
            {JobStatus::Completed, JobStatus::Failed}},
        {JobStatus::Failed, {JobStatus::Pending}},
        {JobStatus::Completed, {}}
    };

public:
    void addJob(const Job& job) {
        if (job.id <= 0) {
            throw invalid_argument("Job ID must be positive");
        }

        if (job.name.empty()) {
            throw invalid_argument("Job name cannot be empty");
        }

        int priority = static_cast<int>(job.priority);

        if (priority < 1 || priority > 4) {
            throw invalid_argument("Invalid priority");
        }

        if (jobs.count(job.id)) {
            throw invalid_argument("Duplicate job ID");
        }

        jobs.emplace(job.id, job);
    }

    void transition(int id, JobStatus next) {
        auto iterator = jobs.find(id);

        if (iterator == jobs.end()) {
            throw out_of_range("Job does not exist");
        }

        Job& job = iterator->second;

        const auto& allowed = transitions.at(job.status);

        if (!allowed.count(next)) {
            throw logic_error(
                "Invalid transition: " +
                toString(job.status) + " -> " + toString(next)
            );
        }

        job.status = next;

        if (next == JobStatus::Running) {
            ++job.attempts;
        }
    }

    vector<Job> orderedJobs() const {
        vector<Job> result;

        for (const auto& entry : jobs) {
            result.push_back(entry.second);
        }

        sort(
            result.begin(),
            result.end(),
            [](const Job& a, const Job& b) {
                if (a.priority != b.priority) {
                    return static_cast<int>(a.priority) >
                           static_cast<int>(b.priority);
                }
                return a.id < b.id;
            }
        );

        return result;
    }

    map<string, int> statistics() const {
        map<string, int> result;

        for (const auto& entry : jobs) {
            ++result[toString(entry.second.status)];
        }

        return result;
    }

    optional<Job> find(int id) const {
        auto iterator = jobs.find(id);

        if (iterator == jobs.end()) {
            return nullopt;
        }

        return iterator->second;
    }

    void exportCsv(const string& filename) const {
        ofstream file(filename);

        if (!file) {
            throw runtime_error("Cannot open output file");
        }

        file << "id,name,priority,status,attempts\n";

        for (const Job& job : orderedJobs()) {
            string escapedName = job.name;

            size_t position = 0;

            while ((position = escapedName.find('"', position))
                   != string::npos) {
                escapedName.insert(position, "\"");
                position += 2;
            }

            file << job.id << ",\""
                 << escapedName << "\","
                 << static_cast<int>(job.priority) << ","
                 << toString(job.status) << ","
                 << job.attempts << "\n";
        }

        if (!file) {
            throw runtime_error("Failed writing CSV");
        }
    }
};

class DependencyGraph {
private:
    map<int, vector<int>> adjacency;

public:
    void addDependency(int job, int dependency) {
        if (job <= 0 || dependency <= 0 || job == dependency) {
            throw invalid_argument("Invalid dependency");
        }

        adjacency[job].push_back(dependency);
        adjacency.try_emplace(dependency);
    }

    bool hasCycle() const {
        enum class Color {
            White,
            Gray,
            Black
        };

        map<int, Color> colors;

        for (const auto& entry : adjacency) {
            colors[entry.first] = Color::White;
        }

        function<bool(int)> visit = [&](int node) {
            colors[node] = Color::Gray;

            auto iterator = adjacency.find(node);

            if (iterator != adjacency.end()) {
                for (int neighbor : iterator->second) {
                    if (colors[neighbor] == Color::Gray) {
                        return true;
                    }

                    if (
                        colors[neighbor] == Color::White &&
                        visit(neighbor)
                    ) {
                        return true;
                    }
                }
            }

            colors[node] = Color::Black;
            return false;
        };

        for (const auto& entry : adjacency) {
            if (
                colors[entry.first] == Color::White &&
                visit(entry.first)
            ) {
                return true;
            }
        }

        return false;
    }

    vector<int> topologicalOrder() const {
        if (hasCycle()) {
            throw logic_error("Dependency cycle detected");
        }

        map<int, int> indegree;

        for (const auto& entry : adjacency) {
            indegree.try_emplace(entry.first, 0);

            for (int dependency : entry.second) {
                ++indegree[dependency];
            }
        }

        queue<int> ready;

        for (const auto& entry : indegree) {
            if (entry.second == 0) {
                ready.push(entry.first);
            }
        }

        vector<int> result;

        while (!ready.empty()) {
            int current = ready.front();
            ready.pop();

            result.push_back(current);

            for (int dependency : adjacency.at(current)) {
                if (--indegree[dependency] == 0) {
                    ready.push(dependency);
                }
            }
        }

        return result;
    }
};

class RateLimiter {
private:
    struct Entry {
        chrono::steady_clock::time_point windowStart;
        int requests = 0;
    };

    map<string, Entry> clients;
    int limit;
    chrono::seconds window;

public:
    RateLimiter(int maximum, chrono::seconds duration)
        : limit(maximum), window(duration) {
        if (limit <= 0 || duration.count() <= 0) {
            throw invalid_argument("Invalid rate limit configuration");
        }
    }

    bool allow(const string& client) {
        if (client.empty()) {
            return false;
        }

        auto now = chrono::steady_clock::now();
        auto& entry = clients[client];

        if (
            entry.requests == 0 ||
            now - entry.windowStart >= window
        ) {
            entry.windowStart = now;
            entry.requests = 0;
        }

        if (entry.requests >= limit) {
            return false;
        }

        ++entry.requests;
        return true;
    }
};

double calculateMean(const vector<double>& values) {
    if (values.empty()) {
        throw invalid_argument("Empty numeric collection");
    }

    return accumulate(values.begin(), values.end(), 0.0) /
           values.size();
}

string sha256UnavailableSafeDigest(const string& value) {
    // Standard C++17 has no cryptographic hash implementation.
    // This FNV-1a checksum is for non-security identification only.
    uint64_t hash = 14695981039346656037ULL;

    for (unsigned char character : value) {
        hash ^= character;
        hash *= 1099511628211ULL;
    }

    ostringstream output;
    output << hex << setw(16) << setfill('0') << hash;
    return output.str();
}

void runTests() {
    JobEngine engine;

    engine.addJob({1, "Unit test", Priority::High});

    engine.transition(1, JobStatus::Running);
    engine.transition(1, JobStatus::Completed);

    if (
        engine.find(1)->status != JobStatus::Completed
    ) {
        throw runtime_error("Job transition test failed");
    }

    bool rejected = false;

    try {
        engine.transition(1, JobStatus::Running);
    } catch (const logic_error&) {
        rejected = true;
    }

    if (!rejected) {
        throw runtime_error("Invalid transition was accepted");
    }

    DependencyGraph graph;
    graph.addDependency(1, 2);
    graph.addDependency(2, 3);

    if (graph.hasCycle()) {
        throw runtime_error("Unexpected graph cycle");
    }

    DependencyGraph cyclic;
    cyclic.addDependency(1, 2);
    cyclic.addDependency(2, 1);

    if (!cyclic.hasCycle()) {
        throw runtime_error("Cycle detection failed");
    }

    if (calculateMean({10, 20, 30}) != 20) {
        throw runtime_error("Mean calculation failed");
    }

    cout << "All C++ tests passed.\n";
}

int main() {
    try {
        JobEngine engine;

        engine.addJob({
            1001,
            "Import operational records",
            Priority::High
        });

        engine.addJob({
            1002,
            "Validate security controls",
            Priority::Critical
        });

        engine.addJob({
            1003,
            "Generate analytics report",
            Priority::Normal
        });

        engine.transition(1001, JobStatus::Running);
        engine.transition(1001, JobStatus::Completed);

        engine.transition(1002, JobStatus::Running);
        engine.transition(1002, JobStatus::Failed);
        engine.transition(1002, JobStatus::Pending);

        DependencyGraph dependencies;

        dependencies.addDependency(1003, 1001);
        dependencies.addDependency(1003, 1002);

        cout << "JOB QUEUE\n";

        for (const Job& job : engine.orderedJobs()) {
            cout << job.id << " | "
                 << job.name << " | "
                 << static_cast<int>(job.priority) << " | "
                 << toString(job.status) << " | "
                 << job.attempts << "\n";
        }

        cout << "\nJOB STATISTICS\n";

        for (const auto& entry : engine.statistics()) {
            cout << entry.first << ": "
                 << entry.second << "\n";
        }

        cout << "\nDEPENDENCY ORDER\n";

        for (int id : dependencies.topologicalOrder()) {
            cout << id << " ";
        }

        cout << "\n";

        RateLimiter limiter(3, chrono::seconds(60));

        cout << "\nRATE LIMITING\n";

        for (int i = 1; i <= 5; ++i) {
            cout << "Request " << i << ": "
                 << (limiter.allow("client-A")
                     ? "ALLOWED" : "REJECTED")
                 << "\n";
        }

        cout << "\nNUMERIC ANALYSIS\n";

        vector<double> measurements = {
            12.5, 15.0, 18.5, 20.0, 24.0
        };

        cout << "Mean: "
             << calculateMean(measurements)
             << "\n";

        cout << "\nNON-CRYPTOGRAPHIC CHECKSUM\n";
        cout << sha256UnavailableSafeDigest(
            "Python Standard Library"
        ) << "\n";

        engine.exportCsv("cpp_jobs.csv");

        runTests();

        cout << "CSV export completed.\n";

    } catch (const exception& error) {
        cerr << "Execution failed: "
             << error.what() << "\n";

        return 1;
    }

    return 0;
}
