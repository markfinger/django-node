var error = function(request, response) {
	throw new Error('Error service')
};

module.exports = error;