import ezomero
import requests

def check_web_response(address='htps://images.jax.org'):
    r = requests.get(address)
    return r.status_code == requests.codes.ok


def check_ldap_login(user, pwd, address='bhomero01lp.jax.org', port=4064, secure=True, group=''):
    conn = ezomero.connect(user=user, password=pwd, host=address, port=port, secure=secure, group=group)
    ret = (conn != None)
    conn.close()
    return ret


def check_img_return(img_id, user, pwd, address='bhomero01lp.jax.org', port=4064, secure=True, group=''):
    conn = ezomero.connect(user=user, password=pwd, host=address, port=port, secure=secure, group=group)
    img, arr = ezomero.get_image(conn, img_id)
    conn.close()
    return img != None
