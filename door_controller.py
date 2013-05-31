import time
import json
import imaplib
import httplib

IP_ADDRESS_FRONT = "10.10.10.2"
IP_ADDRESS_BACK = "10.10.10.3"
GMAIL_USERNAME = "sae.massit@gmail.com"
GMAIL_PASSWORD = "saemit09"

class Door_Controller():
  def __init__(self):
    self.running = True
    self.gmail_inbox = Gmail_Inbox()
    self.door_one = Door_Lock(IP_ADDRESS_BACK)
    self.door_two = Door_Lock(IP_ADDRESS_BACK)
    self.allowed = {}
    self.get_allowed()

  def monitor(self):
    while self.running:
      command = self.gmail_inbox.get_command()
      if command:
        if command["sender"] in self.allowed:
          self.execute_command(command)
      time.sleep(1.0)
    
  def write_to_log(self, message):
    log = open(".log.txt", "a+")
    log.write(str(message) + '\n')
    log.close()

  def execute_command(self, command):
    try:
      method = getattr(self, command["method"]) 
      try:
        method(*command["arguments"])
      except Exception, error:
        self.write_to_log(error)
    except Exception, error:
      self.write_to_log(error)

  def get_allowed(self):
    allowed_file = open(".allowed.txt", 'r')
    for allowed in allowed_file:
      try:
        person_dict = json.loads(allowed)
        self.allowed[person_dict["number"]] = person_dict
      except Exception, error:
        self.write_to_log(error)
    allowed_file.close()
  
  def unlock(self, door, name):
    #TODO need to write.  already have door connections, and the allowed dictionary has objecs with name number and admin=true/false. (look at .allowed.txt)
    print "unlock"
    
  def add(self, name, number, is_admin="false"):
    if number not in self.allowed:
      self.allowed[number] = {"name":name, "number":number, "admin":is_admin}
      allowed_file = open(".allowed.txt", 'a+')
      allowed_file.write('{"name":"'+name+'", "number":"'+number+'", "admin":'+is_admin+'}\n')
      allowed_file.close()
      #TODO add to arduino
      print "add"

  def remove(self, name=None, number=None):
    line_to_delete = None
    allowed_file = open(".allowed.txt", 'r')
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
      allowed_file = open(".allowed.txt", 'w+')
      for allowed in allowed_lines:
        if allowed != line_to_delete:
          allowed_file.write(allowed)
      allowed_file.write('\n')
      allowed_file.close()
    print "remove"

class Gmail_Inbox():
  def __init__(self):
    self.mailbox = imaplib.IMAP4_SSL("imap.gmail.com")
    self.mailbox.login(GMAIL_USERNAME, GMAIL_PASSWORD)

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
