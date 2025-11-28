from enum import Enum
from typing import Optional


class MobileSimulateMode(str, Enum):
    PROPERTIES_ONLY = "PropertiesOnly"
    SENSORS_ONLY = "SensorsOnly"
    PACKAGES_ONLY = "PackagesOnly"
    SERVICES_ONLY = "ServicesOnly"
    ALL = "All"


class MobileSimulateConfig:
    """
    Configuration for mobile simulation.
    """

    def __init__(
        self,
        simulate: bool,
        simulate_path: Optional[str],
        simulate_mode: MobileSimulateMode,
        simulated_context_id: Optional[str],
    ):
        self.simulate = simulate
        self.simulate_path = simulate_path
        self.simulate_mode = simulate_mode
        self.simulated_context_id = simulated_context_id

