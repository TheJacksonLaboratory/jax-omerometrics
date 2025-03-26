"""
server-up: check if an OMERO server is up.

Module with multiple functions for checking whether
an OMERO server is up and running properly.

"""
import ezomero
import requests
import signal
from ezomero import json_api


def handler(signum, frame):
    """Handle signal."""
    raise Exception("Blitz connection timeout")


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
        _, session, base_url = json_api.create_json_session(web_host=address, user=user, password=pwd)
        print("created session successfully")
    except Exception as e:
        print(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
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
