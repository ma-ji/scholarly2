---
permalink: /contributing.html
---

# Developers' Notes

We welcome contributions from you!

If you find a feature in Google Scholar missing in `scholarly2`, or find a bug, please feel free to open an appropriate issue based on the two templates you will find.
Additionally, if you are interested in contributing to the codebase, submit a pull request _after_ you open an issue.

## What to contribute

1. If you are new to open-source projects, go through the Issues page and pick one that interests you. The ones with the label "good first issue" are usually simple enough and are new-contributor friendly.
2. If you use `scholarly2` in your projects and encounter a bug or need a feature, create an issue first before working on a solution. The issue page can be used for decision-making and design-choices and is meant to utilize your efforts better.

## How to contribute

1. Create a fork of `ma-ji/scholarly2` repository.
2. If you add a new feature, try to include tests in already existing test cases, or create a new test case if that is not possible.
3. Make sure the unit tests pass before raising a PR. For local proxy testing, use a `.env.socks5` file in your working directory — `scholarly2` loads it automatically at import time. See `.env.socks5.example` in the repository root for the expected format. Without a proxy, some test cases that hit Google Scholar directly may be skipped.
4. Check that the documentation is consistent with the code. Check that the documentation builds successfully.
5. Submit a PR with `main` as your base branch.
6. After an initial code review by the maintainers, the unit tests will be run. Passing all test cases is necessary before merging your PR.

## Build Docs

To build the documentation execute the make file as:

```bash
cd docs
make html
```
