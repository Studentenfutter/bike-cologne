// Import JSON file with organisations

// Remove length limit for console output
const util = require('util')
util.inspect.defaultOptions.maxArrayLength = null; 

const fs = require('fs');
const {counters, data} = require('eco-counter-client')


counters(677)
.then((counters) => {
	const c = counters[13]
	return data(c.organisation.id, c.id, c.instruments, c.periodStart, c.periodEnd)
})
.then(console.log)
.catch(console.error)

