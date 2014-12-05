class ErrorInterrogatingEnvironment(Exception):
    pass


class MissingDependency(Exception):
    pass


class OutdatedDependency(Exception):
    pass


class MalformedVersionInput(Exception):
    pass


class NpmInstallError(Exception):
    pass


class NpmInstallArgumentsError(Exception):
    pass


class NpmInstallDisallowed(Exception):
    pass