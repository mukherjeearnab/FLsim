# FLsim: A Simulation Framework for Federated Learning

[![License](https://img.shields.io/badge/license-GPL-blue.svg)](LICENSE)

A Federated Learning simulation framework designed to facilitate research and experimentation with Federated Learning algorithms and techniques.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Federated Learning is a machine learning paradigm that allows training models across multiple decentralized devices or servers while keeping the training data local. This repository contains a Federated Learning simulation framework that provides tools and utilities for conducting experiments, evaluating algorithms, and benchmarking performance. The primary goals of FLsim are to:

1. Support diverse FL framework requirements and customization at various levels and stages of the FL workflow.
2. Enabling the learning over different data distribution across clients.
3. Achieving complete ML library agnosticism to meet the demands of the diverse community of users preferring one ML library over the others.
4. Support diverse network topologies ranging from client-server to decentralized topology.
5. Controlled reproducibility of experimental outcomes to easily gauge the effect on experimental outcomes through tweaking and tuning hyperparameters and architectures.
6. Scalable enough to support a large number of nodes since real-world FL use cases might scale from siloed data sites to thousands of edge clients.

## Features

- **Modular Architecture**: The framework is built with a modular design, allowing easy extension and customization of components.
- **Flexible Configuration**: Configure various parameters such as network topology, dataset distribution, and learning algorithms.
- **Visualization Tools**: Visualization tools for monitoring training progress, analyzing performance metrics, and visualizing results.

## Installation

Refer to the Quick Start Guide for more information at: [Quick Start](docs/quick-start/readme.md)

## Examples

Check out the Examples Guide for more information at: [Examples](docs/examples/readme.md)

## License

This project is licensed under the GNU GPLv3 License - see the [`LICENSE`](./LICENSE) file for details.
