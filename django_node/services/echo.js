var service = function(data, response) {
	var echo = data.echo;

	if (!echo) {
		var err = 'Missing `echo` in data';
		response.status(500).send(err);
		console.error(new Error(err));
		return;
	}

	response.send(echo);
};

module.exports = service;
