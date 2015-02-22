# Publish-Subscribe Service

This is example service, please ignore it :)

## Running

Python 2.7 (might work under other versions, not tested), pip, virtualenv:

    make


## Tests

With service running (on default localhost:3000):

    make test

This performs simple integration testing.

## Some notes

Implementation uses Twisted Web to implement REST API, due to Twisted nature we don't
need any kind of locking here.

Some things left out:

 * topics and users are never deleted, even if they are not used anymore
 * some kind of resource control: currently it's easy to eat all memory simply by
   touching some resources (topics, users)
 * scalability (doesn't scale beyond one server)