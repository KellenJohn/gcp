import functions_framework

@functions_framework.http
def hello_world(request):
    """
    Responds to any HTTP request.

    This function responds to incoming HTTP requests with a customizable message.
    If a 'message' parameter is provided as a query parameter or in the JSON body,
    it will be returned in the response. Otherwise, a default "Hello World!matayuuu!"
    message will be sent.

    Args:
        request (flask.Request): The incoming HTTP request object.

    Returns:
        str: The response message. If a 'message' parameter is provided, it will be returned.
             Otherwise, the default message will be returned.

    Example Usage:
        If you make a GET request to this function with a query parameter:
        /hello?message=Greetings

        The response will be:
        "Greetings"

        If you make a POST request with the following JSON body:
        {
            "message": "Custom Message"
        }

        The response will be:
        "Custom Message"

        If no 'message' parameter is provided, the response will be:
        "Hello World ~ Cloud Build"
    """
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World ~ Cloud Build'