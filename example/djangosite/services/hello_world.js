var service = function(request, response) {
	var greeting = 'Hello, ' + request.query.name + '!';
	response.send(greeting);
};

module.exports = service;