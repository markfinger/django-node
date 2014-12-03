class EnvironmentInterrogationException(Exception):
    pass


class MissingDependencyException(Exception):
    pass


class OutdatedVersionException(Exception):
    pass


class MalformedVersionInputException(Exception):
    pass