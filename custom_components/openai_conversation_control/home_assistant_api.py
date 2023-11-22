import json

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.json import JSONEncoder


class HomeAssistantApi:
    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize HomeAssistant instance with the given URL.

        :param instance_url: The URL of the Home Assistant instance, e.g., http://YOUR_HA_URL:8123/

        Ensure you have a long-lived access token created from http://YOUR_HA_URL:8123/profile
        store the token in environment variable named HOME_ASSISTANT_TOKEN
        """

        self.all_entities: list[State] = []
        self.hass = hass

    def get_entities(self, entity_type: str):
        """Pass in a string of the entity type, e.g "light", "sensor", "automation".
        will return a list of all available entities of the specified type
        :param entity_type:
        :return: list of entities of 'type'
        """

        print("we get queried by AI")
        print(entity_type)

        if len(self.all_entities) <= 0:
            self.all_entities = self.hass.states.async_all()

        entity_type_dict = {
            "light": "light.",
            "sensor": "sensor.",
            "binary_sensor": "binary_sensor.",
            "switch": "switch.",
            "automation": "automation.",
            "media": "media_player.",
            "vacuum": "vacuum.",
            "button": "button.",
            "camera": "camera.",
            "climate": "climate.",
            "input_boolean": "input_boolean.",
            "person": "person.",
            "scene": "scene.",
            "timer": "timer.",
            "cover": "cover.",
            "shutter": "cover."
            "lock": "lock."
        }
        if entity_type == "all":
            return json.dumps({"action_not_clear": "Please be more specific."})

        if entity_type not in entity_type_dict:
            entity_type_dict[entity_type] = f"{entity_type}."

        try:
            entity_list: list[State] = [
                entity
                for entity in self.all_entities
                if entity.entity_id.startswith(entity_type)
                and entity.state != "unavailable"
            ]

        except KeyError:
            return f"Error, No entities of type {entity_type} found"

        entity_ids = [state.entity_id for state in entity_list]

        return json.dumps(entity_ids)

    def get_entity_state(self, entity_id: str):
        """Pass in entity id to read state and value of device
        :param entity_id:
        :return: state of entity
        """
        state = self.hass.states.get(entity_id)
        if state is not None:
            return json.dumps({"state": state.state})

        return json.dumps(
            {"action_not_performed": "Cant' find a device which fits the description"}
        )

    # call function with entity_id to toggle
    def toggle_device(self, entity_id: str):
        """Pass in entity id to toggle device
        :param entity_id:
        :return:
        """

        toggleType = "light"

        if entity_id.startswith("switch."):
            toggleType = "switch"

        service_data = {"entity_id": entity_id}
        self.hass.services.call(toggleType, "toggle", service_data)

    def broadcast_message(self, media_player_id: str, message: str):
        """Pass in media entity and string to announce a message
        :param media_player_id:
        :param message:

        :return: returns message to GPT to indicate the function was run
        """
        service_data = {"entity_id": media_player_id, "message": message}
        self.hass.services.call("tts", "google_translate_say", service_data)

        action_performed = {
            "action_performed": "The message was broadcast successfully, no further action required.",
        }
        return json.dumps(action_performed)

    # method for light dimming
    def light_adjust(self, lights, brightness=None, color=()):
        light_list = lights.split(",")

        for light in light_list:
            service_data = {"entity_id": light, "brightness_pct": brightness}
            self.hass.services.call("light", "turn_on", service_data)

        action_performed = {
            "action_performed": f"The specified lights have been adjusted to {brightness}%",
        }
        return json.dumps(action_performed)

    def turn_on_lights(self, lights):
        """:param lights:
        :return: returns message to GPT to indicate the function was run
        """
        light_list = lights.split(",")

        print(light_list)
        for light in light_list:
            service_data = {"entity_id": light}
            self.hass.services.call("light", "turn_on", service_data)

        action_performed = {
            "action_performed": "The specified lights have been turned on",
        }
        return json.dumps(action_performed)

    def turn_off_lights(self, lights):
        """:param lights:
        :return: returns message to GPT to indicate the function was run
        """
        light_list = lights.split(",")

        for light in light_list:
            service_data = {"entity_id": light}
            self.hass.services.call("light", "turn_off", service_data)
        action_performed = {
            "action_performed": "The specified lights have been turned off",
        }
        return json.dumps(action_performed)

    def close_shutters(self, shutters):
        """:param :
        :return: returns message to GPT to indicate the function was run
        """
        shutter_list = shutters.split(",")

        print(shutter_list)
        for shutter in shutter_list:
            service_data = {"entity_id": shutter}
            self.hass.services.call("cover", "close", service_data)

        action_performed = {
            "action_performed": "The specified shutters have been closed",
        }
        return json.dumps(action_performed)

    def open_shutters(self, shutters):
        """:param shutters:
        :return: returns message to GPT to indicate the function was run
        """
        shutter_list = shutters.split(",")

        for shutter in shutter_list:
            service_data = {"entity_id": shutter}
            self.hass.services.call("cover", "open", service_data)
        action_performed = {
            "action_performed": "The specified shutters have been opened",
        }
        return json.dumps(action_performed)
