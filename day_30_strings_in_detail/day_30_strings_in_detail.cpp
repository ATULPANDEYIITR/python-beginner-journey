#include <algorithm>
#include <cctype>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using namespace std;

/*
 * C++17 case study: a text indexing and search engine.
 *
 * The system accepts documents, validates metadata, tokenizes text,
 * builds an inverted index, supports exact term search, computes
 * edit distance for fuzzy matching, and produces redacted output.
 *
 * The implementation deliberately uses C++ string and string_view
 * facilities where their lifetime and ownership properties are useful.
 */

struct Document {
    int id;
    string title;
    string body;
};

struct SearchResult {
    int documentId;
    string title;
    size_t occurrences;
};

class TextEngine {
private:
    vector<Document> documents;
    unordered_map<string, unordered_map<int, size_t>> invertedIndex;

    static string normalizeWord(string_view value) {
        string result;

        for (unsigned char character : value) {
            if (isalnum(character)) {
                result.push_back(static_cast<char>(tolower(character)));
            }
        }

        return result;
    }

    static vector<string> tokenize(string_view text) {
        vector<string> tokens;
        string current;

        for (unsigned char character : text) {
            if (isalnum(character)) {
                current.push_back(static_cast<char>(tolower(character)));
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

public:
    void addDocument(const Document& document) {
        if (document.id <= 0) {
            throw invalid_argument("document ID must be positive");
        }

        if (document.title.empty()) {
            throw invalid_argument("document title cannot be empty");
        }

        if (document.body.size() > 1'000'000) {
            throw invalid_argument("document body exceeds the allowed size");
        }

        for (const Document& existing : documents) {
            if (existing.id == document.id) {
                throw invalid_argument("document ID already exists");
            }
        }

        documents.push_back(document);

        const vector<string> tokens = tokenize(document.body);

        for (const string& token : tokens) {
            ++invertedIndex[token][document.id];
        }
    }

    vector<SearchResult> exactSearch(string_view query) const {
        const string normalized = normalizeWord(query);

        if (normalized.empty()) {
            return {};
        }

        const auto found = invertedIndex.find(normalized);

        if (found == invertedIndex.end()) {
            return {};
        }

        vector<SearchResult> results;

        for (const auto& [documentId, occurrences] : found->second) {
            const auto document = find_if(
                documents.begin(),
                documents.end(),
                [documentId](const Document& item) {
                    return item.id == documentId;
                }
            );

            if (document != documents.end()) {
                results.push_back(
                    {document->id, document->title, occurrences}
                );
            }
        }

        sort(
            results.begin(),
            results.end(),
            [](const SearchResult& left, const SearchResult& right) {
                if (left.occurrences != right.occurrences) {
                    return left.occurrences > right.occurrences;
                }

                return left.documentId < right.documentId;
            }
        );

        return results;
    }

    static size_t levenshtein(string_view first, string_view second) {
        if (first.size() < second.size()) {
            swap(first, second);
        }

        vector<size_t> previous(second.size() + 1);

        for (size_t index = 0; index <= second.size(); ++index) {
            previous[index] = index;
        }

        for (size_t i = 1; i <= first.size(); ++i) {
            vector<size_t> current(second.size() + 1);
            current[0] = i;

            for (size_t j = 1; j <= second.size(); ++j) {
                const size_t insertion = current[j - 1] + 1;
                const size_t deletion = previous[j] + 1;
                const size_t substitution =
                    previous[j - 1] +
                    (first[i - 1] == second[j - 1] ? 0 : 1);

                current[j] = min(
                    {insertion, deletion, substitution}
                );
            }

            previous.swap(current);
        }

        return previous.back();
    }

    vector<pair<string, size_t>> fuzzyTerms(
        string_view query,
        size_t maximumDistance
    ) const {
        const string normalizedQuery = normalizeWord(query);
        vector<pair<string, size_t>> matches;
        unordered_set<string> uniqueTerms;

        for (const auto& [term, postings] : invertedIndex) {
            uniqueTerms.insert(term);
        }

        for (const string& term : uniqueTerms) {
            const size_t distance =
                levenshtein(normalizedQuery, term);

            if (distance <= maximumDistance) {
                matches.emplace_back(term, distance);
            }
        }

        sort(
            matches.begin(),
            matches.end(),
            [](const auto& left, const auto& right) {
                if (left.second != right.second) {
                    return left.second < right.second;
                }

                return left.first < right.first;
            }
        );

        return matches;
    }

    static string redactEmails(string_view text) {
        /*
         * This regular expression targets common email forms. It is not
         * intended to prove that an address is deliverable. Redaction
         * should happen before sensitive text is logged or displayed.
         */
        const regex emailPattern(
            R"([A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)"
        );

        return regex_replace(
            string(text),
            emailPattern,
            "[EMAIL]"
        );
    }

    void printStatistics() const {
        unordered_map<string, size_t> frequency;

        for (const Document& document : documents) {
            for (const string& token : tokenize(document.body)) {
                ++frequency[token];
            }
        }

        cout << "\nCorpus statistics\n";
        cout << "Documents: " << documents.size() << '\n';
        cout << "Unique terms: " << invertedIndex.size() << '\n';

        vector<pair<string, size_t>> ranked(
            frequency.begin(),
            frequency.end()
        );

        sort(
            ranked.begin(),
            ranked.end(),
            [](const auto& left, const auto& right) {
                if (left.second != right.second) {
                    return left.second > right.second;
                }

                return left.first < right.first;
            }
        );

        cout << "Most frequent terms:\n";

        const size_t limit = min<size_t>(5, ranked.size());

        for (size_t index = 0; index < limit; ++index) {
            cout << "  " << ranked[index].first
                 << ": " << ranked[index].second << '\n';
        }
    }
};

static void printSearch(
    const TextEngine& engine,
    const string& query
) {
    cout << "\nExact search: " << query << '\n';

    const auto results = engine.exactSearch(query);

    if (results.empty()) {
        cout << "  No documents matched.\n";
        return;
    }

    for (const SearchResult& result : results) {
        cout << "  [" << result.documentId << "] "
             << result.title
             << " occurrences=" << result.occurrences << '\n';
    }
}

static void runCaseStudy() {
    TextEngine engine;

    engine.addDocument({
        1,
        "String Processing Architecture",
        "A string processing service normalizes text, tokenizes input, "
        "indexes terms, and provides exact search."
    });

    engine.addDocument({
        2,
        "Search Performance",
        "Efficient search depends on data structures, string matching "
        "algorithms, indexing, and careful memory management."
    });

    engine.addDocument({
        3,
        "Unicode Text",
        "Unicode text requires attention to encoding, normalization, "
        "code points, and the distinction between bytes and characters."
    });

    printSearch(engine, "string");
    printSearch(engine, "search");
    printSearch(engine, "unicode");
    printSearch(engine, "missing");

    cout << "\nFuzzy terms for 'strng' with distance <= 1:\n";

    for (const auto& [term, distance] :
         engine.fuzzyTerms("strng", 1)) {
        cout << "  " << term << " distance=" << distance << '\n';
    }

    engine.printStatistics();

    const string message =
        "Incident contact: alice@example.com; backup=bob@example.org";

    cout << "\nRedacted message:\n";
    cout << "  " << TextEngine::redactEmails(message) << '\n';

    cout << "\nEdit-distance examples\n";
    cout << "  kitten -> sitting: "
         << TextEngine::levenshtein("kitten", "sitting") << '\n';
    cout << "  database -> databse: "
         << TextEngine::levenshtein("database", "databse") << '\n';

    cout << "\nComplexity notes\n";
    cout << "  Tokenization: O(n) for input length n.\n";
    cout << "  Inverted-index lookup: average O(1) hash lookup for a term.\n";
    cout << "  Edit distance: O(n*m) time and O(min(n,m)) auxiliary space.\n";
    cout << "  Result sorting: O(r log r) for r matching documents.\n";
}

int main() {
    try {
        runCaseStudy();
        return 0;
    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << '\n';
        return 1;
    }
}
