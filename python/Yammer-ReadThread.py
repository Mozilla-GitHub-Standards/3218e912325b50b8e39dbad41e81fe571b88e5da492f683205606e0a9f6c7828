import time
import yampy

#Secrets scrubbed
client_id = ""
client_secret = ""
redirect_uri = ""
code = ""
access_token = ""


newestMsgID = 0
currentID = 0
MAX_MSG_LIMIT = 10000000000
currentPgLowerMsgID = MAX_MSG_LIMIT
users = dict()
moreToProcess = True
MAX_MSG_PER_PAGE = 20
restCall = 0  # Keep track of how many times we make web calls due to API limits / throttling
MAX_REQ_PER_INTERVAL = 10  # How many Yammer requests you can make in 30 seconds. Once reached, wait 30 seconds.

# Various Yammer threads for testing
GMAIL_THREAD = 414357831     # 268-ish
AURORA_THREAD = 387871026    # 12 messages
PASTEBIN_THREAD = 421373941  # Exactly 20 messages (as of 27-JUL-2014)


# Setup authenticator - Don't delete any of this! You'll need it when the access token expires
authenticator = yampy.Authenticator(client_id, client_secret)
#auth_url = authenticator.authorization_url(redirect_uri)
#print(auth_url) #Debug: show the code to stdout
#access_token = authenticator.fetch_access_token(code)
#print(access_token)

#Get your Yammer object for making requests
yammer = yampy.Yammer(access_token)

# Create a dictionary from the Yammer messages.

# The RESTful API to the "messages" endpoint will result in one response with two blocks of structures within:
# 1. messages: the actual posts/replies/polls within the message thread
# 2. references: usually users.

# Start by grabbing the latest reply in thread and go backwards from there using message ID.
# Start without newer_than or older_than parameters to get the newestMsgID.

while moreToProcess:
    # Be respectful of Yammer API limits; else we get throttled / banned.
    restCall += 1
   
    if restCall % MAX_REQ_PER_INTERVAL == 0:
        time.sleep(31)  # Pause for a little more than 30 seconds ever MAX_REQ_PER_INTERVAL requests

    # Grab the latest set of messages in the thread and set newestMsgID
    yammerMessages = dict(yammer.messages.in_thread(GMAIL_THREAD, older_than=currentPgLowerMsgID))

    # Read the latest set messages and users who posted them
    # Users: Load up the id:full_name key/value pair dictionary now
    for user in yammerMessages.get("references"):
        users[user.get("id")] = user.get("full_name")  # The format here is dictionary[key]=value

    # Messages:
    for message in yammerMessages.get("messages"):
        # Note: in the messages context, sender_id is the same integer as "id" in the references context.
        print(users[message.get("sender_id")], ":", sep='')  # Don't add space between user and colon character

        #Get the currentID, and set newestMsgID
        currentID = message.get("id")
        if currentID > newestMsgID:
            newestMsgID = currentID

        #Set the current page's lowest ID to the current ID.
        currentPgLowerMsgID = currentID

        print("ID:", currentID)
        print("newestMsgID:", newestMsgID)

        print(message.get("body").get("plain"))
        print(
            "=========================================================================================================")

    if len(yammerMessages.get("messages")) < MAX_MSG_PER_PAGE:
        moreToProcess = False
