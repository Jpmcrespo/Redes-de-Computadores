#Translation Contact Server
import socket
import sys
import traceback
BUFFER_SIZE=1024	
invalidArgs='\nInvalid arguments.\nusage: python3 TCS.py [-p TCSport]'
portMsg="port must be an integer between 0-65535"


class ArgumentsError(Exception):
	def __init__(self, message):
		self.message=message

def sendList(sock, ipAddress, port, lst):
	print ("List request: "+socket.gethostbyaddr(ipAddress)[0]+ " "+ str(port))
	Msg= "ULR "+str(len(lst))
	for entry in lst:
		Msg+=" " + entry
	sock.sendto(Msg.encode(), (ipAddress, port))



def RegisterServer(language, name, port, LanguageList ):
	Msg="SRR"
	if language in LanguageList:
		Msg+=" NOK"
	else:
		Msg+=" OK"
		print("+"+language+" "+name+" "+port)
		LanguageList[language]=[name,port]
	return Msg
	


def validateArgs():
	arguments=sys.argv
	port=58056
	if len(arguments)>3:
		raise ArgumentsError(invalidArgs)

	try:
		if len(arguments)>1:
			if arguments[1]=="-p":
				port=int(arguments[2])  
				return port
			raise ArgumentsError(invalidArgs)
	except ValueError as e:
		traceback.print_exc()
		print (portMsg)
		sys.exit(-1)
	except:
		raise ArgumentsError(invalidArgs)
	




def main():
	port=validateArgs()
		

	LanguageList={}
	UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	UDP_socket.bind((socket.gethostbyname(socket.gethostname()), port))

	while(True):
		#passerelle pah isto ta mm horrivel vv
		command,(Host_Address,Host_Port)= UDP_socket.recvfrom(BUFFER_SIZE)
		command= command.decode().split()

		print (command)
		if command[0]=="ULQ":

			sendList(UDP_socket, Host_Address, Host_Port, LanguageList)
			
		elif command[0]=="UNQ":
			Lang, name, port= command[1], LanguageList[command[1]][0], LanguageList[command[1]][1]
			
			Msg="UNR "+ Lang + " " + name + " " + port
			UDP_socket.sendto(Msg.encode(), (Host_Address, Host_Port))

		elif command[0]=="SRG":

			try:
				Msg=RegisterServer(command[1], command[2], command[3], LanguageList)
			except Exception:
				Msg="SRR ERR"
			finally:
				UDP_socket.sendto(Msg.encode(), (Host_Address, Host_Port))







main()
