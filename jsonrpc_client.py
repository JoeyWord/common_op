# coding=utf-8
import requests
import json
def main():
    url = "http://127.0.0.1:4001/jsonrpc"
    headers = {"content-type":"application/json; charset=utf-8"}
    perform_data = {
                    "method":"desc",
                    "params":[1,2],
                    "jsonrpc":2.0,
                    "id":0
                }
    request = requests.post(url,data=json.dumps(perform_data),headers=headers)
    if not request.encoding:
        request.encoding = 'gbk'
    else:
        print("request encoding:",request.encoding)
    result = request.json()
    print("result={}".format(result))
    if "error" not in result:
        assert result["result"] == 3
    assert result["id"] == 0
    assert result["jsonrpc"]


if __name__=="__main__":
    main()
   