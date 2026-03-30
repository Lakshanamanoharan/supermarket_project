import assistant from '../src/logic/assistant.js';

console.log('--- Testing Assistant Logic ---');

// Set a known inventory
assistant.setInventory([
  { id: 1, name: 'Apple', tamil_name: 'ஆப்பிள்', price_per_unit: 100, unit: 'kg', stock: 50, category: 'Fruits' }
]);

console.log('\n1. Test asking for too much stock (60kg of Apple)');
let res = assistant.processMessage('add 60kg apple');
console.log('Bot:', res.text);

console.log('\n2. Test asking for exact stock (50kg of Apple)');
res = assistant.processMessage('add 50kg apple');
console.log('Bot:', res.text);
assistant.processMessage('yes'); // Confirm add

console.log('\n3. Checkout 50kg of Apple');
res = assistant.processMessage('checkout');
console.log('Bot:', res.text);
res = assistant.processMessage('yes'); // Confirm checkout
console.log('Bot:', res.text);

console.log('\n4. Test asking for out of stock item (Apple)');
res = assistant.processMessage('add 1kg apple');
console.log('Bot:', res.text);
