'use strict';

/*
 * Copying Data in JavaScript
 *
 * This program focuses on JavaScript-specific copying behavior:
 * reference assignment, shallow copies, structuredClone(), object spread,
 * array methods, prototypes, circular structures, JSON boundaries,
 * event-driven state snapshots, and defensive API boundaries.
 *
 * Run with:
 *   node copying-data.js
 */

const heading = (title) => {
    console.log(`\n${'='.repeat(78)}\n${title}\n${'='.repeat(78)}`);
};

const showIdentity = (label, left, right) => {
    console.log(
        `${label}: same reference=${left === right}, same JSON value=${
            JSON.stringify(left) === JSON.stringify(right)
        }`
    );
};

function assignmentIsNotCopying() {
    heading('Reference assignment is not copying');

    const liveConfig = {
        service: 'orders',
        limits: {
            requestsPerMinute: 500
        },
        regions: ['ap-south-1']
    };

    const alias = liveConfig;

    alias.limits.requestsPerMinute = 1000;
    alias.regions.push('eu-west-1');

    console.log('Live configuration:', JSON.stringify(liveConfig, null, 2));
    console.log('Same outer object:', liveConfig === alias);
}

function demonstrateShallowCopies() {
    heading('Shallow copies with spread and Object.assign');

    const source = {
        service: 'search',
        limits: {
            timeoutSeconds: 5
        },
        tags: ['critical', 'customer-facing']
    };

    const spreadCopy = { ...source };
    const assignCopy = Object.assign({}, source);

    spreadCopy.service = 'search-canary';
    spreadCopy.limits.timeoutSeconds = 15;
    assignCopy.tags.push('production');

    console.log('Original:', JSON.stringify(source, null, 2));
    console.log('Spread copy:', JSON.stringify(spreadCopy, null, 2));
    console.log('Object.assign copy:', JSON.stringify(assignCopy, null, 2));

    console.log('Outer object isolated:', source !== spreadCopy);
    console.log(
        'Nested object shared:',
        source.limits === spreadCopy.limits
    );
    console.log(
        'Nested array shared:',
        source.tags === assignCopy.tags
    );
}

function demonstrateArrayCopying() {
    heading('Array copying and nested elements');

    const deployments = [
        {
            region: 'ap-south-1',
            replicas: 3
        },
        {
            region: 'eu-west-1',
            replicas: 2
        }
    ];

    const shallow = [...deployments];
    const deep = structuredClone(deployments);

    shallow[0].replicas = 5;
    deep[1].replicas = 7;

    console.log('Original:', JSON.stringify(deployments, null, 2));
    console.log('Shallow:', JSON.stringify(shallow, null, 2));
    console.log('Deep:', JSON.stringify(deep, null, 2));

    console.log(
        'Nested object shared by shallow copy:',
        deployments[0] === shallow[0]
    );
    console.log(
        'Nested object shared by deep copy:',
        deployments[1] === deep[1]
    );
}

function demonstrateStructuredClone() {
    heading('structuredClone for recursive data copying');

    const source = {
        service: 'payment-api',
        configuration: {
            retry: {
                maxAttempts: 4,
                backoffMs: 250
            },
            regions: ['IN', 'EU']
        }
    };

    const clone = structuredClone(source);

    clone.configuration.retry.maxAttempts = 8;
    clone.configuration.regions.push('US');

    console.log('Original:', JSON.stringify(source, null, 2));
    console.log('Clone:', JSON.stringify(clone, null, 2));

    console.log(
        'Nested retry object shared:',
        source.configuration.retry === clone.configuration.retry
    );
}

function demonstrateCircularReferences() {
    heading('Circular references');

    const node = {
        name: 'root',
        children: []
    };

    node.parent = node;

    const clone = structuredClone(node);

    console.log('Original self-reference:', node.parent === node);
    console.log('Clone self-reference:', clone.parent === clone);
    console.log('Clone independent:', clone !== node);

    try {
        JSON.stringify(node);
    } catch (error) {
        console.log(
            'JSON.stringify cannot serialize the circular object:',
            error.name
        );
    }
}

function demonstrateJSONCopyBoundary() {
    heading('JSON serialization as a representation boundary');

    const request = {
        operation: 'rebuild-index',
        options: {
            dryRun: false,
            shards: [1, 2, 3]
        }
    };

    const transferred = JSON.parse(JSON.stringify(request));

    transferred.options.shards.push(4);

    console.log('Original:', JSON.stringify(request, null, 2));
    console.log('Transferred:', JSON.stringify(transferred, null, 2));

    console.log(
        'Nested options are separate objects:',
        request.options !== transferred.options
    );

    console.log(
        'JSON is not equivalent to a general-purpose clone. It cannot preserve '
        + 'functions, undefined values, prototypes, Map, Set, circular graphs, '
        + 'and several special object types.'
    );
}

class ConfigurationRepository {
    #state;
    #history = [];

    constructor(initialState) {
        this.#state = structuredClone(initialState);
        this.#validate(this.#state);
    }

    #validate(state) {
        if (!state || typeof state !== 'object' || Array.isArray(state)) {
            throw new TypeError('Configuration must be an object.');
        }

        if (!state.features || typeof state.features !== 'object') {
            throw new TypeError('features must be an object.');
        }

        if (!state.limits || typeof state.limits !== 'object') {
            throw new TypeError('limits must be an object.');
        }
    }

    read() {
        // Returning the clone protects private repository state from callers.
        return structuredClone(this.#state);
    }

    setFeature(name, enabled) {
        if (typeof name !== 'string' || name.trim() === '') {
            throw new TypeError('Feature name must be a non-empty string.');
        }

        if (typeof enabled !== 'boolean') {
            throw new TypeError('Feature state must be boolean.');
        }

        this.#history.push(structuredClone(this.#state));
        this.#state.features[name] = enabled;
    }

    setLimit(name, value) {
        if (!Number.isInteger(value) || value < 0) {
            throw new RangeError('Limit must be a non-negative integer.');
        }

        this.#history.push(structuredClone(this.#state));
        this.#state.limits[name] = value;
    }

    rollback() {
        if (this.#history.length === 0) {
            throw new Error('No previous state is available.');
        }

        this.#state = this.#history.pop();
    }

    historyDepth() {
        return this.#history.length;
    }
}

function demonstrateDefensiveAPI() {
    heading('Defensive copying at API boundaries');

    const repository = new ConfigurationRepository({
        features: {
            auditLogging: true
        },
        limits: {
            requestsPerMinute: 1000
        }
    });

    const externalState = repository.read();

    externalState.features.auditLogging = false;
    externalState.limits.requestsPerMinute = 1;

    console.log('Caller-modified state:', JSON.stringify(externalState, null, 2));
    console.log(
        'Protected repository state:',
        JSON.stringify(repository.read(), null, 2)
    );

    repository.setFeature('riskScoring', true);
    repository.setLimit('requestsPerMinute', 2000);

    console.log('After updates:', JSON.stringify(repository.read(), null, 2));

    repository.rollback();

    console.log(
        'After rollback:',
        JSON.stringify(repository.read(), null, 2)
    );
}

function demonstrateEventDrivenSnapshots() {
    heading('Event-driven state snapshots');

    class StateBus extends EventTarget {
        #state;

        constructor(initialState) {
            super();
            this.#state = structuredClone(initialState);
        }

        update(mutator) {
            const previous = structuredClone(this.#state);
            const next = structuredClone(this.#state);

            mutator(next);

            this.#state = next;

            this.dispatchEvent(
                new CustomEvent('stateChanged', {
                    detail: {
                        previous,
                        current: structuredClone(this.#state)
                    }
                })
            );
        }

        getState() {
            return structuredClone(this.#state);
        }
    }

    const bus = new StateBus({
        mode: 'production',
        features: {
            cache: true
        }
    });

    bus.addEventListener('stateChanged', (event) => {
        const { previous, current } = event.detail;

        console.log('Previous mode:', previous.mode);
        console.log('Current mode:', current.mode);
        console.log(
            'Previous and current are different snapshots:',
            previous !== current
        );
    });

    bus.update((next) => {
        next.mode = 'maintenance';
        next.features.cache = false;
    });

    console.log('Final state:', JSON.stringify(bus.getState(), null, 2));
}

function demonstrateDatesMapsAndSets() {
    heading('structuredClone preserves several built-in data types');

    const source = {
        capturedAt: new Date('2026-10-04T00:00:00Z'),
        labels: new Set(['critical', 'audited']),
        regionCodes: new Map([
            ['IN', 'ap-south-1'],
            ['DE', 'eu-central-1']
        ])
    };

    const clone = structuredClone(source);

    clone.labels.add('production');
    clone.regionCodes.set('US', 'us-east-1');

    console.log('Original Date is Date:', source.capturedAt instanceof Date);
    console.log('Clone Date is Date:', clone.capturedAt instanceof Date);
    console.log('Original labels:', [...source.labels]);
    console.log('Clone labels:', [...clone.labels]);
    console.log('Original regions:', [...source.regionCodes.entries()]);
    console.log('Clone regions:', [...clone.regionCodes.entries()]);
}

function demonstratePrototypeCaveat() {
    heading('Copying class instances and prototypes');

    class Deployment {
        constructor(service, replicas) {
            this.service = service;
            this.replicas = replicas;
        }

        scale(count) {
            if (!Number.isInteger(count) || count < 1) {
                throw new RangeError('Replica count must be a positive integer.');
            }

            this.replicas = count;
        }
    }

    const deployment = new Deployment('checkout', 3);
    const clone = structuredClone(deployment);

    console.log(
        'Original has Deployment prototype method:',
        typeof deployment.scale === 'function'
    );

    console.log(
        'Structured clone has Deployment prototype method:',
        typeof clone.scale === 'function'
    );

    console.log(
        'The data is cloned, but application-specific class behavior should '
        + 'not be assumed to survive a generic structured clone.'
    );
}

function demonstrateSecurityBoundary() {
    heading('Security and copying');

    const session = {
        user: 'service-account',
        token: 'example-token',
        permissions: ['read', 'write']
    };

    const copiedSession = structuredClone(session);

    copiedSession.permissions.push('admin');
    copiedSession.token = 'rotated-token';

    console.log(
        'Original permissions remain unchanged:',
        session.permissions
    );
    console.log('Original token:', session.token);
    console.log('Copied token:', copiedSession.token);

    console.log(
        'Copying sensitive data creates another in-memory representation. '
        + 'It does not encrypt, revoke, or securely erase the original.'
    );
}

function demonstrateCopyStrategy() {
    heading('Copying strategy based on ownership');

    const decisions = [
        {
            need: 'Same live state',
            mechanism: 'assignment',
            reason: 'Both consumers intentionally share one object.'
        },
        {
            need: 'Independent outer object',
            mechanism: 'spread/Object.assign',
            reason: 'Nested reference sharing is acceptable.'
        },
        {
            need: 'Independent nested state',
            mechanism: 'structuredClone',
            reason: 'The supported object graph needs recursive isolation.'
        },
        {
            need: 'Cross-process or API representation',
            mechanism: 'JSON or another explicit format',
            reason: 'The receiving side should get a defined serialized representation.'
        },
        {
            need: 'Immutable application state',
            mechanism: 'new state plus controlled updates',
            reason: 'Ownership and mutation boundaries become explicit.'
        }
    ];

    for (const decision of decisions) {
        console.log(
            `${decision.need}\n` +
            `  Mechanism: ${decision.mechanism}\n` +
            `  Reason: ${decision.reason}\n`
        );
    }
}

function runAssertions() {
    heading('Copying semantics checks');

    const source = {
        settings: {
            retries: 3
        },
        servers: ['api-1', 'api-2']
    };

    const shallow = { ...source };
    const deep = structuredClone(source);

    console.assert(source !== shallow);
    console.assert(source !== deep);
    console.assert(source.settings === shallow.settings);
    console.assert(source.settings !== deep.settings);

    shallow.settings.retries = 5;
    console.assert(source.settings.retries === 5);

    deep.settings.retries = 7;
    console.assert(source.settings.retries === 5);

    console.log('All copy-semantics assertions passed.');
}

function main() {
    console.log('COPYING DATA IN JAVASCRIPT');
    console.log(`Node.js ${process.version}`);

    assignmentIsNotCopying();
    demonstrateShallowCopies();
    demonstrateArrayCopying();
    demonstrateStructuredClone();
    demonstrateCircularReferences();
    demonstrateJSONCopyBoundary();
    demonstrateDefensiveAPI();
    demonstrateEventDrivenSnapshots();
    demonstrateDatesMapsAndSets();
    demonstratePrototypeCaveat();
    demonstrateSecurityBoundary();
    demonstrateCopyStrategy();
    runAssertions();

    console.log('\nAll JavaScript copying demonstrations completed.');
}

main();
