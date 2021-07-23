import ezomero
import requests

def check_web_response(address='https://images.jax.org'):
    r = requests.get(address)
    return r.status_code == requests.codes.ok


def check_ldap_login(user, pwd, address='bhomero01lp.jax.org', port=4064, secure=True, group=''):
    ret = False
    try:
        conn = ezomero.connect(user=user, password=pwd, host=address, port=port, secure=secure, group=group)
        ret = (conn != None)
        conn.close()
    except AttributeError:
        pass
    return ret


def check_img_return(img_id, user, pwd, address='bhomero01lp.jax.org', port=4064, secure=True, group=''):
    ret = False
    try:
        conn = ezomero.connect(user=user, password=pwd, host=address, port=port, secure=secure, group=group)
        img, _ = ezomero.get_image(conn, img_id)
        conn.close()
        ret = (img != None)
    except AttributeError:
        pass
    return ret
    
