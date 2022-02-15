# coding=utf-8
from werkzeug.serving import run_simple
from werkzeug.wrappers import Response,Request
from jsonrpc import JSONRPCResponseManager,dispatcher


app1=Response("hello,werkzeug!")
@dispatcher.add_method
def params(**kwargs):
    return kwargs["param1"] + kwargs["param2"]

@dispatcher.method_map
def descrease(**kwargs):
    return kwargs["param1"]-kwargs["param2"]

@Request.application
def app(request):
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a,b: a+b
    dispatcher["desc"] = lambda a,b: a-b
    response = JSONRPCResponseManager.handle(request.data,dispatcher)
    return Response(response=response.json,mimetype="application/json")

if __name__ == "__main__":
    #run_simple("localhost",4000,app1)
    run_simple("localhost",4001,app)