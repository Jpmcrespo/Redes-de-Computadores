#Translation Server
import socket
import sys

BUFFER_SIZE=256
TCS_ip=socket.gethostbyname("lab10p8")
TCS_port=49000


def RegisterServer(language,port):
	UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	UDP_socket.bind((socket.gethostbyname(socket.gethostname()), port))

	RegMsg="SRG "+ language+ " "+ socket.gethostbyaddr("127.0.0.1")[0]+" "+ str(port)
	UDP_socket.sendto(RegMsg.encode(), (TCS_ip, TCS_port))
	

	data= UDP_socket.recvfrom(BUFFER_SIZE)
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
	TCP_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	TCP_socket.bind((socket.gethostbyname(socket.gethostname()),port))
	TCP_socket.listen(1)
	connection=TCP_socket.accept()
	print("Accepted")
	received= TCP_socket.recv(BUFFER_SIZE)
	received=received.split()
	if received[0]=="TRQ":
		if received[1]=="t":
			for word in received[3:]:
				result+=getTranslation(language, word)+" "
			result=result.strip()
			connection.send("TRR t "+received[2]+" "+result)






def getTranslation(language, word):
	file= open(language, 'r')
	for line in file:
		trans=line.split()
		if word==trans[0]:
			return trans[1]
	#o que acontece quando falha scrubs??





def main():
	port=-1
	arguments=sys.argv
	language= arguments[1]

	for i in range(len(arguments)):
		if arguments[i]=="-p":
			port= int(arguments[i+1])
	
	RegisterServer(language,port)
	translate(language,port)

	


	







main()
