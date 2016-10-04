#Translation Server
import socket
import sys
import signal
import os

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


def RegisterServer(TCS, language,port):
	UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#no need to bind anything because the system allready binds sockets that send stuff
	#you only need to bind sockets that receive before sending, which is not the case
	RegMsg="SRG "+ language+ " "+ socket.gethostname()+" "+ str(port)
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
	RegMsg="SUN "+ language+ " "+ socket.gethostname()+" "+ str(port)
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
			print (word, trans[1])
			return trans[1]

	#o que acontece quando falha scrubs??


def translateWordList(Client, language, wordlist):
	result=""
	langFile= open(language, 'r')
	print (wordlist)
	for word in wordlist:	
		result+=getTranslation(langFile, word)+" "
	result=result.strip()
	message="TRR t "+str(len(wordlist))+" "+result
	Client['socket'].send(message.encode())


def receiveFile(Client, size, extradata):
	file=open("TRSreceived.png","wb")

	print("receiving " +str(size)+" bytes")
	file.write(extradata)
	while(size>0):
		buff=Client['socket'].recv(BUFFER_SIZE)
		file.write(buff)
		size-=BUFFER_SIZE
	print("done")





def translate(Client, language,port):
	#FaltaPasserelle
	
	received= Client['socket'].recv(BUFFER_SIZE)
	
	#passerelle - funcao nova para os \n's e splits e espaço-espaço

	print (received.decode()[4])

	if received[:3].decode()=="TRQ":			#outros casos, try except
		if received.decode()[4]=="t":
			received=received.split()
			for i in range(len(received)):
				received[i]=received[i].decode()
			translateWordList(Client, language, received[3:])

			

		elif received.decode()[4]=="f":
			received=received.split(b' ',4)
			for i in range(4):
				received[i]=received[i].decode()
			extradata=received[-1]
			receiveFile(Client, int(received[3]), extradata)
			sendBack(Client, language, received[2])
			






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
		size-=BUFFER_SIZE
	print("done")






def validateArgs(TCS):
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
				p=0
			elif arguments[i]=="-n" and n:
				TCS['name']=arguments[i+1]
				n=0
			elif arguments[i]=="-e" and e:
				TCS['port']=arguments[i+1]
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
