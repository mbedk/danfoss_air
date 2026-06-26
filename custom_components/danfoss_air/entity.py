"""Base entity for Danfoss Air."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DanfossAirCoordinator


class DanfossAirEntity(CoordinatorEntity[DanfossAirCoordinator]):
    """Base class for all Danfoss Air entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DanfossAirCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="Danfoss Air",
            manufacturer="Danfoss",
            model="Air CCM",
        )
