import os
import email
import imaplib

IP_ADDRESS_FRONT = "10.10.10.2"
IP_ADDRESS_BACK = "10.10.10.3"
GMAIL_USERNAME = "massiotatau09@gmail.com"
GMAIL_PASSWORD = "saemit09"

class Door_Controller():
  def __init__(self):
    self.gmail_inbox = Gmail_Inbox()
    self.door_one = Door_Lock(IP_ADDRESS_BACK)
    self.door_two = Door_Lock(IP_ADDRESS_BACK)
    self.brothers = self.get_brothers()
    self.guests = self.get_guests()

  def monitor(self):
    email_message = self.gmail_inbox.get_messages()
    data = self.gmail_inbox.parse_header(email_message)
    self.execute_command(data)
    
  def execute_command(self, data):
    # TODO fill out

  def get_brothers(self):
    # TODO fill out

  def get_guests(self):
    # TODO fill out
  
  def unlock_door(self, name):
    # TODO fill out
    
  def add_user(self, name, number, id="brother", expiration=None):
    # TODO fill out

  def remove_user(self, id="brother", name=None, number=None):
    # TODO fill out

class Gmail_Inbox():
  def __init__(self):
    self.mailbox = imaplib.IMAP4_SSL("imap.gmail.com")
    self.mailbox.login(GMAIL_USERNAME, GMAIL_PASSWORD)
    self.mailbox.select("Box")

  def get_messages(self):
    # TODO fill out

  def parse_header(self, email_message):
    # TODO fill out

class Door_Lock():
  def __init__(self, ip_address):
    # TODO fill out

  def send_message(self, data):
    # TODO fill out

if __name__ == "__main__":
  door_controller = Door_Controller()
  door_controller.monitor()
