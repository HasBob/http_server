import socket
import sys
import os
import pathlib
import mimetypes

def response_ok(body, mimetype):
    """returns a basic HTTP response"""
    #print('body', body, type(body), file=logbuffer)
    #print('mimetype', mimetype, type(mimetype), file=logbuffer)
    m = b'Content-Type: '
    resp = []
    resp.append(b"HTTP/1.1 200 OK")
    #import pdb; pdb.set_trace()
    #resp.append('Content-Type: {}'.format(mimetype))
    #resp.append((b'Content-Type: ' + mimetype))  # '; charset=UTF-8'
    resp.append(m + mimetype)
    resp.append(b"")
    resp.append(body)
    print(resp)
    return b"\r\n".join(resp)

def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return "\r\n".join(resp).encode('utf8')


def response_not_found():
    """returns a 404 Not Found response"""
    resp = []
    resp.append("HTTP/1.1 404 Not Found")
    resp.append("")
    return "\r\n".join(resp).encode('utf8')


def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    return uri

def resolve_uri(uri):
    """This method should return appropriate content and a mime type"""
    #mimetype = ('Content-Type: {}'.format(mimetypes.guess_type(uri)[0]))
    mimetype = mimetypes.guess_type(uri)[0]
    uripath = '{}/'.format(os.path.dirname(__file__)) + 'webroot' + os.path.dirname(uri) + '/'
    fil = uri.split('/')[-1]

    #if not mimetype:
    #    return response_not_found()
    # 
    #import pdb; pdb.set_trace()
    if os.path.isfile(uripath + fil): 
        #import pdb; pdb.set_trace()
        content = open(uripath + fil, 'rb').read()
        return content, bytes(mimetype,'utf-8')
    elif os.path.isdir(uripath + fil):
        content = ('\r\n'.join(os.listdir(uripath)))#.encode('utf8')
        mimetype = b'text/plain'
        return bytes(content,'utf8'), mimetype
    else:
        raise NameError(response_not_found())

def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)
                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')
                    if len(data) < 1024:
                        break

                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    try:
                        content, mimetype = resolve_uri(uri)
                    except NameError:
                        response = response_not_found()
                    else:
                        response = response_ok(content, mimetype)

                print('sending response', file=log_buffer)
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
