---
paths:
  - "**/*.test.*"
  - "**/*_test.*"
---

# Testing conventions

When writing or reviewing test files in this repo:
- Use pytest-style assertions (assert x == y, not self.assertEqual)
- Each test function should test one behavior
- Name tests as test_<behavior>_<condition>_<expected>
