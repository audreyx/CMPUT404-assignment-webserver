# coding: utf-8

import SocketServer, os, sys

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.2
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved



# Copyright 2015 (Audrey) Xuefeng Li
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.2



# http://docs.python.org/2/library/socketserver.html
# run: python freetests.py
# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):

    # Set by receive_request()
    ## e.g. request_msg = "GET / HTTP/1.1..."
    request_msg = ""      
    
    # Set by parse_request()
    ## e.g. request_type = "GET"
    ## e.g. request_source = "/deep"
    ## e.g. content_type = "css"
    request_type = ""    
    request_source = ""   
    content_type = ""     

    # Set by set_valid_sources()
    ## e.g. valid_sources = ["/","/deep","/deep/","/index.html",...]
    valid_sources = []    
    
    # Set by set_response_status
    ## e.g. response_status = 404
    response_status = -1  

    # Set by set_response_path
    ## e.g. response_path = "cwd/www/index.html"
    response_path = ""    

    def handle(self):
        self.receive_request()
        self.parse_request()
        self.set_valid_sources()
        self.set_response_status()
        self.set_response_path()        
        self.send_response_header()
        self.send_response_body()
        
    '''Receive request message'''
    def receive_request(self):
        self.request_msg = self.request.recv(1024).strip()
        print ("Receive Request: %s\n" % self.request_msg)
    
        
    '''Parse request type and source'''
    def parse_request(self):
        first_line = self.request_msg.split("\r\n")[0]
        self.request_type = first_line.split(" ")[0]
        self.request_source = first_line.split(" ")[1]
        self.content_type = self.request_source.split(".")[-1]
        
    '''Set files and dirs sources that client is eligible to request'''    
    def set_valid_sources(self):
        ## root, dirs, files = os.walk("./").next()
        ## root = ['./'], dirs = ['deep'], files = ['index.html', 'base.css']
        files_www = os.walk("./www").next()[2]
        files_deep = os.walk("./www/deep/").next()[2]
        files_www = ['/{0}'.format(element) for element in files_www]
        files_deep = ['/deep/{0}'.format(element) for element in files_deep]
        valid_files = files_www + files_deep   # e.g. ["/index.html"...]
        valid_dirs = ["/", "/deep", "/deep/"]
        self.valid_sources = valid_files + valid_dirs
       
    '''Determine the status of response'''
    def set_response_status(self):
        if self.type_is_valid():
            if self.request_source == "/deep":
                self.response_status = 301
            elif self.source_is_valid():
                self.response_status = 200
            else:
                self.response_status = 404
        else:
            self.response_status = 404
            
    '''Determine the file path to read file'''
    def set_response_path(self):
        if self.response_status == 404:
            self.response_path = os.getcwd() + "/www/404.html"
        elif self.request_source == "/":
            self.response_path = os.getcwd() + "/www/index.html"
        elif self.request_source in ("/deep", "/deep/"):
            self.response_path = os.getcwd() + "/www/deep/index.html"            
        else:
            self.response_path = os.getcwd() + "/www" + self.request_source
            
    '''Send header to the client'''    
    def send_response_header(self):
        con = ""
        seq = ""
        date = self.make_date_string()
        seq2 = ("Date: " + date + "\r\n",
                "Server: C410ASN1\r\n"
                "Connection: close\r\n",
                "\r\n")
        if self.response_status == 301:
            seq = ("HTTP/1.1 301 Moved Permanently\r\n",
                   "Content-Type: text/html; charset=UTF-8\r\n",
                   "Location: /deep/index.html\r\n")
        elif self.response_status == 200:
            if self.content_type == "css":
                seq = ("HTTP/1.1 200 OK\r\n",
                       "Content-Type: text/css; charset=UTF-8\r\n")
            else:
                seq = ("HTTP/1.1 200 OK\r\n",
                       "Content-Type: text/html; charset=UTF-8\r\n")
        elif self.response_status == 404:
            seq = ("HTTP/1.1 404 NOT FOUND\r\n",
                    "Content-Type: text/html; charset=UTF-8\r\n")
        seq = seq + seq2
        header = con.join(seq)
        self.request.sendall(header)
        
    '''Send body to the client'''    
    def send_response_body(self):
#        if self.response_status != 404:
            fp = open(self.response_path, 'r')
            body = fp.read()
            self.request.sendall(body)

    ######################## 
    ## HELPER FUNCTIONS OF 
    ## set_response_status()        
     
    '''Check if the request type is valid'''    
    def type_is_valid(self):
        if self.request_type == "GET":
            return True
        else:
            return False
        
    '''Check if the request source is valid'''    
    def source_is_valid(self):
        exist = self.request_source in self.valid_sources
        #readable = os.access("." + self.request_source, os.R_OK)
        if exist:
            return True 
        else:
            return False

    ''''Make date string for response header'''
    def make_date_string(self):
        from wsgiref.handlers import format_date_time
        from datetime import datetime
        from time import mktime
        now = datetime.now()
        stamp = mktime(now.timetuple())
        date = format_date_time(stamp)
        return date
        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


