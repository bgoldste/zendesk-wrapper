from pymongo import MongoClient
import time, datetime
import requests, json 
import sys


def connect_to_db():
	#return db instance an
	uri = "mongodb://zendesk:zendesk@ds049150.mongolab.com:49150/zendesk"
	client = MongoClient(uri)
	print "connected to :" , client
	db = client['zendesk']
	print "db: " , db
	print "adding uninque index on ticket ids"
	db.tickets.ensure_index( 'id', unique=True)
	return db

def drop_all_tickets(db):
	#drop db and reindex

	db.tickets.remove()
	print "all tickets from db removed"
	db.tickets.ensure_index( 'id', unique=True)
	print "reindexing db for unique tickets"
	return db

def get_ticket_by_id_from_web(tid=1):
	url = 'https://kimonolabs.zendesk.com/api/v2/tickets/%d.json' % tid
	#url = 'https://kimonolabs.zendesk.com/api/v2/tickets/recent.json'
	user = 'ben@kimonolabs.com'
	pwd = 'k1m1n0'
	response = requests.get(url, auth=(user, pwd))
	return response.json()

def get_1000_tickets_from_web(next_time= 1390073264):
	#default is first ticket
	#
	# Set the request parameters
	url = 'https://kimonolabs.zendesk.com/api/v2/exports/tickets.json?start_time=%d' % int(next_time)
	#url = 'https://kimonolabs.zendesk.com/api/v2/tickets/recent.json'
	user = 'ben@kimonolabs.com'
	pwd = 'k1m1n0'
	print url 
	
	response = requests.get(url, auth=(user, pwd))

	try:
		return response.json()
	except:
		print 'error sleeping 60'
		time.sleep(60)
		response = requests.get(url, auth=(user, pwd))
		try:
			return response.json()
		except:
			print 'error sleeping 120'
			time.sleep(120)
			response = requests.get(url, auth=(user, pwd))
			try:
				return response.json()
			except:
				print "tried 3 times and faileds"
				pass


def get_all_tickets():
	#1409094489
	#1413573033
	# get all tickets and return them--crazy to store in memory?
	#tickets =
	get_1000_tickets()



#print db.tickets.find_one().keys()
def write_bulk_to_db(repsonse):
	# takes response object
	#write tickets to db
	db.tickets.insert(tickets)

def write_one_to_db(ticket, db ):
	db.tickets.insert(ticket)


def set_index():
	db.tickets.ensure_index( 'id', unique=True)


def write_1000_tickets_to_db(response , db ):
	#print "response = %s, db = %s" % ( response, db)
	tickets = response['results']
	next_page = response['next_page']
	print "total tickets:" , len(tickets)
	print "next page:" , next_page

	for ticket in tickets:
		try:
			write_one_to_db(ticket , db )
			print "ticket id %s written to db" % ticket['id']

		except :
			print sys.exc_info()[0]
			pass


def get_current_time():
	return int(time.time())

def get_previous_week_time():
	WEEK = 604800 #week in seconds..
	return get_current_time() - WEEK


def remove_non_new_tickets(db):
	#dedupe based on time created

	time = datetime.datetime.fromtimestamp(get_previous_week_time()).strftime('%Y-%m-%d %H:%M:%S')
	print time 
	db.tickets.remove({"created_at" : {"$lte" : time}})


def generate_wow():
	#first drop stats, then pull in, then clean
	db = connect_to_db()
	drop_all_tickets(db)

	response = get_1000_tickets_from_web(get_previous_week_time())
	
	write_1000_tickets_to_db(response, db)

	remove_non_new_tickets(db)

def pull_stats():
	#make pulling queries easy
	db = connect_to_db()


	ticket_types = ["User Issue/General Help", "Kimono bug", "Feature Suggestion", "kimono issue", "Other", "Unsupported extraction", None]
	function_types = get_function_types()
	total_tickets = db.tickets.count()
	print "Total Tickets" , total_tickets
	#total_issues = db.tickets.find({ "field_21387869":"User Issue/General Help" })
	
	for ticket_type in ticket_types:
		ticket_type_total = 0
		#results = db.tickets.find({ "field_21387869" : ticket_type }).count()
		for function_type in function_types:

			function_type_total = db.tickets.find({ "field_21387869" : ticket_type, "field_22637914" : function_type }).count()
			ticket_type_total += function_type_total
			print ticket_type, function_type, ", ", function_type_total
		print ticket_type , ", " , ticket_type_total
	

def get_function_types():
	url = "https://kimonolabs.zendesk.com/api/v2/ticket_fields.json"

	#url = 'https://kimonolabs.zendesk.com/api/v2/tickets/recent.json'
	user = 'ben@kimonolabs.com'
	pwd = 'k1m1n0'
	response = requests.get(url, auth=(user, pwd))
	function_types = [None,]
	for a in response.json()['ticket_fields']:
		try:
			if ( a['raw_title'] == 'Function'):
				for b in a['custom_field_options']:
					function_types.append(b['name'])
		except:
			pass
	return function_types


def get_ticket_comments(id):
	url = "https://kimonolabs.zendesk.com/api/v2/tickets/%d/comments.json" % id
	user = 'ben@kimonolabs.com'
	pwd = 'k1m1n0'
	response = requests.get(url, auth=(user, pwd)).json()
	comments = []
	for comment in response['comments']:
		print comment
		comments.append(comment['body'])
	return comments




#ticket_with_comments = get_ticket_comments(4739)


def pull_bugs():
	db = connect_to_db()
	pivotal_field = 'field_22640804'
	bug_count = db.tickets.find({ pivotal_field : {'$ne': None} })
	bugs = []
	for bug in bug_count:
		try:
			bugs.append( {'pivotal_id': int(bug[pivotal_field]), 'user_email': bug['req_email']    } )
		except:
			pass

	bug_count = {}
	for bug in bugs:
		try:
			
			bug_count[bug['pivotal_id']]['count'] += 1
			bug_count[bug['pivotal_id']]['emails'].append(bug['user_email'])
		except:
		

			bug_count[bug['pivotal_id']] = {}
			
			bug_count[bug['pivotal_id']]['count'] = 1
			bug_count[bug['pivotal_id']]['emails'] = [bug['user_email'],]
	return bug_count		






# for bug in pull_bugs(): print bug
def print_sorted_bugs():
	bugs = pull_bugs()
	bug_order = sorted(bugs, key=lambda x: (bugs[x]['count']), reverse=True)

	for a in bug_order: 
		print a, bugs[a] 

#print_sorted_bugs()
# import operator
# x = {1: 2, 3: 4, 4:3, 2:1, 0:0}

# sorted_x = sorted(bugs.items(), key=operator.itemgetter(0), reverse = True)
# print 'sorted', sorted_x.reverse()

#get_function_types()
#generate_wow()

#field_22640804 = pivotal number
def get_open_tickets():
	db = connect_to_db()
	
	open_count = db.tickets.find({ 'status' : 'Open' }).count()
	new_count = db.tickets.find({ 'status' : 'New' }).count()
	closed_count = db.tickets.find({ 'status' : 'Closed' }).count()
	print "new count", new_count
	print "open count", open_count
	#change to return new count in prod
	return new_count


def main():
	generate_wow()
	open_tickets = get_open_tickets()
	print "open tickets:", open_tickets
	if open_tickets > 10:
		#send email
		print "email alert triggered"
		return True
	else:
		print "email alert not triggered"
		return False














