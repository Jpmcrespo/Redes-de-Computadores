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

#---------------------------------------------------------------------------------
#							   		List operation
#---------------------------------------------------------------------------------

def sendList(sock, ipAddress, port, lst):
	'''sends the list of available languages to the Client'''
	print ("List request: "+socket.gethostbyaddr(ipAddress)[0]+ " "+ str(port))
	print(" ".join(lst.keys()))
	if len(lst)==0:
		Msg='ULR EOF\n'
	else:
		Msg= "ULR "+str(len(lst))+ " "
		Msg+=" ".join(lst)+ "\n"


	sock.sendto(Msg.encode(), (ipAddress, port))

#---------------------------------------------------------------------------------
#							   TRServer Operations
#---------------------------------------------------------------------------------

def RegisterServer(language, name, port, LanguageList ):
	'''registers a TRS in LanguageList to let TCS know that a new language is available for translation'''

	Msg="SRR"
	if language in LanguageList:
		Msg+=" NOK\n"
	else:
		Msg+=" OK\n"
		print("+"+language+" "+name+" "+port)
		LanguageList[language]=[name,port]
	return Msg

def UnRegisterServer(language, name, port, LanguageList ):
	'''unregisters a TRS in LanguageList to let TCS know that the specified language is not available for translation anymore'''

	Msg="SUR "
	if language in LanguageList:
		Msg+="OK\n"
		print("-"+language+" "+name+" "+port)
		del LanguageList[language]
	else:
		Msg+="NOK\n"

	return Msg

#---------------------------------------------------------------------------------
#							Argument Validation
#---------------------------------------------------------------------------------

def validateArgs():
	'''validates the arguments given to the program upon runtime'''

	arguments=sys.argv
	port=58056
	if len(arguments)>3:
		raise ArgumentsError(invalidArgs)

	try:
		if len(arguments)>2:
			if arguments[1]=="-p":
				port=int(arguments[2])
				if port not in range(65536):
					raise ValueError
				return port
			raise ArgumentsError(invalidArgs)
		else:
			return port
	except ValueError as e:
		traceback.print_exc()
		print (portMsg)
		sys.exit(-1)
	except:
		raise ArgumentsError(invalidArgs)
	

#---------------------------------------------------------------------------------
#							Protocol Syntax Verification
#---------------------------------------------------------------------------------

def protocolSyntaxVerification(msg):
	if "  " in msg or msg[-1]!="\n" or msg[0]==" " or " \n" in msg:
		return False
	return True



def sendTRScred(sock, language, LanguageList, Host_Address,Host_Port):
	if language not in LanguageList:
		Msg= "UNR EOF\n"
	else:
		name, port= LanguageList[language][0], LanguageList[language][1]
		Msg="UNR "+ socket.gethostbyname(name) + " " + port+"\n"
	sock.sendto(Msg.encode(), (Host_Address, Host_Port))


#---------------------------------------------------------------------------------
#										Main
#---------------------------------------------------------------------------------

def main():
	port=validateArgs()

	LanguageList={}
	UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	UDP_socket.bind((socket.gethostbyname(socket.gethostname()), port))

	while(True):
		#passerelle pah isto ta mm horrivel vv
		command,(Host_Address,Host_Port)= UDP_socket.recvfrom(BUFFER_SIZE)    #DICIONARIO
		command= command.decode()
		if not protocolSyntaxVerification(command):
			Msg="Invalid Request\n"
			UDP_socket.sendto(Msg.encode(), (Host_Address,Host_Port))
			continue
		command=command.split()
		if command[0]=="ULQ":

			if len(command)==1:
				sendList(UDP_socket, Host_Address, Host_Port, LanguageList)
			else:
				UDP_socket.sendto("ULR ERR\n".encode(), (Host_Address, Host_Port))

		elif command[0]=="UNQ":

			if len(command)==2:
				Lang=command[1]
				sendTRScred(UDP_socket, Lang, LanguageList, Host_Address,Host_Port)
			else:
				UDP_socket.sendto("UNR ERR\n".encode(), (Host_Address, Host_Port))


		elif command[0]=="SRG":

			try:
				Lang, name, port=command[1], command[2], command[3]
				Msg=RegisterServer(Lang, name, port, LanguageList)
			except Exception:
				Msg="SRR ERR\n"
			finally:
				UDP_socket.sendto(Msg.encode(), (Host_Address, Host_Port))

		elif command[0]=="SUN":

			try:
				Lang, name, port=command[1], command[2], command[3]
				Msg=UnRegisterServer(Lang, name, port, LanguageList)
			except Exception:
				Msg="SUR ERR\n"
			finally:
				UDP_socket.sendto(Msg.encode(), (Host_Address, Host_Port))
		else:
			Msg="Invalid Request\n"
			UDP_socket.sendto(Msg.encode(), (Host_Address,Host_Port))






main()
