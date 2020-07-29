import string
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
stop_words = set(stopwords.words('english'))

import metapy
from bs4 import BeautifulSoup
import requests

import math
import sys
import time
import metapy
import pytoml
import os

import shutil
metapy.log_to_stderr()

movieList = []
linkList = []
synList = []
TopMovieList = []
#querytext = ""
tok = metapy.analyzers.ICUTokenizer()
from flask import Flask,request,render_template
from todo.forms import InputForm
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = 'shengjueyuan'
if __name__ == '__main__':
    app.run(debug = True,port=5000)
def getMovies():
    movieList.clear()
    source = requests.get('https://www.imdb.com/movies-in-theaters/').text
    soup = BeautifulSoup(source, 'lxml')
    #print(soup.prettify())

    base = 'https://www.imdb.com/'
    extention = 'plotsummary'



    # Get Movie and links
    for name in soup.find_all('h4'):
        #Get movie
        movie = name.find('a')['title']
        movieList.append(movie)
        link = base + name.find('a')['href'] + extention
        linkList.append(link)
        #Write movie
        #file1.write(movie+'\n')
        #print(movie)
        #print (link)
    for x in movieList:
        movieList[movieList.index(x)] = x[:-7]
        #print(x)

def getSyn():
    synList.clear()
    for link in linkList:
        source = requests.get(link).text
        soup = BeautifulSoup(source, 'lxml')
        synopsis = ''
        for sonp in soup.find_all('li', attrs={"class":"ipl-zebra-list__item"}):
            synopsis += sonp.text
        synList.append(synopsis)


def remove_punctuation(text):
    no_punct = "".join([c for c in text if c not in string.punctuation])
    return no_punct

def tokenAndStopwords (text):
    textNoPunctLower = remove_punctuation(text).lower()
    word_tokens = word_tokenize(textNoPunctLower)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    listToStr = ' '.join([str(elem) for elem in filtered_sentence])
    return listToStr


#organize data
def organData(str):
    with open('QueryData.txt', 'r') as f:
        aggData = f.readline()
    #print(aggData)
    #print("_________________________________________________________________")

    #tokenize teh synopsys that we got
    iterr = 0
    for x in synList:
        tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
        tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)
        tok = metapy.analyzers.LowercaseFilter(tok)
        tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)
        tok.set_content(x)
        tokens = [token for token in tok]
   
        #save the tokenized versiuons as strings in synList
        query = ''
        for y in tokens:
            query += y + ' '
        synList[iterr] = query
        iterr = iterr + 1
    
    tok.set_content(aggData)
    tokens = [token for token in tok]
   
    #save the tokenized versiuons as strings in synList
    query = ''
    for y in tokens:
        query += y + ' '
    aggData = query


    querytext = aggData + synList[movieList.index(str)]   
    return querytext




#First Step 
#Check to see if inputText contains movie tittle
def firstStep( str, movie):
    #remove punct and set to lowercase
    movieNoPunctLower = remove_punctuation(movie).lower()
    inputTextNoPunctLower = remove_punctuation(str).lower()
    
    if inputTextNoPunctLower.find(movieNoPunctLower) != -1:
        return True
    else: 
        return False

def secondStep(str, str2):
    documents = []
    documents.insert(0,str2)
    documents.insert(1,str)
    
    documents = [tokenAndStopwords(document) for document in documents]

    #print (documents)


    tfidf_vectorizer = TfidfVectorizer()

    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

    #print (tfidf_matrix)
    #print (tfidf_matrix.shape)
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)[0][1]

    








#_______________________________________________________________________________
@app.route('/search',methods=["GET","POST"])
def process_spoiler():
    """get the name of the movie and detect spoiler."""
    form = InputForm()
    #drop = DropForm()

    colours = movieList
    #Get List of movies(movieList)
    getMovies()
    colours = movieList


    if form.is_submitted():
        result = request.form
        text = result["movie"]
        movieT = result["movieTitle"]

        #get twitter data and synopsys
        getSyn()#(synList)
        arg1 = remove_punctuation(movieT).lower()

        command = 'python todo/Exp1.py ' + '"'+arg1+ '"'
        os.system(command)

        # Organice data ints query
        query = organData(movieT)

        #Run checks
        first = firstStep( text, movieT)
        decSecond = secondStep(text, query)
        print(first)
        print(decSecond)

        #Spoiler Decision Tree
        if first and decSecond > .1:
            #Should say it is a spoiler and not display the results
            print("Spoiler!!")
        else:
            #Should Display results
            print("No Spoiler Detected")


        """ 
        name is the movie name 
        we are going to have all the backend work done here
        and return the result later
        """
        """
        backend code here
        """
        
        return render_template("result.html",result = result,text = text)
    return render_template("main.html",form = form, colours=colours)


#def dropdown():
#    colours = ['Red', 'Blue', 'Black', 'Orange']
 #   return render_template('test.html', colours=colours)


