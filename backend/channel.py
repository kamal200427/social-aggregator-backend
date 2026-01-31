#backend/channel.py
import os
import json

STATE_FILE = "channel_state.json"

def save_channel_state_yout(channel_id):
    with open(STATE_FILE, "w") as f1:
        json.dump({"channel_id": channel_id}, f1)

def load_channel_state_yout():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f1:
            data = json.load(f1)
            
            return data.get("channel_id") 
    return None
 
#for facebook
STATE_FILE1 = "channel_state_fb.json"
def save_channel_state_faceb(channel_id):
    with open(STATE_FILE1, "w") as f2:
        json.dump({"channel_id": channel_id}, f2)

def load_channel_state_faceb():
    if os.path.exists(STATE_FILE1):
        with open(STATE_FILE1, "r") as f2:
            data = json.load(f2)
            return data.get("channel_id")
    return None
def save_channel_state(channel_id,source):
    if(source=="youtube"):
        save_channel_state_yout(channel_id)
    elif(source=="facebook"):
        save_channel_state_faceb(channel_id)
    
def load_channel_state(source):
    if(source=="youtube"):
        return load_channel_state_yout()
    elif(source=="facebook"):
        return load_channel_state_faceb()
     
