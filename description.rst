========
Sharrock
========

Sharrock is a Python-based RPC framework design for easy integration into Django.  It was created because of my frustrations with the way that many existing REST-based RPC frameworks work.  Sharrock is based on the idea that while sometimes it is a good idea to represent RPC as resources (the REST model), other times plain old function calls are what you want.

The central idea of Sharrock is the *descriptor*, a declarative model that both represents the function call at the code level, and additionally provides automatically generated API documentation.

Following the tradition of naming Django projects after Jazz musicians, Sharrock is named after `Sonny Sharrock(http://en.wikipedia.org/wiki/Sonny_Sharrock`_.
