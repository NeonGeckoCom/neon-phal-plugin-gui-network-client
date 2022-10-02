# PHAL plugin - GUI Network Client

this plugin provides the GUI interface for the wifi setup and is part of a larger collection of Wifi client plugins

# Install

`pip install ovos-PHAL-plugin-gui-network-client`

# Events

```python
     # WIFI Plugin Registeration and Activation Specific Events        
        self.bus.on("ovos.phal.wifi.plugin.stop.setup.event", self.handle_stop_setup)
        self.bus.on("ovos.phal.wifi.plugin.client.registered", self.handle_registered)
        self.bus.on("ovos.phal.wifi.plugin.client.deregistered", self.handle_deregistered)
        self.bus.on("ovos.phal.wifi.plugin.client.registration.failure", self.handle_registration_failure)
        self.bus.on("ovos.phal.wifi.plugin.alive", self.register_client)
        
        # OVOS PHAL NM EVENTS
        self.bus.on("ovos.phal.nm.connection.successful", self.display_success)
        self.bus.on("ovos.phal.nm.connection.failure", self.display_failure)

        # INTERNAL GUI EVENTS
        self.bus.on("ovos.phal.gui.network.client.back",
                    self.display_path_exit)
        self.bus.on("ovos.phal.gui.display.connected.network.settings",
                    self.display_connected_network_settings)
        self.bus.on("ovos.phal.gui.display.disconnected.network.settings",
                    self.display_disconnected_network_settings)
        self.bus.on("ovos.phal.gui.network.client.internal.back",
                    self.display_internal_back)
        
        # Also listen for certain events that can forcefully deactivate the client
        self.bus.on("system.display.homescreen", self.clean_shutdown)
        self.bus.on("mycroft.device.settings", self.clean_shutdown)
```
