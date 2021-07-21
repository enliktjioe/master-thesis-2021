from gensim.test.utils import datapath
import ktrain
from utils import *

# Import hold_out validation dataset
term_doc_train = pd.read_pickle('preprocessed_data/term_doc.pkl')
dictionary = pd.read_pickle('preprocessed_data/dictionary.pkl')

# Import ldamallet model
ldamallet = gensim.models.wrappers.LdaMallet.load(datapath('model'))
ldamallet = gensim.models.wrappers.ldamallet.malletmodel2ldamodel(ldamallet)

# Import bert model
bert_model = ktrain.load_predictor('bert_model').model
bert_preproc = ktrain.load_predictor('bert_model').preproc
bert_predictor = ktrain.get_predictor(bert_model, bert_preproc)

topics = ["Platform/Device", "User Experience", "Value", "Service", "Trouble-shooting", "Shows"]

def make_prediction_ldamallet(input):
    """
    Output:
    Returns (list of topics, list of probs) in a descending order of probabilities
    """
    clean_text = NLPpipe().preprocess(pd.Series(input))
    term_doc_new = [dictionary.doc2bow(text) for text in clean_text]
    if input is not None:
        percentages = [perc for topic, perc in ldamallet[term_doc_new][0]]
        indices = np.argsort(percentages)[::-1]
        return list(zip([topics[index] for index in indices], [100*np.round(percentages[index], 3) for index in indices]))

    return None

def make_prediction_bert(input):
    """
    Output:
    Returns (list of topics, list of probs) in a descending order of probabilities
    """
    if input is not None:
        percentages = bert_predictor.predict(input, return_proba=True)
        indices = np.argsort(percentages)[::-1]
        return list(zip([topics[index] for index in indices], np.round(percentages[indices]*100,3).tolist()))

    return None

def make_suggestion(topic):
    suggestion = None
    if topic == "Platform/Device":
        suggestion = "Your review may be about platforms or device. Please send an email to our Device Support team at " \
                     "privacy@netflix.com or contact us at 1-(866)-579-7172. Thank you."
    if topic == "User Experience":
        suggestion = "If your review is about Account or Profile settings, please refer to our \"Manage my account\" at " \
                     "https://help.netflix.com/en/ or contact us at 1-844-505-2993 for more information."
    if topic == "Value":
        suggestion = "Thank you for sharing your experience with Netflix! If you'd like to ask about programs, " \
                     "subscriptions, costs, or anything else, please contact us at 1-844-505-2993."
    if topic == "Service":
        suggestion = "If you have any question about the services we provide, please contact Netflix Customer Service" \
                     " through the app or call us at 1-(866)-579-7172."
    if topic == "Trouble-shooting":
        suggestion = "If this is about any inconvenience caused when using the app, we are so sorry. We will carefully read your" \
                     " feedback and try to fix the issue as soon as possible."
    if topic == "Shows":
        suggestion = "Thank you for leaving a review about the programs/shows in Netflix. We value your experience with" \
                     " our programs and it will be shared with our partners and film companies as well."
    return suggestion