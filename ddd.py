# coding: UTF-8
import sys
import json
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import EventDAO
import urlparse
import createHTML

class JsonResponseHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        parsed_path = urlparse.urlparse(self.path)

        if 'create' in parsed_path.path:
            content_len = int(self.headers.get('content-length'))
            requestBody = self.rfile.read(content_len).decode('UTF-8')
            eList = json.loads(requestBody)

            event = EventDAO.Event()

            date = eList['date'].encode('utf-8')
            ftime = eList['ftime'].encode('utf-8')
            time = eList['time'].encode('utf-8')
            event.title = eList['title'].encode('utf-8')
            event.room = eList['room'].encode('utf-8')
            event.promotor_name = eList['promotor_name'].encode('utf-8')
            event.promotor_mail = eList['promotor_email'].encode('utf-8')
            event.capacity = eList['capacity'].encode('utf-8')
            event.descri = eList['descri'].encode('utf-8')
            event.agenda = eList['agenda'].encode('utf-8')
            event.note = eList['note'].encode('utf-8')

            event.start_time = date + " " + time
            event.end_time = date + " " + ftime

            event.save()
            self.send_response(200)
            self.end_headers()

        elif 'events' in parsed_path.path:
            content_len = int(self.headers.get('content-length'))
            requestBody = self.rfile.read(content_len).decode('UTF-8')
            eList = json.loads(requestBody)

            event_id = int(eList['event_id'])
            promotor_email = eList['promotor_email']

            event = EventDAO.Event()
            event.get(event_id).attend(promotor_email)
            self.send_response(200)
            self.end_headers()


    def do_GET(self):

        parsed_path = urlparse.urlparse(self.path)

        if 'showlist' in parsed_path.path:

            makeHTML = createHTML.createHTML()
            res = makeHTML.showlistHTML()

            self.send_response(200)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write(res)

        elif 'events' in parsed_path.path:

            event = EventDAO.Event()
            eventlist = event.list()
            cnt = len(eventlist)

            eventID = parsed_path.path[8:]
            evID = int(eventID)

            selectOBJ=event.get(evID)
            partname=event.get(evID).list_participate()

            makeHTML = createHTML.createHTML()
            res = makeHTML.detailHTML(evID,selectOBJ,partname)

            self.send_response(200)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()
            self.wfile.write(res)

    def do_DELETE(self):
        print "DELETE"

        parsed_path = urlparse.urlparse(self.path)
        print parsed_path.path

        if 'cancel' in parsed_path.path:
            content_len = int(self.headers.get('content-length'))
            requestBody = self.rfile.read(content_len).decode('UTF-8')
            eList = json.loads(requestBody)

            event_id = int(eList['event_id'])
            promotor_email = eList['promotor_email']

            event = EventDAO.Event()
            event.get(event_id).attend(promotor_email,cancel=True)
            
            self.send_response(200)
            self.end_headers()


        elif parsed_path.path.find(''):
            print "madamada"


if __name__ == '__main__':
    server = HTTPServer(('', 3389), JsonResponseHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
