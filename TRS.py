#Translation Server
import socket
import sys
import signal
import os
import time

BUFFER_SIZE=1024

invalidArgs='\nInvalid arguments.\nusage: python3 TRS.py language [-p TRSport] [-n TCSname] [-e TCSport]'
portMsg="port must be an integer between 0-65535"

class ArgumentsError(Exception):
	def __init__(self, message):
		self.message=message


def sendMsg(sock, ipAddress, port, message):
	sock.sendto(message.encode(), (ipAddress, port))
	response=sock.recv(BUFFER_SIZE)
	return (response.decode())



def protocolSyntaxVerification(msg):
	if "  " in msg or msg[-1]!="\n" or msg[0]==" " or " \n" in msg:
		return False
	return True

def protocolSyntaxVerification2(msg):
	if "  " in msg or msg[0]==" " or " \n" in msg:
		return False
	return True

def RegisterServer(TCS, language,port):
	UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#no need to bind anything because the system allready binds sockets that send stuff
	#you only need to bind sockets that receive before sending, which is not the case
	RegMsg="SRG "+ language+ " "+ socket.gethostname()+" "+ str(port)+"\n"
	command=sendMsg(UDP_socket, TCS['ip'], TCS['port'], RegMsg).split()
	UDP_socket.close()

	if command[0]=="SRR":
		if command[1]=="OK":
			print ("Successfully registered Translation Server.")
		elif command[1]=="NOK":
			print ("Registration refused.")
		elif command[1]=="ERR":
			print ("Registration Error.")
			sys.exit()


def UnRegisterServer(TCS, language,port):
	UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

def getTranslation(file, word):
	file.seek(0)
	for line in file:
		trans=line.split()
		if word==trans[0]:

			return trans[1]
	return "NTA"

	#o que acontece quando falha scrubs??


def translateWordList(Client, language, wordlist):
	result=""
	langFile= open(language, 'r')
	for word in wordlist:
		result+=getTranslation(langFile, word)+" "
	result=result.strip()
	print(result+" ("+str(len(result.split()))+")")
	if "NTA" in result:
		message="TRR NTA\n"
	else:
		message="TRR t "+str(len(wordlist))+" "+result+"\n"
	Client['socket'].send(message.encode())


def receiveFile(Client, size):
	file=open("TRSreceived.png","wb")
	buff=""
	print("receiving " +str(size)+" bytes")
	while(size>-1):
		buff=Client['socket'].recv(BUFFER_SIZE)
		file.write(buff)
		size-=len(buff)
	if buff[-1]!=10:
		print(buff[-1])
		Client['socket'].send('TRR ERR\n'.encode())
		return
	print("done")
	file.seek(-1, os.SEEK_END)
	file.truncate()
	file.close()


def translate(Client, language,port):
	#FaltaPasserelle

	received= Client['socket'].recv(BUFFER_SIZE)
	print(socket.gethostbyaddr(Client["ip"])[0]+" "+str(Client["port"])+": "+" ".join((received[3:].decode()).split()))
	if received[:3].decode()=="TRQ":			#variavel auxiliar ao received?
		if received.split()[1].decode()=="t":
			#if not protocolSyntaxVerification(received.decode()):
			#	Msg="Invalid Request\n"
			#	Client['socket'].sendto(Msg.encode(), (ipAddress, port))
			#		return
			received=received.split()
			if int(received[2])!=len(received)-3:
				Client['socket'].send('TRR ERR\n'.encode())
				return
			for i in range(len(received)):
				received[i]=received[i].decode()
			translateWordList(Client, language, received[3:])


		elif received.split()[1].decode()=="f":
			protocolSyntaxVerification2(received.decode())
			received=received.split(b' ',4)   	#nao verificamos se segue o protocolo tipo espaço espaço e \n
			if len(received)!=5:
				Client['socket'].send('TRR ERR\n'.encode())
				return
			for i in range(4):
				received[i]=received[i].decode()
			receiveFile(Client, int(received[3]))
			sendBack(Client, language, received[2])

	else:
		Client['socket'].send('Invalid Request\n'.encode())


def sendBack(Client, language, filename):
	langFile= open(language+"Img", 'r')
	filename=getTranslation(langFile, filename)
	file=open(filename,"rb")
	size=os.path.getsize(filename)
	message= "TRR f " + filename + " " + str(size) + " "
	Client['socket'].send(message.encode())
	print("Sending back "+str(size)+" bytes")
	while(size>0):
		buff=file.read(BUFFER_SIZE)
		Client['socket'].send(buff)
		size-=len(buff)
	print("done")
	Client['socket'].send("\n".encode())
	Client['socket'].shutdown(socket.SHUT_WR)



#---------------------------------------------------------------------------------
#							Argument Validation
#---------------------------------------------------------------------------------

def validateArgs(TCS):
	'''validates the arguments given to the program upon runtime'''

	arguments=sys.argv
	port=59000
	if len(arguments)%2!=0:
		raise ArgumentsError (invalidArgs)

	i=2
	p,n,e=1,1,1
	try:
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
		return port
	except ValueError as e:
		traceback.print_exc()
		print ("port must be an integer between 0-65535")
		sys.exit(-1)
	except:
		raise ArgumentsError(invalidArgs)
	try:
		test=socket.gethostbyname(TCS['name'])
	except:
		traceback.print_exc()
		print("Invalid server name")
		sys.exit(-1)


def main():

	language=sys.argv[1]
	TCS={'name':socket.gethostname(),'port':58056}
	TCS['ip']=socket.gethostbyname(TCS['name'])

	port=validateArgs(TCS)


	TCP_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	TCP_socket.bind((socket.gethostbyname(socket.gethostname()),port))
	TCP_socket.listen(1)
	Client={}
	RegisterServer(TCS, language,port)
	#falta fazer a coisa quando se faz CTRL-C
	while(1):
		try:
			Client['socket'] , (Client['ip'], Client['port'])=TCP_socket.accept()
			translate(Client, language,port)
		except KeyboardInterrupt:
			UnRegisterServer(TCS,language,port)
			sys.exit()


main()
