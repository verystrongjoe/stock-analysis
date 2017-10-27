"""
1) get
curl                            localhost:5050/hello.json
2) post
curl -d 'msg2flask=hello-flask' localhost:5050/hello.json
"""

import flask         as fl
import flask_restful as fr
import os

# I should ready flask_restful:
application = fl.Flask(__name__)
api         = fr.Api(application)
  
class Hello(fr.Resource):
  """
  This class should be a simple syntax demo.
  """
  def get(self):
    my_k_s = 'hello'
    my_v_s = 'world'
    return {my_k_s: my_v_s}

  # curl -d msg2flask=hello-flask  localhost:5050/hello.json
  def post(self):
    my_k_s    = 'post-hello'
    my_v_s    = 'world'
    curlmsg_s = fl.request.form['msg2flask']
    return {my_k_s: my_v_s, 'curlmsg': curlmsg_s}

api.add_resource(Hello, '/hello.json')
  
if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5050))
  application.run(host='0.0.0.0', port=port)
'bye'


