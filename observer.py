class Observer(object):
    # observers should override this to define behaviour
    def notify(self, event, id, data):
        pass


class Observable(object):
    def __init__(self):
        self.observers = []

    def addObserver(self, observer):
        self.observers.append(observer)

    def notifyObservers(self, event, id, data):
        for observer in self.observers:
            observer.notify(event, id, data)
