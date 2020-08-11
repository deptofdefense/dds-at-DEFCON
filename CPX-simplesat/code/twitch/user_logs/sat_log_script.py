import sys
import fnmatch
import os
import json
import csv
import smtplib
import base64
import datetime
import time as ti
import email, smtplib, ssl


from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


#store which kit's logs we are going through - used in the email and storing properly named csv.
kit_name = str(sys.argv[1])
winners_file = kit_name + "_winners.csv"

##############################
# EDIT RECEIVER EMAIL ADDRESS HERE
###########################################
receiver_email = str(sys.argv[2])#input("What will be the Receiver's Email Address?")
###########################################
##############################
minutes = int(sys.argv[3])


while True:
	#load json file of previous winners
	#can't be empty (already has a test values in it)
	try:
		with open('./winners.json') as users_file:
			userdict = json.load(users_file)
	except:
		userdict = {"test": 0}

	#open all log files in directory

	for file in os.listdir('./'):
		
		if file.endswith(".log"):
			
			with open(file) as json_file:
				#turn log into dict
				user_json = json.load(json_file)

	#this section just gets us the last step minus one
			
			l = []
			for key, value in user_json["complete_steps"].items():
				l.append(int(key))
			
			completed = False
			if len(l) > 12: #12 bc there's a step 0
				completed = True
				time = user_json["complete_steps"]["12"][0]

			if completed:
				user = user_json["name"]
				#if the user hasn't already won, add to list
				if user not in userdict:
					userdict[user] = datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
					

	#save user dict back to winners.json file
	#This saves the file to be referred to again when the script re-runs
	with open('winners.json', 'w') as fp:
		json.dump(userdict, fp)
		#kit username jointime highestlevel timestamp didcomplete timestamp
		#winners list 1 hr

	#This is saving the same data but as a CSV for human readability in the email below
	with open(winners_file, 'w') as f:
		for key in userdict.keys():
			f.write("%s, %s\n" %(key, userdict[key]))

	
##############################EMAIL SECTION##############################
	#email created for sending emails
	sender_email = os.environ['EMAIL']
	
	password = os.environ['EMAILPASSWORD']


	project = kit_name
	subject = project + "winners"
	body = "Here are the updated winners from " + project
	# Create a multipart message and set headers
	message = MIMEMultipart()
	message["From"] = sender_email
	message["To"] = receiver_email
	message["Subject"] = project + " Winners"
	message["Bcc"] = receiver_email  # Recommended for mass emails

	# Add body to email
	message.attach(MIMEText(body, "plain"))

	filename = winners_file  # In same directory as script

	# Open PDF file in binary mode
	with open(filename, "rb") as attachment:
	    # Add file as application/octet-stream
	    # Email client can usually download this automatically as attachment
	    part = MIMEBase("application", "octet-stream")
	    part.set_payload(attachment.read())

	# Encode file in ASCII characters to send by email    
	encoders.encode_base64(part)

	# Add header as key/value pair to attachment part
	part.add_header(
	    "Content-Disposition",
	    f"attachment; filename= {filename}",
	)

	# Add attachment to message and convert message to string
	message.attach(part)
	text = message.as_string()

	# Log in to server using secure context and send email
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
	    server.login(sender_email, password)
	    server.sendmail(sender_email, receiver_email, text)

#########################SLEEP FOR 15 MIN#######################
	ti.sleep(60*minutes)

	