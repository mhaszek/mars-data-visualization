from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)


# Route to render index.html template using data from Mongo
@app.route("/")
def home():
    
    # Return template and data
    return render_template("index.html")


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():
    
    # Run the scrape function
    mars_data = scrape_mars.scrape()

if __name__ == "__main__":
    app.run(debug=True)
