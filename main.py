def transactions(wallet: str = None) -> list:
    assert(wallet is not None)
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': wallet,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 10,
        'sort': 'asc',
        'apikey': ETHERSCAN_KEY # Use your API key here!
    }
    response = requests.get('https://api.etherscan.io/api', params=url_params)
    response_parsed = json.loads(response.content)
    assert(response_parsed['message'] == 'OK')
    txs = response_parsed['result']
    return [ {'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp']} \
        for tx in txs ]
What this does is creates the URL we looked at to Etherscan before, but dynamically adds in the ETHERSCAN_KEY (the API Key you generated earlier) and the wallet parameter (the wallet we are interested in).

It then sends that request as a GET request, and parses the result from JSON into a dictionary, and creates a list of transactions including the information regarding who sent it to who, the value of the transaction as well as the time it occurred.

If you then call this method with a wallet you will see the full API result as described before!

Note: If you are lost with the Python at this point don’t worry! The full script with Telegram functions can be found at the bottom of this article.

Handling Telegram User Input Messages
So now that we have our bot connecting to Etherscan, it’s time to handle user input to our bot, and generate some responses. For interfacing with Telegram, I have used pyTelegramBot, which you will need to add as a pip dependency using the following:

$ pip install pyTelegramBotAPI
We can then setup the bot in Python with the following code:

import telebot
import os
BOT_KEY = os.environ.get('BOT_KEY')
bot = telebot.TeleBot(BOT_KEY, parse_mode=None)
This will instantiate the bot, using the API key as an environment variable, but will not handle any user actions. Therefore, the current script could be run as:

$ BOT_KEY="MyBotAPIKey" python3 main.py
To handle input, we need to set up message handlers. In this case, we will set up a dictionary which keeps a track of what users are subscribing to, so lets add this state management and message handling as follows:

# Setup global state runtime store
subscriptions = {}
# Update the transaction list for a specific chat's wallet
def update_subscriptions(chat_id, wallet) -> bool:
    global subscriptions
    try:
        txs = transactions(wallet)
        if chat_id not in subscriptions.keys():
            subscriptions[chat_id] = {} 
            subscriptions[chat_id][wallet] = txs
        return True
    except:
        return False
# Setup a message handler for 'add_wallet_listener'
@bot.message_handler(commands=['add_wallet_listener'])
def handle_add_wallet_listener(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide a wallet address.')
        return
    wallet_addr = message_text[1]
    if not update_subscriptions(message.chat.id, wallet_addr):
        bot.reply_to(message, f'Failed to add the wallet to subsription list! Is it a real address?')
        return
    bot.reply_to(message, f'You are now subscribed to events from the following wallets: {subscriptions[message.chat.id].keys()}')
The above code now creates a dictionary mapping which stores the state regarding which chat is subscribed to which wallet address notifications.

It also adds a message callback which runs the function when the user enters /add_wallet_listener in a chat with the bot.

Monitoring the Wallet
Now that we have all of the parts separately, it’s time to put them together. So the first thing we need to do is attempt to poll Etherscan once every n seconds or minutes (there unfortunately is no web-sockets API as of yet).

Since our Telegram bot polling blocks the main thread, we need to run the polling in a separate thread, for convenience we can setup a decorator function that handles this for us:

import threading
def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func
And then use this to create a background function which will execute the polling:

# Get the latest transaction timestamp from a list
def get_latest_tx(txs: list) -> int:
    return max(txs,key=lambda tx: int(tx['timestamp']))
# Format a transaction to string nicely
def format_tx(tx: dict) -> str:
    return f'From: {tx["from"]}, To: {tx["to"]}, Amount: {tx["value"]}'

@background
def infinity_wallet_updates():
    while True:
        for chat in subscriptions:
            for wallet in subscriptions[chat]:
                previous_latest_tx = get_latest_tx(subscriptions[chat][wallet])
                print(previous_latest_tx)
                update_subscriptions(chat, wallet)
                current_latest_tx = get_latest_tx(subscriptions[chat][wallet])
                if int(current_latest_tx['timestamp']) > int(previous_latest_tx['timestamp']):
                    bot.send_message(chat, f'New transactions occurred for {wallet}!')
                    [bot.send_message(chat, format_tx(tx)) for tx in \
                        filter(lambda tx: int(tx['timestamp']) > previous_latest_tx, subscriptions[chat][wallet])]
        time.sleep(60)
This function infinity_wallet_updates() will now run forever on a separate thread, and sleep for 60 seconds between each poll.

It iterates through every chat and every wallet that the chat subscribes to and looks at the latest cached state of the most recent transaction timestamp, which is then compared to the updated cache timestamp. This way we will see any transactions that were newly added in the 60 seconds we weren’t listening.

It will then send all new transactions via Telegram to the chat to inform the user that some new transactions have occurred on that wallet.

The Full Picture
So there are a lot of moving parts as expected, but putting them altogether and adding some additional case handling looks like:

import telebot
import os
import requests
import json
import time
import threading
def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func
ETHERSCAN_KEY = os.environ.get('ETHERSCAN_KEY')
BOT_KEY = os.environ.get('BOT_KEY')
SUBSCRIPTIONS_FILE_PATH = 'subscriptions.json'
# Create the bot
bot = telebot.TeleBot(BOT_KEY, parse_mode=None)
subscriptions = {
    # Example of dict structure
    # 'chat_id': {
    #     'wallet_addr': [] # List of most recent transactions
    # }
}
# Read the cached config on the system
if os.path.exists(SUBSCRIPTIONS_FILE_PATH):
    with open(SUBSCRIPTIONS_FILE_PATH) as file:
        subscriptions = json.load(file)
def transactions(wallet: str = None) -> list:
    assert(wallet is not None)
    url_params = {
        'module': 'account',
        'action': 'txlist',
        'address': wallet,
        'startblock': 0,
        'endblock': 99999999,
        'page': 1,
        'offset': 10,
        'sort': 'asc',
        'apikey': ETHERSCAN_KEY
    }
    
    response = requests.get('https://api.etherscan.io/api', params=url_params)
    response_parsed = json.loads(response.content)
    assert(response_parsed['message'] == 'OK')
    txs = response_parsed['result']
    return [ {'from': tx['from'], 'to': tx['to'], 'value': tx['value'], 'timestamp': tx['timeStamp']} \
         for tx in txs ]
def update_subscriptions(chat_id, wallet) -> bool:
    global subscriptions
    try:
        txs = transactions(wallet)
        if chat_id not in subscriptions.keys():
            subscriptions[chat_id] = {}
        subscriptions[chat_id][wallet] = txs
        return True
    except:
        return False
# Show the user the wallets they're listening to
@bot.message_handler(commands=['get_listening_wallets'])
def handle_get_listening_wallets(message):
    if message.chat.id in subscriptions.keys():
        bot.reply_to(message, f'You are currently subscribed to events from: {subscriptions[message.chat.id].keys()}')
    else:
        bot.reply_to(message, 'You are not subscribed to any wallet transactions!')
# Add a new wallet to listen to
@bot.message_handler(commands=['add_wallet_listener'])
def handle_add_wallet_listener(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide a wallet address.')
        return 
    wallet_addr = message_text[1]
    if not update_subscriptions(message.chat.id, wallet_addr):
        bot.reply_to(message, f'Failed to add the wallet to subsription list! Is it a real address?')
        print(subscriptions)
        return
    bot.reply_to(message, f'You are now subscribed to events from the following wallets: {subscriptions[message.chat.id].keys()}')
# Remove a wallet that is being listened to
@bot.message_handler(commands=['remove_wallet_listener'])
def handle_remove_wallet_listener(message):
    message_text = message.text.split()
    if len(message_text) != 2:
        bot.reply_to(message, f'Please provide a wallet address.')
        return 
    wallet_addr = message_text[1]
    if wallet_addr in subscriptions[message.chat.id].keys():
        del subscriptions[message.chat.id][wallet_addr]
        bot.reply_to(message, f'Wallet address {wallet_addr} now unsubscribed!')
    else:
        bot.reply_to(message, f'Could not find wallet address subscription - did you ever subscribe? address: {wallet_addr}')
# Get the latest transaction from a list of transactions, based on timestamp
def get_latest_tx(txs: list) -> int:
    return max(txs,key=lambda tx: int(tx['timestamp']))
# Format a transaction dict item to printable string
def format_tx(tx: dict) -> str:
    return f'From: {tx["from"]}, To: {tx["to"]}, Amount: {tx["value"]}'
# Background poll Etherscan for all wallets and update users
@background
def infinity_wallet_updates():
    while True:
        for chat in subscriptions:
            for wallet in subscriptions[chat]:
                previous_latest_tx = get_latest_tx(subscriptions[chat][wallet])
                print(previous_latest_tx)
                update_subscriptions(chat, wallet)
                current_latest_tx = get_latest_tx(subscriptions[chat][wallet])
                if int(current_latest_tx['timestamp']) > int(previous_latest_tx['timestamp']):
                    bot.send_message(chat, f'New transactions occured for {wallet}!')
                    [bot.send_message(chat, format_tx(tx)) for tx in \
                        filter(lambda tx: int(tx['timestamp']) > previous_latest_tx, subscriptions[chat][wallet])]
        with open(SUBSCRIPTIONS_FILE_PATH, 'w') as file:
            json.dump(subscriptions, file)
        time.sleep(60*3)
# Run the bot!
infinity_wallet_updates()
bot.infinity_polling()
Which can be run with the environment variables setup:

$ BOT_KEY="5705483837:AAGlCVUP7rU0vbpbDJQk64VhTaDXy9_G3hE" ETHERSCAN_KEY="VQTY5N9HCGVZWTDN7T7FSGRDRD39R75RIX" python3 main.py
This complete version of the bot now handles:

U
