import time
import json
import imaplib
import httplib

# server for IMAP connections
GMAIL_IMAP = "imap.gmail.com"

# disk files
ALLOWED_FILE = ".allowed.txt"
CREDENTIALS_FILE = ".credentials.txt"
LOG_FILE = ".log.txt"

# allowed users
ALLOWED = {}

# credentials
CREDENTIALS = {}

# keys into credentials dictionary
USER_KEY = "user"
PASS_KEY = "pass"
FRONT_IP_KEY = "front_ip"
BACK_IP_KEY = "back_ip"

class Door_Controller():
  def __init__(self):
    # authenticate with gmail
    self.running = True
    self.gmail_inbox = Gmail_Inbox()
    # create door objects
    self.front_door = Door_Lock(CREDENTIALS[FRONT_IP_KEY])
    self.back_door = Door_Lock(CREDENTIALS[BACK_IP_KEY])

  def monitor(self):
    while self.running:
      command = self.gmail_inbox.get_command()
      if command:
        print "weeee"
        if command["sender"] in ALLOWED:
          self.execute_command(command)
      time.sleep(1.0)
    
  def execute_command(self, command):
    try:
      method = getattr(self, command["method"]) 
      try:
        method(*command["arguments"])
      except Exception, error:
        write_to_log(error)
        print error
    except Exception, error:
      write_to_log(error)
      print error

  def Front(self):
    response = self.front_door.open()

  def Back(self):
    response = self.back_door.open()

  def unlock(self, door):
    door.send_message("send message")
    
  def Add(self, name, number, is_admin="false"):
    ALLOWED[number] = {"name":name, "number":number, "admin":is_admin}
    allowed_file = open(ALLOWED_FILE, 'a+')
    allowed_file.write('{"name":"'+name+'", "number":"'+number+'", "admin":'+is_admin+'}')
    allowed_file.close()
#self.front_door.send_message("send a message")
    print "add"

  def Remove(self, name=None, number=None):
    line_to_delete = None
    ALLOWED[number] = None
    del ALLOWED[number]
    allowed_file = open(ALLOWED_FILE, 'r')
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
      allowed_file = open(ALLOWED_FILE, 'w+')
      for allowed in allowed_lines:
        if allowed != line_to_delete:
          allowed_file.write(allowed)
      allowed_file.close()
#    self.front_door.send_message("send a message")
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

  def send_message(self, command):
    self.socket.request("GET", command)
    time.sleep(1.0)
    self.socket.getresponse()
    print "penis"

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
  allowed_file = open(ALLOWED_FILE, 'r')
  for allowed in allowed_file:
    person_dict = json.loads(allowed)
    ALLOWED[person_dict["number"]] = person_dict
  allowed_file.close()

def write_to_log(message):
  log = open(".log.txt", "a+")
  log.write(str(message))
  log.close()

  def open(self, name):
    self.socket.request("GET", "o %s" % name)
    return self.socket.getresponse()

if __name__ == "__main__":
  load_credentials()
  get_allowed()
  door_controller = Door_Controller()
  door_controller.monitor()
