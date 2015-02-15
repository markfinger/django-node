var handler = function(req, res) {
	setTimeout(function() {
		res.send(500, 'timeout should have occurred already')
	}, 5000);
};

module.exports = handler;