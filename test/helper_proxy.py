from mitmproxy import proxy, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import http

from flask import Flask, Blueprint, request, send_from_directory
try:
    from mitmproxy.addons import wsgiapp
except ImportError:
    from mitmproxy.addons import asgiapp as wsgiapp
import threading
import asyncio
import json
import time
import hashlib
import uuid
from datetime import datetime, timedelta
import os


class ResponseType:
    def __init__(self):
        self.type = []
        self.Version = None  # [[0,7,7],[0,7,8],[0,7,9]]
        self.parent = None

    def set_type(self, new):
        self.type = new

    def set_Version(self, version):
        self.Version = version

    def pop_type(self):
        if len(self.type):
            self.type.pop(0)

    def get_type(self):
        if len(self.type):
            return self.type[0]
        return None

    def get_Version(self):
        return self.Version

    def get_release(self):
        resp1 = []
        for ele in self.Version:
            ver = '{}.{}.{}'.format(*ele)
            element = {
                "tag_name": ver,
                "body": 'Release Info {}'.format(ver),
                "zipball_url": "https://api.github.com/repos/janeczku/calibre-web/zipball/{}".format(ver)
            }
            resp1.append(element)
        return resp1

    def get_current_master(self):
        self.parent = hashlib.sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()
        return {"object": {"sha": self.parent,
                           "url": "https://api.github.com/repos/janeczku/calibre-web/git/commits/" + self.parent}}

    def get_comitinfo(self, _hash):
        if self.parent == _hash:
            self.parent = hashlib.sha256(str(uuid.uuid4()).encode('utf-8')).hexdigest()
            now = datetime.now() - timedelta(days=1)
            commitDate = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            commit1 = {
                "committer": {
                                "name": "Comitter",
                                "email": "comitter@gcomit.com",
                                "date": commitDate
                             },
                "message": "Update message for hash " + _hash,
                "sha": _hash,
                "parents": [
                            {
                                "sha": self.parent,
                                "url": "https://api.github.com/repos/janeczku/calibre-web/git/commits/" + self.parent,
                                "html_url": "https://github.com/janeczku/calibre-web/commit/" + self.parent
                            }
                           ],
                      }
            return commit1
        return ''


git = Blueprint('git', __name__)


@git.route("/git/refs/heads/master")
def request_master() -> str:
    if request.accept_mimetypes.best == 'application/vnd.github.v3+json':
        type = val.get_type()
        val.pop_type()
        if type == 'HTTPError':
            return '{}', 404
        if type == 'Timeout':
            time.sleep(12)
            return '{}'
        if type == 'GeneralError':
            return "{committer:Object}"
        if type == 'MissingObject':
            resp2 = val.get_current_master()
            resp2.pop('object')
            return json.dumps(resp2)
        if type == 'MissingSha':
            resp2 = val.get_current_master()
            resp2['object'].pop('sha')
            return json.dumps(resp2)
        if type == 'MissingUrl':
            resp2 = val.get_current_master()
            resp2['object'].pop('url')
            return json.dumps(resp2)
        else:
            return json.dumps(val.get_current_master())
    else:
        return '{}', 404


@git.route("/git/commits/<sha1string>")
def request_commit(sha1string) -> str:
    try:
        if request.accept_mimetypes.best == 'application/vnd.github.v3+json':
            type = val.get_type()
            val.pop_type()
            if type == 'HTTPError':
                return '{}', 404
            if type == 'Timeout':
                time.sleep(12)
                return '{}'
            if type == 'GeneralError':
                return "{object:None}"
            if type == 'MissingComitter':
                resp2 = val.get_comitinfo(sha1string)
                resp2.pop('committer')
                return json.dumps(resp2)
            if type == 'MissingMessage':
                resp2 = val.get_comitinfo(sha1string)
                resp2.pop('message')
                return json.dumps(resp2)
            if type == 'MissingSha':
                resp2 = val.get_comitinfo(sha1string)
                resp2.pop('sha')
                return json.dumps(resp2)
            if type == 'MissingParents':
                resp2 = val.get_comitinfo(sha1string)
                resp2.pop('parents')
                return json.dumps(resp2)
            else:
                return json.dumps(val.get_comitinfo(sha1string))
        else:
            return '{}', 404
    except Exception:
        print('Testfixture broken')
        return '{}', 404


@git.route("/releases")
def releases() -> str:
    if request.accept_mimetypes.best == 'application/vnd.github.v3+json':
        type = val.get_type()
        val.pop_type()
        if type == 'HTTPError':
            return '{}', 404
        if type == 'Timeout':
            time.sleep(12)
            return '{}'
        if type == 'GeneralError':
            return '{tag_name:error}'
        if type == 'MissingTagName':
            resp2 = val.get_release()
            resp2[0].pop('tag_name')
            return json.dumps(resp2)
        if type == 'MissingBody':
            resp2 = val.get_release()
            resp2[0].pop('body')
            return json.dumps(resp2)
        if type == 'MissingZip':
            resp2 = val.get_release()
            resp2[1].pop('zipball_url')
            return json.dumps(resp2)
        else:
            resp1 = val.get_release()
            return json.dumps(resp1)
    else:
        return '{}', 404


@git.route("/zipball/<version>")
def zipball(version) -> str:
    try:
        if version != 'master':
            # check if versionlist has only integervalues
            versionlist = [int(x) for x in version.split('.')]

        if request.accept_mimetypes.best == 'application/vnd.github.v3+json':
            type = val.get_type()
            val.pop_type()
            if type == 'HTTPError':
                return '{}', 404
            if type == 'Timeout':
                time.sleep(612)
                return '{}'
            if type == 'GeneralError':
                return "Lulu"
            else:
                result = send_from_directory(os.getcwd(), 'cps_copy.zip',
                                             as_attachment=True,
                                             mimetype='application/zip',
                                             download_name='calibre-web-0.6.6.zip')
                result.headers['Accept-Ranges'] = 'bytes'
                return result
        else:
            return '{}', 404
    except Exception:
        print('Testfixture broken')
        return '{}', 404


@git.route("/cover/<type>")
def cover(type) -> str:
    try:
        error_type = val.get_type()
        val.pop_type()
        if error_type == 'HTTPError':
            return '', 404
        if error_type == 'GeneralError':    # invalid file
            return "Lulu"
        if error_type == 'Timeout':
            time.sleep(612)
            return ''
        else:
            # version='{}.{}.{}'.format(*val.get_Version()[0])
            result = None
            cover_path = os.path.join(os.getcwd(), 'files')
            if type == 'test.jpg':
                result = send_from_directory(cover_path, 'cover.jpg',
                                             as_attachment=True,
                                             mimetype='image/jpeg',
                                             attachment_filename='äo.jpg')
            elif type == 'test.png':
                result = send_from_directory(cover_path, 'cover.png',
                                             as_attachment=True,
                                             mimetype='image/png',
                                             attachment_filename='o.pgk')
            elif type == 'test.webp':
                result = send_from_directory(cover_path, 'cover.webp',
                                             as_attachment=True,
                                             mimetype='image/webp',
                                             attachment_filename='äo.webp')
            elif type == 'test.bmp':
                result = send_from_directory(cover_path, 'cover.bmp',
                                             as_attachment=True,
                                             mimetype='image/bmp',
                                             attachment_filename='äo.bmp')
            elif type == 'test.jol':
                result = send_from_directory(cover_path, 'cover.bmp',
                                             as_attachment=True,
                                             mimetype='image/jpeg',
                                             attachment_filename='äo.bmp')
            elif type == 'test.brk':
                result = send_from_directory(cover_path, 'book.cbz',
                                             as_attachment=True,
                                             mimetype='image/png',
                                             attachment_filename='äo.cbz')

            result.headers['Accept-Ranges'] = 'bytes'
            return result
    except Exception as e:
        print('Testfixture broken %e', e)
        return '', 404


app = Flask("gitty")
app.register_blueprint(git, url_prefix='/repos/janeczku/calibre-web')


val = ResponseType()


class Github_Proxy:
    def __init__(self):
        self.num = 0

    def request(self, flow: http.HTTPFlow) -> None:
        # redirects all requests to api.github.com to local server (flask instance)
        if flow.request.host == "api.github.com":
            if val.get_type() != 'ConnectionError':
                flow.request.host = "gitty.local"
            else:
                val.pop_type()
                flow.kill()

    def responseheaders(flow):
        def modify(chunks):
            time.sleep(0)
            # continue to stream original response
            yield from chunks
        flow.response.stream = modify


class Proxy(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        opts = options.Options(listen_host='127.0.0.1', listen_port=8080)
        opts.add_option("body_size_limit", int, 0, "")

        pconf = proxy.config.ProxyConfig(opts)

        self.m = DumpMaster(None, with_termlog=False, with_dumper=False)
        self.m.server = proxy.server.ProxyServer(pconf)
        if self.m.server.channel.loop.is_closed():
            self.m.server.channel.loop = asyncio.new_event_loop()
        self.m.addons.add(Github_Proxy())
        self.m.addons.add(wsgiapp.WSGIApp(app, "gitty.local", 443))

    def run(self):
        try:
            asyncio.set_event_loop(self.m.server.channel.loop)
            self.m.run()
        except Exception as e:
            print(e)

    def stop_proxy(self):
        try:
            self.m.shutdown()
        except Exception as e:
            print(e)
