# Web Scraping Project Coding Rules and Standards

## Core Rules

### Exception Handling
1. Never use try and except
2. Never use try-except-else
3. Never use try-except-finally
4. Never use try-except-raise
5. Never use try-except-raise-from
6. Never use try-except-return
7. Never use try-except-try
8. Never use try-finally
9. Never use try-with

### Code Quality
10. Never define cognitive complexity > 15
11. Always respect the framework structure and best practices
12. Always have a streamlined approach with just the core generic methods to have a cleaner and more maintainable code base
13. Always take linting into account

### Testing
14. Do not use print statements in tests
15. Do not use comments in test steps
16. Always check the correct locator names before using them anywhere
17. Never use time.sleep in tests
18. Never use sleep in tests
19. Always define locators and test steps on a single line, I will separate them in multiple lines myself

### JavaScript
20. Do not unnecessarily use JS

## ✅ Additional Enhanced Rules

### 🔒 Exception & Error Handling
30. Use specific exception types (e.g. `NoSuchElementException`) only in framework-level code, never in test scripts.
31. Avoid broad exception handling like `except Exception:`.
32. Use custom exception classes where necessary for better clarity and control.
33. All exception handling must log actionable error messages using the logger, not `print`.

### 🧱 Structure & Design
34. Tests must be modular — follow one test, one purpose.
35. Page Object Model (POM) must be strictly followed; do not mix test logic with page locators or interactions.
36. All scraping logic must be abstracted in data extraction classes, separate from navigation logic.
37. Never use hardcoded values for URLs, credentials, or expected values.
38. All dynamic values must come from config files or environment variables.

### 🔍 Locator & Element Handling
39. Locators must be stored in centralized locator classes.
40. Use explicit waits (`WebDriverWait`) with expected conditions.
41. Never rely on `sleep()` or implicit waits.
42. All locators must be uniquely descriptive and stable (avoid brittle XPath).
43. Avoid using overly complex XPath expressions.

### 🔧 Tools, Logs & Linting
44. Logging must be implemented for all exceptions and key steps.
45. Integrate pylint/flake8/black for consistent formatting and linting.
46. Set up pre-commit hooks for linting and test formatting validation.
47. All scripts must be compatible with CI tools (e.g. GitHub Actions, GitLab CI).

### 🧪 Test Quality
48. All tests must include setup and teardown methods.
49. Every test must assert expected results clearly and explicitly.
50. All test data must be managed through fixtures or factories.
51. Each test must be idempotent (re-runnable without side effects).
52. Retry logic must be handled by the framework, not within the test.

### 🧼 Clean Code Conventions
53. Function/method names must be descriptive, no abbreviations or unclear naming.
54. Maintain consistent naming conventions across all modules (snake_case, PascalCase, etc.).
55. Cognitive complexity should ideally stay under 10 unless truly justified.
56. No inline `lambda` functions inside test scripts — use named functions.
57. Never commit commented-out code or TODOs unless tracked by an issue.
