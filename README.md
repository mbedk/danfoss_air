# Danfoss Air — Home Assistant Integration

A Home Assistant integration for the Danfoss Air HRV (Heat Recovery Ventilation) system, communicating locally with the CCM unit over the network.

## Features

| Platform | Entity | Description |
|---|---|---|
| `sensor` | Exhaust Temperature | Temperature of exhaust air (°C) |
| `sensor` | Outdoor Temperature | Outdoor air temperature (°C) |
| `sensor` | Supply Temperature | Temperature of supply air (°C) |
| `sensor` | Extract Temperature | Temperature of extracted air (°C) |
| `sensor` | Humidity | Current humidity (%) |
| `sensor` | Remaining Filter | Filter life remaining (%) |
| `sensor` | Exhaust Fan Speed | Exhaust fan RPM *(diagnostic, disabled by default)* |
| `sensor` | Supply Fan Speed | Supply fan RPM *(diagnostic, disabled by default)* |
| `sensor` | Dial Battery | CCM dial battery level (%) *(diagnostic, disabled by default)* |
| `binary_sensor` | Bypass Active | Whether the bypass damper is open |
| `binary_sensor` | Away Mode Active | Whether away mode is enabled |
| `switch` | Boost | Toggle boost mode |
| `switch` | Bypass | Toggle bypass damper |
| `switch` | Automatic Bypass | Toggle automatic bypass |
| `number` | Fan Step | Control fan speed (steps 1–10) |

## Requirements

- [`pydanfossair`](https://github.com/JonasPed/pydanfoss-air) >= 0.3.0
- Home Assistant (UI configuration via config flow)

## Installation

### Via HACS (recommended)

1. In HACS, go to **Integrations** → **⋮** → **Custom repositories**.
2. Add `https://github.com/mbedk/danfoss_air` with category **Integration**.
3. Search for **Danfoss Air** and click **Download**.
4. Restart Home Assistant.
5. Go to **Settings** → **Devices & Services** → **Add Integration**, search for **Danfoss Air**, and enter the IP address of your CCM unit.

### Manual

1. Copy the `danfoss_air` folder into your Home Assistant `custom_components` directory:
   ```
   config/custom_components/danfoss_air/
   ```
2. Restart Home Assistant.
3. Go to **Settings** → **Devices & Services** → **Add Integration**, search for **Danfoss Air**, and enter the IP address of your CCM unit.

## Notes

- The integration polls the CCM unit every 60 seconds. If the CCM is unreachable at startup, Home Assistant will retry automatically.
- All entities become unavailable if the CCM stops responding, and recover automatically on the next successful poll.
- The **Fan Step** slider (1–10) updates immediately in the UI when moved. The device reports fan speed as a percentage (0–100) internally; the integration divides by 10 to map it to the 1–10 step scale.
- If the fan step is changed from the physical dial or another source, Home Assistant will self-correct on the next 60-second poll.
- To change the CCM IP address without removing the integration, go to **Settings** → **Devices & Services** → **Danfoss Air** → **⋮** → **Reconfigure**.
- Diagnostic entities (fan RPM, dial battery) are disabled by default. Enable them individually via **Settings** → **Devices & Services** → **Danfoss Air** → the device → the entity.
- This integration is based on the upstream [Home Assistant core integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/danfoss_air), extended with fan step control.
