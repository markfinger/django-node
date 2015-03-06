class ErrorInterrogatingEnvironment(Exception):
    pass


class MissingDependency(Exception):
    pass


class OutdatedDependency(Exception):
    pass


class MalformedVersionInput(Exception):
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


class NodeServiceError(Exception):
    pass


class ServiceSourceDoesNotExist(Exception):
    pass


class MalformedServiceName(Exception):
    pass


class ServerConfigMissingService(Exception):
    pass


class MalformedServiceConfig(Exception):
    pass


class ModuleDoesNotContainAnyServices(Exception):
    pass