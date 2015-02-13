var handler = function(req, res) {
	res.send(req.query.output);
};

module.exports = handler;