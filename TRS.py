#Translation Server
import socket
import sys

BUFFER_SIZE=1024	
TCS_ip=socket.gethostbyname(socket.gethostname())
TCS_port=58056
invalidArgs='\nInvalid arguments.\nusage: python3 TRS.py language [-p TRSport] [-n TCSname] [-e TCSport]'


class ArgumentsError(Exception):
	def __init__(self, message):
		self.message=message



def RegisterServer(language,port):
	#passerelle?
	UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	UDP_socket.bind((socket.gethostbyname(socket.gethostname()), port))

	RegMsg="SRG "+ language+ " "+ socket.gethostname()+" "+ str(port)
	UDP_socket.sendto(RegMsg.encode(), (TCS_ip, TCS_port))


	data= UDP_socket.recvfrom(BUFFER_SIZE)
	UDP_socket.close()
	command= data[0].decode().split()
	Host_Address= data[1][0]
	Host_Port=data[1][1]
	if command[0]=="SRR":
		if command[1]=="OK":
			print ("Successfully registered Translation Server.")
		elif command[1]=="NOK":
			print ("Registration refused.")
		elif command[1]=="ERR":
			print ("Registration Error.")
			sys.exit()


def translate(language,port):
	#FaltaPasserelle

	result=""
	TCP_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	TCP_socket.bind((socket.gethostbyname(socket.gethostname()),port))
	TCP_socket.listen(1)
	connection , address=TCP_socket.accept()
	print("Accepted")
	received= connection.recv(BUFFER_SIZE)
	received=received.split()
	print ("LENGTH:" + str(len(received)))
	received[0]=received[0].decode()
	received[1]=received[1].decode()
	received[2]=received[2].decode()
	received[3]=received[3].decode()
	if received[0]=="TRQ":			#outros casos
		if received[1]=="t":

			for word in received[3:]:
				result+=getTranslation(language, word)+" "
			result=result.strip()
			message="TRR t "+received[2]+" "+result
			connection.send(message.encode())
		elif received[1]=="f":
			print("LETS GO BABY")
			file=open("popo.png","wb")
			size=int(received[3])
			print("receiving " +str(size)+" bytes")
			file.write(extradata)
			size-=1000
			while(size>0):
				print(".")
				buff=connection.recv(BUFFER_SIZE)
				file.write(buff)
				size-=1024
			print("done")









def getTranslation(language, word):
	file= open(language, 'r')
	for line in file:
		trans=line.split()
		if word==trans[0]:
			return trans[1]
	#o que acontece quando falha scrubs??





def main():
	port=59000
	TCSname="localhost"

	#meter TCS em dicionario e validar os argumentos

	arguments=sys.argv
	language= arguments[1]
	if len(arguments)%2!=0:
		raise ArgumentsError (invalidArgs)

	i=2
	p,n,e=1,1,1
	while i<len(arguments):
		if arguments[i]=="-p" and p:
			port= int(arguments[i+1])
			p=0
		elif arguments[i]=="-n" and n:
			TCS_name=arguments[i+1]
			n=0
		elif arguments[i]=="-e" and e:
			TCS_port=arguments[i+1]
			e=0
		else:
			raise InputError (invalidArgs)
		i+=2

	RegisterServer(language,port)

	#while

	translate(language,port)












main()
