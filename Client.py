#Client
import socket
import sys

UDP_IP="127.0.0.1"
TRS_IP=socket.gethostbyname(socket.gethostname())
BUFFER_SIZE=256

def sendMsg(sock, ipAddress, port, message):


	sock.sendto(message.encode(), (ipAddress, port))
	response=sock.recv(BUFFER_SIZE)
	return (response.decode())

	
def requestTRS(sock, ipAddress, port, word):
	sock.connect((ipAddress,port))
	message = "TRQ t "+str(len(word.split()))+" "+ word 
	sock.send(message.encode())
	response=sock.recv(BUFFER_SIZE)
	print(response.decode())




def main():
	name=""
	port=-1
	arguments=sys.argv
	for i in range(len(arguments)):
		if arguments[i]=="-n":
			name= arguments[i+1]
		elif arguments[i]=='-p':
			port= arguments[i+1]
		
	TCS_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	TRS_socket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	while(True):
		command= input(">").split()
		if command[0]=="list":
			Msg="ULQ\n"
			lst=sendMsg(TCS_socket, socket.gethostbyname(name), int(port), Msg).split()
			i=1
			if lst[0]=="ULR" and lst[1]!="EOF" and lst[1]!="ERR":
				for lang in lst[2:]:
					print (str(i)+"- "+lang)
					i+=1
			else:
				print (lst[0] + " "+ lst[1])



		elif command[0]=="request":
			requestTRS(TRS_socket,TRS_IP,58001, command[3])
		elif command[0]=="exit":
			return
		else:
			print ("command not found")







main()