var service = function(data, res) {
	var greeting = 'Hello, ' + data.name + '!';
	res.end(greeting);
};

module.exports = service;