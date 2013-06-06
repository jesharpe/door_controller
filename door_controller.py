import time
import json
import time
import imaplib
import httplib

# server for IMAP connections
GMAIL_IMAP = "imap.gmail.com"

# disk files
RESIDENTS_FILE = ".allowed.txt"
CREDENTIALS_FILE = ".credentials.txt"
LOG_FILE = ".log.txt"

# allowed users
RESIDENTS = {}

# credentials
CREDENTIALS = {}

# keys into credentials dictionary
USER_KEY = "user"
PASS_KEY = "pass"
FRONT_IP_KEY = "front_ip"
BACK_IP_KEY = "back_ip"

class Door_Controller():
  def __init__(self):
    try:
      # authenticate with gmail
      self.running = True
      self.gmail_inbox = Gmail_Inbox()
      # create door objects
      self.front_door = Door_Lock(CREDENTIALS[FRONT_IP_KEY])
      self.back_door = Door_Lock(CREDENTIALS[BACK_IP_KEY])
    except Exception as e:
      write_to_log(e)
      print e

  def monitor(self):
    while self.running:
      command = self.gmail_inbox.get_command()
      if command:
        if command["sender"] in RESIDENTS:
          self.execute_command(command)
      time.sleep(1.0)
    
  def execute_command(self, command):
    try:
      method = getattr(self, string.lower(command["method"])) 
      try:
        method(command)
      except Exception as e:
        write_to_log(e)
        print e
    except Exception as e:
      write_to_log(e)
      print e

  def front(self, command):
    response = self.front_door.open_door(RESIDENTS[command["sender"]]["name"])

  def back(self, command):
    response = self.back_door.open_door(RESIDENTS[command["sender"]]["name"])

  def add(self, command):
    name = command["arguments"][0]
    number = command["arguments"][1]
    if len(command["arguments"]) > 2:
      is_admin = command["arguments"][2]
    else:
      is_admin = False
    if number not in RESIDENTS:
      RESIDENTS[number] = {"name":name, "number":number, "admin":is_admin}
      allowed_file = open(RESIDENTS_FILE, 'a+')
      is_admin = string.lower(str(is_admin))
      allowed_file.write('{"name":"'+name+'", "number":"'+number+'", "admin":'+str(is_admin)+'}\n')
      allowed_file.close()
      self.front_door.add_card_access(name)
    print "add"

  def remove(self, command):
    name = command["arguments"][0]
    number = command["arguments"][1]
    if number in RESIDENTS:
      line_to_delete = None
      RESIDENTS[number] = None
      del RESIDENTS[number]
      allowed_file = open(RESIDENTS_FILE, 'r')
      allowed_lines = allowed_file.readlines()
      allowed_file.close()
      for allowed in allowed_lines:
        if name:
          if name in allowed:
            line_to_delete = allowed
        elif number:
          if number in allowed:
            line_to_delete = allowed
      if line_to_delete:
        allowed_file = open(RESIDENTS_FILE, 'w+')
        for allowed in allowed_lines:
          if allowed != line_to_delete:
            allowed_file.write(allowed)
        allowed_file.close()
      self.front_door.remove_card_access(name)
      self.back_door.remove_card_access(name)
      print "remove"

class Gmail_Inbox():
  def __init__(self):
    self.mailbox = imaplib.IMAP4_SSL(GMAIL_IMAP)
    self.mailbox.login(CREDENTIALS[USER_KEY], CREDENTIALS[PASS_KEY])

  def get_command(self):
    command = {}
    self.mailbox.select("door_lock")
    msg_type, inbox = self.mailbox.search(None, "UNSEEN")
    messages = inbox[0].split()
    if len(messages) > 0:
      message = messages[0]
      msg_type, data = self.mailbox.fetch(message, "(BODY[HEADER.FIELDS (FROM)])")
      command["sender"] = data[0][1].split("\"")[1].replace("(", "").replace(")", "").replace(" ", ".").replace("-", ".")
      msg_type, data = self.mailbox.fetch(message, "(BODY[TEXT])")
      command["method"] = data[0][1].split('\r')[0].split()[0]
      command["arguments"] = data[0][1].split('\r')[0].split()[1:]
      self.mailbox.store(message, "+FLAGS", "\\Deleted")
      self.mailbox.expunge()
      return command

class Door_Lock():
  def __init__(self, door_ip):
    self.socket = httplib.HTTPConnection(door_ip)

  def open_door(self, name):
    self.socket.request("GET", "o %s" % (name))
    return self.socket.getresponse()

  def add_card_access(self, name):
    self.socket.request("GET", "a %s" % (name))
    return self.socket.getresponse()

  def remove_card_access(self, name):
    self.socket.request("GET", "r %s" % (name))
    return self.socket.getresponse()

def load_credentials():
  """
  Load credential files from disk. 
  """
  cred_file = open(CREDENTIALS_FILE, 'r')
  for line in cred_file:
    config_dict = json.loads(line)
    CREDENTIALS[USER_KEY] = config_dict[USER_KEY]
    CREDENTIALS[PASS_KEY] = config_dict[PASS_KEY]
    CREDENTIALS[FRONT_IP_KEY] = config_dict[FRONT_IP_KEY]
    CREDENTIALS[BACK_IP_KEY] = config_dict[BACK_IP_KEY]
  cred_file.close()

def get_allowed():
  allowed_file = open(RESIDENTS_FILE, 'r')
  for allowed in allowed_file:
    person_dict = json.loads(allowed)
    RESIDENTS[person_dict["number"]] = person_dict
  allowed_file.close()

def write_to_log(message):
  log = open(".log.txt", "a+")
  log.write(str(message) + '\n')
  log.close()

if __name__ == "__main__":
  load_credentials()
  get_allowed()
  door_controller = Door_Controller()
  door_controller.monitor()
