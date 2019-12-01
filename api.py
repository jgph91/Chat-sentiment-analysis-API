#!/usr/bin/python3

from pymongo import MongoClient,ASCENDING
from bottle import request, response, post, get, run, route
from bson.json_util import dumps
import requests
from src.mongo import connectCollection, stop_existence, stop_not_existence,get_name
from src.nltk import analyzer,get_text

# collections
db, chats = connectCollection('API', 'chats')
db, users = connectCollection('API', 'users')
db, messages = connectCollection('API', 'messages')

# users endpoints
@post('/users/<userName>/create')
def user_creator(userName):
    '''Create a user and save into DB'''

    # user can't be already created
    stop_existence(userName, 'userName', users)
    #assigning a new id
    new_id = users.distinct("idUser")[-1] + 1
    db.users.insert_one({'idUser': new_id,
                         'userName': userName})

    return (f'Welcome {userName}!. Your id is {new_id}')

@get('/users/<userName>')
def get_userid(userName):
    '''Get the user id for the user name specified'''

    # user must be already created
    stop_not_existence(userName, 'userName', users)

    return dumps(users.find({'userName': userName},
                            {'_id': 0, 'idUser': 1,
                             'userName': 1}))

# chat endpoints
@post('/chat/create')
def chat_creator():
    '''Create a conversation to load messages'''
    idChat = chats.distinct("idChat")[-1] + 1
    db.chats.insert_one({'idChat': idChat})

    return (f'Chat created, the id is {idChat}.')

@post('/messages/<idChat>/<idUser>/addmessage')
def add_message(idChat, idUser):
    '''Add a message to the conversation.'''

    # user must be already created
    stop_not_existence(idUser, 'idUser', users)
    # chat must be already created
    stop_not_existence(idChat, 'idChat', chats)

    #text entered via params
    dict(request.forms)
    datetime=request.forms.get('datetime')
    text=request.forms.get('text')

    #getting the user name from the users collection
    userName = get_name(idUser)

    new_id = messages.distinct("idMessage")[-1] + 1
    messages.insert_one({'idUser': new_id,'userName': userName,
                        'idMessage':new_id,'idChat':idChat,
                        'datetime':datetime,'text':text})

    return (f'Your message has been inserted sucessfully!')

@get('/messages/<idChat>')
def get_messages(idChat):
    '''Get all messages from the specified chat'''
    idChat = int(idChat)
    # chat must be already created
    stop_not_existence(idChat, 'idChat', chats)

    return dumps(messages.find({'idChat': idChat},
                               {'datetime':1,'_id':0,
                               'userName':1,'idMessage':1,
                               'text':1}).sort('idMessage',ASCENDING))

@get('/chat/<idChat>/sentiment')
def mood_analyzer(idChat):
    '''Analyze messages from `chat_id` using NLTK's sentiment.'''

    text = get_text(idChat)
    mood = analyzer(text)
    
    return mood

run(host='0.0.0.0', port=8080, debug=True)
