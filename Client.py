#Client
import socket
import sys

UDP_IP="127.0.0.1"
TRS_IP=socket.gethostbyname(socket.gethostname())
BUFFER_SIZE=256
invalidArgs='\nInvalid arguments.\nusage: python3 Client.py [-n TCSname] [-p TCSport]'

class ArgumentsError(Exception):
	def __init__(self, message):
		self.message=message

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
	name="localhost"
	port=58056
	arguments=sys.argv

	n,p=1,1
	for i in range(1,len(arguments),2):
		if arguments[i]=="-n" and n:
			name= arguments[i+1]
			n=0
		elif arguments[i]=='-p' and p:
			port= arguments[i+1]
			n=0
		else:
			raise ArgumentsError(invalidArgs)
	print (name, port)
	TCS_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	TRS_socket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	while(True):
		command= input(">").split()
		if command[0]=="list":
			Msg="ULQ"
			lst=sendMsg(TCS_socket, socket.gethostbyname(socket.gethostname()), int(port), Msg).split()
			i=1
			if lst[0]=="ULR" and lst[1]!="EOF" and lst[1]!="ERR":
				languages=lst[2:]
				for lang in languages:
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
