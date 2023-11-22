import json
import openai

from homeassistant.core import HomeAssistant

from .available_functions import available_functions
from .const import DOMAIN
from .home_assistant_api import HomeAssistantApi

FUNCTIONS = available_functions


class FunctionCalling:
    def __init__(self, hass: HomeAssistant) -> None:
        print(hass.data[DOMAIN]["API_KEY"])
        openai.api_key = hass.data[DOMAIN]["API_KEY"]
        self.home_assistant = HomeAssistantApi(hass)
        self.hass = hass

    # send model the user query and what functions it has access to.

    def run_conversation(self, user_message: str, messages: list[dict]):
        # If GPT Wants to call a function, it gets called in this first request

        if len(messages) <= 0:
            messages.append(
                {
                    "role": "system",
                    "content": "You are called Jarvis. You are a very ironic and sarcastic but also helpful AI designed for assisting the user and controlling or reading data from devices in his home."
                    "Keep your answers as short as possible!"
                    "You can use a number of functions to satisfy the users intent."
                    "When you were able to use a function without error and you do not need to return a state or a value then answer with: 'Done'"
                }
            )

        messages.append({"role": "user", "content": user_message})

        print(messages)
        # First call to API with initial user request
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=FUNCTIONS,
            function_call="auto",
        )

        model_response = response["choices"][0]["message"]  # First response
        print(f"First Response: {model_response}")

        # append the model_response to messages so the assistant can keep context
        messages.append(model_response)

        # Now check if the model wants to call a function and call it if so
        if model_response.get("function_call"):  # If function called needed...
            function_name = model_response["function_call"]["name"]
            arguments = json.loads(model_response["function_call"]["arguments"])
            print(f'to be json loaded: {model_response["function_call"]["arguments"]}')

            # call the function
            # Note: the JSON response from the model may not be valid JSON
            function_response = getattr(self.home_assistant, function_name)(**arguments)

            # Step 4, send model the info on the function call and what the function returned
            # append the function response to messages so assistant has the context
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )

            second_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                functions=FUNCTIONS,
                function_call="auto",
            )

            model_response = second_response["choices"][0]["message"]
            print(f"Second Response: {model_response}")

            # append the model_response to messages so the assistant can keep context
            messages.append(model_response)
        else:
            return model_response, messages, "Function call was not requested"

        # Step 2.1, check if the model wants to call another function
        if model_response.get("function_call"):
            function_name = model_response["function_call"]["name"]
            arguments = json.loads(model_response["function_call"]["arguments"])

            # Step 3, call the function
            # Note: the JSON response from the model may not be valid JSON

            function_response = getattr(self.home_assistant, function_name)(**arguments)

            # Step 4, send model the info on the function call and function response
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )
            third_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                functions=FUNCTIONS,
                function_call="auto",
            )

            model_response = third_response["choices"][0]["message"]
            # append the model_response to messages so the assistant can keep context
            messages.append(model_response)
            return model_response, messages, "Third Response"

        else:
            return model_response, messages, "Function call was not requested"
