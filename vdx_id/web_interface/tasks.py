from web_interface.sockets import send_notification as send_socket_notification


def send_notification_task(**payload):
    send_socket_notification(**payload)
