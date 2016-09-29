#Client
import socket
import sys

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
	words=""
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

	LanguageList=[]
	print (name, port)
	TCS_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	TRS_socket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	while(True):
		command= input(">").split()
		if command[0]=="list":
			Msg="ULQ"
			lst=sendMsg(TCS_socket, socket.gethostbyname(name), int(port), Msg).split()
			i=1
			if lst[0]=="ULR" and lst[1]!="EOF" and lst[1]!="ERR":
				languages=lst[2:]
				for lang in languages:
					LanguageList+=[lang]
					print (str(i)+"- "+lang)
					i+=1


			else:
				print (lst[0] + " "+ lst[1])



		elif command[0]=="request":
			if command[2]=="t":
				Msg="UNQ "+ LanguageList[int(command[1])-1]
				TRS_credentials=sendMsg(TCS_socket, socket.gethostbyname(name), int(port), Msg).split()
				TRS_IP=TRS_credentials[2]
				TRS_port=int(TRS_credentials[3])
				for word in command[3:]:
					words+=word+" "
				words=words.strip()
				requestTRS(TRS_socket,TRS_IP,TRS_port, words)
		elif command[0]=="exit":
			return
		else:
			print ("command not found")







main()
