# -*- coding: cp1252 -*-
# <PythonProxy.py>
#
# Copyright (c) <2009> <F�bio Domingues - fnds3000 in gmail.com>

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
Copyright (c) <2009> <F�bio Domingues - fnds3000 in gmail.com> <MIT Licence>

                  **************************************
                 *** Python Proxy - A Fast HTTP proxy ***
                  **************************************

Neste momento este proxy � um Elie Proxy.

Suporta os m�todos HTTP:
 - OPTIONS;
 - GET;
 - HEAD;
 - POST;
 - PUT;
 - DELETE;
 - TRACE;
 - CONENCT.

Suporta:
 - Conex�es dos cliente em IPv4 ou IPv6;
 - Conex�es ao alvo em IPv4 e IPv6;
 - Conex�es todo o tipo de transmiss�o de dados TCP (CONNECT tunneling),
     p.e. liga��es SSL, como � o caso do HTTPS.

A fazer:
 - Verificar se o input vindo do cliente est� correcto;
   - Enviar os devidos HTTP erros se n�o, ou simplesmente quebrar a liga��o;
 - Criar um gestor de erros;
 - Criar ficheiro log de erros;
 - Colocar excep��es nos s�tios onde � previs�vel a ocorr�ncia de erros,
     p.e.sockets e ficheiros;
 - Rever tudo e melhorar a estrutura do programar e colocar nomes adequados nas
     vari�veis e m�todos;
 - Comentar o programa decentemente;
 - Doc Strings.

Funcionalidades futuras:
 - Adiconar a funcionalidade de proxy an�nimo e transparente;
 - Suportar FTP?.


(!) Aten��o o que se segue s� tem efeito em conex�es n�o CONNECT, para estas o
 proxy � sempre Elite.

Qual a diferen�a entre um proxy Elite, An�nimo e Transparente?
 - Um proxy elite � totalmente an�nimo, o servidor que o recebe n�o consegue ter
     conhecimento da exist�ncia do proxy e n�o recebe o endere�o IP do cliente;
 - Quando � usado um proxy an�nimo o servidor sabe que o cliente est� a usar um
     proxy mas n�o sabe o endere�o IP do cliente;
     � enviado o cabe�alho HTTP "Proxy-agent".
 - Um proxy transparente fornece ao servidor o IP do cliente e um informa��o que
     se est� a usar um proxy.
     S�o enviados os cabe�alhos HTTP "Proxy-agent" e "HTTP_X_FORWARDED_FOR".

"""

import socket, thread, select
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

        #print the request and it extracts the protocol and path
        self.method, self.path, self.protocol = self.get_base_header()
        self.get_content_length()

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
        self.target.send('%s %s %s\n%s\n'%('HEAD'+self.method, path, self.protocol)+self.client_buffer)
        
        data = self.target.recv(BUFLEN)
        print("data: ", data)
        #check accept_range.. bytes means OK to split

    def get_base_header(self):
        while 1:
            self.client_buffer += self.client.recv(BUFLEN)
            end = self.client_buffer.find('\n')
            if end!=-1:
                break

        #print the request
        print("get_base_header::self.client_buffer: ", self.client_buffer)
        #self.content_length = self.get_content_length()

        print '%s'%self.client_buffer[:end]#debug
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
        print("percent: ", type(percent))
        first = percent * float(int(self.content_length))
        first = int(math.floor(first))
        #print("first: ", first)
        return first

    #forward the packet to its final destination
    def method_others(self):
        self.path = self.path[7:]
        print("self.path: ", self.path)
        i = self.path.find('/')
        host = self.path[:i]
        path = self.path[i:]
        print("path: ", path)
        self._connect_target(host)

        #TO DO: first find out the Content-Length by sending a RANGE request

        # print("content_length: ", self.get_content_length())
        # print("protocol: ", self.protocol)
        # print("method: ", self.method)
        # print("client_buffer: ", self.client_buffer)
        percent = 0.3
        range1 = self.get_range(percent)
        print(self.create_range(0,range1))
        print(self.create_range(range1+1,self.content_length))

        #### Target 1
        print("*"*10)
        print('%s %s %s\n%s\n'%(self.method, path, self.protocol,self.create_range(0,range1))+
                         self.client_buffer)

        self.target.send('%s %s %s\n%s\n'%(self.method, path, self.protocol,
                         self.create_range(0,range1))+self.client_buffer)

        #### Target 2
        #TO DO: need to send another request to "target2" that GETs a different range of bytes
        print("*"*10)
        print('%s %s %s\n%s\n'%(self.method, path, self.protocol,self.create_range(range1+1, self.content_length))+
                         self.client_buffer)

        self.target2.send('%s %s %s\n%s\n'%(self.method, path, self.protocol,
                         self.create_range(range1+1, self.content_length))+self.client_buffer)

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
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        (soc_family2, _, _, _, address) = socket.getaddrinfo(host, 9000)[0]
        self.target = socket.socket(soc_family)
        self.target2 = socket.socket(soc_family2)
        self.target.connect(address)
        self.target2.connect(address)

    #"revolving door" to re-direct the packets in the right direction
    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target, self.target2]
        count = 0
        while 1:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)
                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
                        #TO DO: Check if it's response to the RANGE request and extract the Content-Length


                        #TO DO: merge the data from both interfaces into one big data, if we are receiving

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
