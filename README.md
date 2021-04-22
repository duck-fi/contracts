# duck-fi/contracts

Vyper contracts used in [Duck Finance](https://www.duck.finance) farming contracts.

## Overview

Duck finance is a metapharming project on the Ethereum network. It allows members to earn money from providing liquidity and reduce transaction fees. 
View the [litepaper](docs/litepaper.pdf) to get more info about the project.
For in-depth technical explanation please view the [smart contracts documentation](https://duck-fi.github.io/contracts/).

## Testing and Development

### Dependencies

* [python3](https://www.python.org/downloads/release/python-368/) version 3.6 or greater, python3-dev
* [ganache-cli](https://github.com/trufflesuite/ganache-cli) - tested with version [6.11.0](https://github.com/trufflesuite/ganache-cli/releases/tag/v6.11.0)
* [vyper](https://github.com/vyperlang/vyper) version [0.2.11](https://github.com/vyperlang/vyper/releases/tag/v0.2.11)
* [brownie](https://github.com/iamdefinitelyahuman/brownie) - tested with version [1.13.0](https://github.com/eth-brownie/brownie/releases/tag/v1.13.0)

Duck finance contracts are compiled using [Vyper](https://github.com/vyperlang/vyper), however installation of the required Vyper versions is handled by Brownie.

### Setup

To get started, first create and initialize a Python [virtual environment](https://docs.python.org/3/library/venv.html). Next, clone the repo and install the developer dependencies:

```bash
git clone https://github.com/duck-fi/contracts.git
python3 -m venv .venv
pip3 install -r requirements.txt
```

### Compiling the contracts

To compile all project contracts:

```bash
brownie compile
```

The compiled contracts and ABIs will be located in build directory.

### Running the Tests

The [test suite](tests) contains common tests. To run the entire suite:

```bash
brownie test
```

To launch only unit or integration tests:

```bash
brownie test tests/unitary
brownie test tests/integration
```

### Communication

If you have any questions about the project, feel free to contats with us:

* [Telegram](https://t.me/duck_finance)

## License

Copyright (c) 2020, Duck.Finance - [All rights reserved](LICENSE).