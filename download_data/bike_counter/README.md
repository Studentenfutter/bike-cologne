The data is obtained by utilizing the [eco-counter client](https://github.com/derhuerst/eco-counter-client/), which is a npm module.
A organasation id has to be provided - for Cologne this is 677.
All counters in an organisation (=city) can be retrieved by using `node counters.js`.
Sadly I dont have JavaScript-Skills and could not figure out how to save the data to a file using the promise object that gets returned.
Any help would be appreciated here, as a dirty workaround I called `data.js` from the terminal and saved the console output to a file, e.g. `node data.js > 1.json`
