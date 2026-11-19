#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace std;

enum class DeviceStatus {
    Active,
    Inactive,
    Maintenance
};

string statusToString(DeviceStatus status) {
    switch (status) {
        case DeviceStatus::Active:
            return "ACTIVE";
        case DeviceStatus::Inactive:
            return "INACTIVE";
        case DeviceStatus::Maintenance:
            return "MAINTENANCE";
    }

    throw logic_error("Unknown device status.");
}

class ValidationError : public runtime_error {
public:
    explicit ValidationError(const string& message)
        : runtime_error(message) {}
};

struct Configuration {
    string ipAddress;
    int ports;

    Configuration(string ip, int portCount)
        : ipAddress(move(ip)), ports(portCount) {
        if (ipAddress.empty()) {
            throw ValidationError("IP address cannot be empty.");
        }

        if (ports < 1 || ports > 65535) {
            throw ValidationError("Invalid port count.");
        }
    }
};

class Device {
private:
    // Class attribute: shared static state.
    inline static string category = "Network Equipment";

    // Instance attributes: independent for every Device object.
    string id;
    string name;
    string manufacturer;
    double temperature;
    DeviceStatus status;
    Configuration configuration;
    vector<string> tags;
    unsigned int revision;

    static void validateText(
        const string& value,
        const string& field
    ) {
        if (value.empty()) {
            throw ValidationError(field + " cannot be empty.");
        }
    }

    static void validateTemperature(double value) {
        if (!isfinite(value) || value < -50.0 || value > 150.0) {
            throw ValidationError("Temperature outside valid range.");
        }
    }

public:
    Device(
        string deviceId,
        string deviceName,
        string maker,
        double initialTemperature,
        DeviceStatus initialStatus,
        Configuration config,
        vector<string> deviceTags
    )
        : id(move(deviceId)),
          name(move(deviceName)),
          manufacturer(move(maker)),
          temperature(initialTemperature),
          status(initialStatus),
          configuration(move(config)),
          tags(move(deviceTags)),
          revision(0) {

        validateText(id, "Device ID");
        validateText(name, "Device name");
        validateText(manufacturer, "Manufacturer");
        validateTemperature(temperature);
    }

    const string& getId() const {
        return id;
    }

    const string& getName() const {
        return name;
    }

    double getTemperature() const {
        return temperature;
    }

    DeviceStatus getStatus() const {
        return status;
    }

    unsigned int getRevision() const {
        return revision;
    }

    static const string& getCategory() {
        return category;
    }

    // Modifying an instance does not modify other instances.
    void setTemperature(double value) {
        validateTemperature(value);
        temperature = value;
        ++revision;
    }

    void setStatus(DeviceStatus newStatus) {
        status = newStatus;
        ++revision;
    }

    void setName(const string& newName) {
        validateText(newName, "Device name");
        name = newName;
        ++revision;
    }

    void setConfiguration(const Configuration& newConfig) {
        configuration = newConfig;
        ++revision;
    }

    void addTag(const string& tag) {
        validateText(tag, "Tag");

        if (find(tags.begin(), tags.end(), tag) == tags.end()) {
            tags.push_back(tag);
            ++revision;
        }
    }

    bool isOverheating(double threshold = 70.0) const {
        return temperature >= threshold;
    }

    void print() const {
        cout << "\nDevice ID: " << id
             << "\nName: " << name
             << "\nManufacturer: " << manufacturer
             << "\nTemperature: " << temperature
             << "\nStatus: " << statusToString(status)
             << "\nIP: " << configuration.ipAddress
             << "\nPorts: " << configuration.ports
             << "\nCategory: " << category
             << "\nRevision: " << revision
             << "\nTags: ";

        for (const auto& tag : tags) {
            cout << tag << " ";
        }

        cout << '\n';
    }

    // A separate object may override the class-level category.
    void setLocalCategory(string value) {
        validateText(value, "Category override");
        localCategory = move(value);
    }

    string getEffectiveCategory() const {
        return localCategory.empty() ? category : localCategory;
    }

private:
    string localCategory;
};

class DeviceRegistry {
private:
    map<string, Device> devices;

public:
    void registerDevice(const Device& device) {
        auto result = devices.emplace(device.getId(), device);

        if (!result.second) {
            throw ValidationError("Duplicate device ID.");
        }
    }

    Device& getDevice(const string& id) {
        auto iterator = devices.find(id);

        if (iterator == devices.end()) {
            throw ValidationError("Device not found: " + id);
        }

        return iterator->second;
    }

    const Device& getDevice(const string& id) const {
        auto iterator = devices.find(id);

        if (iterator == devices.end()) {
            throw ValidationError("Device not found: " + id);
        }

        return iterator->second;
    }

    vector<string> overheatingDevices(
        double threshold = 70.0
    ) const {
        vector<string> result;

        for (const auto& [id, device] : devices) {
            if (device.isOverheating(threshold)) {
                result.push_back(id);
            }
        }

        return result;
    }

    map<string, int> statusReport() const {
        map<string, int> result{
            {"ACTIVE", 0},
            {"INACTIVE", 0},
            {"MAINTENANCE", 0}
        };

        for (const auto& [id, device] : devices) {
            ++result[statusToString(device.getStatus())];
        }

        return result;
    }

    void saveReport(const string& filename) const {
        ofstream file(filename);

        if (!file) {
            throw runtime_error("Unable to open report file.");
        }

        file << "ID,NAME,TEMPERATURE,STATUS,REVISION\n";

        for (const auto& [id, device] : devices) {
            file << id << ","
                 << device.getName() << ","
                 << device.getTemperature() << ","
                 << statusToString(device.getStatus()) << ","
                 << device.getRevision() << "\n";
        }

        if (!file.good()) {
            throw runtime_error("Failed while writing report.");
        }
    }

    size_t size() const {
        return devices.size();
    }
};

int main() {
    try {
        cout << "INSTANCE ATTRIBUTES: C++17\n";
        cout << string(55, '=') << '\n';

        Device router(
            "DEV-001",
            "Core Router",
            "Cisco",
            42.5,
            DeviceStatus::Active,
            Configuration("192.168.1.1", 24),
            {"network", "critical"}
        );

        Device firewall(
            "DEV-002",
            "Enterprise Firewall",
            "Fortinet",
            78.0,
            DeviceStatus::Active,
            Configuration("192.168.1.2", 8),
            {"security", "critical"}
        );

        cout << "\n1. Independent object attributes\n";

        router.print();
        firewall.print();

        cout << "\n2. Independent instance state\n";

        router.setTemperature(35.0);

        cout << "Router temperature: "
             << router.getTemperature() << '\n';

        cout << "Firewall temperature: "
             << firewall.getTemperature() << '\n';

        if (router.getTemperature() == firewall.getTemperature()) {
            throw logic_error("Instance isolation failed.");
        }

        cout << "\n3. Shared class attribute\n";

        cout << "Router category: " << Device::getCategory() << '\n';
        cout << "Firewall category: " << Device::getCategory() << '\n';

        cout << "\n4. Instance-level category override\n";

        router.setLocalCategory("Core Infrastructure");

        cout << "Router: " << router.getEffectiveCategory() << '\n';
        cout << "Firewall: " << firewall.getEffectiveCategory() << '\n';
        cout << "Shared: " << Device::getCategory() << '\n';

        cout << "\n5. Updating nested instance state\n";

        router.setConfiguration(
            Configuration("10.0.0.1", 48)
        );

        router.addTag("production");

        router.print();

        cout << "\n6. Device registry\n";

        DeviceRegistry registry;

        registry.registerDevice(router);
        registry.registerDevice(firewall);

        cout << "Registered devices: " << registry.size() << '\n';

        cout << "\n7. Overheating evaluation\n";

        for (const auto& id : registry.overheatingDevices()) {
            cout << "Overheating device: " << id << '\n';
        }

        cout << "\n8. Status aggregation\n";

        for (const auto& [status, count] : registry.statusReport()) {
            cout << status << ": " << count << '\n';
        }

        cout << "\n9. Invalid update\n";

        try {
            router.setTemperature(250.0);
        } catch (const ValidationError& error) {
            cout << "Rejected: " << error.what() << '\n';
        }

        cout << "Temperature preserved: "
             << router.getTemperature() << '\n';

        cout << "\n10. Duplicate registration\n";

        try {
            registry.registerDevice(router);
        } catch (const ValidationError& error) {
            cout << "Rejected: " << error.what() << '\n';
        }

        cout << "\n11. Missing device\n";

        try {
            registry.getDevice("DEV-999");
        } catch (const ValidationError& error) {
            cout << "Rejected: " << error.what() << '\n';
        }

        cout << "\n12. Report persistence\n";

        registry.saveReport("device_instances_cpp.csv");

        cout << "Report saved successfully.\n";

        cout << "\nAll demonstrations completed.\n";

    } catch (const exception& error) {
        cerr << "Application error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
