#Client
import socket
import sys

UDP_IP="127.0.0.1"
BUFFER_SIZE=256

def sendMsg(sock, ipAddress, port, message):


	sock.sendto(message.encode(), (ipAddress, port))
	response=sock.recv(BUFFER_SIZE)
	print (response.decode())
	return
	
def requestTRS(sock, ipAddress, port, word):
	sock.connect((ipAddress,port))
	sock.send("TRQ t "+str(len(word.split))+" "+ word )




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
	TCS_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	TRS_socket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	while(True):
		command= input(">").split()
		if command[0]=="list":
			sendMsg(TCS_socket, socket.gethostbyname(name), int(port), "ULQ")

		elif command[0]=="request":
			requestTRS(TRS_socket,"127.0.0.1",58000, command[3])
		elif command[0]=="exit":
			return
		else:
			print ("command not found")







main()