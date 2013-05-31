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
    
  def execute_command(self, command):
    try:
      method = getattr(self, command["method"]) 
      method(*command["arguments"])
    except:
      print "invalid text format"

  def get_allowed(self):
    allowed_file = open(".allowed.txt", 'r')
    for person_string in allowed_file:
      person_dict = json.loads(person_string)
      self.allowed[person_dict["number"]] = person_dict
    allowed_file.close()
  
  def unlock(self, door, name):
#TODO need to write.  already have door connections, and the allowed dictionary has objecs with name number and admin=true/false. (look at .allowed.txt)
    print "unlock"
    
  def add(self, name, number, is_admin="false"):
    allowed_file = open(".allowed.txt", 'a+')
    allowed_file.write('{"name":"'+name+'", "number":"'+number+'", "admin":'+is_admin+'}')
    #TODO add to self.allowed dictionary
    #TODO add to arduino
    allowed_file.close()
    print "add"

  def remove(self, name=None, number=None):
#TODO Not working yet. i know the problem though
    line_to_delete = None
    allowed_file = open(".allowed.txt", 'r+')
    for person_string in allowed_file:
      if name:
        if name in person_string:
          line_to_delete = person_string
      elif number:
        if number in person_string:
          line_to_delete = person_string
    allowed_file = open(".allowed.txt", 'w')
    for person_string in allowed_file:
      if person_string != line_to_delete:
        allowed_file.write(person_string + '\n')
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

if __name__ == "__main__":
  door_controller = Door_Controller()
  door_controller.monitor()
