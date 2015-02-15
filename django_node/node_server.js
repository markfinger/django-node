var http = require('http');
var fs = require('fs');
var argv = require('yargs').argv;
var express = require('express');
var bodyParser = require('body-parser');

var getArg = function(arg, example) {
	var value = argv[arg];
	if (value === undefined) {
		var message = 'Missing argument "' + arg + '".';
		if (example) {
			message += ' Example: ' + example;
		}
		throw new Error(message);
	}
	return value;
};

var address = getArg('address', '--address 127.0.0.1');
var port = getArg('port', '--port 0');
var expectedStartupOutput = getArg('expectedStartupOutput', '--expected-startup-output "server has started"');
var testEndpoint = getArg('testEndpoint', '--test-endpoint "/__test__"');
var expectedTestOutput = getArg('expectedTestOutput', '--expected-test-output "server has started"');
var addServiceEndpoint = getArg('addServiceEndpoint', '--add-service-endpoint "/__add_service__"');
var expectedAddServiceOutput = getArg('expectedAddServiceOutput', '--expected-add-service-output "Added service"');
var getEndpointsEndpoint = getArg('getEndpointsEndpoint', '--get-endpoints-endpoint "/__get_endpoints__"');
var blacklistedEndpoints = getArg('blacklistedEndpoints', '--blacklisted-endpoints "["", "/"]');
blacklistedEndpoints = JSON.parse(blacklistedEndpoints);

var app = express();

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }));

var server = app.listen(port, address, function() {
	console.log(expectedStartupOutput);
});

var getEndpoints = function() {
	return app._router.stack.filter(function(obj) {
		return obj.route !== undefined
	}).map(function(obj) {
		return obj.route.path
	});
};

app.get('/', function(req, res) {
	var endpoints = getEndpoints().map(function(endpoint) {
		return '<li>' + endpoint + '</li>';
	});
	res.send('<h1>Endpoints</h1><ul>' + endpoints.join('') + '</ul>');
});

app.get(testEndpoint, function(req, res) {
	res.send(expectedTestOutput);
});

app.post(addServiceEndpoint, function(req, res) {
	var endpoint = req.body.endpoint;
	var pathToSource = req.body.path_to_source;

	if (!endpoint) {
		throw new Error('No endpoint provided');
	}
	if (blacklistedEndpoints.indexOf(endpoint) !== -1) {
		throw new Error('Endpoint "' + endpoint + '" cannot be added');
	}
	if (endpoint[0] !== '/') {
		throw new Error('Endpoints must start with a forward-slash, cannot add "' + endpoint + '"');
	}
	if (getEndpoints().indexOf(endpoint) !== -1) {
		throw new Error('Endpoint "' + endpoint + '" has already been added');
	}
	if (!fs.existsSync(pathToSource)) {
		throw new Error(
			'Trying to add endpoint "' + endpoint + '" with source file "' + pathToSource + '", ' +
			'but the specified file does not exist'
		);
	}

	var handler = require(pathToSource);
	app.get(endpoint, handler);

	res.send(expectedAddServiceOutput);
});

app.get(getEndpointsEndpoint, function(req, res) {
	res.send(JSON.stringify(getEndpoints()));
});

module.exports = {
	app: app,
	server: server
};