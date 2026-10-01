#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

/*
 * String Methods Case Study:
 *
 * A C++17 repository-import service receives textual deployment records.
 * The service must normalize fields, validate identifiers, parse structured
 * records, classify operations, redact sensitive values, and produce an
 * audit report.
 *
 * The implementation intentionally uses C++ string facilities rather than
 * reproducing a Python or JavaScript string-method laboratory.
 */

namespace text {

std::string trim(std::string_view input) {
    const auto not_space = [](unsigned char character) {
        return !std::isspace(character);
    };

    std::size_t first = 0;
    while (first < input.size() &&
           std::isspace(static_cast<unsigned char>(input[first]))) {
        ++first;
    }

    std::size_t last = input.size();
    while (last > first &&
           std::isspace(static_cast<unsigned char>(input[last - 1]))) {
        --last;
    }

    return std::string(input.substr(first, last - first));
}

std::string to_lower_ascii(std::string value) {
    std::transform(
        value.begin(),
        value.end(),
        value.begin(),
        [](unsigned char character) {
            return static_cast<char>(std::tolower(character));
        }
    );

    return value;
}

std::string to_upper_ascii(std::string value) {
    std::transform(
        value.begin(),
        value.end(),
        value.begin(),
        [](unsigned char character) {
            return static_cast<char>(std::toupper(character));
        }
    );

    return value;
}

bool starts_with(std::string_view value, std::string_view prefix) {
    return value.size() >= prefix.size() &&
           value.compare(0, prefix.size(), prefix) == 0;
}

bool ends_with(std::string_view value, std::string_view suffix) {
    return value.size() >= suffix.size() &&
           value.compare(
               value.size() - suffix.size(),
               suffix.size(),
               suffix
           ) == 0;
}

std::vector<std::string> split(std::string_view value, char delimiter) {
    std::vector<std::string> parts;
    std::size_t start = 0;

    while (start <= value.size()) {
        const std::size_t position = value.find(delimiter, start);

        if (position == std::string_view::npos) {
            parts.emplace_back(value.substr(start));
            break;
        }

        parts.emplace_back(value.substr(start, position - start));
        start = position + 1;
    }

    return parts;
}

std::string join(
    const std::vector<std::string>& parts,
    std::string_view separator
) {
    std::string result;

    for (std::size_t index = 0; index < parts.size(); ++index) {
        if (index != 0) {
            result += separator;
        }

        result += parts[index];
    }

    return result;
}

std::string replace_all(
    std::string value,
    std::string_view search,
    std::string_view replacement
) {
    if (search.empty()) {
        return value;
    }

    std::size_t position = 0;

    while ((position = value.find(search, position)) != std::string::npos) {
        value.replace(position, search.size(), replacement);
        position += replacement.size();
    }

    return value;
}

bool is_identifier(std::string_view value) {
    if (value.empty()) {
        return false;
    }

    const auto first = static_cast<unsigned char>(value.front());

    if (!(std::isalpha(first) || value.front() == '_')) {
        return false;
    }

    for (char character : value.substr(1)) {
        const auto current = static_cast<unsigned char>(character);

        if (!(std::isalnum(current) || character == '_')) {
            return false;
        }
    }

    return true;
}

std::string normalize_service(std::string_view raw) {
    std::string service = trim(raw);

    if (!is_identifier(service)) {
        throw std::invalid_argument(
            "service must contain letters, digits, and underscores only"
        );
    }

    return to_lower_ascii(std::move(service));
}

std::string redact_token(std::string value) {
    const std::string marker = "token=";
    const std::size_t start = value.find(marker);

    if (start == std::string::npos) {
        return value;
    }

    const std::size_t secret_start = start + marker.size();
    const std::size_t end = value.find(' ', secret_start);

    if (end == std::string::npos) {
        value.replace(secret_start, std::string::npos, "[REDACTED]");
    } else {
        value.replace(
            secret_start,
            end - secret_start,
            "[REDACTED]"
        );
    }

    return value;
}

}  // namespace text


struct DeploymentRecord {
    std::string timestamp;
    std::string operation;
    std::string service;
    std::string environment;
    std::string details;
};

struct ParseResult {
    bool accepted;
    std::string error;
    std::optional<DeploymentRecord> record;
};


class DeploymentImportService {
private:
    std::vector<DeploymentRecord> records_;
    std::map<std::string, std::size_t> operation_counts_;
    std::map<std::string, std::size_t> service_counts_;

    static bool valid_operation(std::string_view operation) {
        return operation == "CREATE" ||
               operation == "UPDATE" ||
               operation == "ROLLBACK" ||
               operation == "DELETE";
    }

    static bool valid_environment(std::string_view environment) {
        return environment == "development" ||
               environment == "staging" ||
               environment == "production";
    }

public:
    ParseResult parse(std::string_view line) const {
        const std::string cleaned = text::trim(line);

        if (cleaned.empty()) {
            return {false, "blank record", std::nullopt};
        }

        /*
         * The import format is:
         *
         * timestamp|operation|service|environment|details
         *
         * split() preserves empty fields. That is important because a missing
         * field must be distinguishable from an omitted delimiter.
         */
        const std::vector<std::string> parts = text::split(cleaned, '|');

        if (parts.size() != 5) {
            return {
                false,
                "record must contain exactly five pipe-separated fields",
                std::nullopt
            };
        }

        DeploymentRecord record{
            text::trim(parts[0]),
            text::to_upper_ascii(text::trim(parts[1])),
            text::normalize_service(parts[2]),
            text::to_lower_ascii(text::trim(parts[3])),
            text::redact_token(text::trim(parts[4]))
        };

        if (record.timestamp.empty()) {
            return {false, "timestamp is empty", std::nullopt};
        }

        if (!valid_operation(record.operation)) {
            return {
                false,
                "unsupported operation: " + record.operation,
                std::nullopt
            };
        }

        if (!valid_environment(record.environment)) {
            return {
                false,
                "unsupported environment: " + record.environment,
                std::nullopt
            };
        }

        if (record.details.empty()) {
            return {false, "details cannot be empty", std::nullopt};
        }

        return {true, "", std::move(record)};
    }

    void ingest(const std::vector<std::string>& lines) {
        for (const std::string& line : lines) {
            const ParseResult result = parse(line);

            if (!result.accepted) {
                std::cerr << "Rejected record: " << result.error << '\n';
                continue;
            }

            records_.push_back(*result.record);
            ++operation_counts_[result.record->operation];
            ++service_counts_[result.record->service];
        }
    }

    const std::vector<DeploymentRecord>& records() const {
        return records_;
    }

    void print_report() const {
        std::cout << "\nDeployment Audit Report\n";
        std::cout << std::string(78, '=') << '\n';

        std::cout << std::left
                  << std::setw(22) << "Timestamp"
                  << std::setw(12) << "Operation"
                  << std::setw(18) << "Service"
                  << std::setw(15) << "Environment"
                  << "Details\n";

        std::cout << std::string(78, '-') << '\n';

        for (const auto& record : records_) {
            std::cout << std::left
                      << std::setw(22) << record.timestamp
                      << std::setw(12) << record.operation
                      << std::setw(18) << record.service
                      << std::setw(15) << record.environment
                      << record.details << '\n';
        }

        std::cout << "\nOperation counts\n";
        for (const auto& [operation, count] : operation_counts_) {
            std::cout << "  " << operation << ": " << count << '\n';
        }

        std::cout << "\nService counts\n";
        for (const auto& [service, count] : service_counts_) {
            std::cout << "  " << service << ": " << count << '\n';
        }
    }
};


void demonstrate_core_string_operations() {
    std::cout << "\nCore C++ String Operations\n";
    std::cout << std::string(78, '=') << '\n';

    const std::string original = "  Market Prism Deployment  ";
    std::cout << "Original: " << std::quoted(original) << '\n';

    const std::string trimmed = text::trim(original);
    std::cout << "Trimmed:  " << std::quoted(trimmed) << '\n';

    std::cout << "Length: " << trimmed.length() << '\n';
    std::cout << "Starts with Market: "
              << std::boolalpha
              << text::starts_with(trimmed, "Market")
              << '\n';

    std::cout << "Ends with Deployment: "
              << text::ends_with(trimmed, "Deployment")
              << '\n';

    const std::size_t position = trimmed.find("Prism");
    if (position != std::string::npos) {
        std::cout << "Prism starts at byte position: "
                  << position << '\n';
    }

    const std::string replaced =
        text::replace_all(trimmed, "Deployment", "Release");

    std::cout << "replace_all(): " << replaced << '\n';

    const std::vector<std::string> words =
        text::split(trimmed, ' ');

    std::cout << "split(): ";
    for (const auto& word : words) {
        std::cout << '[' << word << "] ";
    }
    std::cout << '\n';

    std::cout << "join(): "
              << text::join(words, " / ")
              << '\n';
}


void demonstrate_failure_modes() {
    std::cout << "\nFailure Conditions\n";
    std::cout << std::string(78, '=') << '\n';

    const std::vector<std::string> invalid_lines{
        "",
        "2026-10-01|CREATE|api",
        "2026-10-01|PATCH|api|production|Unsupported operation",
        "2026-10-01|UPDATE|api-service|production|Invalid service name",
        "2026-10-01|DELETE|api|testing|Unknown environment",
        "2026-10-01|UPDATE|api|production|"
    };

    DeploymentImportService service;

    for (const auto& line : invalid_lines) {
        try {
            const ParseResult result = service.parse(line);

            std::cout << "Input: " << std::quoted(line) << '\n';

            if (result.accepted) {
                std::cout << "  accepted\n";
            } else {
                std::cout << "  rejected: " << result.error << '\n';
            }
        } catch (const std::exception& error) {
            /*
             * Parsing converts expected malformed input into a controlled
             * failure rather than allowing an unchecked exception to escape.
             */
            std::cout << "  validation exception: "
                      << error.what()
                      << '\n';
        }
    }
}


void run_assertions() {
    std::cout << "\nExecutable Checks\n";
    std::cout << std::string(78, '=') << '\n';

    if (text::trim("  C++  ") != "C++") {
        throw std::runtime_error("trim assertion failed");
    }

    if (!text::starts_with("String methods", "String")) {
        throw std::runtime_error("starts_with assertion failed");
    }

    if (!text::ends_with("report.csv", ".csv")) {
        throw std::runtime_error("ends_with assertion failed");
    }

    if (text::replace_all("a-b-c", "-", "/") != "a/b/c") {
        throw std::runtime_error("replace_all assertion failed");
    }

    const auto fields = text::split("a,,b", ',');

    if (fields.size() != 3 || fields[1] != "") {
        throw std::runtime_error("split empty-field assertion failed");
    }

    if (!text::is_identifier("deployment_service")) {
        throw std::runtime_error("identifier assertion failed");
    }

    if (text::is_identifier("deployment-service")) {
        throw std::runtime_error("invalid identifier assertion failed");
    }

    std::cout << "All C++ string-processing assertions passed.\n";
}


int main() {
    try {
        std::cout << "STRING METHODS CASE STUDY\n";
        std::cout << "C++17 deployment-record import service\n";

        demonstrate_core_string_operations();

        DeploymentImportService service;

        const std::vector<std::string> deployment_records{
            "2026-10-01T07:20:01|CREATE|Gateway_API|production|New API deployment",
            "2026-10-01T07:20:03|UPDATE|Payments_Service|production|token=sk_live_12345 payment configuration changed",
            "2026-10-01T07:20:05|ROLLBACK|Gateway_API|production|Release reverted after health check failure",
            "2026-10-01T07:20:08|UPDATE|Analytics_Service|staging|Dashboard index updated",
            "2026-10-01T07:20:12|DELETE|Old_Service|development|Retired test deployment",
            "2026-10-01T07:20:14|PATCH|Gateway_API|production|Unsupported operation",
            "2026-10-01T07:20:15|UPDATE|bad-service|production|Invalid service identifier"
        };

        service.ingest(deployment_records);
        service.print_report();

        demonstrate_failure_modes();
        run_assertions();

        /*
         * String processing is linear for the ordinary operations used here.
         * Repeated concatenation can become costly for very large workloads,
         * so production code should consider streams or pre-sized buffers.
         */
        std::cout << "\nComplexity note: most single string searches and scans "
                     "are O(n), where n is the string length.\n";
        std::cout << "The audit importer processes each input record once, "
                     "with parsing cost dominated by field scanning.\n";

        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Fatal processing error: "
                  << error.what()
                  << '\n';
        return 1;
    }
}
