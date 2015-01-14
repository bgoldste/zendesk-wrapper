from flask.ext.script import Manager

import zendesk

import os
from postmark import PMMail

manager = Manager(app)

@manager.command
def hello():
	# zendesk do stuff
	# if need to send message, then do it
	message = PMMail(api_key = os.environ.get('POSTMARK_API_TOKEN'),
	                 subject = "Hello from Postmark",
	                 sender = "ben@kimonolabs.com",
	                 to = "dan@kimonolabs.com",
	                 text_body = "Hello",
	                 tag = "hello")

	message.send()

if __name__ == "__main__":
  manager.run()