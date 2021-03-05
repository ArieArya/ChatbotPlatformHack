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


def create_new_model(secret_key, training_data):
    # save training data
    training_data_dir = 'saved_training_data/data-' + str(secret_key) + '.json'
    with open(training_data_dir, "w+") as f:
        json.dump(training_data, f)
    
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in training_data["intents"]:
        for pattern in intent["patterns"]:
            # stemming will turn a sentence into the root word
            # tokenize is to get all separate words in our sentence into a list
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    # Note, enumerate simply returns (index, item), i.e. gives both the item and its index
    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)
    
    # saved parsed data
    parsed_data_dir = 'saved_parsed_data/data-' + str(secret_key) + '.pickle'
    
    with open(parsed_data_dir, "wb") as f:
        pickle.dump((words, labels, training, output), f)
        

    model = Sequential()
    model.add(Dense(32, activation='relu',
                    input_shape=(None, len(training[0]))))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(len(output[0]), activation='softmax'))
    model.compile(optimizer='adam',
                    loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x=training, y=output, epochs=1000, batch_size=8)
    
    
    model_id = 'model-' + str(secret_key) + '.h5'
    model_dir = 'saved_models/' + model_id
    model.save(model_dir)

    return {'response': 'model created successfully'}


