#index photo
import json
import boto3
import logging
from botocore.vendored import requests
import http.client

def lambda_handler(event,context):

    rekognition = boto3.client('rekognition')
    
    b=event["Records"][0]["s3"]["bucket"]["name"]
    t=event["Records"][0]["eventTime"]
    result = rekognition.detect_labels(Image={'S3Object':{'Bucket':'b2photo','Name':event["Records"][0]["s3"]["object"]["key"]}}, MaxLabels=4, MinConfidence=70)
    l = []
    for label in result['Labels']:   
        l.append(label['Name'])
    
    item = {"objectKey": fileName, "bucket": b,"createdTimestamp": t, "labels": l}
    
    # Store to ElasticSearch
    s3 = "https://vpc-photo-nk52ep2p44xxur6sp7vi2lwxpu.us-east-1.es.amazonaws.com/photo/pho"
    result = requests.post(s3, json=item)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result.text)
    }
    
#search photo
def lambda_handler(event, context):
    
    lex = boto3.client('lex-runtime')
    lex_result = lex.post_text(
        botName='photos',
        botAlias='prod',
        userId="1",  
        inputText=event['q']
    )
    a = []
    a.append(lex_result['slots']['keyone'])
    if lex_result['slots']['keytwo']:
        a.append(lex_result['slots']['keytwo'])
   
    results = []
    b = boto3.resource('s3', region_name='us-east-1').Bucket('b2photo') 
    for keyword in a:
        s3 = "https://vpc-photo-nk52ep2p44xxur6sp7vi2lwxpu.us-east-1.es.amazonaws.com"
        url2 = s3 + "/photo/_search?q=" + keyword
        result = requests.get(url2)
        result = result.json()
        for hit in result["hits"]["hits"]:
            _source = hit["_source"]
            bucket = _source["bucket"]
            result = {"url": "https://s3.amazonaws.com/b2photo/" + _source["objectKey"], "labels": _source["labels"]}
            results.append(result)
    return {
        'statusCode': 200,
        'body': {"results": results}
    }



