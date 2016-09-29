#Translation Contact Server
import socket
import sys
BUFFER_SIZE=256


def main():
	port=58056
	arguments=sys.argv
	
	if len(arguments)>1:
		if arguments[1]=="-p":
			port=int(arguments[2])


	languageList={}
	UDP_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	UDP_socket.bind((socket.gethostbyname(socket.gethostname()), port))

	while(True):

		data= UDP_socket.recvfrom(BUFFER_SIZE)
		command= data[0].decode().split()
		Host_Address= data[1][0]
		Host_Port=data[1][1]
		print (command)
		if command[0]=="ULQ":
			print ("List request: "+socket.gethostbyaddr(Host_Address)[0]+ " "+ str(Host_Port))
			Msg= "ULR "+str(len(languageList))
			for entry in languageList:
				Msg+=" " + entry
			UDP_socket.sendto(Msg.encode(), (Host_Address, Host_Port))
			

		elif command[0]=="SRG":
			print ("SRG")
			Msg="SRR"
			try:
				if command[1] in languageList:
					Msg+=" NOK"
				else:
					Msg+=" OK"
					print("+"+command[1]+" "+command[2]+" "+ command[3])
				UDP_socket.sendto(Msg.encode(), (Host_Address, Host_Port))
			except:
				print ("hi")

		





main()