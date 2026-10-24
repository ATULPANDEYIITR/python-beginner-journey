#include <algorithm>
#include <cassert>
#include <chrono>
#include <cmath>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

class ValidationError : public std::runtime_error {
public:
    explicit ValidationError(const std::string& message)
        : std::runtime_error(message) {}
};

enum class TaskStatus {
    Pending,
    Running,
    Completed,
    Failed
};

std::string toString(TaskStatus status) {
    switch (status) {
        case TaskStatus::Pending: return "pending";
        case TaskStatus::Running: return "running";
        case TaskStatus::Completed: return "completed";
        case TaskStatus::Failed: return "failed";
    }
    return "unknown";
}

struct Statistics {
    std::size_t count;
    double minimum;
    double maximum;
    double mean;
    double populationStdDev;
};

Statistics calculateStatistics(const std::vector<double>& values) {
    if (values.empty()) {
        throw ValidationError("At least one numeric value is required.");
    }

    for (double value : values) {
        if (!std::isfinite(value)) {
            throw ValidationError("All values must be finite.");
        }
    }

    const double total =
        std::accumulate(values.begin(), values.end(), 0.0);

    const double mean = total / static_cast<double>(values.size());

    double squaredDifference = 0.0;
    for (double value : values) {
        const double difference = value - mean;
        squaredDifference += difference * difference;
    }

    const double variance =
        squaredDifference / static_cast<double>(values.size());

    const auto [minimum, maximum] =
        std::minmax_element(values.begin(), values.end());

    return {
        values.size(),
        *minimum,
        *maximum,
        mean,
        std::sqrt(variance)
    };
}

std::vector<std::string> normalizeTags(
    const std::vector<std::string>& tags
) {
    std::set<std::string> uniqueTags;

    for (const std::string& tag : tags) {
        std::string normalized;

        std::copy_if(
            tag.begin(),
            tag.end(),
            std::back_inserter(normalized),
            [](unsigned char character) {
                return !std::isspace(character);
            }
        );

        if (normalized.empty()) {
            continue;
        }

        if (normalized.size() > 40) {
            throw ValidationError("A tag cannot exceed 40 characters.");
        }

        std::transform(
            normalized.begin(),
            normalized.end(),
            normalized.begin(),
            [](unsigned char character) {
                return static_cast<char>(std::tolower(character));
            }
        );

        uniqueTags.insert(normalized);
    }

    return {
        uniqueTags.begin(),
        uniqueTags.end()
    };
}

std::vector<std::vector<int>> chunk(
    const std::vector<int>& values,
    std::size_t size
) {
    if (size == 0) {
        throw ValidationError("Chunk size must be greater than zero.");
    }

    std::vector<std::vector<int>> result;

    for (std::size_t index = 0; index < values.size(); index += size) {
        const auto end =
            std::min(index + size, values.size());

        result.emplace_back(
            values.begin() + static_cast<std::ptrdiff_t>(index),
            values.begin() + static_cast<std::ptrdiff_t>(end)
        );
    }

    return result;
}

class FunctionRegistry {
public:
    using Function = std::function<std::string(const std::string&)>;

    struct Metrics {
        std::size_t calls = 0;
        std::size_t failures = 0;
        double milliseconds = 0.0;
    };

    void registerFunction(
        const std::string& name,
        Function function
    ) {
        if (name.empty()) {
            throw ValidationError("Function name cannot be empty.");
        }

        if (!function) {
            throw ValidationError("Function must be callable.");
        }

        if (functions_.contains(name)) {
            throw ValidationError("Function already registered: " + name);
        }

        functions_.emplace(name, std::move(function));
        metrics_.emplace(name, Metrics{});
    }

    std::string call(
        const std::string& name,
        const std::string& input
    ) {
        const auto iterator = functions_.find(name);

        if (iterator == functions_.end()) {
            throw std::out_of_range("Unknown function: " + name);
        }

        Metrics& metrics = metrics_.at(name);
        ++metrics.calls;

        const auto started = std::chrono::steady_clock::now();

        try {
            return iterator->second(input);
        } catch (...) {
            ++metrics.failures;
            throw;
        } finally_unavailable:
        return {};
    }

    Metrics getMetrics(const std::string& name) const {
        const auto iterator = metrics_.find(name);

        if (iterator == metrics_.end()) {
            throw std::out_of_range("Unknown function: " + name);
        }

        return iterator->second;
    }

private:
    std::unordered_map<std::string, Function> functions_;
    std::unordered_map<std::string, Metrics> metrics_;
};

std::string normalizeTagInput(const std::string& input) {
    std::vector<std::string> tags;
    std::string current;

    for (char character : input) {
        if (character == ',') {
            if (!current.empty()) {
                tags.push_back(current);
            }
            current.clear();
        } else {
            current += character;
        }
    }

    if (!current.empty()) {
        tags.push_back(current);
    }

    const auto normalized = normalizeTags(tags);

    std::string output;
    for (std::size_t i = 0; i < normalized.size(); ++i) {
        if (i > 0) {
            output += ",";
        }
        output += normalized[i];
    }

    return output;
}

std::string statisticsInput(const std::string& input) {
    std::vector<double> values;
    std::string current;

    for (char character : input) {
        if (character == ',') {
            if (!current.empty()) {
                values.push_back(std::stod(current));
            }
            current.clear();
        } else {
            current += character;
        }
    }

    if (!current.empty()) {
        values.push_back(std::stod(current));
    }

    const Statistics statistics = calculateStatistics(values);

    std::ostringstream output;
    output << std::fixed << std::setprecision(3)
           << "count=" << statistics.count
           << ",mean=" << statistics.mean
           << ",min=" << statistics.minimum
           << ",max=" << statistics.maximum
           << ",stddev=" << statistics.populationStdDev;

    return output.str();
}

int main() {
    try {
        const auto tags = normalizeTags(
            {" C++ ", "functions", "C++", "reuse"}
        );

        std::cout << "Normalized tags:";
        for (const auto& tag : tags) {
            std::cout << " " << tag;
        }
        std::cout << '\n';

        const Statistics statistics =
            calculateStatistics({10, 20, 30, 40, 50});

        std::cout << std::fixed << std::setprecision(3)
                  << "Mean: " << statistics.mean << '\n'
                  << "Population standard deviation: "
                  << statistics.populationStdDev << '\n';

        const auto batches = chunk({1, 2, 3, 4, 5}, 2);

        std::cout << "Chunks:\n";
        for (const auto& batch : batches) {
            std::cout << "[";
            for (std::size_t index = 0; index < batch.size(); ++index) {
                if (index > 0) {
                    std::cout << ", ";
                }
                std::cout << batch[index];
            }
            std::cout << "]\n";
        }

        FunctionRegistry registry;

        registry.registerFunction(
            "normalize",
            normalizeTagInput
        );

        registry.registerFunction(
            "statistics",
            statisticsInput
        );

        std::cout << "Registry normalize: "
                  << registry.call(
                         "normalize",
                         "API,api,database"
                     )
                  << '\n';

        std::cout << "Registry statistics: "
                  << registry.call(
                         "statistics",
                         "4,8,15,16,23,42"
                     )
                  << '\n';

        assert(
            normalizeTags({"A", "a", "B"}) ==
            std::vector<std::string>{"a", "b"}
        );

        assert(
            calculateStatistics({10, 20}).mean == 15.0
        );

        try {
            calculateStatistics({});
            assert(false);
        } catch (const ValidationError&) {
            std::cout << "Empty-input validation passed.\n";
        }

        try {
            chunk({1, 2}, 0);
            assert(false);
        } catch (const ValidationError&) {
            std::cout << "Chunk-size validation passed.\n";
        }

    } catch (const std::exception& error) {
        std::cerr << "Execution failed: "
                  << error.what() << '\n';
        return 1;
    }

    return 0;
}
