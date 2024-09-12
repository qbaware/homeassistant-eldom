# Eldom Flat Boiler Integration For Home Assistant

Connect your [Eldom](https://eldominvest.com/en/index.html) devices to Home Assitant and operate them via Eldom's Cloud APIs with [pyeldom](https://github.com/qbaware/pyeldom).

![eldom-integration](https://github.com/user-attachments/assets/d058d86b-0796-4d2f-b686-e9d4312ecd76)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/danielgospodinow)

--- 

# Features

Allows you to control Eldom devices via Home Assistant.

Note that there's only one way to connect to the Eldom devices - via their Cloud APIs.

Supported devices:

- Flat boilers
    - Operational mode selection 
        - `Electric` (corresponds to "Heating")
        - `Eco` (corresponds to "Smart")
        - `High Demand` (corresponds to "Study")
        - `Off`
    - Enable Powerful mode switch (only works while `Eco` mode is enabled)

![Flat boiler main view](./docs/flat-boiler-main-view.png)

![Flat boiler detailed view](./docs/flat-boiler-detailed-view.png)

# Installation

## HACS Installation

Available soon.

## Custom components

1. Download or clone the integration to your local machine.
2. Navigate to the `custom_components` directory in your Home Assistant installation directory.
3. Copy the folder `custom_components/eldom` from the downloaded integration to the Home Assistant `custom_components` directory.
4. Restart Home Assistant.

# Usage

- After installation, go to `Settings > Devices & services > Add integration` and search for `Eldom`.
- Provide an Eldom account `email` and `password` and click `Submit`.
