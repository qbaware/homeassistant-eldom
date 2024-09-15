# Eldom Integration For Home Assistant

Connect your [Eldom](https://eldominvest.com/en/index.html) devices to Home Assitant and operate them via Eldom's Cloud APIs with [pyeldom](https://github.com/qbaware/pyeldom).

![eldom-integration](https://github.com/user-attachments/assets/d058d86b-0796-4d2f-b686-e9d4312ecd76)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/danielgospodinow)

---

## Features

This integration allows you to control Eldom devices via Home Assistant.

Note that there's only one way to control your Eldom devices - via their Cloud APIs. There's no support for local network control.

Supported devices:

- Flat boilers
  - Operational mode selection
    - `Electric` (corresponds to "Heating")
    - `Eco` (corresponds to "Smart")
    - `High Demand` (corresponds to "Study")
    - `Off`
  - Enable `Powerful mode` switch (only works while `Eco` mode is enabled)

![Flat boiler detailed view](./docs/flat-boiler-detailed-view.png)

![Flat boiler main view](./docs/flat-boiler-main-view.png)

## Usage

- After installation, go to `Settings > Devices & services > Add integration` and search for `Eldom`.
- Provide an Eldom account `email` and `password` and click `Submit`.
