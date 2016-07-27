#!/usr/bin/python3


from os import listdir
from os.path import isfile, join
import re

# https://github.com/esnme/ultrajson
import ujson

# https://github.com/elastic/elasticsearch-py
import elasticsearch
from elasticsearch import helpers


## INIT

indexname = 'tweets'

es = elasticsearch.Elasticsearch()

es.indices.delete(index=indexname, ignore=[400, 404])
es.indices.create(index=indexname, ignore=400)
#print (create_index)


## MAPPING

with open('elasticsearch-mapping.json', 'r', encoding='utf-8') as inputfh:
    mapping = inputfh.read()
ujson.loads(mapping)
es.indices.put_mapping(index=indexname, doc_type='tweet', body=mapping)


## FILES

filelist = list()
path = './'
for item in listdir(path):
    if isfile(join(path, item)):
        if re.match(r'A-REGEX-PATTERN-HERE', item):
            filelist.append(join(path, item))


## INJECT

i = 0
actions = list()
for filename in filelist:
    print (filename)
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            if len(line) > 1:
                i += 1
                # print (i)
                tweet = ujson.loads(line.strip())
                try:
                    del tweet['entities']
                except KeyError:
                    pass
                try:
                    del tweet['extended_entities']
                except KeyError:
                    pass
                try:
                    del tweet['quoted_status']
                    del tweet['quoted_status_id']
                    del tweet['quoted_status_id_str']
                except KeyError:
                    pass
                try:
                    del tweet['retweeted_status']
                    #del tweet['retweeted_status']['entities']
                    #del tweet['retweeted_status']['extended_entities']
                except KeyError:
                    pass

                # delete profile variables
                del tweet['user']['profile_background_tile']
                del tweet['user']['profile_sidebar_border_color']
                del tweet['user']['profile_sidebar_fill_color']
                del tweet['user']['profile_link_color']
                del tweet['user']['profile_background_image_url_https']
                del tweet['user']['profile_background_image_url']
                del tweet['user']['profile_use_background_image']
                del tweet['user']['profile_background_color']
                del tweet['user']['profile_image_url_https']
                del tweet['user']['profile_image_url']
                del tweet['user']['profile_text_color']
                try:
                    del tweet['user']['profile_banner_url']
                except KeyError:
                    pass

                del tweet['user']['default_profile_image']
                del tweet['user']['entities']
                del tweet['user']['id_str']
                del tweet['user']['follow_request_sent']
                del tweet['user']['following']
                del tweet['user']['notifications']
                del tweet['user']['protected']
                del tweet['user']['url']

                del tweet['id_str']
                del tweet['in_reply_to_status_id_str']
                del tweet['in_reply_to_user_id_str']

                try:
                    del tweet['place']['bounding_box']['type']
                except TypeError:
                    pass
                try:
                    del tweet['place']['url']
                except TypeError:
                    pass


                # reverse geolocations (sometimes necessary)
                try:
                    # del tweet['geo']['type']
                    if len(tweet['geo']['coordinates']) == 2:
                        vallist = tweet['geo']['coordinates']
                        tweet['geo']['coordinates'] = vallist[::-1]
                except TypeError:
                    pass

                action = {
                    '_index': indexname,
                    '_type': 'tweet',
                    '_id': tweet['id'],
                    '_source': tweet
                }
                actions.append(action)


                if len(actions) > 1000:
                    helpers.bulk(es, actions)
                    del actions[:]


# index the last ones
if len(actions) > 0:
    helpers.bulk(es, actions)




## CATCH

#try:
#    ...
#except elasticsearch.exceptions.RequestError:
#    print ('caught!')
#    pass

