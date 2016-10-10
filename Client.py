#Client
import socket
import sys
import os
import traceback

BUFFER_SIZE=1024
ListMSG="ULQ\n"
invalidArgs='\nInvalid arguments.\nusage: python3 Client.py [-n TCSname] [-p TCSport]'

class ArgumentsError(Exception):
	def __init__(self, message):
		self.message=message


def sendMsg(sock, ipAddress, port, message):
	'''sends a message and waits for the answer'''

	sock.sendto(message.encode(), (ipAddress, port))
	response=sock.recv(BUFFER_SIZE)
	return (response.decode())


#---------------------------------------------------------------------------------
#							Word Translation
#---------------------------------------------------------------------------------

def requestWordTanslation(TRS, word):
	'''requests and prints a translated word'''

	TRS['socket'].connect((TRS['ip'] ,TRS['port']))
	message = "TRQ t "+str(len(word.split()))+" "+ word+ "\n"
	response=sendMsg(TRS['socket'],TRS['ip'],TRS['port'], message)
	if response=="TRR NTA\n":
		print(TRS['ip']+": ERROR: One or more of the words you requested have no valid translation.")
	elif response=="TRR ERR\n":
		print("An error ocurred in translation                                                                   ")
	else:
		print (TRS['ip']+": "+" ".join(response.split()[3:]))

#---------------------------------------------------------------------------------
#							File Translation
#---------------------------------------------------------------------------------

def requestFileTranslation(TRS, filename):
	'''requests a file translation'''


	sendForeignFile(TRS, filename)
	rcvTransFile(TRS)

#----------------------------Send Foreign File------------------------------------

def sendForeignFile(TRS,filename):
	'''sends the foreign file to TRS'''

	file=open(filename,"rb")
	size=os.path.getsize(filename)

	TRS['socket'].connect((TRS['ip'] ,TRS['port']))
	message= "TRQ f " + filename + " " + str(size) + " "

	TRS['socket'].sendto(message.encode(), (TRS['ip'], TRS['port']))
	print(str(size)+" bytes to Transmit")
	while(size>0):
		buff=file.read(BUFFER_SIZE)
		TRS['socket'].send(buff)
		size-=len(buff)
	TRS['socket'].send("\n".encode())
	print("done")
	


#----------------------------Receive translated file-------------------------------

def rcvTransFile(TRS):
	'''receives the translated file from TRS'''

	received= TRS['socket'].recv(BUFFER_SIZE)
	received=received.decode().split()

	if received[0]=="TRR":			#outros casos, try except
		if received[1]=="f":
			receiveFile(TRS, received[2], int(received[3]))
		elif received[1]=="ERR":
			print("An error ocurred in translation")




def receiveFile(TRS, name, size):
	'''auxiliary function to rcvTransFile'''

	file=open(name.rsplit(".",1)[0]+"RECEIVED"+"."+name.rsplit(".",1)[1],"wb")

	print("receiving " +str(size)+" bytes")
	
	i=0
	while(size>0):
		buff=TRS['socket'].recv(BUFFER_SIZE)
		file.write(buff)
		size-=len(buff)
	print("done")
	file.seek(-1, os.SEEK_END)
	file.truncate()
	file.close()
	print("END OF FILE TRANSLATION")



#---------------------------------------------------------------------------------
#						Language List Request aka "list" command
#---------------------------------------------------------------------------------

def updateLanguageList(TCS):
	'''prints and updates the list of available languages to translate'''

	lst=sendMsg(TCS['socket'], socket.gethostbyname(TCS['name']), TCS['port'], ListMSG).split()
	languages=[]
	i=1
	if lst[0]=="ULR" and lst[1]!="EOF" and lst[1]!="ERR":
		languages=lst[2:]
		for lang in languages:
			print (str(i)+"- "+lang)
			i+=1
	else:
		print (lst[0] + " "+ lst[1])

	return languages


#---------------------------------------------------------------------------------
#							Argument Validation
#---------------------------------------------------------------------------------

def validateArgs(TCS):
	'''validates the arguments given to the program upon runtime'''

	n,p=1,1
	arguments=sys.argv
	try:
		for i in range(1,len(arguments),2):
			if arguments[i]=="-n" and n:
				TCS['name']= arguments[i+1]
				n=0
				
				
			elif arguments[i]=='-p' and p:
				TCS['port']= int(arguments[i+1])  
				if TCS['port'] not in range(65536):
					raise ValueError
				p=0
			else:
				raise ArgumentsError(invalidArgs)
	except ValueError as e:
		sys.exit("port must be an integer between 0-65535")
	except:
		raise ArgumentsError(invalidArgs)
	try:
		test=socket.gethostbyname(TCS['name'])
	except:
		sys.exit("Invalid server name")



#---------------------------------------------------------------------------------
#   						Translation Server Credentials
#---------------------------------------------------------------------------------

def requestTRSCred(TCS, language):
	'''requests the TRS credentials of a specific language, returns a dictionary'''

	Msg="UNQ "+language+ "\n"
	cred=sendMsg(TCS['socket'], socket.gethostbyname(TCS['name']), TCS['port'], Msg).split()
	if cred[1]=="EOF" or cred[1]=="ERR":
		print (cred[0]+ " "+ cred[1])
	#return {'ip': cred[2], 'port' : int(cred[3])}
	print(cred[1]+" "+cred[2])
	return {'ip': cred[1], 'port' : int(cred[2])}




#---------------------------------------------------------------------------------
#										Main
#---------------------------------------------------------------------------------

def main():
	words=""
	TCS={'name':"localhost", "port": 58056, "socket":socket.socket(socket.AF_INET, socket.SOCK_DGRAM)}

	validateArgs(TCS)

	languages=[]

	while(True):
		command= input(">").split()
		try:
			if command[0]=="list":
				TCS['socket'].settimeout(2)
				languages=updateLanguageList(TCS)

			elif command[0]=="request":   #se fizer logo request crasha tudo

				TRS=requestTRSCred(TCS, languages[int(command[1])-1])
				TRS['socket']=socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
				TRS['socket'].settimeout(5)

				if command[2]=="t":
					requestWordTanslation(TRS, " ".join(command[3:]))

				elif command[2]=="f":
					requestFileTranslation(TRS, command[3])

				TRS['socket'].shutdown(socket.SHUT_RDWR)


			elif command[0]=="exit":
				return
			else:
				print ("command not found")
		except FileNotFoundError as err:
			print (err.string())
		except socket.timeout:
			print ('request timed out, please try again')
		except socket.error as err:
			sys.exit("Connection Failed: " + str(err[1]))









main()
