import jsonpickle
import tweepy
import jsonlines
from bs4 import BeautifulSoup
import requests
import metapy
import re
from urllib.parse import urlparse
import urllib.request
from youtube_transcript_api import YouTubeTranscriptApi
import sys

dataAg = []

metapy.log_to_stderr()
def remove_url(txt):
    """Replace URLs found in a text string with nothing 
    (i.e. it will remove the URL from the string).
    """
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())

#tidies extracted text 
def process_bio(bio):
    bio = bio.encode('ascii',errors='ignore').decode('utf-8')       #removes non-ascii characters
    bio = re.sub('\s+',' ',bio)       #repalces repeated whitespace characters with single space
    return bio

''' More tidying
Sometimes the text extracted HTML webpage may contain javascript code and some style elements. 
This function removes script and style tags from HTML so that extracted text does not contain them.
'''
def remove_script(soup):
    for script in soup(["script", "style"]):
        script.decompose()
    return soup

def remove_nonText(txt):
    """Replace unusual chars found in a text string with nothing 
    """
    return " ".join(re.sub("([^0-9A-Za-z: \t])", "", txt).split())
'''
The keys are required for using Twitter APIs. You can get them by registering an app to a Twitter account at
https://developer.twitter.com/.  There is a form to fill out, then you can get the keys. 
'''
keys = {
        'consumer_key':        'MhdGrg5DSE66WWJjcCcfW6xc9',
        'consumer_secret':     'e841D6HaecWCmDvZbtZ7HMac4OfaEXUDiIrlOLPyDlrppjyklp',
        'access_token_key':    '1204604357133471745-hGTplRiAWXKJ80uI0QZ1WyvWjS5Vk1',
        'access_token_secret': 'IgAY32WUJdnOOyPO4APkmjoTDxA72KZoBC4Io2taoiEkp'
    }
auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token_key'], keys['access_token_secret'])

api = tweepy.API(auth)
filters = '-filter:retweets'
trailers = 'Movie Trailers'
Reviews = 'Movie Review'
#Movie = "jumanji the next level "
Movie = str(sys.argv[1]) + ' '
#print(Movie)
query = "todo/" +Movie + Reviews
query2 = Movie + trailers
MaxList = 500
Review_Tweet = []

open("QueryData.txt", "w").close()
file2 = open("QueryData.txt","a")

    


'''
The uncommented stuff underneath TweeterQuery_file = query + '.json' is the code to scrap twitter. Essentually,
it will do a search in Twitter on the query and save the file as a json. Twitter returns dictionaries of dictionies as 
a dataset
'''
TweeterQuery_file = query + '.json'
'''
with open(TweeterQuery_file, 'w') as f:
    for tweet in tweepy.Cursor(api.search, q=query,
                           include_entities=True,
                           tweet_mode='extended',    
                           lang="en").items(MaxList):
        f.write(jsonpickle.encode(tweet._json, unpicklable=False) + '\n')
'''
'''
This will break-up the dictionaries of dictionaries into just a list of dictionaries. It makes it easier to manipulate 
'''
jsonObjects=[]
with jsonlines.open(TweeterQuery_file) as reader:
    for obj in reader:
        jsonObjects.append(obj) 

'''
This will extract the twitter text and any urls that will take you to a website.
'''
count = 0
ReviewList = []
try:
    while jsonObjects[count]!=None:
        Text_Value = remove_url(jsonObjects[count]['full_text'])
        Link_Value = []
        Doc_Value = ''
        if jsonObjects[count]['entities']['urls']!=[]:
            Link_Value = jsonObjects[count]['entities']['urls'][0]['expanded_url']
        ReviewList.append({'Text':Text_Value, 'Link':Link_Value})    
        count+=1
except IndexError:
    count-=1
    pass        

#DataSet_file = open("cranfield/cranfield.dat","w")

'''
This strips out certain info from the website's page and extracts the text from the website. There is more work that needs 
to be done here but, it is close. The end results is stored as a set of documents in the file ceanfield.dat
'''

blacklist = ['[document]','noscript','header','html','meta','head','input','script',
             # there may be more elements you don't want, such as "style", etc.
]

for k in range(count):
    if ReviewList[k]['Link']!=[]:
        res = requests.get(ReviewList[k]['Link'])
        html_page = res.content
        soup = remove_script(BeautifulSoup(html_page, 'html.parser'))
        text = soup.find_all(text=True)
        output = ''
        for t in text:
            if t.parent.name not in blacklist:
                output += '{} '.format(t)
        output = remove_url(output)        
    if ReviewList[k]['Link']==[]:
        output = ReviewList[k]['Text']
    doc = process_bio(output)
    #dataAg.append(doc)
    file2.write(doc + ' ')
#DataSet_file.close()    

#fwd_idx = metapy.index.make_forward_index('config.toml')

'''
This will get YouTube movie trailer clips from the query entry on movie and store 5 youtube sites 
'''
query_string = urllib.parse.urlencode({"search_query" : query2})
html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
#print("http://www.youtube.com/watch?v=" + search_results[0])
#print("http://www.youtube.com/watch?v=" + search_results[1])
#print("http://www.youtube.com/watch?v=" + search_results[2])

'''
Store you tube web links
'''
QueryDataSet = []
for l in range(5):
    QueryDataSet.append("http://www.youtube.com/watch?v=" + search_results[l])


#for h in range(5):
    #print(QueryDataSet[h])


'''
If the YouTube set has close caption, then the following logic will capture it and store the data in 
cranfield-queries.txt
'''
#QueryDataSet_file = open("cranfield-queries.txt","w")
for v in range(5):
    url_data = urllib.parse.urlparse(QueryDataSet[v])
    YouTube_query = urllib.parse.parse_qs(url_data.query)
    video = YouTube_query["v"][0]
    try:
        query_content = YouTubeTranscriptApi.get_transcript(video)
        j = 0
        try:
            while query_content[j]!=None:
                file2.write(remove_nonText(query_content[j]['text']) + ' ')
                #dataAg.append(remove_nonText(query_content[j]['text']))
                j+=1
        except IndexError:
            j-=1
            pass
    except: 
        pass
#QueryDataSet_file.close()      

file2.close()

#for x in dataAg:
#	print(x)

'''
With the cranfield.dat file for the data set and cranfield-queries.txt, one can then do a ranking function routine
which should yield the top ranking spoiler documents down to the most likily not a spoiler document. Hence, if a 
thresshold value is used to determine the fine line between spoiler and not spoiler, then one has a binary
classification algorithm for spoilers.  
'''