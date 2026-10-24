'use strict';

const fs = require('node:fs');
const path = require('node:path');

class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}

class FunctionRegistry {
    constructor() {
        this.functions = new Map();
        this.metrics = new Map();
    }

    register(name, fn) {
        if (typeof name !== 'string' || name.trim() === '') {
            throw new ValidationError('Function name cannot be empty.');
        }

        if (typeof fn !== 'function') {
            throw new TypeError('Registered value must be a function.');
        }

        if (this.functions.has(name)) {
            throw new ValidationError(`Function already registered: ${name}`);
        }

        this.functions.set(name, fn);
        this.metrics.set(name, {
            calls: 0,
            failures: 0,
            totalMilliseconds: 0
        });
    }

    async call(name, ...args) {
        if (!this.functions.has(name)) {
            throw new Error(`Unknown function: ${name}`);
        }

        const metric = this.metrics.get(name);
        const started = process.hrtime.bigint();
        metric.calls += 1;

        try {
            return await this.functions.get(name)(...args);
        } catch (error) {
            metric.failures += 1;
            throw error;
        } finally {
            const elapsed = process.hrtime.bigint() - started;
            metric.totalMilliseconds += Number(elapsed) / 1_000_000;
        }
    }

    getMetrics(name) {
        if (!this.metrics.has(name)) {
            throw new Error(`Unknown function: ${name}`);
        }

        const metric = this.metrics.get(name);
        return {
            ...metric,
            averageMilliseconds:
                metric.calls === 0
                    ? 0
                    : metric.totalMilliseconds / metric.calls
        };
    }
}

function validateText(value, fieldName = 'value') {
    if (typeof value !== 'string') {
        throw new ValidationError(`${fieldName} must be a string.`);
    }

    const normalized = value.trim();

    if (normalized.length === 0) {
        throw new ValidationError(`${fieldName} cannot be empty.`);
    }

    return normalized;
}

function normalizeTags(tags) {
    if (!Array.isArray(tags)) {
        throw new ValidationError('Tags must be an array.');
    }

    const result = new Set();

    for (const tag of tags) {
        if (typeof tag !== 'string') {
            throw new ValidationError('Every tag must be a string.');
        }

        const normalized = tag.trim().toLowerCase();

        if (normalized === '') {
            continue;
        }

        if (normalized.length > 40) {
            throw new ValidationError('A tag cannot exceed 40 characters.');
        }

        result.add(normalized);
    }

    return [...result].sort();
}

function calculateStatistics(values) {
    if (!Array.isArray(values) || values.length === 0) {
        throw new ValidationError('At least one numeric value is required.');
    }

    if (!values.every(
        value => typeof value === 'number' && Number.isFinite(value)
    )) {
        throw new ValidationError('All values must be finite numbers.');
    }

    const total = values.reduce((sum, value) => sum + value, 0);
    const mean = total / values.length;
    const variance = values.reduce(
        (sum, value) => sum + ((value - mean) ** 2),
        0
    ) / values.length;

    return {
        count: values.length,
        minimum: Math.min(...values),
        maximum: Math.max(...values),
        mean,
        populationStdDev: Math.sqrt(variance)
    };
}

function* chunked(items, size) {
    if (!Number.isInteger(size) || size <= 0) {
        throw new ValidationError('Chunk size must be a positive integer.');
    }

    for (let index = 0; index < items.length; index += size) {
        yield items.slice(index, index + size);
    }
}

function retry(fn, attempts = 3, delayMilliseconds = 0) {
    if (!Number.isInteger(attempts) || attempts <= 0) {
        throw new ValidationError('Attempts must be a positive integer.');
    }

    if (!Number.isFinite(delayMilliseconds) || delayMilliseconds < 0) {
        throw new ValidationError('Delay must be a non-negative number.');
    }

    return async (...args) => {
        let lastError;

        for (let attempt = 1; attempt <= attempts; attempt += 1) {
            try {
                return await fn(...args);
            } catch (error) {
                lastError = error;

                if (attempt < attempts && delayMilliseconds > 0) {
                    await new Promise(resolve =>
                        setTimeout(resolve, delayMilliseconds)
                    );
                }
            }
        }

        throw lastError;
    };
}

async function processTasks(tasks) {
    if (!Array.isArray(tasks)) {
        throw new ValidationError('Tasks must be an array.');
    }

    return Promise.all(
        tasks.map(async task => {
            const name = validateText(task.name, 'task.name');

            if (typeof task.operation !== 'function') {
                throw new ValidationError(
                    `Task ${name} does not contain a callable operation.`
                );
            }

            const result = {
                name,
                status: 'running',
                value: null,
                error: null
            };

            try {
                result.value = await task.operation(task.input);
                result.status = 'completed';
            } catch (error) {
                result.status = 'failed';
                result.error = error instanceof Error
                    ? error.message
                    : String(error);
            }

            return result;
        })
    );
}

function writeJsonSafely(filename, payload) {
    const absolutePath = path.resolve(filename);

    if (path.extname(absolutePath).toLowerCase() !== '.json') {
        throw new ValidationError('Output file must use .json.');
    }

    const directory = path.dirname(absolutePath);
    fs.mkdirSync(directory, { recursive: true });

    const temporaryPath = `${absolutePath}.tmp`;

    try {
        fs.writeFileSync(
            temporaryPath,
            JSON.stringify(payload, null, 2),
            {
                encoding: 'utf8',
                flag: 'w'
            }
        );

        fs.renameSync(temporaryPath, absolutePath);
    } catch (error) {
        if (fs.existsSync(temporaryPath)) {
            fs.rmSync(temporaryPath);
        }
        throw new Error(`Could not write ${absolutePath}: ${error.message}`);
    }

    return absolutePath;
}

async function main() {
    const registry = new FunctionRegistry();

    registry.register('normalizeTags', normalizeTags);
    registry.register('statistics', calculateStatistics);
    registry.register('validateText', validateText);

    const tags = await registry.call(
        'normalizeTags',
        [' JavaScript ', 'javascript', 'functions', 'reuse']
    );

    const statistics = await registry.call(
        'statistics',
        [10, 20, 30, 40, 50]
    );

    const text = await registry.call(
        'validateText',
        'Reusable functions reduce duplication.',
        'description'
    );

    console.log('Normalized tags:', tags);
    console.log('Statistics:', statistics);
    console.log('Validated text:', text);

    const tasks = [
        {
            name: 'tags',
            operation: normalizeTags,
            input: ['API', 'api', 'database']
        },
        {
            name: 'statistics',
            operation: calculateStatistics,
            input: [4, 8, 15, 16, 23, 42]
        },
        {
            name: 'invalid-statistics',
            operation: calculateStatistics,
            input: []
        }
    ];

    const results = await processTasks(tasks);

    console.log('Task results:');
    console.table(results);

    const retryingOperation = retry(
        async value => {
            if (value < 3) {
                throw new Error('Transient failure');
            }
            return value * 10;
        },
        3
    );

    console.log('Retry result:', await retryingOperation(3));

    const report = {
        tags,
        statistics,
        metrics: registry.getMetrics('statistics'),
        chunks: [...chunked([1, 2, 3, 4, 5], 2)],
        tasks: results
    };

    const outputPath = writeJsonSafely(
        path.join(process.cwd(), 'function-report.json'),
        report
    );

    console.log(`Report written to ${outputPath}`);

    if (
        JSON.stringify(normalizeTags(['A', 'a', 'B'])) !==
        JSON.stringify(['a', 'b'])
    ) {
        throw new Error('Normalization assertion failed.');
    }

    if (JSON.stringify([...chunked([1, 2, 3, 4, 5], 2)]) !==
        JSON.stringify([[1, 2], [3, 4], [5]])) {
        throw new Error('Chunking assertion failed.');
    }

    try {
        calculateStatistics([]);
    } catch (error) {
        if (!(error instanceof ValidationError)) {
            throw error;
        }
        console.log('Validation test passed.');
    }
}

main().catch(error => {
    console.error(`Execution failed: ${error.message}`);
    process.exitCode = 1;
});
