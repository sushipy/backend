# coding: UTF-8
import sys
import json
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import EventDAO
import urlparse
import createHTML
import datetime

class MyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)
        else:
            return super(self.__class__, self).default(obj)

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

        elif 'api/v1/alllist' in parsed_path.path:
            event = EventDAO.Event()
            eventlist = event.list()
            aaa=[]
            for bbb in eventlist:
                aaa.append(bbb.__dict__)
            res = json.dumps(aaa,indent=4,encoding='utf8',cls=MyJSONEncoder)

            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            self.wfile.write(res)

        elif 'api/v1/nowlist' in parsed_path.path:
            event = EventDAO.Event()
            eventlist = event.list_from_now()
            aaa=[]
            for bbb in eventlist:
                aaa.append(bbb.__dict__)
            res = json.dumps(aaa,indent=4,encoding='utf8',cls=MyJSONEncoder)

            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            self.wfile.write(res)

        elif 'api/v1/showevent' in parsed_path.path:
            eventID = int(parsed_path.path[18:])

            event = EventDAO.Event()
            eventlist=event.get(eventID)
            res = json.dumps(eventlist.__dict__,indent=4,encoding='utf8',cls=MyJSONEncoder)

            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            self.wfile.write(res)

        elif 'api/v1/partlist' in parsed_path.path:
            eventID = int(parsed_path.path[17:])

            event = EventDAO.Event()
            eventlist=event.get(eventID).list_participate()
            res = json.dumps(eventlist,indent=4,encoding='utf8',cls=MyJSONEncoder)

            self.send_response(200)
            self.send_header('Content-type', 'text/json')
            self.end_headers()
            self.wfile.write(res)

        else:
            self.send_error(404)

    def do_DELETE(self):

        parsed_path = urlparse.urlparse(self.path)

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


        elif 'delete' in parsed_path.path:
            content_len = int(self.headers.get('content-length'))
            requestBody = self.rfile.read(content_len).decode('UTF-8')
            eList = json.loads(requestBody)
            event_id = int(eList['event_id'])

            event = EventDAO.Event()
            event.get(event_id).del_event()

            self.send_response(200)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('', 3389), JsonResponseHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
