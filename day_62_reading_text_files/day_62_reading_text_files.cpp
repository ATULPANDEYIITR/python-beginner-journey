#include <algorithm>
#include <cctype>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

class TextFileError : public std::runtime_error {
public:
    explicit TextFileError(const std::string& message)
        : std::runtime_error(message) {}
};

enum class FileState {
    Available,
    Missing,
    Invalid,
    TooLarge
};

struct SearchResult {
    std::size_t lineNumber;
    std::string line;
};

struct FileStatistics {
    std::size_t lines = 0;
    std::size_t nonEmptyLines = 0;
    std::size_t characters = 0;
    std::size_t words = 0;
    std::size_t uniqueWords = 0;
    std::uint64_t checksum = 1469598103934665603ULL;
};

class TextFileReader {
private:
    std::size_t maxBytes_;

    static std::string lower(std::string value) {
        std::transform(
            value.begin(),
            value.end(),
            value.begin(),
            [](unsigned char ch) {
                return static_cast<char>(std::tolower(ch));
            }
        );
        return value;
    }

    static std::vector<std::string> tokenize(const std::string& line) {
        std::vector<std::string> tokens;
        std::string current;

        for (unsigned char ch : line) {
            if (std::isalnum(ch) || ch == '_' || ch == '\'') {
                current.push_back(
                    static_cast<char>(std::tolower(ch))
                );
            } else if (!current.empty()) {
                tokens.push_back(current);
                current.clear();
            }
        }

        if (!current.empty()) {
            tokens.push_back(current);
        }

        return tokens;
    }

    FileState state(const std::string& fileName) const {
        std::ifstream input(fileName, std::ios::binary);

        if (!input) {
            return FileState::Missing;
        }

        input.seekg(0, std::ios::end);
        const auto size = input.tellg();

        if (size < 0) {
            return FileState::Invalid;
        }

        if (static_cast<std::size_t>(size) > maxBytes_) {
            return FileState::TooLarge;
        }

        return FileState::Available;
    }

    void validate(const std::string& fileName) const {
        switch (state(fileName)) {
        case FileState::Available:
            return;
        case FileState::Missing:
            throw TextFileError("File does not exist: " + fileName);
        case FileState::TooLarge:
            throw TextFileError(
                "File exceeds configured size limit."
            );
        case FileState::Invalid:
            throw TextFileError("Unable to determine file size.");
        }
    }

public:
    explicit TextFileReader(std::size_t maxBytes = 5 * 1024 * 1024)
        : maxBytes_(maxBytes) {
        if (maxBytes == 0) {
            throw TextFileError("Maximum file size must be positive.");
        }
    }

    std::string readAll(const std::string& fileName) const {
        validate(fileName);

        std::ifstream input(fileName);

        if (!input) {
            throw TextFileError("Unable to open file.");
        }

        std::ostringstream buffer;
        buffer << input.rdbuf();

        if (!input.eof() && input.fail()) {
            throw TextFileError("Failure while reading file.");
        }

        return buffer.str();
    }

    std::vector<SearchResult> search(
        const std::string& fileName,
        const std::string& term
    ) const {
        validate(fileName);

        if (term.empty()) {
            throw TextFileError("Search term cannot be empty.");
        }

        std::ifstream input(fileName);
        std::vector<SearchResult> results;

        const std::string target = lower(term);
        std::string line;
        std::size_t lineNumber = 0;

        while (std::getline(input, line)) {
            ++lineNumber;

            if (lower(line).find(target) != std::string::npos) {
                results.push_back({lineNumber, line});
            }
        }

        if (!input.eof() && input.fail()) {
            throw TextFileError("Failure while searching file.");
        }

        return results;
    }

    FileStatistics analyze(const std::string& fileName) const {
        validate(fileName);

        std::ifstream input(fileName);
        FileStatistics stats;
        std::unordered_map<std::string, std::size_t> frequencies;

        std::string line;

        while (std::getline(input, line)) {
            ++stats.lines;
            stats.characters += line.size() + 1;

            if (!line.empty()) {
                ++stats.nonEmptyLines;
            }

            // FNV-1a provides a lightweight integrity fingerprint.
            for (unsigned char ch : line) {
                stats.checksum ^= ch;
                stats.checksum *= 1099511628211ULL;
            }

            for (const auto& word : tokenize(line)) {
                ++stats.words;
                ++frequencies[word];
            }
        }

        if (!input.eof() && input.fail()) {
            throw TextFileError("Failure while analyzing file.");
        }

        stats.uniqueWords = frequencies.size();
        return stats;
    }

    std::vector<std::pair<std::string, std::size_t>>
    topWords(const std::string& fileName, std::size_t limit) const {
        validate(fileName);

        if (limit == 0) {
            throw TextFileError("Limit must be positive.");
        }

        std::ifstream input(fileName);
        std::unordered_map<std::string, std::size_t> frequency;
        std::string line;

        while (std::getline(input, line)) {
            for (const auto& word : tokenize(line)) {
                ++frequency[word];
            }
        }

        std::vector<std::pair<std::string, std::size_t>> values(
            frequency.begin(),
            frequency.end()
        );

        std::sort(
            values.begin(),
            values.end(),
            [](const auto& a, const auto& b) {
                if (a.second != b.second) {
                    return a.second > b.second;
                }
                return a.first < b.first;
            }
        );

        if (values.size() > limit) {
            values.resize(limit);
        }

        return values;
    }
};

int main() {
    try {
        const std::string fileName = "text_reader_demo.txt";

        {
            std::ofstream output(fileName);

            if (!output) {
                throw TextFileError(
                    "Unable to create demonstration file."
                );
            }

            output
                << "Reading text files requires explicit encoding.\n"
                << "Streaming reads reduce memory usage.\n"
                << "Validation prevents unsafe input.\n"
                << "Streaming reads are useful for large files.\n";
        }

        TextFileReader reader;

        std::cout << "=== Complete Text ===\n";
        std::cout << reader.readAll(fileName) << '\n';

        std::cout << "=== Search Results ===\n";
        for (const auto& result : reader.search(fileName, "streaming")) {
            std::cout
                << result.lineNumber
                << ": "
                << result.line
                << '\n';
        }

        const FileStatistics stats = reader.analyze(fileName);

        std::cout << "\n=== Statistics ===\n";
        std::cout << "Lines: " << stats.lines << '\n';
        std::cout << "Non-empty lines: "
                  << stats.nonEmptyLines << '\n';
        std::cout << "Characters: "
                  << stats.characters << '\n';
        std::cout << "Words: " << stats.words << '\n';
        std::cout << "Unique words: "
                  << stats.uniqueWords << '\n';

        std::cout << "Checksum: 0x"
                  << std::hex
                  << stats.checksum
                  << std::dec
                  << '\n';

        std::cout << "\n=== Top Words ===\n";
        for (const auto& [word, count] :
             reader.topWords(fileName, 5)) {
            std::cout
                << word
                << ": "
                << count
                << '\n';
        }

        if (stats.lines != 4) {
            throw TextFileError("Unexpected line count.");
        }

        if (reader.search(fileName, "STREAMING").size() != 2) {
            throw TextFileError("Unexpected search count.");
        }

        std::cout << "\nValidation checks passed.\n";

        std::remove(fileName.c_str());
        return 0;
    }
    catch (const std::exception& error) {
        std::cerr
            << "[ERROR] "
            << error.what()
            << '\n';
        return 1;
    }
}
