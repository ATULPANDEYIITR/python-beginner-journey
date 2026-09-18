/*
 * WHILE LOOPS IN C++17
 * ====================
 *
 * Industry-style case study:
 * A resilient batch-processing service processes transaction records in
 * controlled batches. The program demonstrates while loops together with
 * validation, queues, retry logic, state machines, rate limiting, searching,
 * statistics, error handling, and complexity considerations.
 *
 * Compile:
 *     g++ -std=c++17 -O2 while_loops.cpp -o while_loops
 *
 * Run:
 *     ./while_loops
 */

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;


// ---------------------------------------------------------------------------
// BASIC DOMAIN MODEL
// ---------------------------------------------------------------------------

struct Transaction {
    long long id;
    string customer;
    double amount;
    string status;
};


// ---------------------------------------------------------------------------
// VALIDATION
// ---------------------------------------------------------------------------

bool isValidTransaction(const Transaction& transaction) {
    if (transaction.id <= 0) {
        return false;
    }

    if (transaction.customer.empty()) {
        return false;
    }

    if (!isfinite(transaction.amount) || transaction.amount < 0.0) {
        return false;
    }

    return true;
}


// ---------------------------------------------------------------------------
// WHILE-BASED BASIC PROCESSING
// ---------------------------------------------------------------------------

double calculateTotal(const vector<Transaction>& transactions) {
    double total = 0.0;
    size_t index = 0;

    while (index < transactions.size()) {
        if (isValidTransaction(transactions[index])) {
            total += transactions[index].amount;
        }

        ++index;
    }

    return total;
}


// ---------------------------------------------------------------------------
// TRANSACTION SERVICE
// ---------------------------------------------------------------------------

class TransactionProcessor {
private:
    vector<Transaction> accepted;
    vector<Transaction> rejected;

public:
    void ingest(const vector<Transaction>& input) {
        size_t index = 0;

        while (index < input.size()) {
            const Transaction& transaction = input[index];

            if (isValidTransaction(transaction)) {
                accepted.push_back(transaction);
            } else {
                rejected.push_back(transaction);
            }

            ++index;
        }
    }

    const vector<Transaction>& getAccepted() const {
        return accepted;
    }

    const vector<Transaction>& getRejected() const {
        return rejected;
    }

    double acceptedValue() const {
        return calculateTotal(accepted);
    }
};


// ---------------------------------------------------------------------------
// BOUNDED RETRY MECHANISM
// ---------------------------------------------------------------------------

class RetryPolicy {
private:
    int maximumAttempts;

public:
    explicit RetryPolicy(int maximumAttempts)
        : maximumAttempts(maximumAttempts) {
        if (maximumAttempts <= 0) {
            throw invalid_argument("maximumAttempts must be positive.");
        }
    }

    template <typename Operation>
    bool execute(Operation operation) const {
        int attempt = 1;

        while (attempt <= maximumAttempts) {
            try {
                if (operation(attempt)) {
                    return true;
                }
            } catch (const exception& error) {
                cerr << "Attempt " << attempt
                     << " failed: " << error.what() << '\n';
            }

            ++attempt;
        }

        return false;
    }
};


// ---------------------------------------------------------------------------
// QUEUE PROCESSOR
// ---------------------------------------------------------------------------

class BatchQueue {
private:
    queue<Transaction> pending;

public:
    void add(const Transaction& transaction) {
        pending.push(transaction);
    }

    size_t size() const {
        return pending.size();
    }

    template <typename Processor>
    size_t processAll(Processor processor) {
        size_t processed = 0;

        /*
         * std::queue::pop() removes the current front item in constant time.
         * The while condition directly expresses the business rule:
         * process while work remains.
         */
        while (!pending.empty()) {
            Transaction current = pending.front();
            pending.pop();

            processor(current);
            ++processed;
        }

        return processed;
    }
};


// ---------------------------------------------------------------------------
// STATE MACHINE
// ---------------------------------------------------------------------------

enum class TransactionState {
    Pending,
    Validated,
    Approved,
    Completed,
    Rejected
};

string stateName(TransactionState state) {
    switch (state) {
        case TransactionState::Pending:
            return "Pending";
        case TransactionState::Validated:
            return "Validated";
        case TransactionState::Approved:
            return "Approved";
        case TransactionState::Completed:
            return "Completed";
        case TransactionState::Rejected:
            return "Rejected";
    }

    throw logic_error("Unknown transaction state.");
}

class TransactionWorkflow {
private:
    TransactionState state = TransactionState::Pending;

public:
    TransactionState getState() const {
        return state;
    }

    void advance(bool valid, bool approved) {
        while (state != TransactionState::Completed &&
               state != TransactionState::Rejected) {

            if (state == TransactionState::Pending) {
                state = valid
                    ? TransactionState::Validated
                    : TransactionState::Rejected;
            } else if (state == TransactionState::Validated) {
                state = approved
                    ? TransactionState::Approved
                    : TransactionState::Rejected;
            } else if (state == TransactionState::Approved) {
                state = TransactionState::Completed;
            }
        }
    }
};


// ---------------------------------------------------------------------------
// BINARY SEARCH
// ---------------------------------------------------------------------------

int binarySearch(const vector<long long>& values, long long target) {
    if (values.empty()) {
        return -1;
    }

    long long low = 0;
    long long high = static_cast<long long>(values.size()) - 1;

    while (low <= high) {
        long long middle = low + (high - low) / 2;

        if (values[middle] == target) {
            return static_cast<int>(middle);
        }

        if (values[middle] < target) {
            low = middle + 1;
        } else {
            high = middle - 1;
        }
    }

    return -1;
}


// ---------------------------------------------------------------------------
// GREATEST COMMON DIVISOR
// ---------------------------------------------------------------------------

long long greatestCommonDivisor(long long a, long long b) {
    a = llabs(a);
    b = llabs(b);

    while (b != 0) {
        long long remainder = a % b;
        a = b;
        b = remainder;
    }

    return a;
}


// ---------------------------------------------------------------------------
// PRIME TEST
// ---------------------------------------------------------------------------

bool isPrime(long long number) {
    if (number < 2) {
        return false;
    }

    if (number == 2) {
        return true;
    }

    if (number % 2 == 0) {
        return false;
    }

    long long divisor = 3;

    while (divisor <= number / divisor) {
        if (number % divisor == 0) {
            return false;
        }

        divisor += 2;
    }

    return true;
}


// ---------------------------------------------------------------------------
// STATISTICS
// ---------------------------------------------------------------------------

struct Statistics {
    size_t count;
    double sum;
    double minimum;
    double maximum;
    double mean;
};

Statistics calculateStatistics(const vector<Transaction>& transactions) {
    if (transactions.empty()) {
        throw invalid_argument("Cannot calculate statistics for empty data.");
    }

    size_t index = 0;
    double sum = 0.0;
    double minimum = numeric_limits<double>::infinity();
    double maximum = -numeric_limits<double>::infinity();

    while (index < transactions.size()) {
        const double amount = transactions[index].amount;

        if (amount < minimum) {
            minimum = amount;
        }

        if (amount > maximum) {
            maximum = amount;
        }

        sum += amount;
        ++index;
    }

    return {
        transactions.size(),
        sum,
        minimum,
        maximum,
        sum / static_cast<double>(transactions.size())
    };
}


// ---------------------------------------------------------------------------
// SLIDING-WINDOW RATE LIMITER
// ---------------------------------------------------------------------------

class SlidingWindowLimiter {
private:
    queue<long long> timestamps;
    long long windowSize;
    size_t maximumRequests;

public:
    SlidingWindowLimiter(long long windowSize, size_t maximumRequests)
        : windowSize(windowSize),
          maximumRequests(maximumRequests) {

        if (windowSize <= 0 || maximumRequests == 0) {
            throw invalid_argument("Invalid rate limiter configuration.");
        }
    }

    bool allow(long long timestamp) {
        /*
         * Remove timestamps that have fallen outside the active window.
         * Each timestamp is inserted once and removed once, so across a
         * sequence of requests this queue processing is amortized O(n).
         */
        while (!timestamps.empty() &&
               timestamps.front() <= timestamp - windowSize) {
            timestamps.pop();
        }

        if (timestamps.size() >= maximumRequests) {
            return false;
        }

        timestamps.push(timestamp);
        return true;
    }
};


// ---------------------------------------------------------------------------
// BATCH VALIDATION AND PROCESSING
// ---------------------------------------------------------------------------

struct ProcessingReport {
    size_t processed = 0;
    size_t successful = 0;
    size_t failed = 0;
    double successfulValue = 0.0;
};

class BatchService {
private:
    size_t batchSize;
    RetryPolicy retryPolicy;

public:
    BatchService(size_t batchSize, int maximumAttempts)
        : batchSize(batchSize),
          retryPolicy(maximumAttempts) {

        if (batchSize == 0) {
            throw invalid_argument("Batch size must be positive.");
        }
    }

    ProcessingReport process(
        const vector<Transaction>& transactions
    ) const {
        ProcessingReport report;
        size_t position = 0;

        /*
         * Outer while controls batch progression.
         * Inner while controls items within the current batch.
         *
         * This separation makes the operational model explicit:
         *   dataset -> batches -> transactions.
         */
        while (position < transactions.size()) {
            size_t end = min(position + batchSize, transactions.size());

            while (position < end) {
                const Transaction& transaction = transactions[position];
                ++report.processed;

                if (!isValidTransaction(transaction)) {
                    ++report.failed;
                    ++position;
                    continue;
                }

                bool completed = retryPolicy.execute(
                    [&transaction](int attempt) {
                        /*
                         * Deterministic simulation:
                         * transaction 3 fails twice before succeeding.
                         * Other transactions succeed immediately.
                         */
                        if (transaction.id == 3 && attempt < 3) {
                            return false;
                        }

                        return true;
                    }
                );

                if (completed) {
                    ++report.successful;
                    report.successfulValue += transaction.amount;
                } else {
                    ++report.failed;
                }

                ++position;
            }
        }

        return report;
    }
};


// ---------------------------------------------------------------------------
// FRAUD-RULE STYLE THRESHOLD SCAN
// ---------------------------------------------------------------------------

vector<Transaction> findLargeTransactions(
    const vector<Transaction>& transactions,
    double threshold
) {
    if (threshold < 0.0) {
        throw invalid_argument("Threshold cannot be negative.");
    }

    vector<Transaction> result;
    size_t index = 0;

    while (index < transactions.size()) {
        if (transactions[index].amount > threshold) {
            result.push_back(transactions[index]);
        }

        ++index;
    }

    return result;
}


// ---------------------------------------------------------------------------
// CUSTOMER AGGREGATION
// ---------------------------------------------------------------------------

unordered_map<string, double> aggregateByCustomer(
    const vector<Transaction>& transactions
) {
    unordered_map<string, double> totals;
    size_t index = 0;

    while (index < transactions.size()) {
        const Transaction& transaction = transactions[index];

        if (isValidTransaction(transaction)) {
            totals[transaction.customer] += transaction.amount;
        }

        ++index;
    }

    return totals;
}


// ---------------------------------------------------------------------------
// REPORTING
// ---------------------------------------------------------------------------

void printTransactions(const vector<Transaction>& transactions) {
    size_t index = 0;

    while (index < transactions.size()) {
        const Transaction& transaction = transactions[index];

        cout << "ID=" << transaction.id
             << ", customer=" << transaction.customer
             << ", amount=" << fixed << setprecision(2)
             << transaction.amount
             << ", status=" << transaction.status
             << '\n';

        ++index;
    }
}


// ---------------------------------------------------------------------------
// EDGE CASE DEMONSTRATION
// ---------------------------------------------------------------------------

void demonstrateEdgeCases() {
    cout << "\nEDGE CASES\n";

    cout << "GCD(0, 24): "
         << greatestCommonDivisor(0, 24) << '\n';

    cout << "GCD(24, 0): "
         << greatestCommonDivisor(24, 0) << '\n';

    cout << "Binary search empty vector: "
         << binarySearch({}, 10) << '\n';

    cout << "Prime(1): "
         << boolalpha << isPrime(1) << '\n';

    cout << "Prime(97): "
         << boolalpha << isPrime(97) << '\n';

    /*
     * The following conceptual mistake is avoided:
     *
     * while (value != 1.0) {
     *     value += 0.1;
     * }
     *
     * Floating-point representations do not guarantee that repeated decimal
     * additions will produce exactly 1.0. Production numeric loops should
     * use a tolerance or a bounded iteration count when appropriate.
     */
}


// ---------------------------------------------------------------------------
// ASSERTION-STYLE TESTS
// ---------------------------------------------------------------------------

void runTests() {
    if (greatestCommonDivisor(48, 18) != 6) {
        throw runtime_error("GCD test failed.");
    }

    if (binarySearch({1, 3, 5, 7, 9}, 7) != 3) {
        throw runtime_error("Binary search test failed.");
    }

    if (binarySearch({1, 3, 5, 7, 9}, 8) != -1) {
        throw runtime_error("Binary search missing-value test failed.");
    }

    if (!isPrime(97) || isPrime(100)) {
        throw runtime_error("Prime test failed.");
    }

    cout << "\nAll tests passed.\n";
}


// ---------------------------------------------------------------------------
// MAIN CASE STUDY
// ---------------------------------------------------------------------------

int main() {
    try {
        cout << "============================================================\n";
        cout << "WHILE LOOPS IN C++17: TRANSACTION PROCESSING CASE STUDY\n";
        cout << "============================================================\n";

        vector<Transaction> transactions = {
            {1, "ALPHA", 1200.50, "PENDING"},
            {2, "BETA", 250.00, "PENDING"},
            {3, "ALPHA", 7800.00, "PENDING"},
            {4, "", 400.00, "PENDING"},
            {5, "GAMMA", -50.00, "PENDING"},
            {6, "BETA", 1500.75, "PENDING"},
            {7, "GAMMA", 3200.00, "PENDING"}
        };

        // ---------------------------------------------------------------
        // Stage 1: validation
        // ---------------------------------------------------------------

        TransactionProcessor processor;
        processor.ingest(transactions);

        cout << "\nVALID TRANSACTIONS\n";
        printTransactions(processor.getAccepted());

        cout << "\nREJECTED TRANSACTIONS\n";
        printTransactions(processor.getRejected());

        cout << "\nAccepted transaction value: "
             << fixed << setprecision(2)
             << processor.acceptedValue() << '\n';

        // ---------------------------------------------------------------
        // Stage 2: batch processing
        // ---------------------------------------------------------------

        BatchService service(2, 3);
        ProcessingReport report = service.process(transactions);

        cout << "\nBATCH PROCESSING REPORT\n";
        cout << "Processed: " << report.processed << '\n';
        cout << "Successful: " << report.successful << '\n';
        cout << "Failed: " << report.failed << '\n';
        cout << "Successful value: "
             << fixed << setprecision(2)
             << report.successfulValue << '\n';

        // ---------------------------------------------------------------
        // Stage 3: queue processing
        // ---------------------------------------------------------------

        BatchQueue queue;

        size_t index = 0;
        while (index < processor.getAccepted().size()) {
            queue.add(processor.getAccepted()[index]);
            ++index;
        }

        size_t processedFromQueue = queue.processAll(
            [](const Transaction& transaction) {
                cout << "Queue processed transaction "
                     << transaction.id << '\n';
            }
        );

        cout << "Queue processed count: "
             << processedFromQueue << '\n';

        // ---------------------------------------------------------------
        // Stage 4: state-machine workflow
        // ---------------------------------------------------------------

        TransactionWorkflow validWorkflow;
        validWorkflow.advance(true, true);

        cout << "\nVALID WORKFLOW FINAL STATE: "
             << stateName(validWorkflow.getState()) << '\n';

        TransactionWorkflow rejectedWorkflow;
        rejectedWorkflow.advance(false, false);

        cout << "INVALID WORKFLOW FINAL STATE: "
             << stateName(rejectedWorkflow.getState()) << '\n';

        // ---------------------------------------------------------------
        // Stage 5: rate limiting
        // ---------------------------------------------------------------

        SlidingWindowLimiter limiter(5, 3);

        vector<long long> requestTimes = {0, 1, 2, 3, 7, 8};
        index = 0;

        cout << "\nRATE LIMITING\n";

        while (index < requestTimes.size()) {
            const long long timestamp = requestTimes[index];

            cout << "Request at t=" << timestamp
                 << ": "
                 << (limiter.allow(timestamp) ? "ALLOWED" : "BLOCKED")
                 << '\n';

            ++index;
        }

        // ---------------------------------------------------------------
        // Stage 6: analytical processing
        // ---------------------------------------------------------------

        vector<Transaction> largeTransactions =
            findLargeTransactions(processor.getAccepted(), 1000.0);

        cout << "\nTRANSACTIONS ABOVE 1000\n";
        printTransactions(largeTransactions);

        Statistics statistics =
            calculateStatistics(processor.getAccepted());

        cout << "\nSTATISTICS\n";
        cout << "Count: " << statistics.count << '\n';
        cout << "Sum: " << statistics.sum << '\n';
        cout << "Minimum: " << statistics.minimum << '\n';
        cout << "Maximum: " << statistics.maximum << '\n';
        cout << "Mean: " << statistics.mean << '\n';

        // ---------------------------------------------------------------
        // Stage 7: customer aggregation
        // ---------------------------------------------------------------

        auto customerTotals =
            aggregateByCustomer(processor.getAccepted());

        cout << "\nCUSTOMER TOTALS\n";

        for (const auto& [customer, total] : customerTotals) {
            cout << customer << ": " << total << '\n';
        }

        /*
         * The range-based for loop above is intentionally used for reporting.
         * The case study's core state-driven processing remains implemented
         * with while loops. A while loop is not automatically superior to
         * every other loop construct. The appropriate construct depends on
         * the problem's natural control model.
         */

        // ---------------------------------------------------------------
        // Stage 8: classic algorithms
        // ---------------------------------------------------------------

        cout << "\nCLASSIC ALGORITHMS\n";

        cout << "GCD(84, 30): "
             << greatestCommonDivisor(84, 30) << '\n';

        vector<long long> sortedIds = {
            1, 3, 5, 7, 9, 11, 13
        };

        cout << "Binary search for 9: "
             << binarySearch(sortedIds, 9) << '\n';

        cout << "Binary search for 8: "
             << binarySearch(sortedIds, 8) << '\n';

        // ---------------------------------------------------------------
        // Stage 9: edge cases and tests
        // ---------------------------------------------------------------

        demonstrateEdgeCases();
        runTests();

        cout << "\nIMPLEMENTATION CONSIDERATIONS\n";
        cout << "1. A while loop is appropriate when termination depends on state.\n";
        cout << "2. Every iteration should make progress toward termination.\n";
        cout << "3. break is useful for early termination, but excessive use can\n";
        cout << "   make control flow harder to understand.\n";
        cout << "4. continue can simplify filtering but should preserve clarity.\n";
        cout << "5. Empty containers must be handled safely.\n";
        cout << "6. External input should be validated before processing.\n";
        cout << "7. Retry loops should always be bounded or cancellation-aware.\n";
        cout << "8. Long-running service loops need shutdown and resource controls.\n";
        cout << "9. Algorithmic complexity depends on the work inside the loop.\n";
        cout << "10. A while loop itself does not determine whether an algorithm is\n";
        cout << "    efficient; the operations performed per iteration do.\n";

        return 0;
    }
    catch (const exception& error) {
        cerr << "\nFatal error: " << error.what() << '\n';
        return 1;
    }
}
