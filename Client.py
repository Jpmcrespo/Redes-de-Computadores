#Client
import socket
import sys
import os

BUFFER_SIZE=1024
ListMSG="ULQ\n"
invalidArgs='\nInvalid arguments.\nusage: python3 Client.py [-n TCSname] [-p TCSport]'

class ArgumentsError(Exception):
	def __init__(self, message):
		self.message=message


def sendMsg(sock, ipAddress, port, message):
	sock.sendto(message.encode(), (ipAddress, port))
	response=sock.recv(BUFFER_SIZE)
	return (response.decode())


def requestTRS(TRS, word):
	TRS['socket'].connect((TRS['ip'],TRS['port']))
	message = "TRQ t "+str(len(word.split()))+" "+ word+ "\n"
	return sendMsg(TRS['socket'],TRS['ip'],TRS['port'], message)


def requestFile(TRS,filename):
	file=open(filename,"rb")
	size=os.path.getsize(filename)

	TRS['socket'].connect((TRS['ip'],TRS['port']))
	message= "TRQ f " + filename + " " + str(size) + " "

	TRS['socket'].sendto(message.encode(), (TRS['ip'], TRS['port']))
	print(str(size)+" bytes to Transmit")	
	while(size>0):
		buff=file.read(BUFFER_SIZE)
		TRS['socket'].send(buff)
		size-=len(buff)
	print("done")



def receiveFile(TRS, name, size, extradata):
	file=open(name.rsplit(".",1)[0]+"RECEIVED"+"."+name.rsplit(".",1)[1],"wb")

	print("receiving " +str(size)+" bytes")
	file.write(extradata)
	while(size>0):
		buff=TRS['socket'].recv(BUFFER_SIZE)
		file.write(buff)
		size-=BUFFER_SIZE
	print("done")
	print("END OF FILE TRANSLATION")



def receiveTransFile(TRS):
	received= TRS['socket'].recv(BUFFER_SIZE)
	print (received)
	received=received.split(b' ',4)
	for i in range(4):
		received[i]=received[i].decode()

	if received[0]=="TRR":			#outros casos, try except
		if received[1]=="f":
			extradata=received[-1]
			receiveFile(TRS, received[2], int(received[3]), extradata)	

		



def updateLanguageList(TCS):
	lst=sendMsg(TCS['socket'], socket.gethostbyname(TCS['name']), TCS['port'], ListMSG).split()
	languages=[]
	i=1
	if lst[0]=="ULR" and lst[1]!="EOF" and lst[1]!="ERR":
		languages=lst[2:]
		for lang in languages:
			print (str(i)+"- "+lang)
			i+=1
	else:
		print (lst[0] + " "+ lst[1])

	return languages


def requestTRSCred(TCS, language):
	Msg="UNQ "+language+ "\n"
	cred=sendMsg(TCS['socket'], socket.gethostbyname(TCS['name']), TCS['port'], Msg).split()
	print (cred)
	#return {'ip': cred[2], 'port' : int(cred[3])}
	return {'ip': cred[1], 'port' : int(cred[2])}


def validateArgs(TCS):
	n,p=1,1
	arguments=sys.argv
	try:
		for i in range(1,len(arguments),2):
			if arguments[i]=="-n" and n:
				TCS['name']= arguments[i+1]
				n=0
			elif arguments[i]=='-p' and p:
				TCS['port']= int(arguments[i+1])    #Falta ver se é valido o numero
				p=0
			else:
				raise ArgumentsError(invalidArgs)
	except ValueError as e:
		traceback.print_exc()
		print ("port must be an integer between 0-65535")
		sys.exit(-1)
	except:
		raise ArgumentsError(invalidArgs)





def main():
	words=""
	TCS={'name':"localhost", "port": 58056, "socket":socket.socket(socket.AF_INET, socket.SOCK_DGRAM)}
	
	validateArgs(TCS)

	languages=[]
	#print (TCS['name'], TCS['port'])

	while(True):
		command= input(">").split()
		if command[0]=="list":
			languages=updateLanguageList(TCS)

		elif command[0]=="request":

			TRS=requestTRSCred(TCS, languages[int(command[1])-1])
			TRS['socket']=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

			if command[2]=="t":
				response=requestTRS(TRS, " ".join(command[3:]))
				print (response)

			elif command[2]=="f":
				requestFile(TRS,command[3])
				receiveTransFile(TRS)

				
		elif command[0]=="exit":
			return
		else:
			print ("command not found")







main()
