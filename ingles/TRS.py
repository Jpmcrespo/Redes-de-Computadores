#Translation Server
import socket
import sys
import signal
import os
import time
import traceback

BUFFER_SIZE=1024

invalidArgs='Invalid arguments.\nusage: python3 TRS.py language [-p TRSport] [-n TCSname] [-e TCSport]'
portMsg="port must be an integer between 0-65535"

class ArgumentsError(Exception):
	def __init__(self, message):
		self.message=message


def sendMsg(sock, ipAddress, port, message):
	sock.sendto(message.encode(), (ipAddress, port))
	response=sock.recv(BUFFER_SIZE)
	return (response.decode())

#---------------------------------------------------------------------------------
#								Protocol Verification
#---------------------------------------------------------------------------------

def protocolSyntaxVerification(msg):
	'''Protocol Verification for most messages'''
	if "  " in msg or msg[-1]!="\n" or msg[0]==" " or " \n" in msg:
		return False
	return True

def protocolSyntaxVerification2(msg):
	'''Protocol Verification for file transfer case'''
	if "  " in msg or msg[0]==" " or " \n" in msg:
		return False
	return True


#---------------------------------------------------------------------------------
#								TCS Communication
#---------------------------------------------------------------------------------

#-------------------------------Registration--------------------------------------
def RegisterServer(TCS, language,port):
	'''Informs TCS that this server is available for the translation of the provided language'''
	try:
		
		UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		UDP_socket.settimeout(5)
		#no need to bind anything because the system allready binds sockets that send stuff
		#you only need to bind sockets that receive before sending, which is not the case
		RegMsg="SRG "+ language+ " "+ socket.gethostname()+" "+ str(port)+"\n"
		command=sendMsg(UDP_socket, TCS['ip'], TCS['port'], RegMsg).split()
		UDP_socket.close()

		if command[0]=="SRR":
			if command[1]=="OK":
				print ("Successfully registered Translation Server.")
			elif command[1]=="NOK":
				print ("Registration refused, exiting")
				sys.exit(-1)
			elif command[1]=="ERR":
				print ("Registration Error, exiting")
				sys.exit(-1)
	except socket.timeout:
		sys.exit("Request to register timed out.\nExiting...")
#-----------------------------UnRegistration--------------------------------------
def UnRegisterServer(TCS, language,port):
	'''Informs TCS that this server is no longer available for the translation of the provided language'''
	try:
		
		UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		UDP_socket.settimeout(5)
		#no need to bind anything because the system allready binds sockets that send stuff
		#you only need to bind sockets that receive before sending, which is not the case
		RegMsg="SUN "+ language+ " "+ socket.gethostname()+" "+ str(port)+"\n"
		command=sendMsg(UDP_socket, TCS['ip'], TCS['port'], RegMsg).split()
		UDP_socket.close()

		if command[0]=="SUR":
			if command[1]=="OK":
				print ("Successfully unregistered Translation Server.")
			elif command[1]=="NOK":
				print ("Unregistration refused.")
			elif command[1]=="ERR":
				print ("Unregistration Error.")
				sys.exit()
	except socket.timeout:
		sys.exit("Request to unregister timed out.\nExiting...\n")


#---------------------------------------------------------------------------------
#								Word Translation
#---------------------------------------------------------------------------------

def translateWordList(Client, language, wordlist):
	'''Sends to the client the translated wordlist'''
	print (Client['ip'] + " "+ str(Client['port'])+ ": "+ " ".join(wordlist))
	result=""
	langFile= open("text_translation.txt", 'r')
	for word in wordlist:
		result+=getTranslation(langFile, word)+" "
	result=result.strip()
	print(result+" ("+str(len(result.split()))+")")
	if "NTA" in result:
		message="TRR NTA\n"
	else:
		message="TRR t "+str(len(wordlist))+" "+result+"\n"
	Client['socket'].send(message.encode())



def getTranslation(file, word):
	'''finds and gets the translation of the specified word'''
	file.seek(0)
	for line in file:
		trans=line.split()
		if word==trans[0]:

			return trans[1]
	return "NTA"




#---------------------------------------------------------------------------------
#								File Translation
#---------------------------------------------------------------------------------

def receiveFile(Client, size):
	file=open("TRSreceived.png","wb")
	buff=""
	
	while(size>-1):
		buff=Client['socket'].recv(BUFFER_SIZE)
		file.write(buff)
		size-=len(buff)
	if buff[-1]!=10:
		raise ValueError
	
	
	file.seek(-1, os.SEEK_END)
	file.truncate()
	file.close()
	print (str(os.path.getsize("TRSreceived.png")) + " Bytes received")

def translate(Client, language,port):

	aux= Client['socket'].recv(BUFFER_SIZE)
	aux=aux.decode()
	received=aux.split()

	if received[0]=="TRQ":			
		if received[1]=="t":
			# protocolo
			if not protocolSyntaxVerification(aux):
			  raise ValueError
			if int(received[2])!=len(received)-3: 
				raise ValueError

			translateWordList(Client, language, received[3:])


		elif received[1]=="f":
			
			if not protocolSyntaxVerification2(aux):
			  raise ValueError 

			if len(received)!=4:

			  raise IndexError
			
			print (Client['ip']+ " "+ str(Client['port'])+ " " +received[2])
			receiveFile(Client, int(received[3]))
			sendBack(Client, language, received[2])

	else:
		raise ValueError


def sendBack(Client, language, filename):
	langFile= open("file_translation.txt", 'r')		
	filename=getTranslation(langFile, filename)
	file=open(filename,"rb")
	size=os.path.getsize(filename)
	print (filename+ " ("+str(size)+" Bytes)")
	message= "TRR f " + filename + " " + str(size) + " "
	Client['socket'].send(message.encode())
	time.sleep(0.005)
	while(size>0):
		buff=file.read(BUFFER_SIZE)
		Client['socket'].send(buff)
		size-=len(buff)
	Client['socket'].send("\n".encode())
	Client['socket'].shutdown(socket.SHUT_WR)



#---------------------------------------------------------------------------------
#							Argument Validation
#---------------------------------------------------------------------------------

def validateArgs(TCS):
	'''validates the arguments given to the program upon runtime'''
	try:
		arguments=sys.argv
		port=59000
		if len(arguments)%2!=0:
			raise ArgumentsError(invalidArgs)

		i=2
		p,n,e=1,1,1
	
		while i<len(arguments):
			if arguments[i]=="-p" and p:
				port= int(arguments[i+1])
				if port not in range(65536):
					raise ValueError
				p=0
			elif arguments[i]=="-n" and n:
				TCS['name']=arguments[i+1]
				n=0
			elif arguments[i]=="-e" and e:
				TCS['port']=int(arguments[i+1])
				if TCS['port'] not in range(65536):
					raise ValueError
				e=0
			else:
				raise InputError (invalidArgs)
			i+=2
		test=socket.gethostbyname(TCS['name'])
		return port
	except ValueError as e:
		sys.exit("port must be an integer between 0-65535")
	except ArgumentsError as error:
		sys.exit(error)
	except IndexError:
		sys.exit(invalidArgs)
	


#---------------------------------------------------------------------------------
#										Main
#---------------------------------------------------------------------------------

def main():
	try:
		language=sys.argv[1]
		TCS={'name':socket.gethostname(),'port':58056}
	
		port=validateArgs(TCS)
		TCS['ip']=socket.gethostbyname(TCS['name'])

		TCP_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		TCP_socket.bind((socket.gethostbyname(socket.gethostname()),port))
		TCP_socket.listen(1)
		Client={}
		RegisterServer(TCS, language,port)
		while(1):
			try:
				Client['socket'] , (Client['ip'], Client['port'])=TCP_socket.accept()
				translate(Client, language,port) 
			except KeyboardInterrupt:
				UnRegisterServer(TCS,language,port)
				sys.exit()
			except FileNotFoundError:
				Client['socket'].send('TRR NTA\n'.encode())
			except:
				traceback.print_exc()
				Client['socket'].send('TRR ERR\n'.encode())

	except socket.error as error:
		sys.exit(error)


main()

