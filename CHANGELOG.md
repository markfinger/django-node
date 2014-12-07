Changelog
=========

### 0.2.0 (7/12/2014)

Most of the functions are now exposed from `django_node.node` and `django_node.npm`.

The Node.js API is now composed of...
- `django_node.node.is_installed`
- `django_node.node.version`
- `django_node.node.version_raw`
- `django_node.node.run`
- `django_node.node.ensure_installed`
- `django_node.node.ensure_version_gte`

The NPM API is now composed of...
- `django_node.npm.is_installed`
- `django_node.npm.version`
- `django_node.npm.version_raw`
- `django_node.npm.run`
- `django_node.npm.ensure_installed`
- `django_node.npm.ensure_version_gte`
- `django_node.npm.install`


### 0.1.0 (3/12/2014)

- Initial release