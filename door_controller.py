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

# keys into credentials dictionary
USER_KEY = "user"
PASS_KEY = "pass"
FRONT_IP_KEY = "front_ip"
BACK_IP_KEY = "back_ip"
credentials = {}
class Door_Controller():
  def __init__(self):
    # load credentials
    self.load_credentials()
    # authenticate with gmail
    self.running = True
    self.gmail_inbox = Gmail_Inbox()
    # create door objects
    self.door_one = Door_Lock(credentials[FRONT_IP_KEY])
    self.door_two = Door_Lock(credentials[BACK_IP_KEY])
    # load the allowed users
    self.allowed = {}
    self.get_allowed()

  def load_credentials(self):
    """
    Load credential files from disk. 
    """
    cred_file = open(CREDENTIALS_FILE, 'r')
    for line in cred_file:
      config_dict = json.loads(line)
      credentials[USER_KEY] = config_dict[USER_KEY]
      credentials[PASS_KEY] = config_dict[PASS_KEY]
      credentials[FRONT_IP_KEY] = config_dict[FRONT_IP_KEY]
      credentials[BACK_IP_KEY] = config_dict[BACK_IP_KEY]
    cred_file.close()

  def monitor(self):
    while self.running:
      command = self.gmail_inbox.get_command()
      if command:
        if command["sender"] in self.allowed:
          self.execute_command(command)
      time.sleep(1.0)
    
  def write_to_log(self, message):
    log = open(".log.txt", "a+")
    log.write(message)
    log.close()

  def execute_command(self, command):
    try:
      method = getattr(self, command["method"]) 
      try:
        method(*command["arguments"])
      except Exception, error:
        self.write_to_log(error)
        print error
    except Exception, error:
      self.write_to_log(error)
      print error

  def get_allowed(self):
    allowed_file = open(ALLOWED_FILE, 'r')
    for allowed in allowed_file:
      person_dict = json.loads(allowed)
      self.allowed[person_dict["number"]] = person_dict
    allowed_file.close()

  def Front(self):
    self.unlock(self.front_door)
    print "yay"

  def Back(self):
    self.unlock(self.front_door)
    print "boo"

  def unlock(self, door):
    #TODO need to write.  already have door connections, and the allowed dictionary has objecs with name number and admin=true/false. (look at .allowed.txt)
    print "unlock"
    
  def Add(self, name, number, is_admin="false"):
    allowed_file = open(ALLOWED_FILE, 'a+')
    allowed_file.write('{"name":"'+name+'", "number":"'+number+'", "admin":'+is_admin+'}')
    self.allowed[number] = {"name":name, "number":number, "admin":is_admin}
    #TODO add to arduino
    allowed_file.close()
    print "add"

  def Remove(self, name=None, number=None):
    line_to_delete = None
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
    print "remove"

class Gmail_Inbox():
  def __init__(self):
    self.mailbox = imaplib.IMAP4_SSL(GMAIL_IMAP)
    self.mailbox.login(credentials[USER_KEY], credentials[PASS_KEY])

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

  def send_message(self, data):
    #TODO write that shit breahs
    pass

if __name__ == "__main__":
  door_controller = Door_Controller()
  door_controller.monitor()
