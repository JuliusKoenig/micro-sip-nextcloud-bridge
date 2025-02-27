# micro-sip-nextcloud-bridge
A Bridge between MicroSip and Nextcloud.

![PyPI - Version](https://img.shields.io/pypi/v/micro-sip-nextcloud-bridge)
![GitHub License](https://img.shields.io/github/license/JuliusKoenig/micro-sip-nextcloud-bridge)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/JuliusKoenig/micro-sip-nextcloud-bridge/build_and_publish.yml)

## Table of Contents
1. [:pushpin: Overview](#overview) 
2. [:star: Features ](#features) 
3. [:rocket: Quick Start](#quick-start) 
5. [:gear: System Requirements ](#system-requirements)
6. [:pick: Contributing](#contributing)
7. [:page_facing_up: License](#license)

### :pushpin: Overview
The **micro-sip-nextcloud-bridge** is a tool designed to seamlessly integrate **MicroSIP** with **Nextcloud**. The bridge allows you to synchronize contacts.

### :star: Features
- Sync contacts to **MicroSIP** from **Nextcloud**.
- Easy-to-use configuration for instant setup.

### :rocket: Quick Start
First you have to set the environment variables see [config.env](config.env)
Then choose the option that suits you best.
* Use pip:
``` bash
  pip install micro-sip-nextcloud-bridge
  # then call
  micro-sip-nextcloud-bridge # or python -m micro_sip_nextcloud_bridge
```
* Use Docker:
``` bash
  docker run -p 8123:8123 --env-file=config.env micro-sip-nextcloud-bridge
```
* Use source code with pip:
``` bash
  git clone https://github.com/JuliusKoenig/micro-sip-nextcloud-bridge.git
  pip install -e .
  # then call
  micro-sip-nextcloud-bridge # or python -m micro_sip_nextcloud_bridge
```
* Use source code with Docker:
``` bash
  git clone https://github.com/JuliusKoenig/micro-sip-nextcloud-bridge.git
  docker build . -t micro-sip-nextcloud-bridge
  docker run -p 8123:8123 --env-file=config.env micro-sip-nextcloud-bridge
```
Once the micro-sip-nextcloud-bridge has been successfully started, only the user directory needs to be stored.
![Step 1](docs/step1.png)
![Step 2](docs/step2.png)

### :gear: System Requirements
- **Python**: Version 3.12 or later
- **Dependencies**: See the [pyproject.toml](pyproject.toml) file
- **Operating System**: Cross-platform (Windows, macOS, Linux)

### :pick: Contributing
We welcome contributions! To contribute:
1. Fork this repository.
2. Create a new branch for your feature or bug fix:
``` bash
   git checkout -b feature/my-feature
```
1. Commit your changes and push them to your fork:
``` bash
   git commit -m "Add new feature"
   git push origin feature/my-feature
```
1. Open a pull request and provide a description of your changes.

### :page_facing_up: License
This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for details.
