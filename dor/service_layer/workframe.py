def workframe(func):
    def wrap():
        func()

    return wrap
