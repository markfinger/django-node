var http = require('http');
var fs = require('fs');
var argv = require('yargs').argv;
var express = require('express');
var bodyParser = require('body-parser')

var address = argv.address;
if (address === undefined) {
	throw new Error('No address was provided, ex: `--address 127.0.0.1`');
}

var port = argv.port;
if (port === undefined) {
	throw new Error('No port was provided, ex: `--port 0`');
}

var expectedStartupOutput = argv.expectedStartupOutput;
if (expectedStartupOutput === undefined) {
	throw new Error('No expected startup output was provided, ex: `--expected-startup-output "server has started"`');
}

var testEndpoint = argv.testEndpoint;
if (testEndpoint === undefined) {
	throw new Error('No test endpoint was provided, ex: `--test-endpoint "/__test__"`');
}

var expectedTestOutput = argv.expectedTestOutput;
if (expectedTestOutput === undefined) {
	throw new Error('No expected test output was provided, ex: `--expected-test-output "server has started"`');
}

var registerEndpoint = argv.registerEndpoint;
if (registerEndpoint === undefined) {
	throw new Error('No register endpoint was provided, ex: `--register-endpoint "/__register__"`');
}

var expectedRegisterOutput = argv.expectedRegisterOutput;
if (expectedRegisterOutput === undefined) {
	throw new Error('No expected register output was provided, ex: `--expected-register-output "Registered endpoint"`');
}

var app = express();

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }));

var server = app.listen(port, address, function() {
	console.log(expectedStartupOutput);
	var output = JSON.stringify(server.address());
	console.log(output);
});

var _registeredEndpoints = {};

app.get('/', function(req, res) {
	var output = 'django-node NodeServer'
	output += '<br><br>';
	output += 'Registered endpoints..';
	output += '<ul>';
	Object.keys(_registeredEndpoints).forEach(function(endpoint) {
		output += '<li>' + endpoint + '<li>';
	});
	output += '</ul>';
	res.send(output);
});

app.get(testEndpoint, function(req, res) {
	res.send(expectedTestOutput);
});

app.post(registerEndpoint, function(req, res) {
	var endpoint = req.body.endpoint;
	var pathToSource = req.body.path_to_source;

	if (!endpoint) {
		throw new Error('Malformed endpoint provided. Received "' + endpoint + '"');
	}
	if (['/', testEndpoint, registerEndpoint].indexOf(endpoint) !== -1) {
		throw new Error('Endpoint "' + endpoint + '" cannot be registered');
	}
	if (endpoint[0] !== '/') {
		throw new Error('Endpoints must start with a forward-slash, trying to register "' + endpoint + '"');
	}
	if (_registeredEndpoints[endpoint] !== undefined) {
		throw new Error('Endpoint "' + endpoint + '" has already been registered as ' + _registeredEndpoints[endpoint]);
	}
	if (!fs.existsSync(pathToSource)) {
		throw new Error(
			'Trying to register endpoint "' + endpoint + '" with source file "' + pathToSource +
			'", but the specified file does not exist'
		);
	}

	_registeredEndpoints[endpoint] = pathToSource;
	var handler = require(pathToSource);
	app.all(endpoint, handler);

	res.send(expectedRegisterOutput);
});