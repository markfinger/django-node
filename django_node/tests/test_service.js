var handler = function(req, res) {
	// Returns the value of the output param
	res.send(req.query.output);
};

module.exports = handler;