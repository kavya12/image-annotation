# image-annotation
A server based setup for VIA tool(http://www.robots.ox.ac.uk/~vgg/software/via/)

To run the app, set FLASK_APP environment variable as the path to app.py file.

To start annotation make the following changes:

1. Add the <username> in the list ANNOTATORS present in the app.py file. 
2. Create a folder static/annotations/<username> where the annotations will be stored.
3. Create a folder static/images/<username> and populate the folder with images assigned to the user.
4. Create a folder static/attributes/<username> and create a file within this directory titled 'list_of_attributes'. This file must contain the attributes assigned  to the user for annotation, each separated by a newline.

Command to run the app - 'flask run'
