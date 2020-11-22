# Xiaomi Scale Sync

This utility will syncronize your Xiaomi smart scale with your FatSecret account.

## Compatibility

This is compatible with Xiaomi Smart Body Scale version 1 and 2. Only FatSecret calorie tracker is supported.

## Configuration

To configure this, you need to obtain a few tokens and create a configuration file. Take a look at `config.example.toml` for inspiration.

### Obtain API access

Go to https://platform.fatsecret.com/api/ and register your application. You will receive two tokens - those are your `app_key` and `app_secret`. Add them to your configuration file.

### Obtain user tokens

Now, run authorize script:

  pipenv run python scalesync/authorize.py

Click on the link and log in. You will receive a pin. Copy and paste it into console, and press enter.

You should rececive two strings - token and secret. Those are the `token` and `secret` for this user cocnfiguration.

### Scale MAC

To filter out BLE messages, you should specife your Smart Scale's MAC address. Specify it in `scale_mac` in configuration file.

## Running

Running script is simple:

  sudo pipenv run python scalesync

Superuser permissions are required to talk to Bluetooth stack. Alternatively, you can set capabilities manually.

Take a lok at `deploy` folder for more information on deployment.