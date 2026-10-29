import argparse
import base64
import fnmatch
import hashlib
import ipaddress
import json
import logging
import os
import signal
import socket
import socketserver
import ssl
import sys
import urllib.request
from urllib.parse import urlparse, parse_qs, unquote

from http.server import BaseHTTPRequestHandler
from functools import wraps

from jinja2 import Template

### Some options for you to change
LISTENIP = "0.0.0.0"
PORT = 3218
# Set BASEPATH to something like "/home/hass/.homeassistant/" if you're not
# running the configurator from that path
BASEPATH = None
# Set ENFORCE_BASEPATH to True to lock the configurator into the basepath and
# thereby prevent it from opening files outside of the BASEPATH
ENFORCE_BASEPATH = False
# Set the paths to a certificate and the key if you're using SSL,
# e.g "/etc/ssl/certs/mycert.pem"
SSL_CERTIFICATE = None
SSL_KEY = None
# Set the destination where the HASS API is reachable
HASS_API = "http://127.0.0.1:8123/api/"
# Set the destination where the websocket API is reachable (if different
# from HASS_API, e.g. wss://hass.example.com/api/websocket)
HASS_WS_API = None
# If a password is required to access the API, set it in the form of "password"
# if you have HA ignoring SSL locally this is not needed if on same machine.
HASS_API_PASSWORD = None
# Using the CREDENTIALS variable is deprecated.
# It will still work though if USERNAME and PASSWORD are not set.
CREDENTIALS = None
# Set the username used for basic authentication.
USERNAME = None
# Set the password used for basic authentication.
PASSWORD = None
# Limit access to the configurator by adding allowed IP addresses / networks to
# the list, e.g ALLOWED_NETWORKS = ["192.168.0.0/24", "172.16.47.23"]
ALLOWED_NETWORKS = []
# Allow access to the configurator to client IP addesses which match the result
# of DNS lookups for the specified domains.
ALLOWED_DOMAINS = []
# List of statically banned IP addresses, e.g. ["1.1.1.1", "2.2.2.2"]
BANNED_IPS = []
# Ban IPs after n failed login attempts. Restart service to reset banning.
# The default of `0` disables this feature.
BANLIMIT = 0
# Enable git integration.
# GitPython (https://gitpython.readthedocs.io/en/stable/) has to be installed.
GIT = False
# Files to ignore in the UI.  A good example list that cleans up the UI is
# [".*", "*.log", "deps", "icloud", "*.conf", "*.json", "certs", "__pycache__"]
IGNORE_PATTERN = []
# if DIRSFIRST is set to `true`, directories will be displayed at the top
DIRSFIRST = False
# Don't display hidden files (starting with .)
HIDEHIDDEN = False
# Sesame token. Browse to the configurator URL + /secrettoken to unban your
# client IP and add it to the list of allowed IPs.
SESAME = None
# Instead of a static SESAME token you may also use a TOTP based token that
# changes every 30 seconds. The value needs to be a base 32 encoded string.
SESAME_TOTP_SECRET = None
# Verify the hostname used in the request. Block access if it doesn't match
# this value
VERIFY_HOSTNAME = None
# Prefix for environment variables
ENV_PREFIX = "HC_"
# Ignore SSL errors when connecting to the HASS API
IGNORE_SSL = False
# Notification service like `notify.mytelegram`. Default is `persistent_notification.create`
NOTIFY_SERVICE_DEFAULT = "persistent_notification.create"
NOTIFY_SERVICE = NOTIFY_SERVICE_DEFAULT
### End of options

LOGLEVEL_MAPPING = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG
}
DEFAULT_LOGLEVEL = "info"
LOGLEVEL = LOGLEVEL_MAPPING.get(os.environ.get("HC_LOGLEVEL", DEFAULT_LOGLEVEL))
LOG = logging.getLogger(__name__)
LOG.setLevel(LOGLEVEL)
SO = logging.StreamHandler(sys.stdout)
SO.setLevel(LOGLEVEL)
SO.setFormatter(
    logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s'))
LOG.addHandler(SO)
VERSION = "1.0.0"
BASEDIR = "."
DEV = False
LISTENPORT = None
TOTP = None
HTTPD = None
FAIL2BAN_IPS = {}
REPO = None


def signal_handler(sig, frame):
    """Handle signal to shut down server."""
    global HTTPD
    LOG.info("Got signal: %s. Shutting down server", str(sig))
    HTTPD.server_close()
    sys.exit(0)


def load_settings(args):
    """Load settings from file and environment."""
    global LISTENIP, LISTENPORT, BASEPATH, SSL_CERTIFICATE, SSL_KEY, HASS_API, \
    HASS_API_PASSWORD, CREDENTIALS, ALLOWED_NETWORKS, BANNED_IPS, BANLIMIT, \
    DEV, IGNORE_PATTERN, DIRSFIRST, SESAME, VERIFY_HOSTNAME, ENFORCE_BASEPATH, \
    ENV_PREFIX, NOTIFY_SERVICE, USERNAME, PASSWORD, SESAME_TOTP_SECRET, TOTP, \
    GIT, REPO, PORT, IGNORE_SSL, HASS_WS_API, ALLOWED_DOMAINS, HIDEHIDDEN
    settings = {}
    settingsfile = args.settings
    if settingsfile:
        try:
            if os.path.isfile(settingsfile):
                settings = json.loads(load_file(settingsfile).decode("utf-8"))
                LOG.debug("Settings from file:")
                LOG.debug(settings)
            else:
                LOG.warning("File not found: %s", settingsfile)
        except Exception as err:
            LOG.warning(err)
            LOG.warning("Not loading settings from file")
    ENV_PREFIX = settings.get('ENV_PREFIX', ENV_PREFIX)
    for key, value in os.environ.items():
        if key.startswith(ENV_PREFIX):
            # Convert booleans
            if value in ['true', 'false', 'True', 'False']:
                value = value in ['true', 'True']
            # Convert None / null
            elif value in ['none', 'None', 'null']:
                value = None
            # Convert plain numbers
            elif value.isnumeric():
                value = int(value)
            # Make lists out of comma separated values for list-settings
            elif key[len(ENV_PREFIX):] in ["ALLOWED_NETWORKS", "BANNED_IPS", "IGNORE_PATTERN"]:
                value = value.split(',')
            settings[key[len(ENV_PREFIX):]] = value
    LOG.debug("Settings after looking at environment:")
    LOG.debug(settings)
    if args.git:
        GIT = args.git
    else:
        GIT = settings.get("GIT", GIT)
    if GIT:
        try:
            # pylint: disable=redefined-outer-name,import-outside-toplevel
            from git import Repo as REPO
        except ImportError:
            LOG.warning("Unable to import Git module")
    if args.listen:
        LISTENIP = args.listen
    else:
        LISTENIP = settings.get("LISTENIP", LISTENIP)
    if args.port is not None:
        PORT = args.port
    else:
        LISTENPORT = settings.get("LISTENPORT", None)
    PORT = settings.get("PORT", PORT)
    if LISTENPORT is not None:
        PORT = LISTENPORT
    if args.basepath:
        BASEPATH = args.basepath
    else:
        BASEPATH = settings.get("BASEPATH", BASEPATH)
    if args.enforce:
        ENFORCE_BASEPATH = True
    else:
        ENFORCE_BASEPATH = settings.get("ENFORCE_BASEPATH", ENFORCE_BASEPATH)
    SSL_CERTIFICATE = settings.get("SSL_CERTIFICATE", SSL_CERTIFICATE)
    SSL_KEY = settings.get("SSL_KEY", SSL_KEY)
    if args.standalone:
        HASS_API = None
    else:
        HASS_API = settings.get("HASS_API", HASS_API)
    HASS_WS_API = settings.get("HASS_WS_API", HASS_WS_API)
    HASS_API_PASSWORD = settings.get("HASS_API_PASSWORD", HASS_API_PASSWORD)
    CREDENTIALS = settings.get("CREDENTIALS", CREDENTIALS)
    ALLOWED_NETWORKS = settings.get("ALLOWED_NETWORKS", ALLOWED_NETWORKS)
    if ALLOWED_NETWORKS and not all(ALLOWED_NETWORKS):
        LOG.warning("Invalid value for ALLOWED_NETWORKS. Using empty list.")
        ALLOWED_NETWORKS = []
    for net in ALLOWED_NETWORKS:
        try:
            ipaddress.ip_network(net)
        except Exception:
            LOG.warning("Invalid network in ALLOWED_NETWORKS: %s", net)
            ALLOWED_NETWORKS.remove(net)
    ALLOWED_DOMAINS = settings.get("ALLOWED_DOMAINS", ALLOWED_DOMAINS)
    if ALLOWED_DOMAINS and not all(ALLOWED_DOMAINS):
        LOG.warning("Invalid value for ALLOWED_DOMAINS. Using empty list.")
        ALLOWED_DOMAINS = []
    BANNED_IPS = settings.get("BANNED_IPS", BANNED_IPS)
    if BANNED_IPS and not all(BANNED_IPS):
        LOG.warning("Invalid value for BANNED_IPS. Using empty list.")
        BANNED_IPS = []
    for banned_ip in BANNED_IPS:
        try:
            ipaddress.ip_address(banned_ip)
        except Exception:
            LOG.warning("Invalid IP address in BANNED_IPS: %s", banned_ip)
            BANNED_IPS.remove(banned_ip)
    BANLIMIT = settings.get("BANLIMIT", BANLIMIT)
    if args.dev:
        DEV = True
    else:
        DEV = settings.get("DEV", DEV)
    IGNORE_PATTERN = settings.get("IGNORE_PATTERN", IGNORE_PATTERN)
    if IGNORE_PATTERN and not all(IGNORE_PATTERN):
        LOG.warning("Invalid value for IGNORE_PATTERN. Using empty list.")
        IGNORE_PATTERN = []
    if args.dirsfirst:
        DIRSFIRST = args.dirsfirst
    else:
        DIRSFIRST = settings.get("DIRSFIRST", DIRSFIRST)
    if args.hidehidden:
        HIDEHIDDEN = args.hidehidden
    else:
        HIDEHIDDEN = settings.get("HIDEHIDDEN", HIDEHIDDEN)
    SESAME = settings.get("SESAME", SESAME)
    SESAME_TOTP_SECRET = settings.get("SESAME_TOTP_SECRET", SESAME_TOTP_SECRET)
    VERIFY_HOSTNAME = settings.get("VERIFY_HOSTNAME", VERIFY_HOSTNAME)
    NOTIFY_SERVICE = settings.get("NOTIFY_SERVICE", NOTIFY_SERVICE_DEFAULT)
    IGNORE_SSL = settings.get("IGNORE_SSL", IGNORE_SSL)
    if IGNORE_SSL:
        # pylint: disable=protected-access
        ssl._create_default_https_context = ssl._create_unverified_context
    if args.username and args.password:
        USERNAME = args.username
        PASSWORD = args.password
    else:
        USERNAME = settings.get("USERNAME", USERNAME)
        PASSWORD = settings.get("PASSWORD", PASSWORD)
        PASSWORD = str(PASSWORD) if PASSWORD else None
    if CREDENTIALS and (USERNAME is None or PASSWORD is None):
        USERNAME = CREDENTIALS.split(":")[0]
        PASSWORD = ":".join(CREDENTIALS.split(":")[1:])
    if PASSWORD and PASSWORD.startswith("{sha256}"):
        PASSWORD = PASSWORD.lower()
    if SESAME_TOTP_SECRET:
        try:
            #pylint: disable=import-outside-toplevel
            import pyotp
            TOTP = pyotp.TOTP(SESAME_TOTP_SECRET)
        except ImportError:
            LOG.warning("Unable to import pyotp module")
        except Exception as err:
            LOG.warning("Unable to create TOTP object: %s", err)


def is_jwt(token):
    """Perform basic check if token is a JWT token."""
    return len(token.split('.')) == 3


def is_safe_path(basedir, path, follow_symlinks=True):
    """Check path for malicious traversal."""
    if basedir is None:
        return True
    if follow_symlinks:
        return os.path.realpath(path).startswith(basedir.encode('utf-8'))
    return os.path.abspath(path).startswith(basedir.encode('utf-8'))


def get_dircontent(path, repo=None):
    """Get content of directory."""
    dircontent = []
    if repo:
        untracked = [
            "%s%s%s"%(repo.working_dir, os.sep, e) for e in \
            ["%s"%os.sep.join(f.split('/')) for f in repo.untracked_files]
        ]
        staged = {}
        unstaged = {}
        try:
            for element in repo.index.diff("HEAD"):
                staged["%s%s%s" % (repo.working_dir,
                                   os.sep,
                                   "%s"%os.sep.join(
                                       element.b_path.split('/')))] = element.change_type
        except Exception as err:
            LOG.warning("Exception: %s", str(err))
        for element in repo.index.diff(None):
            unstaged["%s%s%s" % (repo.working_dir,
                                 os.sep,
                                 "%s"%os.sep.join(
                                     element.b_path.split('/')))] = element.change_type
    else:
        untracked = []
        staged = {}
        unstaged = {}


    def sorted_file_list():
        """Sort list of files / directories."""
        dirlist = [x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]
        filelist = [x for x in os.listdir(path) if not os.path.isdir(os.path.join(path, x))]
        if HIDEHIDDEN:
            dirlist = [x for x in dirlist if not x.startswith('.')]
            filelist = [x for x in filelist if not x.startswith('.')]
        if DIRSFIRST:
            return sorted(dirlist, key=lambda x: x.lower()) + \
                sorted(filelist, key=lambda x: x.lower())
        return sorted(dirlist + filelist, key=lambda x: x.lower())

    for elem in sorted_file_list():
        edata = {}
        edata['name'] = elem
        edata['dir'] = path
        edata['fullpath'] = os.path.abspath(os.path.join(path, elem))
        edata['type'] = 'dir' if os.path.isdir(edata['fullpath']) else 'file'
        try:
            stats = os.stat(os.path.join(path, elem))
            edata['size'] = stats.st_size
            edata['modified'] = stats.st_mtime
            edata['created'] = stats.st_ctime
        except Exception:
            edata['size'] = 0
            edata['modified'] = 0
            edata['created'] = 0
        edata['changetype'] = None
        edata['gitstatus'] = bool(repo)
        edata['gittracked'] = 'untracked' if edata['fullpath'] in untracked else 'tracked'
        if edata['fullpath'] in unstaged:
            edata['gitstatus'] = 'unstaged'
            edata['changetype'] = unstaged.get(edata['name'], None)
        elif edata['fullpath'] in staged:
            edata['gitstatus'] = 'staged'
            edata['changetype'] = staged.get(edata['name'], None)

        hidden = False
        if IGNORE_PATTERN is not None:
            for file_pattern in IGNORE_PATTERN:
                if fnmatch.fnmatch(edata['name'], file_pattern):
                    hidden = True

        if not hidden:
            dircontent.append(edata)

    return dircontent


def load_file(filename, static=False):
    """Load files. If static is True, set to path of configurator."""
    if static:
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    try:
        with open(filename, 'rb') as fptr:
            content = fptr.read()
            return content
    except Exception as err:
        LOG.critical(err)
        return None


def password_problems(password, name="UNKNOWN"):
    """Rudimentary checks for password strength."""
    problems = 0
    password = str(password)
    if password is None:
        return problems
    if len(password) < 8:
        LOG.warning("Password %s is too short", name)
        problems += 1
    if password.isalpha():
        LOG.warning("Password %s does not contain digits", name)
        problems += 2
    if password.isdigit():
        LOG.warning("Password %s does not contain alphabetic characters", name)
        problems += 4
    quota = len(set(password)) / len(password)
    exp = len(password) ** len(set(password))
    score = exp / quota / 8
    if score < 65536:
        LOG.warning("Password %s does not contain enough unique characters (%i)",
                    name, len(set(password)))
        problems += 8
    return problems


def check_access(clientip):
    """Check if IP is allowed to access the configurator / API."""
    global BANNED_IPS
    if clientip in BANNED_IPS:
        LOG.warning("Client IP banned.")
        return False
    if not ALLOWED_NETWORKS:
        return True
    for net in ALLOWED_NETWORKS:
        ipobject = ipaddress.ip_address(clientip)
        if ipobject in ipaddress.ip_network(net):
            return True
    LOG.warning("Client IP not within allowed networks.")
    if ALLOWED_DOMAINS:
        for domain in ALLOWED_DOMAINS:
            try:
                domain_data = socket.getaddrinfo(domain, None)
            except Exception as err:
                LOG.warning("Unable to lookup domain data: %s", err)
                continue
            for res in domain_data:
                if res[0] in [socket.AF_INET, socket.AF_INET6]:
                    if res[4][0] == clientip:
                        return True
        LOG.warning("Client IP not within allowed domains.")
    BANNED_IPS.append(clientip)
    return False


def verify_hostname(request_hostname):
    """Verify the provided host header is correct."""
    if VERIFY_HOSTNAME:
        if VERIFY_HOSTNAME not in request_hostname:
            return False
    return True


def notify(title="HASS Configurator",
           message="Notification by HASS Configurator",
           notification_id=None):
    """Helper function to send notifications via HASS."""
    if not HASS_API or not NOTIFY_SERVICE:
        return
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "message": message
    }
    if notification_id and NOTIFY_SERVICE == NOTIFY_SERVICE_DEFAULT:
        data["notification_id"] = notification_id
    if HASS_API_PASSWORD:
        if is_jwt(HASS_API_PASSWORD):
            headers["Authorization"] = "Bearer %s" % HASS_API_PASSWORD
        else:
            headers["x-ha-access"] = HASS_API_PASSWORD
    req = urllib.request.Request(
        "%sservices/%s" % (HASS_API, NOTIFY_SERVICE.replace('.', '/')),
        data=bytes(json.dumps(data).encode('utf-8')),
        headers=headers, method='POST')
    LOG.info("%s", data)
    try:
        with urllib.request.urlopen(req) as response:
            message = response.read().decode('utf-8')
            LOG.debug(message)
    except Exception as err:
        LOG.warning("Exception while creating notification: %s", err)


def route(path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.route = path
        return wrapper
    return decorator


@route('/')
def index(request):
    query = parse_qs(urlparse(request.path).query)
    LOG.debug(query)
    loadfile = query.get('loadfile', [None])[0]
    if loadfile is None:
        loadfile = 'null'
    else:
        loadfile = f"'{loadfile}'"
    services = "[]"
    events = "[]"
    states = "[]"

    try:
        if HASS_API:
            headers = {
                "Content-Type": "application/json"
            }
            if HASS_API_PASSWORD:
                if is_jwt(HASS_API_PASSWORD):
                    headers["Authorization"] = "Bearer %s" % HASS_API_PASSWORD
                else:
                    headers["x-ha-access"] = HASS_API_PASSWORD

            req = urllib.request.Request("%sservices" % HASS_API,
                                            headers=headers, method='GET')
            with urllib.request.urlopen(req) as response:
                services = response.read().decode('utf-8')

            req = urllib.request.Request("%sevents" % HASS_API,
                                            headers=headers, method='GET')
            with urllib.request.urlopen(req) as response:
                events = response.read().decode('utf-8')

            req = urllib.request.Request("%sstates" % HASS_API,
                                            headers=headers, method='GET')
            with urllib.request.urlopen(req) as response:
                states_clean = []
                for state in json.loads(response.read().decode('utf-8')):
                    states_clean.append(
                        {
                            "entity_id": state.get("entity_id", ""),
                            "attributes":
                            {"friendly_name": state.get("attributes", {}).get(
                                "friendly_name", state.get("entity_id", ""))}
                        }
                    )
                states = json.dumps(states_clean)

    except Exception as err:
        LOG.warning("Exception getting bootstrap")
        LOG.warning(err)

    color = ""
    ws_api = ""
    if HASS_API:
        protocol, uri = HASS_API.split("//")
        ws_api = "%s://%swebsocket" % (
            "wss" if protocol == 'https' else 'ws', uri
        )
    if HASS_WS_API:
        ws_api = HASS_WS_API
    standalone = ""
    if not HASS_API:
        standalone = "toggle_hass_panels();"
    with open(os.path.join(os.path.dirname(__file__), "templates", "index.html")) as fptr:
        content = Template(fptr.read())
    return content.render(
        services=services,
        events=events,
        states=states,
        loadfile=loadfile,
        current=VERSION,
        versionclass=color,
        githidden="" if GIT else "hiddendiv",
        # pylint: disable=anomalous-backslash-in-string
        separator="\%s" % os.sep if os.sep == "\\" else os.sep,
        your_address="1.2.3.4",# self.client_address[0],
        listening_address="%s://%s:%i" % (
            'https' if SSL_CERTIFICATE else 'http', LISTENIP, PORT),
        hass_api_address="%s" % (HASS_API, ),
        hass_ws_address=ws_api,
        api_password=HASS_API_PASSWORD if HASS_API_PASSWORD else "",
        standalone=standalone)


@route('/api/listdir')
def api_listdir(request):
    query = parse_qs(urlparse(request.path).query)
    LOG.debug(query)
    content = {'error': None}
    dirpath = query.get('path', None)
    if dirpath is None:
        content['error'] = "dirpath not set"
        return json.dumps(content)
    try:
        dirpath = unquote(dirpath[0]).encode('utf-8')
        if os.path.isdir(dirpath):
            if ENFORCE_BASEPATH and not is_safe_path(BASEPATH,
                                                     dirpath):
                raise OSError('Access denied.')
            repo = None
            activebranch = None
            dirty = False
            branches = []
            if REPO:
                try:
                    # pylint: disable=not-callable
                    repo = REPO(dirpath.decode('utf-8'),
                                search_parent_directories=True)
                    activebranch = repo.active_branch.name
                    dirty = repo.is_dirty()
                    for branch in repo.branches:
                        branches.append(branch.name)
                except Exception as err:
                    LOG.debug("Exception (no repo): %s", str(err))
            dircontent = get_dircontent(dirpath.decode('utf-8'), repo)
            filedata = {
                'content': dircontent,
                'abspath': os.path.abspath(dirpath).decode('utf-8'),
                'parent': os.path.dirname(os.path.abspath(dirpath)).decode('utf-8'),
                'branches': branches,
                'activebranch': activebranch,
                'dirty': dirty,
                'error': None
            }
            return json.dumps(filedata)
    except Exception as err:
        LOG.warning(err)
        content['error'] = str(err)
        return json.dumps(content)


ROUTES = [index, api_listdir]


class RequestHandler(BaseHTTPRequestHandler):
    def guess_type(self, path):
        # Define MIME types for different subfolders of the assets directory
        if path.startswith('/images/'):
            return 'image/jpeg' if path.endswith('.jpg') else 'image/png'
        else:
            return super().guess_type(path)

    def log_message(self, format, *args):
        LOG.info("%s - %s", self.client_address[0], format % args)

    def do_BLOCK(self, status=420, reason="Policy not fulfilled"):
        """Customized do_BLOCK method."""
        self.send_response(status)
        self.end_headers()
        self.wfile.write(bytes(reason, "utf8"))

    def do_GET(self):
        if not verify_hostname(self.headers.get('Host', '')):
            self.do_BLOCK(403, "Forbidden")
            return

        if not check_access(self.client_address[0]):
            self.do_BLOCK()
            return

        LOG.debug(self.path)
        for func in ROUTES:
            if func.route == self.path.split("?")[0]:
                self.send_response(200)
                if self.path.startswith("/api/listdir"):
                    self.send_header('Content-type', 'text/json')
                else:
                    self.send_header('Content-type', 'text/html')
                self.end_headers()
                response = func(self)
                self.wfile.write(bytes(response, 'utf-8'))
                return
        
        # Serve static files
        if self.path.startswith('/assets/') and not ".." in self.path:
            path = os.path.join(os.path.dirname(__file__), self.path.lstrip('/'))
            if os.path.isfile(path):
                with open(path, 'rb') as file:
                    content = file.read()
                self.send_response(200)
                self.send_header('Content-type', self.get_content_type(path))
                self.end_headers()
                self.wfile.write(content)
                return

        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'404 Not Found')
        return

    def get_content_type(self, path):
        ext = os.path.splitext(path)[1]
        if ext == '.html':
            return 'text/html'
        elif ext == '.js':
            return 'application/javascript'
        elif ext == '.css':
            return 'text/css'
        elif ext == '.png':
            return 'image/png'
        elif ext == '.jpg' or ext == '.jpeg':
            return 'image/jpeg'
        elif ext == '.gif':
            return 'image/gif'
        else:
            return 'application/octet-stream'



class AuthHandler(RequestHandler):
    """Handler to verify auth header."""
    def do_BLOCK(self, status=420, reason="Policy not fulfilled"):
        self.send_response(status)
        self.end_headers()
        self.wfile.write(bytes(reason, "utf8"))

    # pylint: disable=invalid-name
    def do_AUTHHEAD(self):
        """Request authorization."""
        LOG.info("Requesting authorization")
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"HASS Configurator\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if not verify_hostname(self.headers.get('Host', '')):
            self.do_BLOCK(403, "Forbidden")
            return
        header = self.headers.get('Authorization', None)
        if header is None:
            self.do_AUTHHEAD()
            self.wfile.write(bytes('no auth header received', 'utf-8'))
        else:
            authorization = header.split()
            if len(authorization) == 2 and authorization[0] == "Basic":
                plain = base64.b64decode(authorization[1]).decode("utf-8")
                parts = plain.split(':')
                username = parts[0]
                password = ":".join(parts[1:])
                if PASSWORD.startswith("{sha256}"):
                    password = "{sha256}%s" % hashlib.sha256(password.encode("utf-8")).hexdigest()
                if username == USERNAME and password == PASSWORD:
                    if BANLIMIT:
                        FAIL2BAN_IPS.pop(self.client_address[0], None)
                    super().do_GET()
                    return
            if BANLIMIT:
                bancounter = FAIL2BAN_IPS.get(self.client_address[0], 1)
                if bancounter >= BANLIMIT:
                    LOG.warning("Blocking access from %s", self.client_address[0])
                    self.do_BLOCK()
                    return
                FAIL2BAN_IPS[self.client_address[0]] = bancounter + 1
            self.do_AUTHHEAD()
            self.wfile.write(bytes('Authentication required', 'utf-8'))

    def do_POST(self):
        if not verify_hostname(self.headers.get('Host', '')):
            self.do_BLOCK(403, "Forbidden")
            return
        header = self.headers.get('Authorization', None)
        if header is None:
            self.do_AUTHHEAD()
            self.wfile.write(bytes('no auth header received', 'utf-8'))
        else:
            authorization = header.split()
            if len(authorization) == 2 and authorization[0] == "Basic":
                plain = base64.b64decode(authorization[1]).decode("utf-8")
                parts = plain.split(':')
                username = parts[0]
                password = ":".join(parts[1:])
                if PASSWORD.startswith("{sha256}"):
                    password = "{sha256}%s" % hashlib.sha256(password.encode("utf-8")).hexdigest()
                if username == USERNAME and password == PASSWORD:
                    if BANLIMIT:
                        FAIL2BAN_IPS.pop(self.client_address[0], None)
                    super().do_POST()
                    return
            if BANLIMIT:
                bancounter = FAIL2BAN_IPS.get(self.client_address[0], 1)
                if bancounter >= BANLIMIT:
                    LOG.warning("Blocking access from %s", self.client_address[0])
                    self.do_BLOCK()
                    return
                FAIL2BAN_IPS[self.client_address[0]] = bancounter + 1
            self.do_AUTHHEAD()
            self.wfile.write(bytes('Authentication required', 'utf-8'))


class SimpleServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Server class."""
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)



def main():
    """Main function."""
    global HTTPD
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(description="Visit " \
    "https://github.com/danielperna84/hass-configurator for more details " \
    "about the availble options.")
    parser.add_argument(
        'settings', nargs='?',
        help="Path to file with persistent settings.")
    parser.add_argument(
        '--listen', '-l', nargs='?',
        help="The IP address the service is listening on. Default: 0.0.0.0")
    parser.add_argument(
        '--port', '-p', nargs='?', type=int,
        help="The port the service is listening on. " \
        "0 allocates a dynamic port. Default: 3218")
    parser.add_argument(
        '--allowed_networks', '-a', nargs='?',
        help="Comma-separated list of allowed networks / IP addresses " \
        "from which access is allowed. Eg. 127.0.0.1,192.168.0.0/16. " \
        "By default access is allowed from anywhere.")
    parser.add_argument(
        '--username', '-U', nargs='?',
        help="Username required for access.")
    parser.add_argument(
        '--password', '-P', nargs='?',
        help="Password required for access.")
    parser.add_argument(
        '--sesame', '-S', nargs='?',
        help="SESAME token for whitelisting client IPs by accessing " \
        "a scret URL: http://1.2.3.4:3218/secret_sesame_token")
    parser.add_argument(
        '--basepath', '-b', nargs='?',
        help="Path to initially serve files from")
    parser.add_argument(
        '--enforce', '-e', action='store_true',
        help="Lock the configurator into the basepath.")
    parser.add_argument(
        '--standalone', '-s', action='store_true',
        help="Don't fetch data from HASS_API.")
    parser.add_argument(
        '--dirsfirst', '-d', action='store_true',
        help="Display directories first.")
    parser.add_argument(
        '--hidehidden', '-H', action='store_true',
        help="Don't display hidden files.")
    parser.add_argument(
        '--git', '-g', action='store_true',
        help="Enable GIT support.")
    parser.add_argument(
        '--dev', '-D', action='store_true',
        help="Enable Dev-Mode (serve dev.html instead of embedded HTML).")
    args = parser.parse_args()
    load_settings(args)
    LOG.info("Starting server")

    try:
        problems = None
        if HASS_API_PASSWORD:
            problems = password_problems(HASS_API_PASSWORD, "HASS_API_PASSWORD")
        if problems:
            data = {
                "title": "HASS Configurator - Password warning",
                "message": "Your Home Assistant API password seems insecure (%i). " \
                "Refer to the HASS Configurator logs for further information." % problems,
                "notification_id": "HC_HASS_API_PASSWORD"
            }
            notify(**data)

        problems = None
        if SESAME:
            problems = password_problems(SESAME, "SESAME")
        if problems:
            data = {
                "title": "HASS Configurator - Password warning",
                "message": "Your SESAME seems insecure (%i). " \
                "Refer to the HASS Configurator logs for further information." % problems,
                "notification_id": "HC_SESAME"
            }
            notify(**data)

        problems = None
        if PASSWORD:
            problems = password_problems(PASSWORD, "PASSWORD")
        if problems:
            data = {
                "title": "HASS Configurator - Password warning",
                "message": "Your PASSWORD seems insecure (%i). " \
                "Refer to the HASS Configurator logs for further information." % problems,
                "notification_id": "HC_PASSWORD"
            }
            notify(**data)
    except Exception as err:
        LOG.warning("Exception while checking passwords: %s", err)

    custom_server = SimpleServer
    if ':' in LISTENIP:
        custom_server.address_family = socket.AF_INET6
    server_address = (LISTENIP, PORT)
    if USERNAME and PASSWORD:
        handler = AuthHandler
    else:
        handler = RequestHandler
    HTTPD = custom_server(server_address, handler)
    if SSL_CERTIFICATE:
        HTTPD.socket = ssl.wrap_socket(HTTPD.socket,
                                       certfile=SSL_CERTIFICATE,
                                       keyfile=SSL_KEY,
                                       server_side=True)

    LOG.info('Listening on: %s://%s:%i',
             'https' if SSL_CERTIFICATE else 'http',
             HTTPD.server_address[0], HTTPD.server_address[1])
    if BASEPATH:
        os.chdir(BASEPATH)
    HTTPD.serve_forever()

if __name__ == '__main__':
    main()
