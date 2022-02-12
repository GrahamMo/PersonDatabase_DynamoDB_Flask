import boto3
from flask import Flask, request, Response
import os
import json
#import simplejson as json
import uuid

os.environ["AWS_DEFAULT_REGION"] = "us-west-2" #give boto info to connect to aws
os.environ["AWS_ACCESS_KEY_ID"] = "AKIAQG365STO5WO4VC5V" #my aws account keys
os.environ["AWS_SECRET_ACCESS_KEY"] = "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"

app = Flask(__name__)

table = None
#table obj to communicate w the database


#-------------------------------
#END POINT

@app.route("/")
def default():
    return

@app.route("/people", methods = ["GET"])
def get_people():

    response = table.scan()  # scan allows to return all entries in the db
    data = response['Items']  # this returns the first megabite of data and stores it to a list called data
    while 'LastEvaluatedKey' in response:  # Pagination will only display the first Megabit of data then the next page of data will start and the Last evaluated key / returned data point
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])  # then it adds the additional data to the list
    print(data)

    #data is a list and flask needs to return str so convert, but decimals are not JSON serializable so to change non str to str

    #can just use simple json instead if you uncomment from top and remove this logic
    for i in data: #for each person in the data
        for key in i: #for each key in the dict
            if type(i[key]) != str: #if the value is a num
                i[key] = str(i[key]) # convert the num to a string


    status_code = Response(response=json.dumps(data), status=200) #convert to str
    print(status_code)
    return status_code  # return the master list and successful status code

@app.route("/people", methods=["DELETE"])
def delete():#delete route that removes a given ID
    id = request.args.get('person_id')

    result = table.delete_item(Key={"person_id": id})
    return ""

@app.route("/people", methods=["POST"])
def add_person():
    person_id = str(uuid.uuid4()) #generate random unique ID

    person = request.json  # request the json
    name = person["name"]  # from the json dictionaries pull out variables
    age = person["age"]

    table.put_item(Item={
        'person_id': person_id,
        'name': name,
        'age': age
    })
    print("added!")

    return ""

#--------------------------------------------------
#curl -X PATCH -H "Content-Type: application/json" --data '{"name":"George","age":19}' "http://127.0.0.1:5000/people?id=92fa9768-7cfe-427f-a849-31bda502c5d5"
@app.route("/people", methods=["PATCH"])
def update_user():#update route that removes a given ID
    print("check 1")
    person = request.json  # request the json
    print(person)
    name = person["name"]  # from the json dictionaries pull out variables
    age = person["age"]
    print("check 2")
    id = request.args.get('id')
    print("check 3")
    response = table.update_item(
        Key={
            "person_id": id
        },
        UpdateExpression="set name=:n",
        ExpressionAttributeValues={
            ':n': name,
        },
        ReturnValues="UPDATED_NEW"
    )

    get_people()
    return ""



def create_table(dynamodb):
    table = dynamodb.create_table(
        TableName='People',
        KeySchema=[
            {
                'AttributeName': 'person_id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'person_id',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table


if __name__ == "__main__":
    #set up before starting server because app.run will lock
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://169.62.247.38:8000") #remove endpoint to use aws
    try: #try to access the table
        table = dynamodb.Table('People') #get this existing table
        table.scan() #this one will actually crash it if it doesnt exist
        print("Got existing table")
    except: #set up if it doesnt exist
        table = create_table(dynamodb)
        print("Created new table")


    app.run("0.0.0.0", 5000) #run the app. first parameter indicates bind from anywhere (take all requests) and the 2nd is prot


