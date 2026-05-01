## Description
<!-- Please include a summary of the change and which issue is fixed. Include relevant motivation and context. -->

Fixes # (issue number if applicable)

## Type of change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature / benchmark (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Pre-PR Checklist
<!-- Please verify the following before submitting your PR -->
- [ ] I have read the [CONTRIBUTING.md](../CONTRIBUTING.md) document.
- [ ] My code is formatted with `black` and passes `flake8` without critical warnings.
- [ ] I have verified that the benchmarks run to 100% without crashing (`uv run python main.py -v`).
- [ ] The JSON exporter (`results/run_*.json`) outputs correctly with no unexplained `NaN`, `null`, or `0.0` metrics.
- [ ] If I added a new benchmark, it strictly follows the **time-bounded loop** (`time.perf_counter()`) pattern.
- [ ] I have not blindly altered existing scoring weights in `scorer.py` without justification.

## Additional Context
<!-- Add any other context about the PR here, such as benchmark score impacts, new dependencies added, etc. -->
