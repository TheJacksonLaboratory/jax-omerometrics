"""
server-up: check if an OMERO server is up.

Module with multiple functions for checking whether
an OMERO server is up and running properly.

"""
import ezomero
import requests


def check_web_response(address='https://images.jax.org'):
    """Check whether a web server is returning code 200."""
    r = requests.get(address)
    return r.status_code == requests.codes.ok


def check_ldap_login(user, pwd, address='bhomero01lp.jax.org',
                     port=4064, secure=True, group=''):
    """Check whether an LDAP user can log into OMERO.server."""
    ret = False
    try:
        conn = ezomero.connect(user=user, password=pwd, host=address,
                               port=port, secure=secure, group=group)
        ret = (conn is not None)
        conn.close()
    except AttributeError:
        pass
    return ret


def check_img_return(img_id, user, pwd, address='bhomero01lp.jax.org',
                     port=4064, secure=True, group=''):
    """Check whether an OMERO server is returning an image when asked."""
    ret = False
    try:
        conn = ezomero.connect(user=user, password=pwd, host=address,
                               port=port, secure=secure, group=group)
        img, _ = ezomero.get_image(conn, img_id)
        conn.close()
        ret = (img is not None)
    except AttributeError:
        pass
    return ret
