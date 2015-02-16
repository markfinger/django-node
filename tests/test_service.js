var service = function(request, response) {
	// Returns the value of the output param
	response.send(request.query.output);
};

module.exports = service;