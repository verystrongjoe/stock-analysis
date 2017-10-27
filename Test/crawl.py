import urllib.request, re
import os.path

f = urllib.request.urlopen('https://en.wikipedia.org/wiki/Markov_decision_process')

source= f.read(200000)

print(str(source))

linksList = re.findall('<a href=(.*?)>.*?</a>', str(source))

print(os.path.expanduser('~'))


for links in linksList :
    print(links)











