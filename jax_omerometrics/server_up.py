"""
server-up: check if an OMERO server is up.

Module with multiple functions for checking whether
an OMERO server is up and running properly.

"""
import ezomero
import requests
import signal


def handler(signum, frame):
    """Handle signal."""
    raise Exception("Blitz connection timeout")


def create_json_session(web_host, username, password, verify=True):
    """Create a session for checking JSON API status."""
    session = requests.Session()
    # Start by getting supported versions from the base url...
    api_url = '%s/api/' % web_host
    r = session.get(api_url, verify=verify, timeout=5)
    assert r.status_code == 200
    print(api_url, r)
    # we get a list of versions
    versions = r.json()['data']
    # use most recent version...
    version = versions[-1]
    # get the 'base' url
    base_url = version['url:base']
    r = session.get(base_url, timeout=5)
    # which lists a bunch of urls as starting points
    urls = r.json()
    servers_url = urls['url:servers']
    login_url = urls['url:login']

    # To login we need to get CSRF token
    token_url = urls['url:token']
    token = session.get(token_url, timeout=5).json()['data']
    print('CSRF token', token)
    # We add this to our session header
    # Needed for all POST, PUT, DELETE requests
    session.headers.update({'X-CSRFToken': token,
                            'Referer': login_url})

    # List the servers available to connect to
    servers = session.get(servers_url, timeout=5).json()['data']
    SERVER_NAME = 'omero'
    servers = [s for s in servers if s['server'] == SERVER_NAME]
    if len(servers) < 1:
        raise Exception("Found no server called '%s'" % SERVER_NAME)
    server = servers[0]

    # Login with username, password and token
    payload = {'username': username,
               'password': password,
               # Using CSRFToken in header
               'server': server['id']}

    r = session.post(login_url, data=payload, timeout=5)
    login_rsp = r.json()
    assert r.status_code == 200
    assert login_rsp['success']

    # Can get our 'default' group

    return login_rsp, session, base_url


def check_web_response(address):
    """Check whether a web server is returning code 200."""
    try:
        r = requests.get(address, timeout=5)
    except:
        return False
    return r.status_code == requests.codes.ok


def check_web_api(user, pwd, img_id, address):
    """Check whether the JSON API can return a JPEG from an image."""
    print("checking json api...")
    print(address, user)
    try:
        _, session, base_url = create_json_session(address, user, pwd)
        print("created session successfully")
    except:
        print("failed to create session")
        return False
    print("initial success")
    host = base_url.split("/api")[0]
    img_address = host+"/webgateway/render_birds_eye_view/"+str(img_id)+"/"
    jpeg = session.get(img_address, stream=True)
    ret = (jpeg.status_code == requests.codes.ok)
    print(f"return code is {ret}")
    session.close()
    return ret


def check_ldap_login(user, pwd, address,
                     port=4064, secure=True, group=''):
    """Check whether an LDAP user can log into OMERO.server."""

    # set up signal for a 30s timeout on connection
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)
    ret = False
    try:
        conn = ezomero.connect(user=user, password=pwd, host=address,
                               port=port, secure=secure, group=group)
        ret = (conn is not None)
        conn.close()
    except:
        pass
    return ret


def check_img_return(img_id, user, pwd, address,
                     port=4064, secure=True, group=''):
    """Check whether an OMERO server is returning an image when asked."""
    # set up signal for a 120s timeout on getting image
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(120)
    ret = False
    try:
        conn = ezomero.connect(user=user, password=pwd, host=address,
                               port=port, secure=secure, group=group)
        img, _ = ezomero.get_image(conn, img_id)
        conn.close()
        ret = (img is not None)
    except:
        pass
    return ret
