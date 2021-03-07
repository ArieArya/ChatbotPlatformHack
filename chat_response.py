from keras.models import load_model
from keras.layers import Dense
from keras.models import Sequential
import keras
import pickle
import json
import random
import tensorflow
import numpy
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
nltk.download('punkt')


def chat_response(secret_key, model_name, words_query):
    try:
        # obtain saved model
        model_dir = 'saved_models/model-' + str(secret_key) + '-' + str(model_name) + '.h5'
        model = load_model(model_dir)
        
        # obtain parsed data
        parsed_data_dir = 'saved_parsed_data/data-' + str(secret_key) + '-' + str(model_name) + '.pickle'
        with open(parsed_data_dir, "rb") as f:
            words, labels, training, output = pickle.load(f)
            
        # obtain json training data
        data_dir = 'saved_training_data/data-' + str(secret_key) + '-' + str(model_name) + '.json'
        with open(data_dir) as file:
            data = json.load(file)
            
        answer = "I'm sorry, I didn't quite get that"
        results = model.predict([bag_of_words(words_query, words).tolist()])[0]

        # returns index of highest probability tags
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        if results[results_index] > 0.90:  # 90% threshold
            for tg in data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']

            answer = random.choice(responses)
        return answer, tag
            
    except:
        return "", ""


def bag_of_words(s, words):
    # initializes one hot code with 0's on all words
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)
