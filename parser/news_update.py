import uuid
from io import BytesIO
import json
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError
from openai import OpenAI

from utils.scrape import stock_news_scrape, web_content_scraper
from utils.bucket import upload_file
from utils.openai import completions
from helper.database import bucket_name, idxchannel_path


def get_news_object_name(query: str, date: str) -> str:
    query = "_".join(query.split())
    return "/".join([idxchannel_path, query, f"{query}_{date}.json"])

def is_news_updated(boto_client: boto3.client, query: str, date: str = "") -> bool:
    try:
        if date == None or date == "": date = datetime.now(timezone.utc).date().strftime('%Y-%m-%d')
        boto_client.head_object(Bucket=bucket_name, Key=get_news_object_name(query, date))
        return True
    except ClientError:
        return False


def get_news(boto_client: boto3.client, query: str, date: str = "") -> dict:
    if date == None or date == "": date = datetime.now(timezone.utc).date().strftime('%Y-%m-%d')
    response = boto_client.get_object(Bucket=bucket_name, Key=get_news_object_name(query, date))
    
    # Get the content of the file as bytes
    file_content = response['Body'].read()

    json_data = json.loads(file_content)

    return json_data
    

def update_news(boto_client: boto3.client, openai_client: OpenAI, query: str) -> dict:
    today = datetime.now(timezone.utc).date().strftime('%Y-%m-%d')
    print(f"News for today: {today} for query '{query}' will be updated to database!")

    news = stock_news_scrape(query)[:3]
    for i in range(len(news)):
        ## Scrape news and paraphrase
        temp_content = web_content_scraper(news[i]["link"])
        temp_content = completions(openai_client, None, 
                                   f"Paraphrase this to an organic news in Indonesia, exclude information like source/website/author/etc for legal reason, here is the content:\n{temp_content}")
        news[i]["content"] = temp_content

        ## Paraphrase Title
        temp_title = completions(openai_client, None,
                                 f"Paraphrase this news title to new organic one in Indonesia, here is the title:\n{news[i]['original_title']}")
        news[i]["title"] = temp_title

        news[i]["id"] = str(uuid.uuid4())
        news[i]["timestamp"] = datetime.now().isoformat()

    json_buffer = BytesIO()
    json_data = json.dumps(news)
    json_buffer.write(json_data.encode('utf-8'))
    json_buffer.seek(0)

    upload_file(
        boto_client=boto_client,
        bucket_name=bucket_name,
        object_name=get_news_object_name(query, today),
        source=json_buffer
    )

    return news