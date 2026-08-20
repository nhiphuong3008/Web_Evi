// Syntax check for schedule.js
const fs = require('fs');
try {
    const code = fs.readFileSync('static/js/schedule.js', 'utf8');
    // Test parsing with Function constructor
    new Function(code);
    console.log('✅ static/js/schedule.js syntax is valid!');
} catch (e) {
    console.error('❌ Syntax error in schedule.js:', e.message);
}
