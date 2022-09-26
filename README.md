# PersonDatabase_DynamoDB_Flask
This was my first project using DynamoDB. It uses a Flask Rest API to manages entries of people within the database. 

This project was a good introduction to DynamoDB and noSQL databases, but is very simplistic. For example the people are stored with only the partician key and without sort key, which is poor design which you most likely would not see in a production. It also uses some bad practices such as a paginated table.scan() get endpoint, which I know now is a very expensive call that you would not use on a production level. Nonetheless, its a good project for a quick refresher on DynamoDB syntax and for creating a table with a function instead of dealing with AWS's ui.
