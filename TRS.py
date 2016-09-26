#Translation Server
import socket
import sys

BUFFER_SIZE=256
TCS_ip=socket.gethostbyname("localhost")
TCS_port=50000


def RegisterServer(language,port):
	UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	UDP_socket.bind(("127.0.0.1", port))

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





def main():
	port=-1
	arguments=sys.argv
	language= arguments[1]

	for i in range(len(arguments)):
		if arguments[i]=="-p":
			port= int(arguments[i+1])


	RegisterServer(language,port)
	







main()
