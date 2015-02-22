"""
Web service implementing simple publish/subscribe (probably
more like producer/consumer) protocol.
"""

import collections

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor


class SubscriptionService(object):
    """
    Factory: tracks created user and topics
    objects, makes them single instance (by name).
    """
    def __init__(self):
        self._topics = {}
        self._users = {}

    def getTopic(self, name):
        if name not in self._topics:
            self._topics[name] = Topic(name)

        return self._topics[name]

    def getUser(self, name):
        if name not in self._users:
            self._users[name] = User(name)

        return self._users[name]


class User(object):
    """
    User has number of mailboxes (queues)
    for each of the subscriptions.
    """
    def __init__(self, name):
        self.name = name
        self._mailboxes = {}

    def createMailbox(self, topic):
        self._mailboxes[topic.name] = collections.deque()

    def dropMailbox(self, topic):
        del self._mailboxes[topic.name]

    def putMailbox(self, topic, message):
        self._mailboxes[topic.name].append(message)

    def readMailbox(self, topic):
        return self._mailboxes[topic.name].popleft()


class Topic(object):
    """
    Topic tracks list of users who have
    subscribed for that topic.
    """
    def __init__(self, name):
        self.name = name
        self.subscriptions = set()

    def subscribe(self, user):
        self.subscriptions.add(user)
        user.createMailbox(self)

    def unsubscribe(self, user):
        if not user in self.subscriptions:
            return False

        self.subscriptions.remove(user)
        user.dropMailbox(self)
        return True

    def publish(self, message):
        for user in self.subscriptions:
            user.putMailbox(self, message)


class TopicResource(Resource):
    """
    /<user>/<topic>
    """

    def __init__(self, service, topic):
        Resource.__init__(self)
        self.service = service
        self.topic = topic

    def getChild(self, name, request):
        return UserResource(self.service, self.topic,
                            self.service.getUser(name))

    def render_POST(self, request):
        self.topic.publish(request.content.read())
        return ''


class UserResource(Resource):
    """
    /<user>
    """

    def __init__(self, service, topic, user):
        Resource.__init__(self)
        self.service = service
        self.topic = topic
        self.user = user

    def render_POST(self, request):
        self.topic.subscribe(self.user)
        return ''

    def render_DELETE(self, request):
        if not self.topic.unsubscribe(self.user):
            request.setResponseCode(404)
        return ''

    def render_GET(self, request):
        try:
            request.setHeader("Content-Type", "binary/octet-stream")
            return self.user.readMailbox(self.topic)
        except IndexError:
            request.setResponseCode(204)
        except KeyError:
            request.setResponseCode(404)

        return ''


class RootResource(Resource):
    """
    /
    """

    def __init__(self, service):
        Resource.__init__(self)
        self.service = service

    def getChild(self, name, request):
        return TopicResource(self.service, self.service.getTopic(name))


PORT = 3000

root = RootResource(SubscriptionService())
factory = Site(root)
reactor.listenTCP(PORT, factory)
print "Listening on :%d..." % (PORT, )
reactor.run()
