from command import Command
import json
import time
class Money(Command):
	fileName = 'money.txt'
	bank = {}
	karmaTimer = {}
	karmaPerVote = 1
	voteDelay = 20
	
	def __init__(self, hb):
		self.hb = hb
		self.helpString = "*!give [target] [amount]: Grants target user x monies"
		self.publicHelpString = "!balance: Prints out your current balance ######## !pay [target] [amount]: Pays target x monies from your account ######## [user]++ : Grant a user " + str(self.karmaPerVote) + " point" + ("s" if self.karmaPerVote==1 else "") + " for being awesome ######## [user]-- : Deducts " + str(self.karmaPerVote) + " point" + ("s" if self.karmaPerVote==1 else "") + "from a user for being not awesome "
		self.helpString = "*!setUpvoteAmount [amount]: Sets the number of monies granted by [user]++ ######## *!setUpvoteDelay [seconds]: Sets how long you must wait between upvotes";
		pass
		
	def writeConf(self, conf):
		conf['money'] = {}
		conf['money']['fileName'] = self.fileName
		conf['money']['upvoteDelay'] = self.voteDelay
		conf['money']['moneyPerVote'] = self.karmaPerVote
		pass
	
	def readFromConf(self, conf):
		self.fileName = conf['money']['fileName']
		self.voteDelay = conf['money']['upvoteDelay']
		self.karmaPerVote = conf['money']['moneyPerVote']
		self.loadBankFile()
		pass
		
	def checkMessage(self, message, user):
		lower = message.strip().lower()
		if lower.find('!bal') != -1 or lower.find('!pay ') == 0:
			return True
		elif lower.find('++') != -1:
			return True;
		elif lower.find('--') != -1:
			return True;
		elif self.hb.isOp(user) == True:
			if lower.find('!give ') == 0:
				return True
			if lower.find('!setupvoteamount ') == 0:
				return True
			if lower.find('!setupvotedelay ') == 0:
				return True
				
		return False
		
	def onMessage(self, msg, user):
		lower = msg.strip().lower()
		if lower.find('!bal') != -1:
			if len(self.hb.viewers) == 0:
				self.hb.message(user + ": Give me a sec, I just woke up!")
			else:
				self.hb.message(user + ": You currently have " + str(self.checkBalance(user)) + " monies.")
		elif lower.find('++') != -1:
			curTime = time.time()
			if (user in self.karmaTimer) == False or curTime-self.karmaTimer[user] > self.voteDelay:
				split = lower.split(' ')
				for t in split:
					if t.find('++') == (len(t)-2) and len(t) > 2: #Check if at end
						name = t[:-2]
						if name == user:
							self.hb.message(user + ": You can't upvote yourself!")
							break
						elif self.checkBalance(name) != None:
							self.pay(name, self.karmaPerVote)
							self.karmaTimer[user] = curTime
							break
				pass
		elif lower.find('--') != -1:
			curTime = time.time()
			if (user in self.karmaTimer) == False or curTime-self.karmaTimer[user] > self.voteDelay:
				split = lower.split(' ')
				for t in split:
					if t.find('--') == (len(t)-2) and len(t) > 2: #Check if at end
						name = t[:-2]
						if self.checkBalance(name) != None:
							self.pay(name, -self.karmaPerVote)
							self.karmaTimer[user] = curTime
							break
				pass
		elif lower.find('!pay ') == 0:
			split = msg.split(' ')
			if len(split) == 3:
				amt = split[2]
				target = split[1]
				if target == user:
					self.hb.message(user + ": You can't pay yourself!")
				else:
					try: 
						amount = int(amt)
						bal = self.checkBalance(user)
						if amount > bal:
							self.hb.message(user + ": You don't have enough!")
						elif checkUser(target) == False:
							self.hb.message(user + ": Target does not exist!")
						else:
							self.hb.message(user + ": Paying " + target + " " + str(amount) + " monies.")
							self.pay(target, amount)
							self.pay(user, -amount)
					except ValueError:
						pass

		if(self.hb.isOp(user) == True):
			if lower.find('!give ') == 0:
				split = msg.split(' ')
				if len(split) >= 3:
					amt = split[2]
					target = split[1]
					try: 
						amount = int(amt)
						if self.checkUser(target) == False:
							self.hb.message(user + ": Target does not exist!")
						else:
							self.hb.message(user + ": Giving " + target + " " + str(amount) + " monies.")
							self.pay(target, amount)
					except ValueError:
						self.hb.message(user + ": Error giving money.")
						pass
			if lower.find('!setupvoteamount ') == 0:
				split = msg.split(' ')
				if len(split) >= 2:
					amt = split[1]
					try: 
						amount = int(amt)
						self.karmaPerVote = amount
						self.hb.message(user + ": Upvote amount set to " + str(amount))
						self.hb.saveSettings()
					except ValueError:
						self.hb.message(user + ": Error setting upvote amount.")
						pass
			if lower.find('!setupvotedelay ') == 0:
				split = msg.split(' ')
				if len(split) >= 2:
					amt = split[1]
					try: 
						amount = int(amt)
						self.voteDelay = amount
						self.hb.message(user + ": Upvote delay set to " + str(amount))
						self.hb.saveSettings()
					except ValueError:
						self.hb.message(user + ": Error setting upvote delay.")
						pass
		
	
	def checkBalance(self,user):
		if(user.lower() in self.bank) == False and self.hb.isOnline(user) == True:
			print user + " not found, adding"
			self.bank[user.lower()] = 0
			self.saveBankFile()
		#elif self.hb.isOnline(user) == False:
		#	print user + " not online"
		#	return 0
		
		return self.bank[user.lower()]
	
	def loadBankFile(self):
		f = open(self.fileName,'r')
		self.bank = json.loads(f.read());
		f.close()
	
	def saveBankFile(self):
		with open(self.fileName, 'w') as outfile: 
			json.dump(self.bank,outfile)
	
	def checkUser(self,user):
		if(user.lower() in self.bank) == True:
			return True
		else:
			return False
		
	def pay(self, user, amount):
		if self.checkBalance(user) != None:
			self.bank[user.lower()] += amount
			self.saveBankFile()
		
	def onJoin(self, user):
		self.checkBalance(user)

'''
Free to use
Point Reward System
Drawing/Giveaway System
Balance Checking
Question Queuing
Greeting, Welcome Back, & Part/Quit Messages
Multiple Timed Advertisements
Custom Command Responses
Custom Greetings
Follower, Subscriber, and Donation Overlay Alerts
Chat Filter
Betting Games
Voting System
Fast & Friendly Support
'''