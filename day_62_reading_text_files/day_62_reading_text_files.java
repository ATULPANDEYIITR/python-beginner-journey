import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class TextFileReaderApp {

    enum FileStatus {
        AVAILABLE,
        MISSING,
        NOT_REGULAR,
        TOO_LARGE
    }

    record SearchResult(int lineNumber, String text) {}

    record TextStatistics(
        Path path,
        long characters,
        long lines,
        long nonEmptyLines,
        long words,
        long uniqueWords,
        String sha256
    ) {}

    static class TextFileException extends Exception {
        TextFileException(String message) {
            super(message);
        }

        TextFileException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    interface TextFilePolicy {
        void validate(Path path) throws TextFileException;
    }

    static final class SizePolicy implements TextFilePolicy {
        private final long maximumBytes;

        SizePolicy(long maximumBytes) {
            if (maximumBytes <= 0) {
                throw new IllegalArgumentException(
                    "maximumBytes must be positive."
                );
            }
            this.maximumBytes = maximumBytes;
        }

        @Override
        public void validate(Path path) throws TextFileException {
            if (!Files.exists(path)) {
                throw new TextFileException(
                    "File does not exist: " + path
                );
            }

            if (!Files.isRegularFile(path)) {
                throw new TextFileException(
                    "Path is not a regular file: " + path
                );
            }

            try {
                long size = Files.size(path);

                if (size > maximumBytes) {
                    throw new TextFileException(
                        "File exceeds configured size limit."
                    );
                }
            } catch (IOException error) {
                throw new TextFileException(
                    "Unable to inspect file size.",
                    error
                );
            }
        }
    }

    static final class TextFileService {
        private static final Pattern WORD_PATTERN =
            Pattern.compile("[\\p{L}\\p{N}_'-]+");

        private final TextFilePolicy policy;

        TextFileService(TextFilePolicy policy) {
            this.policy = policy;
        }

        private BufferedReader open(Path path)
            throws TextFileException {

            policy.validate(path);

            try {
                return Files.newBufferedReader(
                    path,
                    StandardCharsets.UTF_8
                );
            } catch (IOException error) {
                throw new TextFileException(
                    "Unable to open text file.",
                    error
                );
            }
        }

        String readAll(Path path) throws TextFileException {
            try (BufferedReader reader = open(path)) {
                return reader.lines()
                    .reduce(
                        new StringBuilder(),
                        (builder, line) ->
                            builder
                                .append(line)
                                .append(System.lineSeparator()),
                        StringBuilder::append
                    )
                    .toString();
            } catch (IOException error) {
                throw new TextFileException(
                    "Failure while reading text file.",
                    error
                );
            }
        }

        List<SearchResult> search(
            Path path,
            String term
        ) throws TextFileException {

            if (term == null || term.isBlank()) {
                throw new TextFileException(
                    "Search term cannot be blank."
                );
            }

            List<SearchResult> results = new ArrayList<>();
            String target = term.toLowerCase();

            try (BufferedReader reader = open(path)) {
                String line;
                int lineNumber = 0;

                while ((line = reader.readLine()) != null) {
                    lineNumber++;

                    if (line.toLowerCase().contains(target)) {
                        results.add(
                            new SearchResult(lineNumber, line)
                        );
                    }
                }

                return List.copyOf(results);
            } catch (IOException error) {
                throw new TextFileException(
                    "Failure while searching text file.",
                    error
                );
            }
        }

        TextStatistics statistics(Path path)
            throws TextFileException {

            Map<String, Long> frequencies = new HashMap<>();

            long characters = 0;
            long lines = 0;
            long nonEmptyLines = 0;
            long words = 0;

            MessageDigest digest;

            try {
                digest = MessageDigest.getInstance("SHA-256");
            } catch (NoSuchAlgorithmException error) {
                throw new TextFileException(
                    "SHA-256 is unavailable.",
                    error
                );
            }

            try (BufferedReader reader = open(path)) {
                String line;

                while ((line = reader.readLine()) != null) {
                    lines++;
                    characters += line.length();

                    if (!line.isBlank()) {
                        nonEmptyLines++;
                    }

                    digest.update(
                        (line + "\n")
                            .getBytes(StandardCharsets.UTF_8)
                    );

                    var matcher = WORD_PATTERN.matcher(
                        line.toLowerCase()
                    );

                    while (matcher.find()) {
                        String word = matcher.group();
                        words++;
                        frequencies.merge(word, 1L, Long::sum);
                    }
                }
            } catch (IOException error) {
                throw new TextFileException(
                    "Failure while analyzing text file.",
                    error
                );
            }

            return new TextStatistics(
                path,
                characters,
                lines,
                nonEmptyLines,
                words,
                frequencies.size(),
                hex(digest.digest())
            );
        }

        List<Map.Entry<String, Long>> topWords(
            Path path,
            int limit
        ) throws TextFileException {

            if (limit <= 0) {
                throw new TextFileException(
                    "Limit must be positive."
                );
            }

            Map<String, Long> frequency = new HashMap<>();

            try (BufferedReader reader = open(path)) {
                String line;

                while ((line = reader.readLine()) != null) {
                    var matcher = WORD_PATTERN.matcher(
                        line.toLowerCase()
                    );

                    while (matcher.find()) {
                        frequency.merge(
                            matcher.group(),
                            1L,
                            Long::sum
                        );
                    }
                }
            } catch (IOException error) {
                throw new TextFileException(
                    "Failure while counting words.",
                    error
                );
            }

            return frequency.entrySet()
                .stream()
                .sorted(
                    Comparator
                        .<Map.Entry<String, Long>>comparingLong(
                            Map.Entry::getValue
                        )
                        .reversed()
                        .thenComparing(Map.Entry::getKey)
                )
                .limit(limit)
                .toList();
        }

        private static String hex(byte[] bytes) {
            StringBuilder result = new StringBuilder();

            for (byte value : bytes) {
                result.append(
                    String.format("%02x", value & 0xff)
                );
            }

            return result.toString();
        }
    }

    private static Path createDemoFile()
        throws IOException {

        Path path = Files.createTempFile(
            "text-reader-",
            ".txt"
        );

        try (BufferedWriter writer =
                 Files.newBufferedWriter(
                     path,
                     StandardCharsets.UTF_8
                 )) {

            writer.write(
                "Reading text files requires explicit encoding.\n"
            );
            writer.write(
                "Streaming reads reduce memory usage.\n"
            );
            writer.write(
                "Validation prevents unsafe input.\n"
            );
            writer.write(
                "Streaming reads are useful for large files.\n"
            );
        }

        return path;
    }

    public static void main(String[] args) {
        Path demoFile = null;

        try {
            demoFile = createDemoFile();

            TextFileService service =
                new TextFileService(
                    new SizePolicy(5 * 1024 * 1024)
                );

            System.out.println("=== Complete Text ===");
            System.out.println(
                service.readAll(demoFile)
            );

            System.out.println("=== Search Results ===");

            for (SearchResult result :
                service.search(demoFile, "streaming")) {

                System.out.printf(
                    "%d: %s%n",
                    result.lineNumber(),
                    result.text()
                );
            }

            TextStatistics statistics =
                service.statistics(demoFile);

            System.out.println("\n=== Statistics ===");
            System.out.println(
                "Lines: " + statistics.lines()
            );
            System.out.println(
                "Non-empty lines: "
                    + statistics.nonEmptyLines()
            );
            System.out.println(
                "Characters: "
                    + statistics.characters()
            );
            System.out.println(
                "Words: " + statistics.words()
            );
            System.out.println(
                "Unique words: "
                    + statistics.uniqueWords()
            );
            System.out.println(
                "SHA-256: "
                    + statistics.sha256()
            );

            System.out.println("\n=== Top Words ===");

            for (var entry :
                service.topWords(demoFile, 5)) {

                System.out.printf(
                    "%s: %d%n",
                    entry.getKey(),
                    entry.getValue()
                );
            }

            if (statistics.lines() != 4) {
                throw new TextFileException(
                    "Unexpected line count."
                );
            }

            if (
                service.search(
                    demoFile,
                    "STREAMING"
                ).size() != 2
            ) {
                throw new TextFileException(
                    "Unexpected search result count."
                );
            }

            System.out.println(
                "\nValidation checks passed."
            );

        } catch (TextFileException | IOException error) {
            System.err.println(
                "[ERROR] " + error.getMessage()
            );
            System.exit(1);
        } finally {
            if (demoFile != null) {
                try {
                    Files.deleteIfExists(demoFile);
                } catch (IOException ignored) {
                    // Cleanup failure does not change processing result.
                }
            }
        }
    }
}
