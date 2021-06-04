import socket

HOST_NAME = socket.gethostname()


def is_docker_server(host_name=HOST_NAME):
    return host_name == 'jd-arvin'


def get_host_name():
    return HOST_NAME
