// This service should cause a timeout exception to be raised

var service = function(request, response) {
	setTimeout(function() {
		response.send(500, 'timeout should have occurred already')
	}, 11000);
};

module.exports = service;