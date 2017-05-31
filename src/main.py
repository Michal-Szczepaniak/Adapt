import json
import socket
import sys
from xml.dom.minidom import parse
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine

engine = IntentDeterminationEngine()

DOMTree = parse('config.xml')
for intent in DOMTree.getElementsByTagName("intent"):
    builder = IntentBuilder(intent.attributes["name"].value)
    for node in intent.getElementsByTagName("keyword"):
        keyword = node.attributes["name"].value;
        required = node.attributes["required"].value;
        ktype = node.attributes["type"].value;
        if ktype == 'normal':
            for child in node.getElementsByTagName("item"):
                engine.register_entity(child.childNodes[0].nodeValue, keyword)
        else:
            engine.register_regex_entity(node.childNodes[0].nodeValue)
        if required == 'true':
            builder.require(keyword)
        else:
            builder.optionally(keyword)
    engine.register_intent_parser(builder.build())


# create and register weather vocabulary
'''weather_keyword = [
    "weather"
]

for wk in weather_keyword:
    engine.register_entity(wk, "WeatherKeyword")

weather_types = [
    "snow",
    "rain",
    "wind",
    "sleet",
    "sun"
]

for wt in weather_types:
    engine.register_entity(wt, "WeatherType")'''

# create regex to parse out locations
# engine.register_regex_entity("in (?P<Location>.*)")

# structure intent
'''weather_intent = IntentBuilder("WeatherIntent")\
    .require("weather")\
    .optionally("type")\
    .require("Location")\
    .build()

engine.register_intent_parser(weather_intent)'''

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind(('', 43202))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
    
server.listen(10)

while 1:
    #wait to accept a connection - blocking call
    client, addr = server.accept()
    print ('Connected with ' + addr[0] + ':' + str(addr[1]))
    text = client.recv(1024).decode()#.split("\\")[0]
    if text.startswith("b'update"):
        engine = IntentDeterminationEngine()
        
        DOMTree = parse('config.xml')
        for intent in DOMTree.getElementsByTagName("intent"):
            builder = IntentBuilder(intent.attributes["name"].value)
            for node in intent.getElementsByTagName("keyword"):
                keyword = node.attributes["name"].value;
                required = node.attributes["required"].value;
                ktype = node.attributes["type"].value;
                if ktype == 'normal':
                    for child in node.getElementsByTagName("item"):
                        engine.register_entity(child.childNodes[0].nodeValue, keyword)
                else:
                    engine.register_regex_entity(node.childNodes[0].nodeValue)
                if required == 'true':
                    builder.require(keyword)
                else:
                    builder.optionally(keyword)
            engine.register_intent_parser(builder.build())
    else:
        for intent in engine.determine_intent(" "+text):
            if intent.get('confidence') > 0:
                client.send(str(json.dumps(intent, indent=4)).encode(encoding='utf_8', errors='strict'))
        client.close()
     
server.close()
