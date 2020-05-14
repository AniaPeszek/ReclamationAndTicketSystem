# Reclamation and Ticket System wrote with Flask Framework

The project has been developed by:
- [Anna Peszek](https://github.com/AniaPeszek)
- [Bartosz Borowski](https://github.com/bartoszborowski)

as an implementation of skills learned during Python Bootcamp classes (2019-2020).

## The idea of Project
An application is a simple and easily customizable ERP reclamations handling system based on task ticketing among employees.

## Main Features
- create claims based on the information from customers,
- create tasks connected to the claim,
- notification once any task is being assigned to you,
- collection all relevant information in claim sheet, like notes, files, internal tasks,
- easily searchable reclamations and tasks by an overview sheet,
- export the report of reclamations or task by email in CSV format,
- search-box located on the navigation bar can look for a partial serial number of claimed parts. 

## First Steps
Go to the main folder of application in terminal to install virtual env  
`$ python -m venv venv`

Type the command below to activate virtual env  
`$ source venv/bin/activate`

Install all relevant packages by pip  
`$ pip install -r requirements.txt`

## Configuration
1. Edit class Config in config.py file. 
2. In class Config set variables (`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USE_SSL`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `ADMINS`) for mailing reports or export them as environment variables from a terminal.
3. Install the Redis server and run it in a new terminal window. 
4. In config.py file edit `REDIS_URL` (default port 6379)
5. In venv terminal window activate Redis worker by command: `rq worker erp-tasks`
6. Download Elastic Search
7. In the new terminal (the third one) run the elastic.
8. In the first run, the indexing of the partdetails table has to take place. In the venv terminal window activate flask shell by typing `flask shell`. Once shell opens, type `PartDetail.reindex()`.
9. To exit flask shell terminal type `exit()`

### The main functionality of an application works without configuration.
Exporting reports is an optional feature. You can skip points 2-5.

The search bar is an optional feature. You can skip points 6-9.

## Starting application
In the terminal in active venv: `$ flask run`

All mentioned above features will be working once Redis and Elastic Search was configured and launched beforehand.

## Screenshots
![image](screens/homepage.jpg?raw=true "Homepage")
![image](screens/reclamations.jpg?raw=true "Reclamations")
![image](screens/reclamation.jpg?raw=true "Reclamation")
![image](screens/tickets.jpg?raw=true "Tickets")
![image](screens/ticket.jpg?raw=true "Ticket")

## Database
You can use data that are in the database already or delete `app.db` and migration folder and create a new database. In the terminal in active venv:
1. `flask db init`
2. `flask db migrate -m "create tables"`
3. `flask db upgrade`
4. in flask shell: `upload()` - this function loads the database with sample data, it may take a while

## Link
[working version deployed on heroku](https://flask-erpsystem.herokuapp.com/)
