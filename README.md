# Prerequisites
For the JavaScript SDK to work your APIs need to support CORS. The Amazon API Gateway developer guide explains how to [setup CORS for an endpoint]().
The generated SDK depends on third-party libraries. Include all of the scripts in your webpage

    <script type="text/javascript" src="lib/axios/dist/axios.standalone.js"></script>
    <script type="text/javascript" src="lib/CryptoJS/rollups/hmac-sha256.js"></script>
    <script type="text/javascript" src="lib/CryptoJS/rollups/sha256.js"></script>
    <script type="text/javascript" src="lib/CryptoJS/components/hmac.js"></script>
    <script type="text/javascript" src="lib/CryptoJS/components/enc-base64.js"></script>
    <script type="text/javascript" src="lib/url-template/url-template.js"></script>
    <script type="text/javascript" src="lib/apiGatewayCore/sigV4Client.js"></script>
    <script type="text/javascript" src="lib/apiGatewayCore/apiGatewayClient.js"></script>
    <script type="text/javascript" src="lib/apiGatewayCore/simpleHttpClient.js"></script>
    <script type="text/javascript" src="lib/apiGatewayCore/utils.js"></script>
    <script type="text/javascript" src="apigClient.js"></script>

# Use the SDK in your project

To initialize the most basic form of the SDK:

```
var apigClient = apigClientFactory.newClient();
```

Calls to an API take the form outlined below. Each API call returns a promise, that invokes either a success and failure callback

```
var params = {
    //This is where any header, path, or querystring request params go. The key is the parameter named as defined in the API
    param0: '',
    param1: ''
};
var body = {
    //This is where you define the body of the request
};
var additionalParams = {
    //If there are any unmodeled query parameters or headers that need to be sent with the request you can add them here
    headers: {
        param0: '',
        param1: ''
    },
    queryParams: {
        param0: '',
        param1: ''
    }
};

apigClient.methodName(params, body, additionalParams)
    .then(function(result){
        //This is where you would put a success callback
    }).catch( function(result){
        //This is where you would put an error callback
    });
```

#Using AWS IAM for authorization
To initialize the SDK with AWS Credentials use the code below. Note, if you use credentials all requests to the API will be signed. This means you will have to set the appropiate CORS accept-* headers for each request.

```
var apigClient = apigClientFactory.newClient({
    accessKey: 'ACCESS_KEY',
    secretKey: 'SECRET_KEY',
    sessionToken: 'SESSION_TOKEN', //OPTIONAL: If you are using temporary credentials you must include the session token
    region: 'eu-west-1' // OPTIONAL: The region where the API is deployed, by default this parameter is set to us-east-1
});
```

#Using API Keys
To use an API Key with the client SDK you can pass the key as a parameter to the Factory object. Note, if you use an apiKey it will be attached as the header 'x-api-key' to all requests to the API will be signed. This means you will have to set the appropiate CORS accept-* headers for each request.

```
var apigClient = apigClientFactory.newClient({
    apiKey: 'API_KEY'
});
```

#Details:
1.	Launch an ElasticSearch instance 
a.	Using AWS ElasticSearch service , create a new domain called “photos”.
b.	Make note of the Security Group (SG1) you attach to the domain.
c.	Deploy the service inside a VPC .
i.	This prevents unauthorized internet access to your service.
2.	Upload & index photos
a.	Create a S3 bucket (B2) to store the photos.
b.	Create a Lambda function (LF1) called “index-photos”.
i.	Launch the Lambda function inside the same VPC as ElasticSearch. This ensures that the function can reach the ElasticSearch instance.
ii.	Make sure the Lambda has the same Security Group (SG1) as ElasticSearch.
c.	Set up a PUT event trigger  on the photos S3 bucket (B2), such that whenever a photo gets uploaded to the bucket, it triggers the Lambda function (LF1) to index it.
i.	To test this functionality, upload a file to the photos S3 bucket (B2) and check the logs of the indexing Lambda function (LF1) to see if it got invoked. If it did, your setup is complete.
●	If the Lambda (LF1) did not get invoked, check to see if you set up the correct permissions  for S3 to invoke your Lambda function.
d.	Implement the indexing Lambda function (LF1):
i.	Given a S3 PUT event (E1) detect labels in the image, using Rekognition  (“detectLabels” method).
ii.	Store a JSON object in an ElasticSearch index (“photos”) that references the S3 object from the PUT event (E1) and an array of string labels, one for each label detected by Rekognition.

Use the following schema for the JSON object:

{
	“objectKey”: “my-photo.jpg”,
	“bucket”: “my-photo-bucket”,
	“createdTimestamp”: “2018-11-05T12:40:02”,
	“labels”: [
		“person”,
		“dog”,
		“ball”,
		“park”
	]
}
3.	Search
a.	Create a Lambda function (LF2) called “search-photos”.
i.	Launch the Lambda function inside the same VPC as ElasticSearch. This ensures that the function can reach the ElasticSearch instance.
ii.	Make sure the Lambda has the same Security Group (SG1) as ElasticSearch.
b.	Create an Amazon Lex bot to handle search queries.
i.	Create one intent named “SearchIntent”.
ii.	Add training utterances to the intent, such that the bot can pick up both keyword searches (“trees”, “birds”), as well as sentence searches (“show me trees”, “show me photos with trees and birds in them”).
●	You should be able to handle at least one or two keywords per query.
c.	Implement the Search Lambda function (LF2):
i.	Given a search query “q”, disambiguate the query using the Amazon Lex bot.
ii.	If the Lex disambiguation request yields any keywords (K1, …, Kn), search the “photos” ElasticSearch index for results, and return them accordingly (as per the API spec).
●	You should look for ElasticSearch SDK libraries to perform the search.
iii.	Otherwise, return an empty array of results (as per the API spec).
4.	Build the API layer
a.	Build an API using API Gateway.
i.	The Swagger API documentation for the API can be found here:
https://github.com/001000001/ai-photo-search-columbia-f2018/blob/master/swagger.yaml 
b.	The API should have two methods:
i.	PUT /photos

Set up the method as an Amazon S3 Proxy . This will allow API Gateway to forward your PUT request directly to S3.

ii.	GET /search?q={query text}

Connect this method to the search Lambda function (LF2).
c.	Setup an API key for your two API methods.
d.	Deploy the API.
e.	Generate a SDK for the API (SDK1).
5.	Frontend
a.	Build a simple frontend application that allows users to:
i.	Make search requests to the GET /search endpoint
ii.	Display the results (photos) resulting from the query
iii.	Upload new photos using the PUT /photos
b.	Create a S3 bucket for your frontend (B2).
c.	Set up the bucket for static website hosting (same as HW1).
d.	Upload the frontend files to the bucket (B2).
e.	Integrate the API Gateway-generated SDK (SDK1) into the frontend, to connect your API.

At this point you should be able to:
1.	Visit your photo album application using the S3 hosted URL.
2.	Search photos using natural language and see relevant results based on what you see in the photos.
3.	Upload new photos and see them appear in search results.


