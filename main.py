import boto3
from flask import Flask, request, Response
import os
import json
#import simplejson as json
import uuid

import AccessKeys

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

'''
GET /people 
=> returns json of all people
'''

'''
DELETE /people?id=<some id here>
=> delete person with id
'''


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


