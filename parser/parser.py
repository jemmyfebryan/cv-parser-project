import asyncio
import json
import time
import os

from openai import AsyncOpenAI
from parser.document import read_docx, read_pdf
from parser.prompter import make_prompt

def read_file_content(file):
    try:
        file_name = file.filename
        file_extension = file_name.split('.')[-1].lower()

        if file_extension == 'pdf':
            return read_pdf(file)
        elif file_extension in ['doc', 'docx']:
            return read_docx(file)
        else:
            raise Exception("Extension denied!")
    except Exception as e:
        raise Exception(str(e))

async def parse_file(file, client, time_now):
    print(f"Parse [1/7]: Parsing File...")
    try:
        print(f"Parse [2/7]: Make Context...")
        context = f"CV\n{read_file_content(file)}\n\n"

        print(f"Parse [3/7]: Make Prompt...")
        prompt = make_prompt(repr(context))

        print(f"Parse [4/7]: Hit OpenAI API...")
        # hit openai api
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are CV Parsing master"
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "cv_parse",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "phone": {"type": "string"},
                            "experience": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "job_title": {"type": "string"},
                                        "company": {"type": "string"},
                                        "job_type": {"type": "string", "enum": ['Full-time', 'Part-time', 'Internship', 'Freelance', 'Contract', 'Remote', 'Other']},
                                        "month_from": {"type": "integer"},
                                        "year_from": {"type": "integer"},
                                        "month_to": {"type": "integer"},
                                        "year_to": {"type": "integer"},
                                        "is_present": {"type": "boolean"},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["job_title", "company", "job_type", "month_from", "year_from", "month_to", "year_to", "is_present", "description"],
                                    "additionalProperties": False
                                }
                            },
                            "education": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "school": {"type": "string"},
                                        "degree": {"type": "string", "enum": ['Elementary School', 'Junior High School', 'Senior High School', 'Diploma 1', 'Diploma 2', 'Diploma 3', 'Diploma 4', 'Bachelor', 'Master', 'Doctoral']},
                                        "field_of_study": {"type": "string"},
                                        "grade": {"type": "number"},
                                        "month_from": {"type": "integer"},
                                        "year_from": {"type": "integer"},
                                        "month_to": {"type": "integer"},
                                        "year_to": {"type": "integer"},
                                        "is_present": {"type": "boolean"},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["school", "degree", "field_of_study", "grade", "month_from", "year_from", "month_to", "year_to", "is_present", "description"],
                                    "additionalProperties": False
                                }
                            },
                            "skill": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "hard skills and soft skills"
                                },
                            },
                            "language": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "communication language"
                                }
                            },
                        },
                        "required": ["name", "email", "phone", "experience", "education", "skill", "language"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )

        print(f"Parse [5/7]: Obtain Response...")

        # Obtain ChatGPT response
        # chatgpt_response = completion.choices[0].message.function_call.arguments
        chatgpt_response = completion.choices[0].message.content

        # print(chatgpt_response)

        print(f"Parse [6/7]: Converting to JSON...")

        # Convert response to JSON
        response_json = json.loads(chatgpt_response)
        print(f"Parse [7/7]: Finish parsing a file with time: ", time.time() - time_now)

        return {
            "cv": response_json,
            "status": {
                "code": 200,
                "message": "CV parsed successfully."
            }
        }
    except Exception as e:
        print(f"Error parsing file: {str(e)}")
        return {
            "cv": None,
            "status": {
                "code": 500,
                "message": str(e)
            }
        }

async def process_files(files, time_now):
    async with AsyncOpenAI(api_key=os.getenv('OPENAI_KEY')) as client:
        tasks = [parse_file(files[i], client, time_now) for i in range(len(files))]
        print("Making tasks")
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses