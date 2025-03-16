import base64
import os

def make_prompt(context):
    # prompt = str(context) + "\n" + str(base64.b64decode(os.getenv('OPENAI_PROMPT')))
    prompt = str(context)
    return prompt