#Client
import socket
import sys

UDP_IP="127.0.0.1"
BUFFER_SIZE=256

def commandList(name, port):

	Message="ULQ"
	TCS_ip=socket.gethostbyname(name)

	TCS_port=port
	TCS_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	TCS_socket.sendto(Message.encode(), (TCS_ip, TCS_port))

	TCS_response=TCS_socket.recv(BUFFER_SIZE)

	print (TCS_response)
	return
	




def main():
	name=""
	port=-1
	arguments=sys.argv
	for i in range(len(arguments)):
		if arguments[i]=="-n":
			name= arguments[i+1]
		elif arguments[i]=='-p':
			port= arguments[i+1]
		
	#print ("name: "+name+ " port: "+port )
	while(True):
		command= input(">")
		if command=="list":
			print ("list")
			commandList(name, int(port))

		elif command=="request":
			print ("request")
		elif command=="exit":
			print ("exit")
			return
		else:
			print ("command not found")







main()