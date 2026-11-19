"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");
const { EventEmitter } = require("node:events");

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = "ValidationError";
    }
}

const DeviceStatus = Object.freeze({
    ACTIVE: "active",
    INACTIVE: "inactive",
    MAINTENANCE: "maintenance"
});

class Device {
    // This property belongs to the prototype, not individual instances.
    static category = "Network Equipment";

    constructor({
        id,
        name,
        manufacturer,
        temperature = 25,
        status = DeviceStatus.ACTIVE,
        configuration = {},
        tags = []
    }) {
        this.validateText(id, "ID");
        this.validateText(name, "Name");
        this.validateText(manufacturer, "Manufacturer");

        this.validateTemperature(temperature);

        if (!Object.values(DeviceStatus).includes(status)) {
            throw new ValidationError("Invalid device status.");
        }

        if (
            configuration === null ||
            typeof configuration !== "object" ||
            Array.isArray(configuration)
        ) {
            throw new ValidationError(
                "Configuration must be an object."
            );
        }

        if (
            !Array.isArray(tags) ||
            !tags.every(tag => typeof tag === "string")
        ) {
            throw new ValidationError(
                "Tags must be an array of strings."
            );
        }

        // Object-specific properties.
        this.id = id.trim();
        this.name = name.trim();
        this.manufacturer = manufacturer.trim();
        this.temperature = temperature;
        this.status = status;

        // Each instance receives independent nested objects.
        this.configuration = structuredClone(configuration);
        this.tags = [...tags];

        this.createdAt = new Date().toISOString();
        this.revision = 0;
    }

    validateText(value, field) {
        if (typeof value !== "string" || !value.trim()) {
            throw new ValidationError(`${field} cannot be empty.`);
        }
    }

    validateTemperature(value) {
        if (
            typeof value !== "number" ||
            !Number.isFinite(value) ||
            value < -50 ||
            value > 150
        ) {
            throw new ValidationError(
                "Temperature must be between -50 and 150."
            );
        }
    }

    update(patch) {
        if (
            patch === null ||
            typeof patch !== "object" ||
            Array.isArray(patch)
        ) {
            throw new ValidationError("Update must be an object.");
        }

        const allowed = new Set([
            "name",
            "manufacturer",
            "temperature",
            "status",
            "configuration",
            "tags"
        ]);

        // Validate the entire patch before changing object state.
        for (const key of Object.keys(patch)) {
            if (!allowed.has(key)) {
                throw new ValidationError(
                    `Attribute '${key}' cannot be modified.`
                );
            }

            const value = patch[key];

            if (key === "temperature") {
                this.validateTemperature(value);
            }

            if (key === "status") {
                if (!Object.values(DeviceStatus).includes(value)) {
                    throw new ValidationError("Invalid device status.");
                }
            }

            if (key === "name" || key === "manufacturer") {
                this.validateText(value, key);
            }

            if (key === "configuration") {
                if (
                    value === null ||
                    typeof value !== "object" ||
                    Array.isArray(value)
                ) {
                    throw new ValidationError(
                        "Configuration must be an object."
                    );
                }
            }

            if (
                key === "tags" &&
                (!Array.isArray(value) ||
                    !value.every(tag => typeof tag === "string"))
            ) {
                throw new ValidationError("Invalid tags.");
            }
        }

        const safePatch = structuredClone(patch);

        for (const [key, value] of Object.entries(safePatch)) {
            this[key] =
                typeof value === "string" &&
                ["name", "manufacturer"].includes(key)
                    ? value.trim()
                    : value;
        }

        this.revision++;
    }

    get isOverheating() {
        return this.temperature >= 70;
    }

    getSnapshot() {
        return {
            ...this,
            configuration: structuredClone(this.configuration),
            tags: [...this.tags]
        };
    }
}

class RepositoryEventBus extends EventEmitter {
    publish(eventName, payload) {
        this.emit(eventName, Object.freeze({
            ...payload,
            timestamp: new Date().toISOString()
        }));
    }
}

class DeviceRegistry {
    constructor(eventBus = new RepositoryEventBus()) {
        this.devices = new Map();
        this.events = eventBus;
    }

    register(device) {
        if (!(device instanceof Device)) {
            throw new ValidationError("Expected a Device instance.");
        }

        if (this.devices.has(device.id)) {
            throw new ValidationError("Duplicate device ID.");
        }

        this.devices.set(device.id, device);

        this.events.publish("device:registered", {
            deviceId: device.id
        });
    }

    get(id) {
        const device = this.devices.get(id);

        if (!device) {
            throw new ValidationError(`Device ${id} not found.`);
        }

        return device;
    }

    update(id, patch) {
        const device = this.get(id);
        const previousRevision = device.revision;

        device.update(patch);

        this.events.publish("device:updated", {
            deviceId: id,
            previousRevision,
            currentRevision: device.revision
        });
    }

    getOverheatingDevices() {
        return Array.from(this.devices.values())
            .filter(device => device.isOverheating)
            .map(device => device.getSnapshot());
    }

    getStatistics() {
        const devices = Array.from(this.devices.values());

        return {
            total: devices.length,
            active: devices.filter(
                d => d.status === DeviceStatus.ACTIVE
            ).length,
            inactive: devices.filter(
                d => d.status === DeviceStatus.INACTIVE
            ).length,
            maintenance: devices.filter(
                d => d.status === DeviceStatus.MAINTENANCE
            ).length,
            overheating: devices.filter(d => d.isOverheating).length
        };
    }

    async save(filename) {
        const destination = path.resolve(filename);
        const temporary = `${destination}.tmp`;

        const records = Array.from(this.devices.values())
            .map(device => device.getSnapshot());

        try {
            await fs.writeFile(
                temporary,
                JSON.stringify(records, null, 2),
                { encoding: "utf8", flag: "wx" }
            );

            // Atomic replacement on filesystems supporting rename.
            await fs.rename(temporary, destination);
        } catch (error) {
            await fs.rm(temporary, { force: true }).catch(() => {});

            throw new Error(
                `Unable to save device registry: ${error.message}`
            );
        }
    }

    static async load(filename) {
        let records;

        try {
            records = JSON.parse(
                await fs.readFile(filename, "utf8")
            );
        } catch (error) {
            throw new Error(
                `Unable to read device registry: ${error.message}`
            );
        }

        if (!Array.isArray(records)) {
            throw new ValidationError("Invalid registry structure.");
        }

        const registry = new DeviceRegistry();

        for (const record of records) {
            const device = new Device({
                id: record.id,
                name: record.name,
                manufacturer: record.manufacturer,
                temperature: record.temperature,
                status: record.status,
                configuration: record.configuration,
                tags: record.tags
            });

            device.createdAt = record.createdAt;
            device.revision = record.revision;

            registry.register(device);
        }

        return registry;
    }
}

async function main() {
    console.log("INSTANCE ATTRIBUTES AND OBJECT STATE");
    console.log("=".repeat(55));

    const events = new RepositoryEventBus();

    events.on("device:registered", event => {
        console.log("Registration event:", event.deviceId);
    });

    events.on("device:updated", event => {
        console.log(
            `Update event: ${event.deviceId}, ` +
            `revision ${event.previousRevision} -> ${event.currentRevision}`
        );
    });

    const registry = new DeviceRegistry(events);

    const router = new Device({
        id: "DEV-001",
        name: "Core Router",
        manufacturer: "Cisco",
        temperature: 42,
        configuration: {
            ip: "192.168.1.1",
            ports: 24
        },
        tags: ["network", "critical"]
    });

    const firewall = new Device({
        id: "DEV-002",
        name: "Enterprise Firewall",
        manufacturer: "Fortinet",
        temperature: 78,
        configuration: {
            ip: "192.168.1.2",
            ports: 8
        },
        tags: ["security"]
    });

    registry.register(router);
    registry.register(firewall);

    console.log("\n1. Own instance properties");

    console.log("Router:", Object.keys(router));
    console.log("Firewall:", Object.keys(firewall));

    console.log("\n2. Prototype and class-level properties");

    console.log("Router category:", router.constructor.category);
    console.log("Firewall category:", firewall.constructor.category);

    console.log(
        "Own category property:",
        Object.hasOwn(router, "category")
    );

    console.log("\n3. Independent instance state");

    router.temperature = 35;

    console.log("Router:", router.temperature);
    console.log("Firewall:", firewall.temperature);

    console.log("\n4. Property shadowing");

    router.category = "Core Infrastructure";

    console.log("Router:", router.category);
    console.log("Firewall:", firewall.category);
    console.log("Prototype:", Device.category);

    console.log("\n5. Nested object independence");

    router.configuration.ports = 48;

    console.log("Router ports:", router.configuration.ports);
    console.log("Firewall ports:", firewall.configuration.ports);

    console.log("\n6. Controlled updates");

    registry.update("DEV-001", {
        temperature: 38,
        status: DeviceStatus.MAINTENANCE
    });

    console.log("Router revision:", router.revision);

    console.log("\n7. Invalid update");

    try {
        registry.update("DEV-001", {
            temperature: 250,
            name: "Invalid update"
        });
    } catch (error) {
        console.log("Update rejected:", error.message);
    }

    console.log("Name remains:", router.name);
    console.log("Temperature remains:", router.temperature);

    console.log("\n8. Monitoring");

    console.log("Overheating:", registry.getOverheatingDevices());
    console.log("Statistics:", registry.getStatistics());

    console.log("\n9. Persistence");

    const filename = "device_instances_js.json";

    await registry.save(filename);

    const restored = await DeviceRegistry.load(filename);

    console.log("Restored statistics:", restored.getStatistics());

    console.log("\n10. Duplicate detection");

    try {
        registry.register(router);
    } catch (error) {
        console.log("Registration rejected:", error.message);
    }

    console.log("\n11. Missing instance");

    try {
        registry.get("DEV-999");
    } catch (error) {
        console.log("Lookup rejected:", error.message);
    }

    console.log("\nAll demonstrations completed.");
}

main().catch(error => {
    console.error("Application failure:", error.message);
    process.exitCode = 1;
});
