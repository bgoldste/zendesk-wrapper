from flask.ext.script import Manager
from flask import Flask

#import zendesk

import os
from postmark import PMMail

app = Flask(__name__)
print app

manager = Manager(app)

@manager.command
def hello():
	# zendesk do stuff
	# if need to send message, then do it
	print app
	message = PMMail(api_key = "621fc6db-f9a7-44c8-90f3-e294803465ed",
	                 subject = "Hello from Postmark",
	                 sender = "ben@kimonolabs.com",
	                 to = "ben@kimonolabs.com",
	                 text_body = "Hello",
	                 tag = "hello")

	message.send()

if __name__ == "__main__":
  manager.run()