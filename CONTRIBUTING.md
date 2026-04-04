# Contributing to StepShield

First off, thank you for considering contributing to StepShield! It's people like you that make StepShield such a great tool for evaluating AI agent security.

## Adding a New Detector

To add a new detector to the benchmark, follow these steps:

1. Create a new file in `benchmark/detectors/` (e.g., `my_detector.py`).
2. Inherit from the base `Detector` class defined in `benchmark/detectors/base.py`.
3. Implement the `evaluate_step()` method. Your detector should take a single trajectory step as input and return a boolean indicating whether the step is rogue, along with a confidence score.
4. Add your detector to the `benchmark/run_benchmark.py` script so it gets evaluated.

## Adding a New Model

To evaluate a new frontier model:

1. Open `ablations/frontier_scaling_eval.py`.
2. Add your model to the `MODELS` list at the top of the file.
3. Ensure you have the appropriate API keys set as environment variables.
4. Run the script: `python ablations/frontier_scaling_eval.py --models your-new-model`

## Submitting Changes

1. Fork the repository.
2. Create a new branch for your feature or bugfix: `git checkout -b feature/my-new-feature`
3. Commit your changes. Please ensure your commit messages are clear and descriptive.
4. Push to your fork and submit a Pull Request.

## Code Style

- We follow PEP 8. Please use `flake8` or `black` to format your code before submitting.
- Avoid hardcoding API keys or credentials. Use environment variables.
- Write docstrings for all new classes and methods.

## Reporting Bugs

If you find a bug, please open an issue on GitHub. Include as much detail as possible, including:
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)

Thank you for your contributions!
