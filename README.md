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
| `sensor` | Fan Step | Current fan step (read-only, %) |
| `sensor` | Exhaust Fan Speed | Exhaust fan RPM |
| `sensor` | Supply Fan Speed | Supply fan RPM |
| `sensor` | Dial Battery | CCM dial battery level (%) |
| `binary_sensor` | Bypass Active | Whether the bypass damper is open |
| `binary_sensor` | Away Mode Active | Whether away mode is enabled |
| `switch` | Boost | Toggle boost mode |
| `switch` | Bypass | Toggle bypass damper |
| `switch` | Automatic Bypass | Toggle automatic bypass |
| `number` | Fan Step | Control fan speed (steps 1–10) |

## Requirements

- [`pydanfossair`](https://github.com/JonasPed/pydanfoss-air) >= 0.3.0
- Home Assistant (YAML configuration, legacy setup)

## Installation

1. Copy the `danfoss_air` folder into your Home Assistant `custom_components` directory:
   ```
   config/custom_components/danfoss_air/
   ```

2. Add the following to your `configuration.yaml`:
   ```yaml
   danfoss_air:
     host: <IP address of your Danfoss Air CCM unit>
   ```

3. Restart Home Assistant.

## Notes

- The integration polls the CCM unit every 60 seconds.
- The `number.danfoss_air_fan_step` entity (slider 1–10) controls the fan speed and stays in sync with the device — if the step is changed from the physical dial or another source, Home Assistant will self-correct on the next poll.
- This integration is based on the upstream [Home Assistant core integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/danfoss_air), extended with fan step control.
