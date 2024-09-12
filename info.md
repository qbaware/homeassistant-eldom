# Eldom integration for Home Assistant

## Features

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

## Usage And Configuration

- After installation, go to `Settings > Devices & services > Add integration` and search for `Eldom`.
- Provide an Eldom account `email` and `password` and click `Submit`.

## Support

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/danielgospodinow)
