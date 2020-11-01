//  Bonn: { id: 4701, name: 'Stadt Bonn ' }
//  Köln: { id: 677, name: 'Dauerzählstellen Radverkehr Köln' },
// Düsseldorf:  { id: 857, name: 'Landeshaupstadt Düsseldorf' }

// Return all counters in Köln

const {counters, data} = require('eco-counter-client')
const fs = require('fs').promises;


counters(677) // Köln
.then(console.log)
.catch(console.error)