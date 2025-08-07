import azure.functions as func
from .main import app
from mangum import Mangum

asgi_handler = Mangum(app)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return asgi_handler(req, context)
