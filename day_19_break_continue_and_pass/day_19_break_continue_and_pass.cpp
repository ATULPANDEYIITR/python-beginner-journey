/*
 * break, continue, and pass in Python:
 * A C++ technical case study
 *
 * Scenario:
 * ----------
 * A security-monitoring service receives a stream of device events.
 *
 * The system must:
 *   1. Ignore inactive devices.
 *   2. Ignore malformed events.
 *   3. Ignore ordinary debug records.
 *   4. Count valid events.
 *   5. Stop processing when a critical shutdown event is received.
 *   6. Search nested structures efficiently.
 *   7. Demonstrate the C++ equivalents of Python's break and continue.
 *
 * C++ does not have Python's pass statement.
 * An empty block or a deliberately unused branch can represent a no-op,
 * but production code should make intentional inactivity clear.
 *
 * Build:
 *   g++ -std=c++17 -Wall -Wextra -pedantic -O2 main.cpp -o monitor
 *
 * Run:
 *   ./monitor
 */

#include <algorithm>
#include <cassert>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

using namespace std;

// ---------------------------------------------------------------------------
// Basic domain types
// ---------------------------------------------------------------------------

enum class Severity {
    Debug,
    Info,
    Warning,
    Error,
    Critical
};

string severityToString(Severity severity) {
    switch (severity) {
        case Severity::Debug:
            return "DEBUG";
        case Severity::Info:
            return "INFO";
        case Severity::Warning:
            return "WARNING";
        case Severity::Error:
            return "ERROR";
        case Severity::Critical:
            return "CRITICAL";
    }

    return "UNKNOWN";
}

struct DeviceEvent {
    string deviceId;
    Severity severity;
    string message;
    bool active;
    optional<double> value;
};

// ---------------------------------------------------------------------------
// Utility output
// ---------------------------------------------------------------------------

void section(const string& title) {
    cout << "\n" << string(78, '=') << '\n';
    cout << title << '\n';
    cout << string(78, '=') << '\n';
}

// ---------------------------------------------------------------------------
// 1. Basic break
// ---------------------------------------------------------------------------

void basicBreak() {
    section("1. Basic break");

    vector<int> processed;

    for (int number = 1; number <= 10; ++number) {
        if (number == 6) {
            break;
        }

        processed.push_back(number);
    }

    cout << "Values before break: ";

    for (int value : processed) {
        cout << value << ' ';
    }

    cout << '\n';
}

// ---------------------------------------------------------------------------
// 2. Basic continue
// ---------------------------------------------------------------------------

void basicContinue() {
    section("2. Basic continue");

    vector<int> oddNumbers;

    for (int number = 1; number <= 10; ++number) {
        if (number % 2 == 0) {
            continue;
        }

        oddNumbers.push_back(number);
    }

    cout << "Odd numbers: ";

    for (int value : oddNumbers) {
        cout << value << ' ';
    }

    cout << '\n';
}

// ---------------------------------------------------------------------------
// 3. Python pass equivalent
// ---------------------------------------------------------------------------

void basicNoOp() {
    section("3. Python pass equivalent");

    /*
     * C++ has no pass keyword.
     *
     * A standalone empty statement:
     *     ;
     *
     * or an empty block:
     *     {}
     *
     * can represent a no-op.
     *
     * It should be used deliberately because unexplained empty statements
     * can hide programming mistakes.
     */

    vector<int> values;

    for (int number = 1; number <= 5; ++number) {
        if (number == 3) {
            // Intentional no-op. Equivalent in spirit to Python's pass.
        }

        values.push_back(number);
    }

    cout << "Values after intentional no-op: ";

    for (int value : values) {
        cout << value << ' ';
    }

    cout << '\n';
}

// ---------------------------------------------------------------------------
// 4. Domain validation
// ---------------------------------------------------------------------------

bool isValidEvent(const DeviceEvent& event) {
    if (event.deviceId.empty()) {
        return false;
    }

    if (event.message.empty()) {
        return false;
    }

    if (!event.active) {
        return false;
    }

    if (event.value.has_value()) {
        const double value = *event.value;

        if (!std::isfinite(value)) {
            return false;
        }
    }

    return true;
}

// ---------------------------------------------------------------------------
// 5. Event analyzer
// ---------------------------------------------------------------------------

class EventAnalyzer {
private:
    size_t processedEvents_ = 0;
    size_t warningEvents_ = 0;
    size_t errorEvents_ = 0;
    optional<string> criticalDevice_;

public:
    void reset() {
        processedEvents_ = 0;
        warningEvents_ = 0;
        errorEvents_ = 0;
        criticalDevice_.reset();
    }

    void process(const vector<DeviceEvent>& events) {
        reset();

        for (const DeviceEvent& event : events) {
            /*
             * continue means:
             * skip this record and move to the next iteration.
             */
            if (!event.active) {
                continue;
            }

            if (!isValidEvent(event)) {
                continue;
            }

            /*
             * break means:
             * terminate the nearest enclosing loop.
             *
             * Here it models a critical operational boundary. Once a
             * critical event is received, later events are deliberately not
             * processed by this analysis pass.
             */
            if (event.severity == Severity::Critical) {
                criticalDevice_ = event.deviceId;
                break;
            }

            /*
             * Debug events are not operational metrics.
             * They are skipped with continue.
             */
            if (event.severity == Severity::Debug) {
                continue;
            }

            ++processedEvents_;

            if (event.severity == Severity::Warning) {
                ++warningEvents_;
            }

            if (event.severity == Severity::Error) {
                ++errorEvents_;
            }

            /*
             * Intentional no-op:
             *
             * For ordinary INFO records there is no additional action.
             * C++ does not require a pass statement to make this legal.
             */
        }
    }

    size_t processedEvents() const {
        return processedEvents_;
    }

    size_t warningEvents() const {
        return warningEvents_;
    }

    size_t errorEvents() const {
        return errorEvents_;
    }

    const optional<string>& criticalDevice() const {
        return criticalDevice_;
    }
};

// ---------------------------------------------------------------------------
// 6. Device registry
// ---------------------------------------------------------------------------

class DeviceRegistry {
private:
    set<string> registeredDevices_;

public:
    bool registerDevice(const string& deviceId) {
        if (deviceId.empty()) {
            return false;
        }

        return registeredDevices_.insert(deviceId).second;
    }

    bool contains(const string& deviceId) const {
        return registeredDevices_.find(deviceId) != registeredDevices_.end();
    }

    size_t size() const {
        return registeredDevices_.size();
    }
};

// ---------------------------------------------------------------------------
// 7. Nested search
// ---------------------------------------------------------------------------

optional<pair<size_t, size_t>> findValue(
    const vector<vector<int>>& matrix,
    int target
) {
    optional<pair<size_t, size_t>> result;

    /*
     * break only exits the nearest loop.
     *
     * A flag/result is therefore used to determine whether the outer loop
     * should also terminate.
     */
    for (size_t row = 0; row < matrix.size(); ++row) {
        for (size_t column = 0; column < matrix[row].size(); ++column) {
            if (matrix[row][column] == target) {
                result = make_pair(row, column);
                break;
            }
        }

        if (result.has_value()) {
            break;
        }
    }

    return result;
}

// ---------------------------------------------------------------------------
// 8. Labeled-break equivalent through a function return
// ---------------------------------------------------------------------------

optional<pair<size_t, size_t>> findValueWithEarlyReturn(
    const vector<vector<int>>& matrix,
    int target
) {
    for (size_t row = 0; row < matrix.size(); ++row) {
        for (size_t column = 0; column < matrix[row].size(); ++column) {
            if (matrix[row][column] == target) {
                /*
                 * Returning from the function exits both loops.
                 * This can be cleaner than maintaining a separate flag.
                 */
                return make_pair(row, column);
            }
        }
    }

    return nullopt;
}

// ---------------------------------------------------------------------------
// 9. Efficient duplicate detection
// ---------------------------------------------------------------------------

bool containsDuplicate(const vector<int>& values) {
    unordered_set<int> seen;

    for (int value : values) {
        if (seen.find(value) != seen.end()) {
            /*
             * Early return avoids processing the remainder of the input.
             */
            return true;
        }

        seen.insert(value);
    }

    return false;
}

// ---------------------------------------------------------------------------
// 10. Sensor threshold processing
// ---------------------------------------------------------------------------

struct SensorReport {
    size_t processed = 0;
    size_t warnings = 0;
    optional<string> criticalSensor;
    optional<double> maximumTemperature;
};

SensorReport analyzeSensors(
    const vector<DeviceEvent>& events,
    double warningThreshold,
    double criticalThreshold
) {
    if (warningThreshold >= criticalThreshold) {
        throw invalid_argument(
            "warning threshold must be below critical threshold"
        );
    }

    SensorReport report;

    for (const DeviceEvent& event : events) {
        if (!event.active) {
            continue;
        }

        if (!event.value.has_value()) {
            continue;
        }

        const double temperature = *event.value;

        if (!std::isfinite(temperature)) {
            continue;
        }

        /*
         * Update the maximum only for values that are actually processed.
         */
        if (!report.maximumTemperature.has_value() ||
            temperature > *report.maximumTemperature) {
            report.maximumTemperature = temperature;
        }

        if (temperature >= criticalThreshold) {
            report.criticalSensor = event.deviceId;
            break;
        }

        if (temperature >= warningThreshold) {
            ++report.warnings;
            ++report.processed;
            continue;
        }

        ++report.processed;

        /*
         * Ordinary temperature:
         * intentionally no additional action.
         */
    }

    return report;
}

// ---------------------------------------------------------------------------
// 11. Input parsing
// ---------------------------------------------------------------------------

optional<int> parsePositiveInteger(const string& text) {
    if (text.empty()) {
        return nullopt;
    }

    try {
        size_t consumed = 0;
        long long value = stoll(text, &consumed);

        if (consumed != text.size()) {
            return nullopt;
        }

        if (value <= 0 ||
            value > numeric_limits<int>::max()) {
            return nullopt;
        }

        return static_cast<int>(value);
    } catch (const invalid_argument&) {
        return nullopt;
    } catch (const out_of_range&) {
        return nullopt;
    }
}

vector<int> parsePositiveIntegers(const vector<string>& inputs) {
    vector<int> result;

    for (const string& input : inputs) {
        optional<int> parsed = parsePositiveInteger(input);

        if (!parsed.has_value()) {
            continue;
        }

        result.push_back(*parsed);
    }

    return result;
}

// ---------------------------------------------------------------------------
// 12. Reporting
// ---------------------------------------------------------------------------

void printEventReport(
    const EventAnalyzer& analyzer,
    const string& title
) {
    cout << title << '\n';
    cout << "Processed events: " << analyzer.processedEvents() << '\n';
    cout << "Warnings: " << analyzer.warningEvents() << '\n';
    cout << "Errors: " << analyzer.errorEvents() << '\n';

    if (analyzer.criticalDevice().has_value()) {
        cout << "Critical device: "
             << *analyzer.criticalDevice()
             << '\n';
    } else {
        cout << "Critical device: none\n";
    }
}

// ---------------------------------------------------------------------------
// 13. Main technical case study
// ---------------------------------------------------------------------------

void runCaseStudy() {
    section("4. Industry-style device event monitoring");

    vector<DeviceEvent> events = {
        {"DEV-001", Severity::Info, "Heartbeat received", true, 21.5},
        {"DEV-002", Severity::Debug, "Internal diagnostic", true, 20.0},
        {"DEV-003", Severity::Warning, "Temperature elevated", true, 31.0},
        {"DEV-004", Severity::Error, "Network retry", true, 42.0},
        {"DEV-005", Severity::Info, "", true, 20.0},
        {"DEV-006", Severity::Info, "Device inactive", false, 25.0},
        {"DEV-007", Severity::Critical, "Thermal shutdown", true, 85.0},
        {"DEV-008", Severity::Error, "Later event", true, 50.0}
    };

    EventAnalyzer analyzer;
    analyzer.process(events);

    printEventReport(analyzer, "Operational event report");

    /*
     * DEV-008 is intentionally not processed because the critical event
     * caused break to terminate the processing loop.
     */
}

// ---------------------------------------------------------------------------
// 14. Matrix case study
// ---------------------------------------------------------------------------

void runMatrixCaseStudy() {
    section("5. Nested data search");

    vector<vector<int>> matrix = {
        {10, 20, 30},
        {40, 50, 60},
        {70, 80, 90}
    };

    auto result = findValue(matrix, 80);

    if (result.has_value()) {
        cout << "80 found at row "
             << result->first
             << ", column "
             << result->second
             << '\n';
    } else {
        cout << "80 was not found\n";
    }

    auto missing = findValueWithEarlyReturn(matrix, 999);

    cout << "999 found: "
         << boolalpha
         << missing.has_value()
         << '\n';
}

// ---------------------------------------------------------------------------
// 15. Validation case study
// ---------------------------------------------------------------------------

void runValidationCaseStudy() {
    section("6. Input validation");

    vector<string> inputs = {
        "10",
        "abc",
        "-5",
        "42",
        "3.14",
        "100",
        "",
        "999999999999999999999999"
    };

    vector<int> valid = parsePositiveIntegers(inputs);

    cout << "Valid positive integers: ";

    for (int value : valid) {
        cout << value << ' ';
    }

    cout << '\n';
}

// ---------------------------------------------------------------------------
// 16. Sensor case study
// ---------------------------------------------------------------------------

void runSensorCaseStudy() {
    section("7. Sensor threshold analysis");

    vector<DeviceEvent> sensors = {
        {"S-01", Severity::Info, "Normal", true, 22.0},
        {"S-02", Severity::Info, "Missing reading", true, nullopt},
        {"S-03", Severity::Info, "Inactive", false, 29.0},
        {"S-04", Severity::Info, "High temperature", true, 35.0},
        {"S-05", Severity::Critical, "Critical temperature", true, 85.0},
        {"S-06", Severity::Info, "After critical", true, 40.0}
    };

    try {
        SensorReport report = analyzeSensors(sensors, 30.0, 80.0);

        cout << "Processed readings: "
             << report.processed
             << '\n';

        cout << "Warnings: "
             << report.warnings
             << '\n';

        if (report.criticalSensor.has_value()) {
            cout << "Critical sensor: "
                 << *report.criticalSensor
                 << '\n';
        }

        if (report.maximumTemperature.has_value()) {
            cout << fixed
                 << setprecision(1)
                 << "Maximum processed temperature: "
                 << *report.maximumTemperature
                 << '\n';
        }
    } catch (const invalid_argument& error) {
        cerr << "Sensor configuration error: "
             << error.what()
             << '\n';
    }
}

// ---------------------------------------------------------------------------
// 17. Tests
// ---------------------------------------------------------------------------

void runTests() {
    section("8. Tests");

    {
        vector<int> result;

        for (int number = 0; number < 5; ++number) {
            if (number == 3) {
                break;
            }

            result.push_back(number);
        }

        assert((result == vector<int>{0, 1, 2}));
    }

    {
        vector<int> result;

        for (int number = 0; number < 5; ++number) {
            if (number == 3) {
                continue;
            }

            result.push_back(number);
        }

        assert((result == vector<int>{0, 1, 2, 4}));
    }

    {
        vector<string> inputs = {"5", "bad", "-2", "10"};
        vector<int> expected = {5, 10};

        assert(parsePositiveIntegers(inputs) == expected);
    }

    {
        vector<int> values = {1, 2, 3, 2};
        assert(containsDuplicate(values));
    }

    {
        vector<int> values = {1, 2, 3, 4};
        assert(!containsDuplicate(values));
    }

    {
        vector<vector<int>> matrix = {
            {1, 2},
            {3, 4}
        };

        auto result = findValue(matrix, 4);

        assert(result.has_value());
        assert(result->first == 1);
        assert(result->second == 1);
    }

    cout << "All assertions passed.\n";
}

// ---------------------------------------------------------------------------
// 18. Complexity demonstration
// ---------------------------------------------------------------------------

void explainComplexityThroughCode() {
    section("9. Complexity considerations");

    /*
     * Set-based duplicate detection:
     *
     * Average time: O(n)
     * Auxiliary space: O(n)
     *
     * The loop can return immediately after finding a duplicate.
     */
    vector<int> values = {10, 20, 30, 40, 50, 30};

    cout << "Duplicate detected: "
         << boolalpha
         << containsDuplicate(values)
         << '\n';

    /*
     * break and continue affect control flow.
     * They do not automatically make an algorithm asymptotically faster.
     *
     * A poorly designed O(n^2) algorithm remains O(n^2) even if break often
     * produces early termination on typical data.
     */
}

// ---------------------------------------------------------------------------
// 19. Main
// ---------------------------------------------------------------------------

int main() {
    try {
        basicBreak();
        basicContinue();
        basicNoOp();

        runCaseStudy();
        runMatrixCaseStudy();
        runValidationCaseStudy();
        runSensorCaseStudy();
        runTests();
        explainComplexityThroughCode();

        section("10. Program completed");
        cout << "All C++ demonstrations completed successfully.\n";

        return 0;
    } catch (const exception& error) {
        cerr << "Unhandled error: "
             << error.what()
             << '\n';

        return 1;
    }
}
