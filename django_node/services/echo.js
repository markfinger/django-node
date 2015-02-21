var echo = function(request, response) {
	var echo = request.query.echo;

	if (!echo) {
		throw new Error('Missing `echo` param');
	}

	response.send(echo);
};

module.exports = echo;
