import sys
import os
import subprocess as sp
import socket
import requests
from time import sleep

def get_content_length(url):
    proc = sp.Popen(["curl","-I",url], stdout=sp.PIPE)
    proc2 = sp.Popen(["grep","Content-Length"],stdin=proc.stdout, stdout=sp.PIPE)
    (output, err) = proc2.communicate()

    # print(output.split(":")[1])
    content_length = output.split(":")[1]
    return content_length

def send_info_to_proxy():
    host = 'localhost'
    port = 8080
    r = requests.post('http://localhost:8080', "This is the data that i sent")

if "__main__" == __name__:
    # print sys.argv[1]
    # url = sys.argv[1]
    # print(get_content_length(url))
    while 1:
        send_info_to_proxy()
        sleep(5)

