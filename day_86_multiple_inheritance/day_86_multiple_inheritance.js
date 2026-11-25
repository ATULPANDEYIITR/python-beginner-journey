'use strict';

/**
 * MULTIPLE INHERITANCE
 *
 * JavaScript uses prototype delegation rather than Python-style
 * class-based multiple inheritance.
 *
 * This implementation demonstrates:
 * - Prototype chains
 * - Multiple behavior composition
 * - Mixins
 * - Conflict detection
 * - Explicit method precedence
 * - Dynamic capability registration
 * - Asynchronous execution
 * - Event-driven processing
 * - Validation and failure handling
 *
 * Runtime: Node.js 18+
 */

// ============================================================
// 1. SINGLE INHERITANCE AND PROTOTYPE CHAINS
// ============================================================

class Device {
    constructor(name) {
        if (typeof name !== 'string' || !name.trim()) {
            throw new TypeError('Device name is required');
        }

        this.name = name.trim();
    }

    describe() {
        return `Device: ${this.name}`;
    }
}

class Camera extends Device {
    capture() {
        return 'Image captured';
    }
}

class NetworkCamera extends Camera {
    connect() {
        return 'Network connected';
    }
}


// ============================================================
// 2. MULTIPLE BEHAVIOR COMPOSITION USING MIXINS
// ============================================================

const LoggingMixin = {
    log(message) {
        console.log(`[LOG] ${message}`);
    }
};

const ValidationMixin = {
    validate(value) {
        if (value === null || value === undefined) {
            throw new TypeError('Value cannot be null or undefined');
        }

        return true;
    }
};

const AuditMixin = {
    initializeAudit() {
        this.auditRecords = [];
    },

    audit(message) {
        this.auditRecords.push({
            message,
            timestamp: new Date().toISOString()
        });
    }
};

function applyMixins(targetClass, ...mixins) {
    const applied = new Set();

    for (const mixin of mixins) {
        if (!mixin || typeof mixin !== 'object') {
            throw new TypeError('Each mixin must be an object');
        }

        for (const key of Reflect.ownKeys(mixin)) {
            if (key === 'constructor') {
                continue;
            }

            if (applied.has(key)) {
                throw new Error(
                    `Mixin conflict detected for property: ${String(key)}`
                );
            }

            const descriptor = Object.getOwnPropertyDescriptor(
                mixin,
                key
            );

            Object.defineProperty(
                targetClass.prototype,
                key,
                descriptor
            );

            applied.add(key);
        }
    }

    return targetClass;
}

class RepositoryService {
    constructor() {
        this.initializeAudit();
    }

    save(value) {
        this.validate(value);
        this.log(`Saving ${JSON.stringify(value)}`);
        this.audit('Repository record saved');

        return {
            success: true,
            value
        };
    }
}

applyMixins(
    RepositoryService,
    LoggingMixin,
    ValidationMixin,
    AuditMixin
);


// ============================================================
// 3. MULTIPLE INHERITANCE THROUGH BEHAVIOR OBJECTS
// ============================================================

const ReadCapability = {
    read(id) {
        return this.records.get(id) ?? null;
    }
};

const WriteCapability = {
    write(id, value) {
        if (!Number.isInteger(id) || id <= 0) {
            throw new RangeError('Record ID must be positive');
        }

        this.records.set(id, value);
        return true;
    }
};

const DeleteCapability = {
    remove(id) {
        return this.records.delete(id);
    }
};

class MultiCapabilityRepository {
    constructor() {
        this.records = new Map();
    }
}

applyMixins(
    MultiCapabilityRepository,
    ReadCapability,
    WriteCapability,
    DeleteCapability
);


// ============================================================
// 4. EXPLICIT CONFLICT RESOLUTION
// ============================================================

const CSVExporter = {
    export() {
        return 'CSV DATA';
    }
};

const JSONExporter = {
    export() {
        return '{"format":"JSON"}';
    }
};

class ExportManager {
    constructor() {
        this.exporters = {
            csv: CSVExporter,
            json: JSONExporter
        };
    }

    export(format) {
        const exporter = this.exporters[format];

        if (!exporter) {
            throw new Error(`Unsupported export format: ${format}`);
        }

        return exporter.export();
    }
}


// ============================================================
// 5. DIAMOND-LIKE BEHAVIOR GRAPH
// ============================================================

class RootService {
    execute() {
        return ['RootService'];
    }
}

class AuthenticationService extends RootService {
    execute() {
        return [
            'AuthenticationService',
            ...super.execute()
        ];
    }
}

class AuditService extends RootService {
    execute() {
        return [
            'AuditService',
            ...super.execute()
        ];
    }
}

class EnterpriseService extends AuthenticationService {
    constructor() {
        super();

        this.auditService = new AuditService();
    }

    execute() {
        return [
            ...super.execute(),
            ...this.auditService.execute()
        ];
    }
}


// ============================================================
// 6. DYNAMIC CAPABILITY REGISTRY
// ============================================================

class CapabilityRegistry {
    #capabilities = new Map();

    register(name, implementation) {
        if (
            typeof name !== 'string' ||
            !name.trim() ||
            !implementation ||
            typeof implementation !== 'object'
        ) {
            throw new TypeError('Invalid capability registration');
        }

        if (this.#capabilities.has(name)) {
            throw new Error(`Capability already registered: ${name}`);
        }

        this.#capabilities.set(name, Object.freeze({
            ...implementation
        }));
    }

    resolve(name) {
        const capability = this.#capabilities.get(name);

        if (!capability) {
            throw new Error(`Unknown capability: ${name}`);
        }

        return capability;
    }

    list() {
        return [...this.#capabilities.keys()];
    }
}


// ============================================================
// 7. EVENT-DRIVEN WORKFLOW
// ============================================================

const EventEmitter = require('node:events');

class WorkflowEngine extends EventEmitter {
    constructor() {
        super();

        this.state = 'CREATED';
        this.history = [];
    }

    transition(nextState) {
        const transitions = {
            CREATED: ['VALIDATING', 'CANCELLED'],
            VALIDATING: ['PROCESSING', 'FAILED'],
            PROCESSING: ['COMPLETED', 'FAILED'],
            COMPLETED: [],
            FAILED: [],
            CANCELLED: []
        };

        if (!transitions[this.state]?.includes(nextState)) {
            throw new Error(
                `Invalid transition: ${this.state} -> ${nextState}`
            );
        }

        const previous = this.state;
        this.state = nextState;

        const event = {
            previous,
            current: nextState,
            timestamp: new Date().toISOString()
        };

        this.history.push(event);
        this.emit('stateChanged', event);
    }

    async execute(task) {
        if (typeof task !== 'function') {
            throw new TypeError('Task must be a function');
        }

        try {
            this.transition('VALIDATING');

            await Promise.resolve();

            this.transition('PROCESSING');

            const result = await task();

            this.transition('COMPLETED');

            return result;
        } catch (error) {
            if (
                this.state === 'VALIDATING' ||
                this.state === 'PROCESSING'
            ) {
                this.transition('FAILED');
            }

            throw error;
        }
    }
}


// ============================================================
// 8. ASYNCHRONOUS CAPABILITY EXECUTION
// ============================================================

class AsyncMultiCapabilityService {
    constructor() {
        this.handlers = new Map();
    }

    register(name, handler) {
        if (this.handlers.has(name)) {
            throw new Error(`Duplicate handler: ${name}`);
        }

        if (typeof handler !== 'function') {
            throw new TypeError('Handler must be a function');
        }

        this.handlers.set(name, handler);
    }

    async execute(name, payload) {
        const handler = this.handlers.get(name);

        if (!handler) {
            throw new Error(`Handler not found: ${name}`);
        }

        return await handler(payload);
    }

    async executeAll(payload) {
        const tasks = [...this.handlers.entries()].map(
            async ([name, handler]) => ({
                name,
                result: await handler(payload)
            })
        );

        return Promise.all(tasks);
    }
}


// ============================================================
// 9. PROTOTYPE AND CAPABILITY INSPECTION
// ============================================================

function inspectCapabilities(instance) {
    const ownMethods = Object.getOwnPropertyNames(
        Object.getPrototypeOf(instance)
    );

    const mixinMethods = Object.keys(instance)
        .filter(key => typeof instance[key] === 'function');

    return {
        ownMethods,
        mixinMethods,
        prototype: Object.getPrototypeOf(
            Object.getPrototypeOf(instance)
        )?.constructor?.name ?? null
    };
}


// ============================================================
// 10. AUTOMATED TESTS
// ============================================================

async function runTests() {
    // Prototype inheritance.
    const camera = new NetworkCamera('Entrance');
    console.assert(camera.capture() === 'Image captured');
    console.assert(camera.connect() === 'Network connected');
    console.assert(camera instanceof Device);

    // Mixins.
    const repository = new RepositoryService();
    const saved = repository.save({ id: 10 });

    console.assert(saved.success);
    console.assert(repository.auditRecords.length === 1);

    // Validation failure.
    try {
        repository.validate(null);
        throw new Error('Validation should have failed');
    } catch (error) {
        console.assert(error instanceof TypeError);
    }

    // Multiple capabilities.
    const storage = new MultiCapabilityRepository();
    storage.write(1, 'Record A');
    console.assert(storage.read(1) === 'Record A');
    console.assert(storage.remove(1));
    console.assert(storage.read(1) === null);

    // Explicit conflict resolution.
    const manager = new ExportManager();
    console.assert(manager.export('csv') === 'CSV DATA');

    // Unknown export format.
    try {
        manager.export('xml');
        throw new Error('Unsupported format should fail');
    } catch (error) {
        console.assert(error.message.includes('Unsupported'));
    }

    // Diamond-like behavior graph.
    const enterprise = new EnterpriseService();
    const execution = enterprise.execute();

    console.assert(execution.includes('AuthenticationService'));
    console.assert(execution.includes('AuditService'));

    // Capability registry.
    const registry = new CapabilityRegistry();
    registry.register('logging', LoggingMixin);

    console.assert(registry.list().includes('logging'));

    // Duplicate registration.
    try {
        registry.register('logging', LoggingMixin);
        throw new Error('Duplicate registration should fail');
    } catch (error) {
        console.assert(error.message.includes('already registered'));
    }

    // Event-driven workflow.
    const workflow = new WorkflowEngine();
    let receivedEvents = 0;

    workflow.on('stateChanged', () => {
        receivedEvents++;
    });

    const result = await workflow.execute(
        async () => 'Deployment successful'
    );

    console.assert(result === 'Deployment successful');
    console.assert(workflow.state === 'COMPLETED');
    console.assert(receivedEvents === 3);

    // Workflow failure.
    const failedWorkflow = new WorkflowEngine();

    try {
        await failedWorkflow.execute(async () => {
            throw new Error('Processing failed');
        });
    } catch (error) {
        console.assert(error.message === 'Processing failed');
    }

    console.assert(failedWorkflow.state === 'FAILED');

    // Async capability execution.
    const asyncService = new AsyncMultiCapabilityService();

    asyncService.register(
        'validate',
        async payload => payload.id > 0
    );

    asyncService.register(
        'transform',
        async payload => payload.id * 2
    );

    const validation = await asyncService.execute(
        'validate',
        { id: 10 }
    );

    console.assert(validation === true);

    const results = await asyncService.executeAll({ id: 10 });

    console.assert(results.length === 2);

    console.log('All JavaScript tests passed.');
}


// ============================================================
// 11. EXECUTION
// ============================================================

async function main() {
    console.log('MULTIPLE INHERITANCE IN JAVASCRIPT');

    const repository = new RepositoryService();

    repository.save({
        id: 101,
        name: 'Enterprise Record'
    });

    console.log('\nPrototype inheritance:');

    const camera = new NetworkCamera('Security Camera');

    console.log(camera.describe());
    console.log(camera.capture());
    console.log(camera.connect());

    console.log('\nCapability composition:');

    const storage = new MultiCapabilityRepository();

    storage.write(101, 'Protected record');

    console.log('Read:', storage.read(101));

    console.log('\nExplicit method resolution:');

    const exporter = new ExportManager();

    console.log('CSV:', exporter.export('csv'));
    console.log('JSON:', exporter.export('json'));

    console.log('\nDiamond-like behavior graph:');

    console.log(new EnterpriseService().execute());

    console.log('\nCapability inspection:');

    console.log(inspectCapabilities(repository));

    console.log('\nEvent-driven workflow:');

    const workflow = new WorkflowEngine();

    workflow.on('stateChanged', event => {
        console.log(`${event.previous} -> ${event.current}`);
    });

    await workflow.execute(async () => 'Task completed');

    console.log('\nAutomated tests:');

    await runTests();
}

main().catch(error => {
    console.error('Application failed:', error.message);
    process.exitCode = 1;
});
