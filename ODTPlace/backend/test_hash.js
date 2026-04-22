const crypto = require('crypto');
const storedHash = 'pbkdf2_sha256$1000000$4gazoTkeYLKIzfrLqSbMoR$2aArCCWphRsnnxzRe+YFZbGFAjD07EIgt+M6midszEk=';
const inputPassword = '123';

const parts = storedHash.split('$');
const iterations = parseInt(parts[1]);
const salt = parts[2];
const expectedHash = parts[3];

console.log('parts:', parts);
console.log('iterations:', iterations);
console.log('salt:', salt);
console.log('expectedHash:', expectedHash);

const derived = crypto.pbkdf2Sync(inputPassword, salt, iterations, 32, 'sha256');
const computedHash = derived.toString('base64');

console.log('Expected:', expectedHash);
console.log('Computed:', computedHash);
console.log('Match:', computedHash === expectedHash);