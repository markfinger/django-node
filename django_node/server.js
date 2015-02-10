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
var addEndpoint = getArg('addEndpoint', '--add-endpoint "/__register__"');
var expectedAddOutput = getArg('expectedAddOutput', '--expected-add-output "Registered endpoint"');

var app = express();

// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }));

var server = app.listen(port, address, function() {
	console.log(expectedStartupOutput);
	var output = JSON.stringify(server.address());
	console.log(output);
});

var _endpointsAdded = {};

app.all('/', function(req, res) {
	var output = '<h1>django-node NodeServer</h1>';
	output += '<br><br>';
	output += '<h2>Registered endpoints</h2>';
	output += '<ul>';
	Object.keys(_endpointsAdded).forEach(function(endpoint) {
		output += '<li>' + endpoint + '<li>';
	});
	output += '</ul>';
	res.send(output);
});

app.all(testEndpoint, function(req, res) {
	res.send(expectedTestOutput);
});

app.post(addEndpoint, function(req, res) {
	var endpoint = req.body.endpoint;
	var pathToSource = req.body.path_to_source;

	if (!endpoint) {
		throw new Error('Malformed endpoint provided. Received "' + endpoint + '"');
	}
	if (['/', testEndpoint, addEndpoint].indexOf(endpoint) !== -1) {
		throw new Error('Endpoint "' + endpoint + '" cannot be added');
	}
	if (endpoint[0] !== '/') {
		throw new Error('Endpoints must start with a forward-slash, cannot add "' + endpoint + '"');
	}
	if (_endpointsAdded[endpoint] !== undefined) {
		throw new Error('Endpoint "' + endpoint + '" has already been added as ' + _endpointsAdded[endpoint]);
	}
	if (!fs.existsSync(pathToSource)) {
		throw new Error(
			'Trying to add endpoint "' + endpoint + '" with source file "' + pathToSource + '", ' +
			'but the specified file does not exist'
		);
	}

	_endpointsAdded[endpoint] = pathToSource;
	var handler = require(pathToSource);
	app.all(endpoint, handler);

	res.send(expectedAddOutput);
});