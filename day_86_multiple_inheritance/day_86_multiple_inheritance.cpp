#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <typeindex>
#include <typeinfo>
#include <utility>
#include <vector>

using namespace std;

// ============================================================
// MULTIPLE INHERITANCE IN C++17
//
// Demonstrates:
// 1. Basic multiple inheritance.
// 2. Diamond inheritance.
// 3. Virtual inheritance.
// 4. Ambiguous member resolution.
// 5. Abstract interfaces.
// 6. Explicit method selection.
// 7. Capability-based design.
// 8. Runtime polymorphism.
// 9. Validation and failure handling.
// ============================================================

// ============================================================
// 1. BASIC MULTIPLE INHERITANCE
// ============================================================

class Logger {
public:
    virtual void log(const string& message) const {
        cout << "[LOG] " << message << '\n';
    }

    virtual ~Logger() = default;
};

class Validator {
public:
    virtual bool validate(const string& value) const {
        return !value.empty();
    }

    virtual ~Validator() = default;
};

class RepositoryService : public Logger, public Validator {
public:
    void save(const string& value) const {
        if (!validate(value)) {
            throw invalid_argument("Empty repository value");
        }

        log("Saved: " + value);
    }
};


// ============================================================
// 2. DIAMOND INHERITANCE WITHOUT VIRTUAL INHERITANCE
// ============================================================

class OrdinaryDevice {
public:
    string name;

    explicit OrdinaryDevice(string deviceName)
        : name(move(deviceName)) {}
};

class OrdinaryCamera : public OrdinaryDevice {
public:
    using OrdinaryDevice::OrdinaryDevice;
};

class OrdinaryNetwork : public OrdinaryDevice {
public:
    using OrdinaryDevice::OrdinaryDevice;
};

class OrdinarySmartDevice
    : public OrdinaryCamera,
      public OrdinaryNetwork {
public:
    OrdinarySmartDevice()
        : OrdinaryCamera("Camera"),
          OrdinaryNetwork("Network") {}

    void demonstrateAmbiguityResolution() const {
        cout << OrdinaryCamera::name << '\n';
        cout << OrdinaryNetwork::name << '\n';
    }
};


// ============================================================
// 3. DIAMOND INHERITANCE WITH VIRTUAL BASE CLASS
// ============================================================

class Device {
protected:
    string name;

public:
    explicit Device(string deviceName)
        : name(move(deviceName)) {}

    virtual string describe() const {
        return "Device: " + name;
    }

    virtual ~Device() = default;
};

class Camera : virtual public Device {
public:
    Camera() : Device("Camera") {}

    string capture() const {
        return "Image captured";
    }
};

class NetworkAdapter : virtual public Device {
public:
    NetworkAdapter() : Device("Network") {}

    string connect() const {
        return "Network connected";
    }
};

class SmartCamera : public Camera, public NetworkAdapter {
public:
    SmartCamera() : Device("Smart Camera") {}

    void operate() const {
        cout << describe() << '\n';
        cout << capture() << '\n';
        cout << connect() << '\n';
    }
};


// ============================================================
// 4. METHOD AMBIGUITY AND EXPLICIT RESOLUTION
// ============================================================

class CSVExporter {
public:
    virtual string exportData() const {
        return "CSV";
    }

    virtual ~CSVExporter() = default;
};

class JSONExporter {
public:
    virtual string exportData() const {
        return "JSON";
    }

    virtual ~JSONExporter() = default;
};

class DataExporter : public CSVExporter, public JSONExporter {
public:
    string exportData() const override {
        return CSVExporter::exportData();
    }

    string exportAsJSON() const {
        return JSONExporter::exportData();
    }
};


// ============================================================
// 5. ABSTRACT INTERFACES
// ============================================================

class Readable {
public:
    virtual string read(int id) const = 0;
    virtual ~Readable() = default;
};

class Writable {
public:
    virtual void write(int id, const string& value) = 0;
    virtual ~Writable() = default;
};

class Deletable {
public:
    virtual bool remove(int id) = 0;
    virtual ~Deletable() = default;
};

class MultiCapabilityRepository
    : public Readable,
      public Writable,
      public Deletable {
private:
    map<int, string> records;

public:
    string read(int id) const override {
        auto it = records.find(id);

        if (it == records.end()) {
            throw out_of_range("Record not found");
        }

        return it->second;
    }

    void write(int id, const string& value) override {
        if (id <= 0) {
            throw invalid_argument("ID must be positive");
        }

        if (value.empty()) {
            throw invalid_argument("Value cannot be empty");
        }

        records[id] = value;
    }

    bool remove(int id) override {
        return records.erase(id) > 0;
    }

    size_t size() const {
        return records.size();
    }
};


// ============================================================
// 6. CAPABILITY REGISTRY
// ============================================================

class Capability {
public:
    virtual string name() const = 0;
    virtual void execute() const = 0;
    virtual ~Capability() = default;
};

class LoggingCapability : public Capability {
public:
    string name() const override {
        return "Logging";
    }

    void execute() const override {
        cout << "Logging operation executed\n";
    }
};

class SecurityCapability : public Capability {
public:
    string name() const override {
        return "Security";
    }

    void execute() const override {
        cout << "Security verification executed\n";
    }
};

class CapabilityManager {
private:
    map<string, shared_ptr<Capability>> capabilities;

public:
    void registerCapability(shared_ptr<Capability> capability) {
        if (!capability) {
            throw invalid_argument("Null capability");
        }

        string key = capability->name();

        if (capabilities.count(key)) {
            throw logic_error("Duplicate capability: " + key);
        }

        capabilities.emplace(key, move(capability));
    }

    void execute(const string& key) const {
        auto it = capabilities.find(key);

        if (it == capabilities.end()) {
            throw out_of_range("Capability not found");
        }

        it->second->execute();
    }

    vector<string> list() const {
        vector<string> result;

        for (const auto& [name, capability] : capabilities) {
            result.push_back(name);
        }

        return result;
    }
};


// ============================================================
// 7. PERMISSION INTERFACES
// ============================================================

class ReadPermission {
public:
    virtual bool canRead() const = 0;
    virtual ~ReadPermission() = default;
};

class WritePermission {
public:
    virtual bool canWrite() const = 0;
    virtual ~WritePermission() = default;
};

class AdminAccount : public ReadPermission, public WritePermission {
private:
    string username;
    bool active;

public:
    AdminAccount(string user, bool enabled)
        : username(move(user)), active(enabled) {
        if (username.empty()) {
            throw invalid_argument("Username is required");
        }
    }

    bool canRead() const override {
        return active;
    }

    bool canWrite() const override {
        return active;
    }

    bool authorize(const string& operation) const {
        if (operation == "read") {
            return canRead();
        }

        if (operation == "write") {
            return canWrite();
        }

        throw invalid_argument("Unsupported operation");
    }

    void deactivate() {
        active = false;
    }
};


// ============================================================
// 8. POLYMORPHIC SERVICE EXECUTION
// ============================================================

class WorkflowStep {
public:
    virtual void execute() const = 0;
    virtual string stepName() const = 0;
    virtual ~WorkflowStep() = default;
};

class AuthenticationStep : public WorkflowStep {
public:
    void execute() const override {
        cout << "Authentication completed\n";
    }

    string stepName() const override {
        return "Authentication";
    }
};

class AuditStep : public WorkflowStep {
public:
    void execute() const override {
        cout << "Audit record created\n";
    }

    string stepName() const override {
        return "Audit";
    }
};

class WorkflowEngine {
private:
    vector<unique_ptr<WorkflowStep>> steps;

public:
    void addStep(unique_ptr<WorkflowStep> step) {
        if (!step) {
            throw invalid_argument("Workflow step cannot be null");
        }

        steps.push_back(move(step));
    }

    void execute() const {
        for (const auto& step : steps) {
            step->execute();
        }
    }
};


// ============================================================
// 9. TESTING
// ============================================================

void runTests() {
    RepositoryService repository;
    repository.save("Record A");

    if (!repository.validate("Record A")) {
        throw runtime_error("Validation failed");
    }

    SmartCamera camera;
    if (camera.describe() != "Device: Smart Camera") {
        throw runtime_error("Virtual inheritance failed");
    }

    DataExporter exporter;

    if (exporter.exportData() != "CSV") {
        throw runtime_error("CSV resolution failed");
    }

    if (exporter.exportAsJSON() != "JSON") {
        throw runtime_error("JSON resolution failed");
    }

    MultiCapabilityRepository storage;

    storage.write(1, "Enterprise Record");

    if (storage.read(1) != "Enterprise Record") {
        throw runtime_error("Read operation failed");
    }

    if (!storage.remove(1)) {
        throw runtime_error("Delete operation failed");
    }

    if (storage.size() != 0) {
        throw runtime_error("Storage state is incorrect");
    }

    AdminAccount admin("operator", true);

    if (!admin.authorize("read")) {
        throw runtime_error("Permission evaluation failed");
    }

    admin.deactivate();

    if (admin.authorize("write")) {
        throw runtime_error("Inactive account was authorized");
    }

    CapabilityManager manager;

    manager.registerCapability(
        make_shared<LoggingCapability>()
    );

    manager.registerCapability(
        make_shared<SecurityCapability>()
    );

    if (manager.list().size() != 2) {
        throw runtime_error("Capability registration failed");
    }

    bool exceptionRaised = false;

    try {
        storage.read(999);
    } catch (const out_of_range&) {
        exceptionRaised = true;
    }

    if (!exceptionRaised) {
        throw runtime_error("Missing record should fail");
    }

    cout << "All C++17 tests passed.\n";
}


// ============================================================
// 10. MAIN
// ============================================================

int main() {
    try {
        cout << "MULTIPLE INHERITANCE IN C++17\n\n";

        cout << "1. Basic multiple inheritance\n";

        RepositoryService service;
        service.save("Production Deployment");

        cout << "\n2. Ordinary diamond ambiguity\n";

        OrdinarySmartDevice ordinary;
        ordinary.demonstrateAmbiguityResolution();

        cout << "\n3. Virtual diamond inheritance\n";

        SmartCamera camera;
        camera.operate();

        cout << "\n4. Explicit method resolution\n";

        DataExporter exporter;
        cout << exporter.exportData() << '\n';
        cout << exporter.exportAsJSON() << '\n';

        cout << "\n5. Capability-based repository\n";

        MultiCapabilityRepository storage;

        storage.write(101, "Protected Enterprise Record");

        cout << storage.read(101) << '\n';
        cout << "Deleted: " << boolalpha
             << storage.remove(101) << '\n';

        cout << "\n6. Capability registry\n";

        CapabilityManager manager;

        manager.registerCapability(
            make_shared<LoggingCapability>()
        );

        manager.registerCapability(
            make_shared<SecurityCapability>()
        );

        for (const auto& name : manager.list()) {
            cout << name << '\n';
            manager.execute(name);
        }

        cout << "\n7. Permission evaluation\n";

        AdminAccount account("security_admin", true);

        cout << "Read: "
             << account.authorize("read") << '\n';

        cout << "Write: "
             << account.authorize("write") << '\n';

        cout << "\n8. Polymorphic workflow\n";

        WorkflowEngine workflow;

        workflow.addStep(
            make_unique<AuthenticationStep>()
        );

        workflow.addStep(
            make_unique<AuditStep>()
        );

        workflow.execute();

        cout << "\n9. Automated validation\n";

        runTests();

    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
