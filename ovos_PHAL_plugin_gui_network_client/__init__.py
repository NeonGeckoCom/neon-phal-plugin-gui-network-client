import random
from os.path import dirname, join
from time import sleep

from mycroft_bus_client.message import Message, dig_for_message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.gui import GUIInterface
from ovos_utils.log import LOG
from ovos_utils.network_utils import is_connected


class GuiNetworkClientPlugin(PHALPlugin):

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-gui-network-client", config=config)
        self.gui = GUIInterface(bus=self.bus, skill_id=self.name)
        self.connected_network = None
        self.client_active = False

        # OVOS PHAL NM EVENTS
        self.bus.on("ovos.phal.nm.activate.gui.client", self.handle_activate)
        self.bus.on("ovos.phal.nm.is.connected", self.handle_is_connected)

        self.bus.on("ovos.phal.nm.connection.successful", self.display_success)
        self.bus.on("ovos.phal.nm.connection.failure", self.display_failure)

        # OVOS PHAL NM MODE SELECT IF GUI IS PRESENT AND INPUT IS AVAILABLE
        self.bus.on("ovos.phal.nm.client.mode.selector",
                    self.display_mode_select)

        # INTERNAL GUI EVENTS
        self.bus.on("ovos.phal.gui.network.client.back",
                    self.display_path_exit)

    def handle_activate(self, message=None):
        self.client_active = True
        self.bus.emit(Message("ovos.phal.nm.set.active.client", {
                      "client": "ovos-PHAL-plugin-gui-network-client"}))
        self.display_network_setup()
        LOG.info("Gui Network Client Plugin Activated")

    # Allow displaying different networking modes to the user to select in GUI
    def display_mode_select(self, message=None):
        self.manage_setup_display(
            "gui-wifi-mode-selector", "network-mode-selector")

    # Actual GUI Networking Operations
    def display_network_setup(self, message=None):
        self.manage_setup_display("network-select", "network-select")

    def display_path_exit(self, message=None):
        self.client_active = False
        self.bus.emit(Message("ovos.phal.nm.remove.active.client"))

        if not is_connected():
            self.bus.emit(Message("ovos.phal.nm.display.mode.select"))
        else:
            self.gui.release()

    def display_success(self, message=None):
        self.manage_setup_display("setup-completed", "status")
        sleep(5)
        self.client_active = False
        self.bus.emit(Message("ovos.phal.nm.remove.active.client"))
        self.gui.release()

    def display_failure(self, message=None):
        """Wifi setup failed"""       
        errorCode = message.data.get("errorCode", "")
        if errorCode == "0":
            self.display_failed_password()
        else:
            self.manage_setup_display("setup-failed", "status")
            self.speak_dialog("debug_wifi_error")
            sleep(5)
            self.display_network_setup()   
    
    def display_failed_password(self):
        self.manage_setup_display("incorrect-password", "status")
        self.speak_dialog("debug_wifi_error")
        sleep(5)
        self.display_network_setup()

    def manage_setup_display(self, state, page_type):
        self.gui.clear()
        page = join(dirname(__file__), "ui", "GuiClientLoader.qml")
        if state == "select-network" and page_type == "select-network":
            self.gui["page_type"] = "NetworkingLoader"
            self.gui["image"] = ""
            self.gui["label"] = ""
            self.gui["color"] = ""
            self.gui.show_page(page, override_idle=True,
                               override_animations=True)
        elif state == "setup-completed" and page_type == "status":
            self.gui["page_type"] = "Status"
            self.gui["image"] = "icons/check-circle.svg"
            self.gui["label"] = "Connected"
            self.gui["color"] = "#40DBB0"
            self.gui.show_page(page, override_animations=True)
        elif state == "setup-failed" and page_type == "status":
            self.gui["page_type"] = "Status"
            self.gui["image"] = "icons/times-circle.svg"
            self.gui["label"] = "Connection Failed"
            self.gui["color"] = "#FF0000"
            self.gui.show_page(page, override_animations=True)
        elif state == "incorrect-password" and page_type == "status":
            self.gui["page_type"] = "Status"
            self.gui["image"] = "icons/times-circle.svg"
            self.gui["label"] = "Incorrect Password"
            self.gui["color"] = "#FF0000"
            self.gui.show_page(page, override_animations=True)
        elif state == "gui-wifi-mode-selector" and page_type == "network-mode-selector":
            self.gui["page_type"] = "ModeChoose"
            self.gui.show_page(page, override_idle=True,
                               override_animations=True)

    def shutdown(self):
        super().shutdown()

    # speech
    @property
    def lang(self):
        return self.config.get("lang") or \
            self.config_core.get("lang") or \
            "en-us"

    def speak_dialog(self, key):
        """ Speak a random sentence from a dialog file.
        Args:
            key (str): dialog file key (e.g. "hello" to speak from the file
                                        "locale/en-us/hello.dialog")
        """
        dialog_file = join(dirname(__file__), "locale",
                           self.lang, key + ".dialog")
        with open(dialog_file) as f:
            utterances = [u for u in f.read().split("\n")
                          if u.strip() and not u.startswith("#")]
        utterance = random.choice(utterances)
        meta = {'dialog': key,
                'skill': self.name}
        data = {'utterance': utterance,
                'expect_response': False,
                'meta': meta,
                'lang': self.lang}
        message = dig_for_message()
        m = message.forward(
            "speak", data) if message else Message("speak", data)
        m.context["skill_id"] = self.name
        self.bus.emit(m)