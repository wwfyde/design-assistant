
const https = require('https');

const url = 'https://huaban.com/v3/ltnwxonyzk/collections/660662?limit=30';
const options = {
    headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://huaban.com/'
    }
};

https.get(url, options, (res) => {
    let data = '';
    res.on('data', (chunk) => { data += chunk; });
    res.on('end', () => {
        try {
            const json = JSON.parse(data);
            console.log('Top Keys:', Object.keys(json));
            if (json.boards) {
                console.log('Found boards array. Length:', json.boards.length);
                console.log('First board keys:', Object.keys(json.boards[0]));
            } else if (json.pins) {
                console.log('Found pins array. Length:', json.pins.length);
                console.log('First pin keys:', Object.keys(json.pins[0]));
                console.log('First pin raw_text:', json.pins[0].raw_text);
            } else {
                console.log('No boards or pins found.');
            }
        } catch (e) {
            console.error(e.message);
        }
    });
}).on('error', (e) => {
    console.error(e);
});
