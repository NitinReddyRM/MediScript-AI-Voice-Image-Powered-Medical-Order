from groq import Groq
import os
from dotenv import load_dotenv
import re
import json
load_dotenv()

class LLM_MODEL:
    def __init__(self):

        self.client = Groq(api_key=os.getenv("groq_api_key"))
        # Store the common system prompt
        self.model_name="openai/gpt-oss-20b"
        self.base_messages = [
            {
                "role": "system",
                "content": (
                    "You are a medical prescription parser. Extract details from the input text "
                    "and return ONLY a valid JSON object in the following format:\n\n"
                    "{\n"
                    '  "name": string or null,\n'
                    '  "age": number or null,\n'
                    '  "medicine": [\n'
                    "    {\n"
                    '      "name": string (medicine or drug name),\n'
                    '      "dosage": string (Strength + frequency, e.g., "500 mg, twice a day"),\n'
                    '      "quantity": Integer or number (number of doses or days)\n'
                    '      "timing":  When to take (e.g., "morning", "evening", "afternoon", "after food", "before sleep", "empty stomach")\n'
                    "    }\n"
                    "  ]\n"
                    "}\n\n"

                    "If name or age is missing, return null for those fields. "
                    "Do not include any explanation — return only the JSON."
                )
            }
        ]

        # This is just a placeholder for the model response
        self.completion = None

    def parse_input(self, input_text):
        # Append user message to system prompt
        messages = self.base_messages + [
            {
                "role": "user",
                "content": input_text
            }
        ]

        # Run completion
        self.completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7
        )

        # Return the content (JSON string)
        return self.extract_json(self.completion.choices[0].message.content)
    
    def extract_json(self,input_string):
        # Extract JSON-like object using regex
        match = re.search(r"\{.*\}", input_string, re.DOTALL)

        if match:
            json_str = match.group()
            return json_str
        return None


