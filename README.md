# performance-decorator

Measure function execution time with a simple decorator.

[![Tests](https://github.com/leonardobartolelli/performance-decorator/actions/workflows/tests.yml/badge.svg)](https://github.com/leonardobartolelli/performance-decorator/actions/workflows/tests.yml)

## Installation

```bash
pip install performance-decorator
```

## Usage

```python
from performance import performance


@performance
def calculate():
    return sum(range(100_000))


result = calculate()
print(result)
print(calculate.last_duration)  # elapsed time in seconds
print(calculate.execution_times)  # duration of every completed call
```

Each call prints a line such as:

```text
calculate took 0.002341 seconds
```

The wrapped function's return value and metadata are preserved. Timing is
recorded even when the wrapped function raises an exception.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for
development setup and pull request guidelines. All participants are expected
to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
