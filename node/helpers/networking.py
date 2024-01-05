'''
Networking Helper Modules
'''
import socket


def check_local_port_bind(port: int, verbose=False) -> bool:
    '''
    Check if a local port is available to bind or not
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        sock.bind(("0.0.0.0", port))
        result = True
    except:
        if verbose:
            print(f"Port {port} is in use.")
    sock.close()
    return result
