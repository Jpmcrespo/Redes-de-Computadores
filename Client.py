#Client
import socket
import sys
import os

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

	TRS['socket'].connect((TRS['ip'],TRS['port']))
	message = "TRQ t "+str(len(word.split()))+" "+ word+ "\n"
	response=sendMsg(TRS['socket'],TRS['ip'],TRS['port'], message)
	print (response)

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

	TRS['socket'].connect((TRS['ip'],TRS['port']))
	message= "TRQ f " + filename + " " + str(size) + " "

	TRS['socket'].sendto(message.encode(), (TRS['ip'], TRS['port']))
	print(str(size)+" bytes to Transmit")	
	while(size>0):
		buff=file.read(BUFFER_SIZE)
		TRS['socket'].send(buff)
		size-=len(buff)
	print("done")


#----------------------------Receive translated file-------------------------------

def rcvTransFile(TRS):
	'''receives the translated file from TRS'''

	received= TRS['socket'].recv(BUFFER_SIZE)
	received=received.split(b' ',4)
	for i in range(4):
		received[i]=received[i].decode()

	if received[0]=="TRR":			#outros casos, try except
		if received[1]=="f":
			extradata=received[-1]
			receiveFile(TRS, received[2], int(received[3]), extradata)	

		


def receiveFile(TRS, name, size, extradata):
	'''auxiliary function to rcvTransFile'''

	file=open(name.rsplit(".",1)[0]+"RECEIVED"+"."+name.rsplit(".",1)[1],"wb")

	print("receiving " +str(size)+" bytes")
	file.write(extradata)
	while(size>0):
		buff=TRS['socket'].recv(BUFFER_SIZE)
		file.write(buff)
		size-=BUFFER_SIZE
	print("done")
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
				TCS['port']= int(arguments[i+1])    #Falta ver se é valido o numero
				p=0
			else:
				raise ArgumentsError(invalidArgs)
	except ValueError as e:
		traceback.print_exc()
		print ("port must be an integer between 0-65535")
		sys.exit(-1)
	except:
		raise ArgumentsError(invalidArgs)



#---------------------------------------------------------------------------------
#   						Translation Server Credentials
#---------------------------------------------------------------------------------

def requestTRSCred(TCS, language):
	'''requests the TRS credentials of a specific language, returns a dictionary'''

	Msg="UNQ "+language+ "\n"
	cred=sendMsg(TCS['socket'], socket.gethostbyname(TCS['name']), TCS['port'], Msg).split()
	#return {'ip': cred[2], 'port' : int(cred[3])}
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
		if command[0]=="list":
			languages=updateLanguageList(TCS)

		elif command[0]=="request":

			TRS=requestTRSCred(TCS, languages[int(command[1])-1])
			TRS['socket']=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

			if command[2]=="t":
				requestWordTanslation(TRS, " ".join(command[3:]))
				
			elif command[2]=="f":
				requestFileTranslation(TRS, command[3])


				
		elif command[0]=="exit":
			return
		else:
			print ("command not found")







main()
