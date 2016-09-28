#Translation Contact Server
import socket
import sys
BUFFER_SIZE=256

def main():
	port=-1
	arguments=sys.argv
	
	for i in range(len(arguments)):
		if arguments[i]=="-p":
			port= int(arguments[i+1])
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
			Msg="list languages"
			UDP_socket.sendto(Msg.encode(), (Host_Address, Host_Port))
			

		elif command[0]=="SRG":
			print ("SRG")
			OkMsg="SRR OK"
			UDP_socket.sendto(OkMsg.encode(), (Host_Address, Host_Port))
			print("+"+command[1]+" "+command[2]+" "+ command[3])

		





main()