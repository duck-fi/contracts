# dispersion-contract

Vyper contract used in [Dispersion](https://www.dispersion.fi) farming contract.

## Testing and Development

### Dependencies

* [python3](https://www.python.org/downloads/release/python-368/) version 3.6 or greater, python3-dev
* [ganache-cli](https://github.com/trufflesuite/ganache-cli) - tested with version [6.11.0](https://github.com/trufflesuite/ganache-cli/releases/tag/v6.11.0)

Dispersion contracts are compiled using [Vyper](https://github.com/vyperlang/vyper), however installation of the required Vyper versions is handled by Brownie.

### Setup

To get started, first create and initialize a Python [virtual environment](https://docs.python.org/3/library/venv.html). Next, clone the repo and install the developer dependencies:

```bash
git clone https://github.com/dispersion-fi/contract.git
cd contract
pip3 install -r requirements.txt
```

### Running the Tests

The [test suite](tests) contains common tests. To run the entire suite:

```bash
brownie test
```

## License

Copyright (c) 2020, Dispersion.Fi - [All rights reserved](LICENSE).