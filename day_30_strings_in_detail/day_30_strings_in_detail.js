'use strict';

/*
 * Strings in Detail
 *
 * A self-contained Node.js program covering:
 * primitive strings, UTF-16 behavior, Unicode normalization,
 * template literals, validation, regular expressions, parsing,
 * event-driven string workflows, substring search, edit distance,
 * streaming-style processing, redaction, and performance.
 *
 * Run:
 *   node strings_in_detail.js
 */

const readline = require('node:readline');

function heading(title) {
    console.log(`\n${'='.repeat(78)}\n${title}\n${'='.repeat(78)}`);
}

function fundamentalStrings() {
    heading('Fundamental String Operations');

    const text = 'JavaScript provides rich string operations.';
    console.log('Original:', text);
    console.log('Length:', text.length);
    console.log('First character:', text[0]);
    console.log('Slice:', text.slice(0, 10));
    console.log('Substring:', text.substring(11, 21));
    console.log('Uppercase:', text.toUpperCase());
    console.log('Includes "string":', text.toLowerCase().includes('string'));
    console.log('Starts with:', text.startsWith('JavaScript'));
    console.log('Ends with:', text.endsWith('.'));

    const words = ['text', 'processing', 'pipeline'];
    console.log('Joined:', words.join(' | '));
    console.log('Split:', 'alpha,beta,gamma'.split(','));

    // Strings are primitive immutable values. replace() returns a new value.
    const original = 'production';
    const changed = original.replace('production', 'staging');
    console.log('Original:', original);
    console.log('Changed:', changed);
}

function formattingAndEscaping() {
    heading('Formatting and Escaping');

    const service = 'api';
    const environment = 'production';
    const latency = 37.42;

    // Template literals provide readable interpolation and multiline text.
    console.log(
        `Service ${service} is running in ${environment}; latency=${latency.toFixed(2)}ms`
    );

    const escaped = 'A quote: "strings" and a newline:\nnext line';
    console.log(escaped);

    const multiline = `
Text can span multiple lines
without explicit concatenation.
`.trim();

    console.log(multiline);
}

function validation() {
    heading('Validation');

    const usernamePattern = /^[a-z][a-z0-9_]{2,31}$/;

    const candidates = [
        'atul_user',
        'Admin User',
        'x',
        'service_01',
        'user-name'
    ];

    for (const candidate of candidates) {
        console.log(
            `${JSON.stringify(candidate)} -> ${usernamePattern.test(candidate)}`
        );
    }

    function validateTitle(value, maximum = 120) {
        if (typeof value !== 'string') {
            throw new TypeError('title must be a string');
        }

        const cleaned = value.trim().replace(/\s+/g, ' ');

        if (cleaned.length === 0) {
            throw new Error('title cannot be empty');
        }

        if (cleaned.length > maximum) {
            throw new Error('title exceeds maximum length');
        }

        return cleaned;
    }

    for (const value of ['  Quarterly   Revenue  ', '   ', 'Production']) {
        try {
            console.log(JSON.stringify(value), '->', validateTitle(value));
        } catch (error) {
            console.log(JSON.stringify(value), '-> rejected:', error.message);
        }
    }
}

function regexParsing() {
    heading('Regular Expressions and Structured Text');

    const logLines = [
        '2026-09-30 INFO user=atul action=login',
        '2026-09-30 WARN user=admin action=failed-login',
        '2026-09-30 ERROR user=service action=timeout'
    ];

    const pattern =
        /^(?<date>\d{4}-\d{2}-\d{2})\s+(?<level>[A-Z]+)\s+user=(?<user>[A-Za-z0-9_]+)\s+action=(?<action>[A-Za-z-]+)$/;

    for (const line of logLines) {
        const match = line.match(pattern);
        if (match) {
            console.log(match.groups);
        }
    }

    const emailPattern =
        /^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$/;

    for (const email of [
        'person@example.com',
        'invalid@',
        'admin@example.co.in'
    ]) {
        console.log(email, '->', emailPattern.test(email));
    }
}

function unicodeAndUtf16() {
    heading('Unicode and UTF-16');

    const samples = ['café', 'cafe\u0301', '東京', 'नमस्ते', '😀', '👨‍💻'];

    for (const value of samples) {
        console.log(
            JSON.stringify(value),
            'length:',
            value.length,
            'code points:',
            [...value].length
        );
    }

    // JavaScript strings are sequences of UTF-16 code units. A character
    // outside the Basic Multilingual Plane may occupy two code units.
    const emoji = '😀';
    console.log('Emoji code units:', emoji.length);
    console.log('Emoji code points:', [...emoji].length);

    console.log(
        'Code points:',
        [...emoji].map(character => `U+${character.codePointAt(0).toString(16).toUpperCase()}`)
    );

    const composed = 'café';
    const decomposed = 'cafe\u0301';

    console.log('Raw equality:', composed === decomposed);
    console.log(
        'NFC equality:',
        composed.normalize('NFC') === decomposed.normalize('NFC')
    );

    console.log(
        'Case-insensitive comparison:',
        'Straße'.toLocaleLowerCase('de-DE') ===
            'STRASSE'.toLocaleLowerCase('de-DE')
    );
}

function tokenization() {
    heading('Tokenization and Frequency Analysis');

    const text =
        'Release v2.10.4: API latency fell by 18.5% after caching.';

    const tokens = text.match(
        /\d+(?:\.\d+)*%?|[A-Za-z]+(?:[-'][A-Za-z]+)*|[^\w\s]/g
    ) ?? [];

    console.log(tokens);

    const words =
        text.toLowerCase().match(/[a-z]+(?:[-'][a-z]+)*/g) ?? [];

    const frequencies = new Map();

    for (const word of words) {
        frequencies.set(word, (frequencies.get(word) ?? 0) + 1);
    }

    console.log('Frequencies:', Object.fromEntries(frequencies));
}

function naiveSearch(text, pattern) {
    if (pattern.length === 0) {
        return 0;
    }

    if (pattern.length > text.length) {
        return -1;
    }

    for (let start = 0; start <= text.length - pattern.length; start++) {
        let matched = true;

        for (let offset = 0; offset < pattern.length; offset++) {
            if (text[start + offset] !== pattern[offset]) {
                matched = false;
                break;
            }
        }

        if (matched) {
            return start;
        }
    }

    return -1;
}

function kmpSearch(text, pattern) {
    if (pattern.length === 0) {
        return 0;
    }

    const prefix = Array(pattern.length).fill(0);

    for (let i = 1, matched = 0; i < pattern.length; i++) {
        while (matched > 0 && pattern[i] !== pattern[matched]) {
            matched = prefix[matched - 1];
        }

        if (pattern[i] === pattern[matched]) {
            matched++;
        }

        prefix[i] = matched;
    }

    let textIndex = 0;
    let patternIndex = 0;

    while (textIndex < text.length) {
        if (text[textIndex] === pattern[patternIndex]) {
            textIndex++;
            patternIndex++;

            if (patternIndex === pattern.length) {
                return textIndex - patternIndex;
            }
        } else if (patternIndex > 0) {
            patternIndex = prefix[patternIndex - 1];
        } else {
            textIndex++;
        }
    }

    return -1;
}

function substringAlgorithms() {
    heading('Substring Search Algorithms');

    const text = 'ababcabcabababd';
    const pattern = 'ababd';

    console.log('Naive:', naiveSearch(text, pattern));
    console.log('KMP:', kmpSearch(text, pattern));
    console.log('Built-in:', text.indexOf(pattern));
}

function levenshtein(first, second) {
    if (first.length < second.length) {
        [first, second] = [second, first];
    }

    let previous = Array.from(
        { length: second.length + 1 },
        (_, index) => index
    );

    for (let i = 1; i <= first.length; i++) {
        const current = [i];

        for (let j = 1; j <= second.length; j++) {
            const insertion = current[j - 1] + 1;
            const deletion = previous[j] + 1;
            const substitution =
                previous[j - 1] + (first[i - 1] === second[j - 1] ? 0 : 1);

            current.push(Math.min(insertion, deletion, substitution));
        }

        previous = current;
    }

    return previous[previous.length - 1];
}

function editDistanceDemo() {
    heading('Edit Distance');

    for (const [first, second] of [
        ['kitten', 'sitting'],
        ['database', 'databse'],
        ['apple', 'apple']
    ]) {
        console.log(
            `${first} -> ${second}: ${levenshtein(first, second)}`
        );
    }
}

function palindromeAndAnagram() {
    heading('Palindrome and Anagram Processing');

    function isPalindrome(value) {
        const normalized = [...value.toLowerCase()]
            .filter(character => /[\p{L}\p{N}]/u.test(character))
            .join('');

        for (let left = 0, right = normalized.length - 1; left < right; left++, right--) {
            if (normalized[left] !== normalized[right]) {
                return false;
            }
        }

        return true;
    }

    function areAnagrams(first, second) {
        const normalize = value =>
            [...value.toLocaleLowerCase()]
                .filter(character => /[\p{L}\p{N}]/u.test(character))
                .sort()
                .join('');

        return normalize(first) === normalize(second);
    }

    for (const value of ['level', 'A man, a plan, a canal: Panama', 'JavaScript']) {
        console.log(value, '->', isPalindrome(value));
    }

    console.log(
        'Debit Card / Bad Credit:',
        areAnagrams('Debit Card', 'Bad Credit')
    );
}

class TextPipeline {
    #handlers = new Map();

    on(eventName, handler) {
        if (!this.#handlers.has(eventName)) {
            this.#handlers.set(eventName, []);
        }

        this.#handlers.get(eventName).push(handler);
        return this;
    }

    emit(eventName, payload) {
        const handlers = this.#handlers.get(eventName) ?? [];

        for (const handler of handlers) {
            handler(payload);
        }
    }

    process(input) {
        if (typeof input !== 'string') {
            throw new TypeError('TextPipeline requires a string');
        }

        const normalized = input.normalize('NFC').trim();
        this.emit('normalized', normalized);

        const tokens = normalized.match(/\b[\p{L}\p{N}'-]+\b/gu) ?? [];
        this.emit('tokenized', tokens);

        const frequency = new Map();

        for (const token of tokens) {
            const key = token.toLocaleLowerCase();
            frequency.set(key, (frequency.get(key) ?? 0) + 1);
        }

        this.emit('analyzed', frequency);
        return { normalized, tokens, frequency };
    }
}

function eventDrivenTextPipeline() {
    heading('Event-Driven Text Pipeline');

    const pipeline = new TextPipeline();

    pipeline
        .on('normalized', value => {
            console.log('Normalized:', value);
        })
        .on('tokenized', tokens => {
            console.log('Token count:', tokens.length);
        })
        .on('analyzed', frequency => {
            console.log('Frequency:', Object.fromEntries(frequency));
        });

    pipeline.process(
        '  API latency improved after API response caching.  '
    );
}

function redactSensitiveText() {
    heading('Sensitive Text Redaction');

    const message =
        'Contact alice@example.com or bob@example.org. Ticket SEC-48291.';

    const emailPattern =
        /\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+\b/g;
    const ticketPattern = /\b[A-Z]{2,8}-\d{3,8}\b/g;

    const redacted = message
        .replace(emailPattern, '[EMAIL]')
        .replace(ticketPattern, '[TICKET]');

    console.log(redacted);
}

function structuredParsing() {
    heading('Structured Text Parsing');

    const csv = [
        'service,environment,status',
        'api,production,healthy',
        'worker,production,degraded',
        'web,staging,healthy'
    ];

    const records = csv.slice(1).map(line => {
        const [service, environment, status] = line.split(',');
        return { service, environment, status };
    });

    console.log(records);

    const healthyProduction = records.filter(
        record =>
            record.environment === 'production' &&
            record.status === 'healthy'
    );

    console.log('Healthy production:', healthyProduction);
}

function stringPerformance() {
    heading('String Performance');

    const fragments = Array.from(
        { length: 10000 },
        (_, index) => `record-${index}`
    );

    // Array.join allows the runtime to assemble many fragments as one
    // operation instead of repeatedly constructing intermediate strings.
    const combined = fragments.join('|');

    console.log('Fragments:', fragments.length);
    console.log('Combined length:', combined.length);

    console.log(
        'For very large text workloads, processing chunks can reduce peak memory.'
    );
}

function securityConsiderations() {
    heading('Security-Relevant String Handling');

    const dangerousFilename = '../../etc/passwd';
    const safeFilenamePattern = /^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$/;

    console.log(
        'Filename accepted:',
        safeFilenamePattern.test(dangerousFilename)
    );

    const userInput = "' OR '1'='1";

    console.log('Untrusted input:', userInput);
    console.log(
        'Database rule: pass this value as a parameter instead of concatenating it into SQL.'
    );

    const html = '<img src=x onerror=alert(1)>';

    console.log('Untrusted HTML:', html);
    console.log(
        'Browser rule: do not assign untrusted HTML to innerHTML unless it has been sanitized for the exact context.'
    );
}

async function asynchronousTextProcessing() {
    heading('Asynchronous Text Processing');

    const chunks = [
        'first chunk\n',
        'second chunk\n',
        'third chunk\n'
    ];

    async function* source() {
        for (const chunk of chunks) {
            // The timeout represents an asynchronous stream source.
            await new Promise(resolve => setTimeout(resolve, 5));
            yield chunk;
        }
    }

    let characterCount = 0;

    for await (const chunk of source()) {
        characterCount += chunk.length;
        console.log('Received chunk:', JSON.stringify(chunk));
    }

    console.log('Total characters:', characterCount);
}

function readlineExample() {
    heading('Line-Oriented Processing API');

    const input = [
        'INFO request=100',
        'ERROR request=101',
        'INFO request=102'
    ].join('\n');

    const lines = readline.createInterface({
        input: require('node:stream').Readable.from([input]),
        crlfDelay: Infinity
    });

    let errors = 0;

    lines.on('line', line => {
        if (line.startsWith('ERROR')) {
            errors++;
        }
    });

    lines.on('close', () => {
        console.log('Error lines:', errors);
    });
}

async function main() {
    fundamentalStrings();
    formattingAndEscaping();
    validation();
    regexParsing();
    unicodeAndUtf16();
    tokenization();
    substringAlgorithms();
    editDistanceDemo();
    palindromeAndAnagram();
    eventDrivenTextPipeline();
    redactSensitiveText();
    structuredParsing();
    stringPerformance();
    securityConsiderations();
    await asynchronousTextProcessing();
    readlineExample();
}

main().catch(error => {
    console.error('Fatal error:', error.message);
    process.exitCode = 1;
});
