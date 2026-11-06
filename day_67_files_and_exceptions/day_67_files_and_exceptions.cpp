#include <algorithm>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace fs = std::filesystem;

class FileError : public std::runtime_error {
public:
    explicit FileError(const std::string& message)
        : std::runtime_error(message) {}
};

class ValidationError : public FileError {
public:
    explicit ValidationError(const std::string& message)
        : FileError(message) {}
};

class StorageError : public FileError {
public:
    explicit StorageError(const std::string& message)
        : FileError(message) {}
};

class ParseError : public FileError {
public:
    explicit ParseError(const std::string& message)
        : FileError(message) {}
};

enum class Status {
    Pending,
    Processing,
    Completed,
    Failed
};

std::string statusName(Status status) {
    switch (status) {
        case Status::Pending: return "PENDING";
        case Status::Processing: return "PROCESSING";
        case Status::Completed: return "COMPLETED";
        case Status::Failed: return "FAILED";
    }

    throw ValidationError("Unknown task status.");
}

Status parseStatus(const std::string& value) {
    if (value == "PENDING") return Status::Pending;
    if (value == "PROCESSING") return Status::Processing;
    if (value == "COMPLETED") return Status::Completed;
    if (value == "FAILED") return Status::Failed;

    throw ParseError("Invalid status: " + value);
}

struct Task {
    int id;
    std::string title;
    int priority;
    Status status;

    void validate() const {
        if (id <= 0) {
            throw ValidationError("Task ID must be positive.");
        }

        if (title.empty() ||
            title.find_first_not_of(" \t\r\n") == std::string::npos) {
            throw ValidationError("Task title cannot be empty.");
        }

        if (priority < 1 || priority > 5) {
            throw ValidationError("Priority must be between 1 and 5.");
        }
    }
};

class TaskFileRepository {
private:
    fs::path filePath;

    static std::string escape(const std::string& value) {
        std::string result;

        for (char character : value) {
            if (character == '\\' || character == '|') {
                result.push_back('\\');
            }

            if (character == '\n' || character == '\r') {
                result.push_back(' ');
            } else {
                result.push_back(character);
            }
        }

        return result;
    }

    static std::vector<std::string> split(const std::string& line) {
        std::vector<std::string> fields;
        std::string field;
        bool escaped = false;

        for (char character : line) {
            if (escaped) {
                field.push_back(character);
                escaped = false;
            } else if (character == '\\') {
                escaped = true;
            } else if (character == '|') {
                fields.push_back(field);
                field.clear();
            } else {
                field.push_back(character);
            }
        }

        if (escaped) {
            throw ParseError("Incomplete escape sequence.");
        }

        fields.push_back(field);
        return fields;
    }

public:
    explicit TaskFileRepository(fs::path directory) {
        std::error_code error;
        fs::create_directories(directory, error);

        if (error) {
            throw StorageError(
                "Cannot create directory: " + error.message()
            );
        }

        filePath = directory / "tasks.txt";
    }

    std::vector<Task> load() const {
        std::ifstream input(filePath);

        if (!input.is_open()) {
            if (!fs::exists(filePath)) {
                return {};
            }

            throw StorageError("Cannot open task file.");
        }

        std::vector<Task> tasks;
        std::set<int> identifiers;
        std::string line;
        std::size_t lineNumber = 0;

        while (std::getline(input, line)) {
            ++lineNumber;

            if (line.empty()) {
                continue;
            }

            try {
                auto fields = split(line);

                if (fields.size() != 4) {
                    throw ParseError("Expected four fields.");
                }

                std::size_t position = 0;
                int id = std::stoi(fields[0], &position);

                if (position != fields[0].size()) {
                    throw ParseError("Invalid task ID.");
                }

                position = 0;
                int priority = std::stoi(fields[2], &position);

                if (position != fields[2].size()) {
                    throw ParseError("Invalid priority.");
                }

                Task task{
                    id,
                    fields[1],
                    priority,
                    parseStatus(fields[3])
                };

                task.validate();

                if (!identifiers.insert(task.id).second) {
                    throw ParseError("Duplicate task ID.");
                }

                tasks.push_back(std::move(task));
            } catch (const std::exception& error) {
                throw ParseError(
                    "Line " + std::to_string(lineNumber) +
                    ": " + error.what()
                );
            }
        }

        if (input.bad()) {
            throw StorageError("Error while reading task file.");
        }

        return tasks;
    }

    void save(const std::vector<Task>& tasks) const {
        std::set<int> identifiers;

        for (const auto& task : tasks) {
            task.validate();

            if (!identifiers.insert(task.id).second) {
                throw ValidationError("Duplicate task ID.");
            }
        }

        fs::path temporary = filePath;
        temporary += ".tmp";

        try {
            {
                std::ofstream output(
                    temporary,
                    std::ios::out | std::ios::trunc
                );

                if (!output.is_open()) {
                    throw StorageError("Cannot create temporary file.");
                }

                for (const auto& task : tasks) {
                    output
                        << task.id << '|'
                        << escape(task.title) << '|'
                        << task.priority << '|'
                        << statusName(task.status) << '\n';
                }

                output.flush();

                if (!output.good()) {
                    throw StorageError("Failed to write temporary file.");
                }
            }

            std::error_code error;
            fs::rename(temporary, filePath, error);

            if (error) {
                // Replacement behavior differs between operating systems.
                fs::remove(filePath, error);
                error.clear();
                fs::rename(temporary, filePath, error);
            }

            if (error) {
                throw StorageError(
                    "Atomic replacement failed: " + error.message()
                );
            }
        } catch (...) {
            std::error_code ignored;
            fs::remove(temporary, ignored);
            throw;
        }
    }

    void add(const Task& task) const {
        auto tasks = load();

        if (std::any_of(
            tasks.begin(),
            tasks.end(),
            [&](const Task& existing) {
                return existing.id == task.id;
            }
        )) {
            throw ValidationError("Task ID already exists.");
        }

        tasks.push_back(task);
        save(tasks);
    }

    bool updateStatus(int id, Status status) const {
        auto tasks = load();

        auto iterator = std::find_if(
            tasks.begin(),
            tasks.end(),
            [id](const Task& task) {
                return task.id == id;
            }
        );

        if (iterator == tasks.end()) {
            return false;
        }

        iterator->status = status;
        save(tasks);
        return true;
    }

    std::size_t countByStatus(Status status) const {
        auto tasks = load();

        return static_cast<std::size_t>(
            std::count_if(
                tasks.begin(),
                tasks.end(),
                [status](const Task& task) {
                    return task.status == status;
                }
            )
        );
    }
};

class ErrorReport {
private:
    std::map<std::string, std::size_t> counts;

public:
    void record(const std::string& category) {
        ++counts[category];
    }

    void print() const {
        std::cout << "\nError report\n";

        for (const auto& [category, count] : counts) {
            std::cout << category << ": " << count << '\n';
        }
    }
};

std::optional<Task> parseInput(
    const std::string& line,
    ErrorReport& report
) {
    std::istringstream input(line);

    int id;
    int priority;
    std::string title;

    if (!(input >> id >> priority)) {
        report.record("Invalid numeric input");
        return std::nullopt;
    }

    std::getline(input >> std::ws, title);

    try {
        Task task{
            id,
            title,
            priority,
            Status::Pending
        };

        task.validate();
        return task;
    } catch (const ValidationError&) {
        report.record("Validation failure");
        return std::nullopt;
    }
}

int main() {
    try {
        fs::path directory =
            fs::temp_directory_path() / "cpp_file_exception_practice";

        TaskFileRepository repository(directory);
        ErrorReport report;

        std::vector<std::string> incoming = {
            "101 1 Validate backup integrity",
            "102 3 Process transaction logs",
            "103 5 Archive audit records",
            "invalid input",
            "104 8 Invalid priority"
        };

        for (const auto& line : incoming) {
            auto task = parseInput(line, report);

            if (task) {
                try {
                    repository.add(*task);
                    std::cout << "Stored task " << task->id << '\n';
                } catch (const ValidationError& error) {
                    std::cerr << error.what() << '\n';
                }
            }
        }

        repository.updateStatus(101, Status::Completed);
        repository.updateStatus(102, Status::Processing);

        auto tasks = repository.load();

        std::sort(
            tasks.begin(),
            tasks.end(),
            [](const Task& left, const Task& right) {
                if (left.priority != right.priority) {
                    return left.priority < right.priority;
                }

                return left.id < right.id;
            }
        );

        std::cout << "\nStored tasks\n";

        for (const auto& task : tasks) {
            std::cout
                << task.id << " | "
                << task.title << " | Priority "
                << task.priority << " | "
                << statusName(task.status) << '\n';
        }

        std::cout << "\nCompleted tasks: "
                  << repository.countByStatus(Status::Completed)
                  << '\n';

        report.print();

        // Verify persistence and error behavior.
        if (repository.load().size() != 3) {
            throw FileError("Persistence test failed.");
        }

        if (!repository.updateStatus(101, Status::Completed)) {
            throw FileError("Status update failed.");
        }

        try {
            Task invalid{105, "", 2, Status::Pending};
            invalid.validate();
            throw FileError("Validation test failed.");
        } catch (const ValidationError&) {
            std::cout << "\nValidation test passed.\n";
        }

        std::cout << "All file operation tests passed.\n";

        return 0;
    } catch (const FileError& error) {
        std::cerr << "Application error: "
                  << error.what() << '\n';
        return 1;
    } catch (const fs::filesystem_error& error) {
        std::cerr << "Filesystem error: "
                  << error.what() << '\n';
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "Unexpected error: "
                  << error.what() << '\n';
        return 1;
    }
}
