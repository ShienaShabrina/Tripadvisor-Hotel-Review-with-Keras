# -*- coding: utf-8 -*-
"""Shiena - Hotel Review with Keras (Submitted 1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AM1khBqb5or3G5nJKbCsgz7ZHE0OJzGg

https://github.com/MainakRepositor/Data-Analysis/blob/master/Hotel_Reviews_Sentiment_Prediction.ipynb
https://medium.com/@nutanbhogendrasharma/sentiment-analysis-for-hotel-reviews-with-nltk-and-keras-ce5cf3db39b
https://www.kaggle.com/datasets/andrewmvd/trip-advisor-hotel-reviews
https://www.kaggle.com/code/lunamcbride24/hotel-review-keras-classification-project

# Import necessary library
"""

from google.colab import files
files.upload()

!pip install opendatasets

import opendatasets as od
import pandas as pd

import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow.keras.layers as L
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.optimizers import Adam

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error

import matplotlib.pyplot as plt
from wordcloud import WordCloud 
import seaborn as sns


import numpy as np 
import pandas as pd

import nltk
nltk.download('stopwords')
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords

import random as rn

import re
print("Necessary packages have been included successfully!")

od.download(
    "https://www.kaggle.com/datasets/andrewmvd/trip-advisor-hotel-reviews")

"""# Check dataset generally"""

#Load data into pandas
dfh = pd.read_csv('trip-advisor-hotel-reviews/tripadvisor_hotel_reviews.csv')
dfh.head()

# check column and rating 
ratings,columns = dfh.shape
print("Number of ratings in the dataset = ",ratings)
print("Number of columns in the dataset = ",columns)

# check if there is null or odd value
print(dfh.isnull().any())
print(dfh["Rating"].value_counts())
print(dfh.loc[dfh["Review"] == ""])

plt.figure(figsize=(17,8))
sns.countplot(x='Rating',data=dfh,palette='hsv')
plt.xlabel('Ratings',size=15)
plt.ylabel('Count',size=15)
plt.title("Count of ratings \n",size=20)

def wordCloud_generator(data, title=None):
    wordcloud = WordCloud(width = 1600, height = 600,
                          background_color ='#064420',
                          min_font_size = 8
                         ).generate(" ".join(data.values))
    # plot the WordCloud image                        
    plt.figure(figsize = (18, 8), facecolor = None) 
    plt.imshow(wordcloud, interpolation='bilinear') 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
    plt.title(title,fontsize=30)
    plt.show()

wordCloud_generator(dfh['Review'], title="Most frequently used words in reviews")

"""We figured there is zero missing value so no data clean needed. In rgeards for rating, everything look normal wih positive rating being the highest. Along with room, resort, hotel as the most used word.

# Deep cleaning for punctuation
"""

# To check off the structure, print a random review
print(dfh["Review"][30])

"""Although no unusual reviews have been detected, additional punctuation may jeopardize the modeling process, so it is best to remove it"""

punctuations = """!()-![]{};:,+'"\,<>./?@#$%^&*_~Â"""

def reviewParse(review):
    splitReview = review.split() #Split the review into words
    parsedReview = "".join([word.translate(str.maketrans('', '', punctuations)) + " " for word in splitReview])
    return parsedReview

dfh["CleanReview"] = dfh["Review"].apply(reviewParse)
dfh.head()

"""## Tokenizing"""

review = dfh["CleanReview"].copy()
print("Example Sentence: ") 
print(review[30])

token = Tokenizer()
token.fit_on_texts(review)
texts = token.texts_to_sequences(review)
print("Into a Sequence: ")
print(texts[30])

texts = pad_sequences(texts, padding='post')
print("After Padding: ")
print(texts[30])

"""# Label Encoding"""

def encodeLabel(label):
    if label == 5 or label == 4:
        return 2
    if label == 3:
        return 1
    return 0

labels = ["Negative", "Neutral", "Positive"]
dfh["EncodedRating"] = dfh["Rating"].apply(encodeLabel)
dfh.head()

"""# Split the data for training and testing"""

X_train, X_test, y_train, y_test = train_test_split(
    texts, dfh["EncodedRating"], test_size=0.33, random_state=24)

size = len(token.word_index) + 1
ratings = dfh["EncodedRating"].copy()

tf.keras.backend.clear_session()

size = len(token.word_index) + 1
ratings = dfh['Rating'].copy()

tf.keras.backend.clear_session() 
epoch = 2
batchSize = 32
outputDimensions = 16
units = 256

model = tf.keras.Sequential([ 
    L.Embedding(size, outputDimensions, input_length = texts.shape[1]), 
    L.Bidirectional(L.LSTM(units, return_sequences = True)), 
    L.GlobalMaxPool1D(),
    L.Dropout(0.3), 
    L.Dense(64, activation="relu"),
    L.Dropout(0.3),
    L.Dense(3)
])

model.compile(loss = SparseCategoricalCrossentropy(from_logits = True),
              optimizer = 'adam', metrics = ['accuracy']
             )

model.summary()

history = model.fit(X_train, y_train, epochs=epoch, validation_split = 0.2, batch_size = batchSize)

"""# Make predictions"""

predict = np.argmax(model.predict(X_test),axis=1)
loss, accuracy = model.evaluate((X_test), (y_test))

#Print the loss and accuracy
print("Test Loss: ", loss)
print("Test Accuracy: ", accuracy)

print('Accuracy: {}'.format(accuracy_score(predict, y_test)))
print("Mean absolute error: {}".format(mean_absolute_error(predict,y_test)))
print("Root mean square error: {}".format(np.sqrt(mean_squared_error(predict,y_test))))

print(classification_report(y_test, predict, target_names=labels))