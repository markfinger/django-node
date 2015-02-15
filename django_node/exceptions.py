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


class DynamicImportError(Exception):
    pass


class NodeServerStartError(Exception):
    pass


class NodeServerAddressInUseError(Exception):
    pass


class NodeServerConnectionError(Exception):
    pass


class NodeServerTimeoutError(Exception):
    pass


class NodeServerError(Exception):
    pass


class ErrorAddingService(Exception):
    pass