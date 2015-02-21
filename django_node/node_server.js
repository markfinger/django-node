var http = require('http');
var fs = require('fs');
var argv = require('yargs').argv;
var express = require('express');

var configFile = argv.c || argv.config;

if (!configFile) {
	throw new Error('No config file specified. Use --config to specify a path to a config file');
}

var config = JSON.parse(fs.readFileSync(configFile));

var address = config.address;
var port = config.port;
var startupOutput = config.startup_output;
var services = config.services;

if (!address) {
	throw new Error('No address defined in config');
}
if (!port) {
	throw new Error('No port defined in config');
}
if (!startupOutput) {
	throw new Error('No startup_output defined in config');
}
if (!services) {
	throw new Error('No services defined in config');
}

var app = express();

var server = app.listen(port, address, function() {
	console.log(startupOutput);
});

app.get('/', function(req, res) {
	var endpoints = app._router.stack.filter(function(obj) {
		return obj.route !== undefined
	}).map(function(obj) {
		return '<li>' + obj.route.path + '</li>';
	});
	res.send('<h1>Endpoints</h1><ul>' + endpoints.join('') + '</ul>');
});

services.forEach(function(service) {
	try {
		app.get(service.name, require(service.path_to_source));
	} catch(e) {
		throw new Error('Failed to add service "' + JSON.stringify(service) + '". ' + e.message);
	}
});

module.exports = {
	app: app,
	server: server
};