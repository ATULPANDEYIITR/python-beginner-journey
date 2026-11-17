'use strict';

/*
 * THE __init__() METHOD
 *
 * JavaScript does not use Python's __init__().
 * JavaScript classes use constructor().
 *
 * This implementation explores:
 * - Constructor initialization
 * - Default parameters
 * - Object validation
 * - Private fields
 * - Static methods
 * - Inheritance and super()
 * - Composition
 * - Factory functions
 * - Event-driven initialization
 * - Asynchronous resource initialization
 * - State transitions
 * - Error handling
 */

const { EventEmitter } = require('node:events');
const { randomUUID } = require('node:crypto');
const assert = require('node:assert/strict');

// ==========================================================
// 1. BASIC CONSTRUCTOR
// ==========================================================

class Student {
    constructor(name, age) {
        if (typeof name !== 'string' || !name.trim()) {
            throw new TypeError('Name must be a non-empty string.');
        }

        if (!Number.isInteger(age) || age < 0 || age > 120) {
            throw new RangeError('Age must be an integer from 0 to 120.');
        }

        this.name = name.trim();
        this.age = age;
    }

    introduce() {
        return `${this.name} is ${this.age} years old.`;
    }
}

// ==========================================================
// 2. DEFAULT PARAMETERS AND OBJECT CONFIGURATION
// ==========================================================

class ServerConfiguration {
    constructor({
        host = 'localhost',
        port = 3000,
        secure = false
    } = {}) {
        if (typeof host !== 'string' || !host.trim()) {
            throw new TypeError('Invalid server host.');
        }

        if (!Number.isInteger(port) || port < 1 || port > 65535) {
            throw new RangeError('Invalid server port.');
        }

        if (typeof secure !== 'boolean') {
            throw new TypeError('Secure must be a boolean.');
        }

        this.host = host.trim();
        this.port = port;
        this.secure = secure;
    }

    get endpoint() {
        const protocol = this.secure ? 'https' : 'http';
        return `${protocol}://${this.host}:${this.port}`;
    }
}

// ==========================================================
// 3. PRIVATE FIELDS AND INITIALIZATION INVARIANTS
// ==========================================================

class BankAccount {
    #balance;
    #status;

    constructor(owner, initialBalance = 0) {
        if (typeof owner !== 'string' || !owner.trim()) {
            throw new TypeError('Account owner is required.');
        }

        if (
            typeof initialBalance !== 'number' ||
            !Number.isFinite(initialBalance) ||
            initialBalance < 0
        ) {
            throw new RangeError('Invalid initial balance.');
        }

        this.id = randomUUID();
        this.owner = owner.trim();
        this.#balance = initialBalance;
        this.#status = 'active';
    }

    get balance() {
        return this.#balance;
    }

    get status() {
        return this.#status;
    }

    deposit(amount) {
        if (this.#status !== 'active') {
            throw new Error('Account is not active.');
        }

        if (
            typeof amount !== 'number' ||
            !Number.isFinite(amount) ||
            amount <= 0
        ) {
            throw new RangeError('Deposit must be positive and finite.');
        }

        this.#balance += amount;
    }

    suspend() {
        if (this.#status === 'closed') {
            throw new Error('Closed accounts cannot be suspended.');
        }

        this.#status = 'suspended';
    }

    static createEmpty(owner) {
        return new BankAccount(owner);
    }
}

// ==========================================================
// 4. INDEPENDENT OBJECT STATE
// ==========================================================

class Project {
    constructor(name, members = []) {
        if (typeof name !== 'string' || !name.trim()) {
            throw new TypeError('Project name is required.');
        }

        if (!Array.isArray(members)) {
            throw new TypeError('Members must be an array.');
        }

        if (!members.every(
            member => typeof member === 'string' && member.trim()
        )) {
            throw new TypeError('Invalid project member.');
        }

        this.name = name.trim();

        // Each project receives its own collection.
        this.members = [...members];
    }

    addMember(member) {
        if (typeof member !== 'string' || !member.trim()) {
            throw new TypeError('Invalid member name.');
        }

        const normalized = member.trim();

        if (!this.members.includes(normalized)) {
            this.members.push(normalized);
        }
    }
}

// ==========================================================
// 5. INHERITANCE AND CONSTRUCTOR CHAINING
// ==========================================================

class Employee {
    constructor(name, employeeId) {
        if (typeof name !== 'string' || !name.trim()) {
            throw new TypeError('Employee name is required.');
        }

        if (typeof employeeId !== 'string' || !employeeId.trim()) {
            throw new TypeError('Employee ID is required.');
        }

        this.name = name.trim();
        this.employeeId = employeeId.trim();
    }
}

class Manager extends Employee {
    constructor(name, employeeId, teamSize) {
        // Parent constructor must execute before using this.
        super(name, employeeId);

        if (!Number.isInteger(teamSize) || teamSize < 0) {
            throw new RangeError('Invalid team size.');
        }

        this.teamSize = teamSize;
    }
}

// ==========================================================
// 6. COMPOSITION
// ==========================================================

class Address {
    constructor(city, country) {
        if (
            typeof city !== 'string' ||
            !city.trim() ||
            typeof country !== 'string' ||
            !country.trim()
        ) {
            throw new TypeError('Valid address information is required.');
        }

        this.city = city.trim();
        this.country = country.trim();
    }
}

class Organization {
    constructor(name, address) {
        if (typeof name !== 'string' || !name.trim()) {
            throw new TypeError('Organization name is required.');
        }

        if (!(address instanceof Address)) {
            throw new TypeError('An Address instance is required.');
        }

        this.name = name.trim();
        this.address = address;
    }
}

// ==========================================================
// 7. FACTORY METHODS AND VALIDATED OBJECT CREATION
// ==========================================================

class Product {
    constructor(name, price, category) {
        if (typeof name !== 'string' || !name.trim()) {
            throw new TypeError('Product name is required.');
        }

        if (typeof price !== 'number' || !Number.isFinite(price) || price < 0) {
            throw new RangeError('Invalid product price.');
        }

        if (typeof category !== 'string' || !category.trim()) {
            throw new TypeError('Category is required.');
        }

        this.name = name.trim();
        this.price = price;
        this.category = category.trim();
    }

    static fromObject(data) {
        if (
            data === null ||
            typeof data !== 'object' ||
            Array.isArray(data)
        ) {
            throw new TypeError('Product data must be an object.');
        }

        const keys = Object.keys(data).sort();
        const expected = ['category', 'name', 'price'];

        if (
            keys.length !== expected.length ||
            keys.some((key, index) => key !== expected[index])
        ) {
            throw new TypeError('Unexpected product properties.');
        }

        return new Product(data.name, data.price, data.category);
    }
}

// ==========================================================
// 8. EVENT-DRIVEN INITIALIZATION
// ==========================================================

class Application extends EventEmitter {
    constructor(name, configuration) {
        super();

        if (typeof name !== 'string' || !name.trim()) {
            throw new TypeError('Application name is required.');
        }

        if (!(configuration instanceof ServerConfiguration)) {
            throw new TypeError('Invalid server configuration.');
        }

        this.name = name.trim();
        this.configuration = configuration;
        this.state = 'created';
        this.initializedAt = new Date();

        this.emit('created', {
            application: this.name,
            state: this.state
        });
    }

    initialize() {
        if (this.state !== 'created') {
            throw new Error('Application has already been initialized.');
        }

        this.state = 'initialized';

        this.emit('initialized', {
            application: this.name,
            endpoint: this.configuration.endpoint
        });
    }

    shutdown() {
        if (this.state !== 'initialized') {
            throw new Error('Application is not running.');
        }

        this.state = 'stopped';
        this.emit('shutdown', this.name);
    }
}

// ==========================================================
// 9. ASYNCHRONOUS RESOURCE INITIALIZATION
// ==========================================================

class ResourceManager {
    #resources = new Map();

    async initialize(resourceName, initializer) {
        if (
            typeof resourceName !== 'string' ||
            !resourceName.trim()
        ) {
            throw new TypeError('Resource name is required.');
        }

        if (typeof initializer !== 'function') {
            throw new TypeError('Initializer must be a function.');
        }

        const name = resourceName.trim();

        if (this.#resources.has(name)) {
            throw new Error(`Resource already exists: ${name}`);
        }

        // Store a pending Promise to prevent duplicate initialization.
        const pending = Promise.resolve().then(initializer);

        this.#resources.set(name, pending);

        try {
            const resource = await pending;

            if (resource === null || resource === undefined) {
                throw new Error('Initializer returned an empty resource.');
            }

            this.#resources.set(name, resource);
            return resource;
        } catch (error) {
            this.#resources.delete(name);
            throw new Error(
                `Initialization failed for ${name}: ${error.message}`,
                { cause: error }
            );
        }
    }

    get(name) {
        if (!this.#resources.has(name)) {
            throw new Error(`Resource not found: ${name}`);
        }

        return this.#resources.get(name);
    }

    async initializeAll(entries) {
        if (!Array.isArray(entries)) {
            throw new TypeError('Entries must be an array.');
        }

        const names = entries.map(entry => entry.name);

        if (new Set(names).size !== names.length) {
            throw new Error('Duplicate resource names are not allowed.');
        }

        // Wait for every initialization operation to finish.
        return Promise.all(
            entries.map(entry =>
                this.initialize(entry.name, entry.initializer)
            )
        );
    }
}

// ==========================================================
// 10. EXECUTABLE TESTS
// ==========================================================

async function main() {
    console.log('\n1. Basic constructor');

    const student = new Student('Atul', 25);
    console.log(student.introduce());

    console.log('\n2. Default configuration');

    const server = new ServerConfiguration();
    console.log(server.endpoint);

    console.log('\n3. Private fields');

    const account = BankAccount.createEmpty('Atul');
    account.deposit(5000);

    console.log(account.balance, account.status);

    console.log('\n4. Independent object collections');

    const projectA = new Project('Cybersecurity');
    const projectB = new Project('Cloud Computing');

    projectA.addMember('Researcher A');

    assert.equal(projectB.members.length, 0);
    console.log(projectA.members, projectB.members);

    console.log('\n5. Constructor chaining');

    const manager = new Manager('Anita', 'EMP-101', 8);
    console.log(manager.name, manager.employeeId, manager.teamSize);

    console.log('\n6. Composition');

    const address = new Address('Lucknow', 'India');
    const organization = new Organization('Research Lab', address);

    console.log(organization.name, organization.address.city);

    console.log('\n7. Factory construction');

    const product = Product.fromObject({
        name: 'Sensor',
        price: 2500,
        category: 'Hardware'
    });

    console.log(product);

    console.log('\n8. Event-driven initialization');

    const app = new Application('Risk Engine', server);

    app.on('initialized', event => {
        console.log('Initialized:', event);
    });

    app.initialize();
    app.shutdown();

    console.log('\n9. Asynchronous resource initialization');

    const resources = new ResourceManager();

    const [database, cache] = await resources.initializeAll([
        {
            name: 'database',
            initializer: async () => ({
                connected: true,
                engine: 'PostgreSQL'
            })
        },
        {
            name: 'cache',
            initializer: async () => ({
                connected: true,
                engine: 'Redis'
            })
        }
    ]);

    console.log(database, cache);

    console.log('\n10. Validation failures');

    const invalidOperations = [
        () => new Student('', 20),
        () => new Student('User', -5),
        () => new ServerConfiguration({ port: 70000 }),
        () => new BankAccount('User', -100),
        () => new Manager('User', 'EMP-1', -1),
        () => new Product('Device', -1, 'Hardware'),
        () => new Organization('Lab', {})
    ];

    for (const operation of invalidOperations) {
        assert.throws(operation);
    }

    console.log('All invalid inputs were rejected.');

    console.log('\n11. Resource failure handling');

    await assert.rejects(
        resources.initialize('broken', async () => {
            throw new Error('Connection refused');
        }),
        /Initialization failed/
    );

    assert.throws(() => resources.get('broken'));

    console.log('\n12. Final assertions');

    assert.equal(student.age, 25);
    assert.equal(account.balance, 5000);
    assert.equal(manager.teamSize, 8);
    assert.equal(app.state, 'stopped');
    assert.equal(resources.get('database').connected, true);

    console.log('All tests passed.');
}

main().catch(error => {
    console.error('Application failure:', error.message);
    process.exitCode = 1;
});
