import flask
from flask import request
from predictor_api import make_prediction_ldamallet, make_prediction_bert, make_suggestion

# Initialize the app
app = flask.Flask(__name__)


# An example of routing:
# If they go to the page "/" (this means a GET request
# to the page http://127.0.0.1:5000/), return a simple
# page that says the site is up!
@app.route("/")
def hello():
    return "It's alive!!!"


@app.route("/predict", methods=["POST", "GET"])
def predict():
    # request.args contains all the arguments passed by our form
    # comes built in with flask. It is a dictionary of the form
    # "form name (as set in template)" (key): "string in the textbox" (value)
    review = request.form.get("review")
    pairs_ldamallet = make_prediction_ldamallet(review)
    pairs_bert = make_prediction_bert(review)
    if pairs_ldamallet is not None:
        suggestion_ldamallet = make_suggestion(pairs_ldamallet[0][0])
    else:
        suggestion_ldamallet = None
    if pairs_bert is not None:
        suggestion_bert = make_suggestion(pairs_bert[0][0])
    else:
        suggestion_bert = None
    return flask.render_template('predictor.html',
                                 review=review,
                                 prediction_ldamallet=pairs_ldamallet,
                                 prediction_bert=pairs_bert,
                                 suggestion_ldamallet=suggestion_ldamallet,
                                 suggestion_bert=suggestion_bert)


# Start the server, continuously listen to requests.
# We'll have a running web app!

# For local development:
if __name__ == '__main__':
    app.run(debug=True)

    # For public web serving:
    # app.run(host='0.0.0.0')
