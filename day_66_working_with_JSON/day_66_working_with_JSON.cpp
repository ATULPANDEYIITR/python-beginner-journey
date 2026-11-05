#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <variant>
#include <stdexcept>
#include <sstream>
#include <iomanip>
#include <cmath>
#include <cctype>
#include <algorithm>
#include <limits>

using namespace std;

/*
 * Working with JSON
 *
 * A self-contained JSON value model and recursive-descent parser.
 *
 * Supports:
 * - Objects and arrays
 * - Strings and escape sequences
 * - Numbers and booleans
 * - Null values
 * - Serialization
 * - Nested property access
 * - Schema validation
 * - Order processing
 * - Error handling
 *
 * No external libraries required.
 */

class JSONError : public runtime_error {
public:
    explicit JSONError(const string& message)
        : runtime_error(message) {}
};

struct JSONValue {
    using Object = map<string, JSONValue>;
    using Array = vector<JSONValue>;

    variant<nullptr_t, bool, double, string, Array, Object> value;

    JSONValue() : value(nullptr) {}
    JSONValue(nullptr_t) : value(nullptr) {}
    JSONValue(bool v) : value(v) {}
    JSONValue(double v) : value(v) {
        if (!isfinite(v)) {
            throw JSONError("Non-finite JSON number");
        }
    }
    JSONValue(int v) : value(static_cast<double>(v)) {}
    JSONValue(const string& v) : value(v) {}
    JSONValue(const char* v) : value(string(v)) {}
    JSONValue(Array v) : value(move(v)) {}
    JSONValue(Object v) : value(move(v)) {}

    bool isObject() const {
        return holds_alternative<Object>(value);
    }

    bool isArray() const {
        return holds_alternative<Array>(value);
    }

    bool isString() const {
        return holds_alternative<string>(value);
    }

    bool isNumber() const {
        return holds_alternative<double>(value);
    }

    const Object& asObject() const {
        if (!isObject()) {
            throw JSONError("Expected JSON object");
        }
        return get<Object>(value);
    }

    Object& asObject() {
        if (!isObject()) {
            throw JSONError("Expected JSON object");
        }
        return get<Object>(value);
    }

    const Array& asArray() const {
        if (!isArray()) {
            throw JSONError("Expected JSON array");
        }
        return get<Array>(value);
    }

    const string& asString() const {
        if (!isString()) {
            throw JSONError("Expected JSON string");
        }
        return get<string>(value);
    }

    double asNumber() const {
        if (!isNumber()) {
            throw JSONError("Expected JSON number");
        }
        return get<double>(value);
    }

    bool asBool() const {
        if (!holds_alternative<bool>(value)) {
            throw JSONError("Expected JSON boolean");
        }
        return get<bool>(value);
    }

    const JSONValue& at(const string& key) const {
        const auto& object = asObject();
        auto it = object.find(key);

        if (it == object.end()) {
            throw JSONError("Missing JSON property: " + key);
        }

        return it->second;
    }
};

class JSONParser {
private:
    string input;
    size_t position = 0;

    static constexpr size_t MAX_DEPTH = 30;
    static constexpr size_t MAX_INPUT = 2 * 1024 * 1024;

    void skipWhitespace() {
        while (
            position < input.size() &&
            isspace(static_cast<unsigned char>(input[position]))
        ) {
            ++position;
        }
    }

    char peek() {
        skipWhitespace();

        if (position >= input.size()) {
            throw JSONError("Unexpected end of JSON");
        }

        return input[position];
    }

    bool consume(char expected) {
        skipWhitespace();

        if (
            position < input.size() &&
            input[position] == expected
        ) {
            ++position;
            return true;
        }

        return false;
    }

    void expect(char expected) {
        if (!consume(expected)) {
            throw JSONError(
                string("Expected character: ") + expected
            );
        }
    }

    static void appendUTF8(string& output, unsigned int codepoint) {
        if (codepoint <= 0x7F) {
            output += static_cast<char>(codepoint);
        } else if (codepoint <= 0x7FF) {
            output += static_cast<char>(0xC0 | (codepoint >> 6));
            output += static_cast<char>(0x80 | (codepoint & 0x3F));
        } else if (codepoint <= 0xFFFF) {
            output += static_cast<char>(0xE0 | (codepoint >> 12));
            output += static_cast<char>(0x80 | ((codepoint >> 6) & 0x3F));
            output += static_cast<char>(0x80 | (codepoint & 0x3F));
        } else {
            output += static_cast<char>(0xF0 | (codepoint >> 18));
            output += static_cast<char>(0x80 | ((codepoint >> 12) & 0x3F));
            output += static_cast<char>(0x80 | ((codepoint >> 6) & 0x3F));
            output += static_cast<char>(0x80 | (codepoint & 0x3F));
        }
    }

    unsigned int readHex4() {
        if (position + 4 > input.size()) {
            throw JSONError("Incomplete Unicode escape");
        }

        unsigned int result = 0;

        for (int i = 0; i < 4; ++i) {
            char c = input[position++];
            result <<= 4;

            if (c >= '0' && c <= '9') {
                result += c - '0';
            } else if (c >= 'a' && c <= 'f') {
                result += c - 'a' + 10;
            } else if (c >= 'A' && c <= 'F') {
                result += c - 'A' + 10;
            } else {
                throw JSONError("Invalid Unicode escape");
            }
        }

        return result;
    }

    string parseString() {
        expect('"');

        string result;

        while (position < input.size()) {
            unsigned char c = input[position++];

            if (c == '"') {
                return result;
            }

            if (c < 0x20) {
                throw JSONError("Unescaped control character");
            }

            if (c != '\\') {
                result += static_cast<char>(c);
                continue;
            }

            if (position >= input.size()) {
                throw JSONError("Incomplete escape sequence");
            }

            char escaped = input[position++];

            switch (escaped) {
                case '"': result += '"'; break;
                case '\\': result += '\\'; break;
                case '/': result += '/'; break;
                case 'b': result += '\b'; break;
                case 'f': result += '\f'; break;
                case 'n': result += '\n'; break;
                case 'r': result += '\r'; break;
                case 't': result += '\t'; break;

                case 'u': {
                    unsigned int codepoint = readHex4();

                    if (codepoint >= 0xD800 && codepoint <= 0xDBFF) {
                        if (
                            position + 2 > input.size() ||
                            input[position] != '\\' ||
                            input[position + 1] != 'u'
                        ) {
                            throw JSONError("Missing low surrogate");
                        }

                        position += 2;

                        unsigned int low = readHex4();

                        if (low < 0xDC00 || low > 0xDFFF) {
                            throw JSONError("Invalid low surrogate");
                        }

                        codepoint =
                            0x10000 +
                            ((codepoint - 0xD800) << 10) +
                            (low - 0xDC00);

                    } else if (codepoint >= 0xDC00 && codepoint <= 0xDFFF) {
                        throw JSONError("Unexpected low surrogate");
                    }

                    appendUTF8(result, codepoint);
                    break;
                }

                default:
                    throw JSONError("Invalid escape sequence");
            }
        }

        throw JSONError("Unterminated JSON string");
    }

    JSONValue parseNumber() {
        size_t start = position;

        consume('-');

        if (position >= input.size()) {
            throw JSONError("Invalid number");
        }

        if (input[position] == '0') {
            ++position;

            if (
                position < input.size() &&
                isdigit(static_cast<unsigned char>(input[position]))
            ) {
                throw JSONError("Leading zeros are not allowed");
            }
        } else {
            if (
                !isdigit(static_cast<unsigned char>(input[position])) ||
                input[position] == '0'
            ) {
                throw JSONError("Invalid integer portion");
            }

            while (
                position < input.size() &&
                isdigit(static_cast<unsigned char>(input[position]))
            ) {
                ++position;
            }
        }

        if (position < input.size() && input[position] == '.') {
            ++position;

            size_t fractionStart = position;

            while (
                position < input.size() &&
                isdigit(static_cast<unsigned char>(input[position]))
            ) {
                ++position;
            }

            if (fractionStart == position) {
                throw JSONError("Invalid decimal fraction");
            }
        }

        if (
            position < input.size() &&
            (input[position] == 'e' || input[position] == 'E')
        ) {
            ++position;

            if (
                position < input.size() &&
                (input[position] == '+' || input[position] == '-')
            ) {
                ++position;
            }

            size_t exponentStart = position;

            while (
                position < input.size() &&
                isdigit(static_cast<unsigned char>(input[position]))
            ) {
                ++position;
            }

            if (exponentStart == position) {
                throw JSONError("Invalid exponent");
            }
        }

        string numberText = input.substr(start, position - start);

        try {
            size_t consumed = 0;
            double number = stod(numberText, &consumed);

            if (consumed != numberText.size() || !isfinite(number)) {
                throw JSONError("Number outside supported range");
            }

            return JSONValue(number);
        } catch (const exception&) {
            throw JSONError("Invalid or out-of-range number");
        }
    }

    JSONValue parseArray(size_t depth) {
        expect('[');

        JSONValue::Array array;

        if (consume(']')) {
            return JSONValue(move(array));
        }

        while (true) {
            array.push_back(parseValue(depth + 1));

            if (consume(']')) {
                break;
            }

            expect(',');
        }

        return JSONValue(move(array));
    }

    JSONValue parseObject(size_t depth) {
        expect('{');

        JSONValue::Object object;

        if (consume('}')) {
            return JSONValue(move(object));
        }

        while (true) {
            if (peek() != '"') {
                throw JSONError("Object key must be a string");
            }

            string key = parseString();

            expect(':');

            JSONValue value = parseValue(depth + 1);

            if (!object.emplace(key, move(value)).second) {
                throw JSONError("Duplicate object key: " + key);
            }

            if (consume('}')) {
                break;
            }

            expect(',');
        }

        return JSONValue(move(object));
    }

    JSONValue parseValue(size_t depth) {
        if (depth > MAX_DEPTH) {
            throw JSONError("Maximum nesting depth exceeded");
        }

        char c = peek();

        if (c == '{') return parseObject(depth);
        if (c == '[') return parseArray(depth);
        if (c == '"') return JSONValue(parseString());
        if (c == '-' || isdigit(static_cast<unsigned char>(c))) {
            return parseNumber();
        }

        if (input.compare(position, 4, "true") == 0) {
            position += 4;
            return JSONValue(true);
        }

        if (input.compare(position, 5, "false") == 0) {
            position += 5;
            return JSONValue(false);
        }

        if (input.compare(position, 4, "null") == 0) {
            position += 4;
            return JSONValue(nullptr);
        }

        throw JSONError("Unexpected JSON token");
    }

public:
    explicit JSONParser(string text) : input(move(text)) {
        if (input.size() > MAX_INPUT) {
            throw JSONError("JSON document exceeds size limit");
        }
    }

    JSONValue parse() {
        JSONValue result = parseValue(0);

        skipWhitespace();

        if (position != input.size()) {
            throw JSONError("Unexpected trailing content");
        }

        return result;
    }
};

class JSONSerializer {
private:
    static string escapeString(const string& value) {
        ostringstream output;

        output << '"';

        for (unsigned char c : value) {
            switch (c) {
                case '"': output << "\\\""; break;
                case '\\': output << "\\\\"; break;
                case '\b': output << "\\b"; break;
                case '\f': output << "\\f"; break;
                case '\n': output << "\\n"; break;
                case '\r': output << "\\r"; break;
                case '\t': output << "\\t"; break;

                default:
                    if (c < 0x20) {
                        output << "\\u"
                               << hex
                               << setw(4)
                               << setfill('0')
                               << static_cast<int>(c)
                               << dec;
                    } else {
                        output << static_cast<char>(c);
                    }
            }
        }

        output << '"';
        return output.str();
    }

public:
    static string stringify(const JSONValue& value, int indent = 0, int depth = 0) {
        if (depth > 30) {
            throw JSONError("Maximum serialization depth exceeded");
        }

        if (holds_alternative<nullptr_t>(value.value)) {
            return "null";
        }

        if (holds_alternative<bool>(value.value)) {
            return get<bool>(value.value) ? "true" : "false";
        }

        if (value.isNumber()) {
            ostringstream output;
            output << setprecision(numeric_limits<double>::max_digits10)
                   << value.asNumber();
            return output.str();
        }

        if (value.isString()) {
            return escapeString(value.asString());
        }

        string spacing(depth * indent, ' ');
        string childSpacing((depth + 1) * indent, ' ');

        if (value.isArray()) {
            const auto& array = value.asArray();

            if (array.empty()) return "[]";

            string result = "[\n";

            for (size_t i = 0; i < array.size(); ++i) {
                result += childSpacing;
                result += stringify(array[i], indent, depth + 1);

                if (i + 1 < array.size()) result += ",";

                result += "\n";
            }

            result += spacing + "]";
            return result;
        }

        const auto& object = value.asObject();

        if (object.empty()) return "{}";

        string result = "{\n";
        size_t index = 0;

        for (const auto& [key, item] : object) {
            result += childSpacing;
            result += escapeString(key);
            result += ": ";
            result += stringify(item, indent, depth + 1);

            if (++index < object.size()) result += ",";

            result += "\n";
        }

        result += spacing + "}";
        return result;
    }
};

struct Product {
    string name;
    double price;
    int quantity;
};

class Order {
private:
    int orderId;
    int customerId;
    vector<Product> products;

public:
    Order(
        int id,
        int customer,
        vector<Product> items
    ) : orderId(id), customerId(customer), products(move(items)) {
        if (orderId <= 0 || customerId <= 0) {
            throw JSONError("Invalid order or customer ID");
        }

        if (products.empty()) {
            throw JSONError("Order must contain at least one product");
        }

        for (const auto& item : products) {
            if (
                item.name.empty() ||
                !isfinite(item.price) ||
                item.price < 0 ||
                item.quantity <= 0
            ) {
                throw JSONError("Invalid product information");
            }
        }
    }

    double total() const {
        double result = 0;

        for (const auto& item : products) {
            result += item.price * item.quantity;
        }

        return result;
    }

    JSONValue toJSON() const {
        JSONValue::Array items;

        for (const auto& item : products) {
            items.push_back(JSONValue::Object{
                {"name", item.name},
                {"price", item.price},
                {"quantity", item.quantity}
            });
        }

        return JSONValue::Object{
            {"order_id", orderId},
            {"customer_id", customerId},
            {"total", total()},
            {"items", move(items)},
            {"status", "completed"}
        };
    }
};

void demonstrateJSON() {
    cout << "\n=== JSON Parsing ===\n";

    string input = R"({
        "customer": {
            "id": 101,
            "name": "Atul Pandey",
            "address": {
                "city": "Lucknow",
                "country": "India"
            }
        },
        "active": true,
        "balance": 12500.50,
        "tags": ["technology", "security", "research"]
    })";

    JSONParser parser(input);
    JSONValue document = parser.parse();

    cout << JSONSerializer::stringify(document, 4) << "\n";

    cout << "\n=== Nested Property Access ===\n";

    const auto& customer = document.at("customer");

    cout << "Customer: "
         << customer.at("name").asString()
         << "\n";

    cout << "City: "
         << customer.at("address").at("city").asString()
         << "\n";

    cout << "\n=== JSON Serialization ===\n";

    Order order(
        5001,
        101,
        {
            {"Laptop", 65000, 1},
            {"Mouse", 800, 2}
        }
    );

    JSONValue orderJSON = order.toJSON();

    cout << JSONSerializer::stringify(orderJSON, 4) << "\n";

    cout << "Order total: " << order.total() << "\n";

    cout << "\n=== JSON Array Processing ===\n";

    JSONValue records = JSONParser(R"([
        {"department":"IT","revenue":50000},
        {"department":"Finance","revenue":35000},
        {"department":"Operations","revenue":25000}
    ])").parse();

    double revenue = 0;

    for (const auto& record : records.asArray()) {
        revenue += record.at("revenue").asNumber();
    }

    cout << "Total revenue: " << revenue << "\n";

    cout << "\n=== JSON Validation ===\n";

    JSONValue::Object customerData{
        {"id", 101},
        {"name", "Atul"},
        {"email", "atul@example.com"},
        {"balance", 12500.50}
    };

    if (
        customerData.at("id").asNumber() <= 0 ||
        customerData.at("name").asString().empty() ||
        customerData.at("balance").asNumber() < 0
    ) {
        throw JSONError("Customer validation failed");
    }

    cout << "Customer validation passed\n";

    cout << "\n=== Error Handling ===\n";

    vector<string> invalidInputs = {
        R"({"name":"Atul",})",
        R"({"value":NaN})",
        R"({"name":"A","name":"B"})",
        R"([1,2,])"
    };

    for (const auto& invalid : invalidInputs) {
        try {
            JSONParser invalidParser(invalid);
            invalidParser.parse();
            cout << "Unexpected acceptance\n";
        } catch (const JSONError& error) {
            cout << "Rejected: " << error.what() << "\n";
        }
    }

    cout << "\n=== Assertions ===\n";

    if (order.total() != 66600) {
        throw JSONError("Order total assertion failed");
    }

    if (
        document.at("customer")
            .at("address")
            .at("city")
            .asString() != "Lucknow"
    ) {
        throw JSONError("Nested property assertion failed");
    }

    cout << "All JSON checks passed.\n";
}

int main() {
    try {
        demonstrateJSON();
        return 0;
    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << "\n";
        return 1;
    }
}
