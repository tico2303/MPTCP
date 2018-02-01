# -*- coding: cp1252 -*-
# <PythonProxy.py>
#
# Copyright (c) <2009> <Fábio Domingues - fnds3000 in gmail.com>

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""\
Copyright (c) <2009> <Fábio Domingues - fnds3000 in gmail.com> <MIT Licence>

                  **************************************
                 *** Python Proxy - A Fast HTTP proxy ***
                  **************************************

Neste momento este proxy é um Elie Proxy.

Suporta os métodos HTTP:
 - OPTIONS;
 - GET;
 - HEAD;
 - POST;
 - PUT;
 - DELETE;
 - TRACE;
 - CONENCT.

Suporta:
 - Conexões dos cliente em IPv4 ou IPv6;
 - Conexões ao alvo em IPv4 e IPv6;
 - Conexões todo o tipo de transmissão de dados TCP (CONNECT tunneling),
     p.e. ligações SSL, como é o caso do HTTPS.

A fazer:
 - Verificar se o input vindo do cliente está correcto;
   - Enviar os devidos HTTP erros se não, ou simplesmente quebrar a ligação;
 - Criar um gestor de erros;
 - Criar ficheiro log de erros;
 - Colocar excepções nos sítios onde é previsível a ocorrência de erros,
     p.e.sockets e ficheiros;
 - Rever tudo e melhorar a estrutura do programar e colocar nomes adequados nas
     variáveis e métodos;
 - Comentar o programa decentemente;
 - Doc Strings.

Funcionalidades futuras:
 - Adiconar a funcionalidade de proxy anónimo e transparente;
 - Suportar FTP?.


(!) Atenção o que se segue só tem efeito em conexões não CONNECT, para estas o
 proxy é sempre Elite.

Qual a diferença entre um proxy Elite, Anónimo e Transparente?
 - Um proxy elite é totalmente anónimo, o servidor que o recebe não consegue ter
     conhecimento da existência do proxy e não recebe o endereço IP do cliente;
 - Quando é usado um proxy anónimo o servidor sabe que o cliente está a usar um
     proxy mas não sabe o endereço IP do cliente;
     É enviado o cabeçalho HTTP "Proxy-agent".
 - Um proxy transparente fornece ao servidor o IP do cliente e um informação que
     se está a usar um proxy.
     São enviados os cabeçalhos HTTP "Proxy-agent" e "HTTP_X_FORWARDED_FOR".

"""

import socket, thread, select, sys
import subprocess as sp
import re
import math

__version__ = '0.1.0 Draft 1'
BUFLEN = 8192
VERSION = 'Python Proxy/'+__version__
HTTPVER = 'HTTP/1.1'

CONTENT_PAT = '(Content-Length:) (\d*)'
class ConnectionHandler:
    def __init__(self, connection, address, timeout):
        self.client = connection
        self.client_buffer = ''
        self.timeout = timeout
        self.content_length = None
        self.host = None

        #print the request and it extracts the protocol and path
        self.method, self.path, self.protocol = self.get_base_header()

        if self.method=='CONNECT':
            self.method_CONNECT()

        #handle the GET request
        elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT',
                             'DELETE', 'TRACE'):
            self.method_others()

        self.client.close()
        self.target.close()
        self.target2.close()


    def get_content_length(self):
        i = self.path.find('/')
        path = self.path[i:]
        s = "HEAD " + path + " " + self.protocol + "\r\n"
        s += "Host: " + self.host + "\r\n\r\n"
        print "Sending Request For Content Length...."
        print s
        self.target.send(s)
        data = self.target.recv(BUFLEN)
        print data
        return re.search(r'Content-Length: \d+', data).group(0).split(" ")[1]

        #check accept_range.. bytes means OK to split

    def get_base_header(self):
        while 1:
            self.client_buffer += self.client.recv(BUFLEN)
            end = self.client_buffer.find('\n')
            if end!=-1:
                break

        #print '%s'%self.client_buffer[:end]#debug
        data = (self.client_buffer[:end+1]).split()
        self.client_buffer = self.client_buffer[end+1:]
        return data

    def method_CONNECT(self):
        self._connect_target(self.path)
        self.client.send(HTTPVER+' 200 Connection established\n'+
                         'Proxy-agent: %s\n\n'%VERSION)
        self.client_buffer = ''
        self._read_write()

    def create_range(self,_from , _to):
        # print("from: ", _from)
        # print("to: ", _to)
        byte_range = "Range: bytes={}-{}".format(_from, _to)
        return byte_range

    def get_range(self,percent):
        # creates range of bits for range using a percent of content_length
        print("percent: ", percent)
        first = percent * float(int(self.content_length))
        first = int(math.floor(first))
        #print("first: ", first)
        return first

    #forward the packet to its final destination
    def method_others(self):
        self.path = self.path[7:]
        i = self.path.find('/')
        self.host = self.path[:i]
        path = self.path[i:]
        self._connect_target(self.host)

        if self.method == 'GET':
            self.content_length = self.get_content_length()
            data1 = ""
            data2 = ""

            percent = 0.5
            byte_range = self.get_range(percent)
            print byte_range
            print type(byte_range)
            print self.content_length
            print type(self.content_length)
            data1 = self.get(self.target2, 0,byte_range)
            raw_input("Press Any Key To Continue....")
            end = str(int(self.content_length) - 1)
            data2 = self.get(self.target, byte_range+1, end)
            #data2 = self.get(self.target, byte_range, end+"/"+self.content_length)
            data = data1 + data2
            print "Merged Data Length: " , sys.getsizeof(data)
            raw_input("Press Any Key To Continue....")



        else:
            self.target.send('%s %s %s\n%s\n'%(self.method, path, self.protocol , self.client_buffer))
            self.client_buffer = ''

            #start the read/write function
            self._read_write()

    def _connect_target(self, host):
        i = host.find(':')
        if i!=-1:
            port = int(host[i+1:])
            host = host[:i]
        else:
            #listen on port 80
            port = 80

        print "Setting Up Connection Target 1...."
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(soc_family)
        self.target.connect(address)

        print "Setting Up Connection Target 2...."
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        self.target2 = socket.socket(soc_family)
        self.target2.connect(address)

        print "Success"
    

    def read(self, socs):
        time_out_max = self.timeout/3
        read = 1
        count = 0
        r = ''
        print "SOCS: ", socs
        while read:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                read = 0
            if recv:
                for in_ in recv:
                    data = in_.recv(10000)
                    if data:
                        r += data
                        count = 0
            if count == time_out_max:
                read = 0

        return r

        pass

    def write(self):
        pass

    def get(self, target, start_byte, end_byte):
        data1 = ''
        i = self.path.find('/')
        path = self.path[i:]
        print("Inside The Get Request\n")

        print('%s %s %s\n%s\n'%(self.method, path, self.protocol,self.create_range(start_byte,end_byte))+self.client_buffer)
        target.send('%s %s %s\n%s\n'%(self.method, path, self.protocol,self.create_range(start_byte,end_byte))+self.client_buffer)
        print type(sys.getsizeof("as;dlfkja;lsdkjf"))
        while(sys.getsizeof(data1) < (int(end_byte) - int(start_byte))):
            data1 += target.recv(10000)
        print "Length of Data : ", sys.getsizeof(data1)
        i = data1.find('\r\n\r\n') + 8
        return data1[i:]


    #"revolving door" to re-direct the packets in the right direction
    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target, self.target2]
        count = 0
        data1 = None
        data2 = None

        while 1:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)
                    print "Recieved, data1 is: ", data1
                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
                        out.send(data)
                        count = 0
            if count == time_out_max:
                break

#start the proxy server and listen for connections on port 8080
def start_server(host='localhost', port=8080, IPv6=False, timeout=60,
                  handler=ConnectionHandler):
    if IPv6==True:
        soc_type=socket.AF_INET6
    else:
        soc_type=socket.AF_INET
    soc = socket.socket(soc_type)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    soc.bind((host, port))
    print "Serving on %s:%d."%(host, port)#debug
    soc.listen(0)
    while 1:
        thread.start_new_thread(handler, soc.accept()+(timeout,))

if __name__ == '__main__':
    start_server()
