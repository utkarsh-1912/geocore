import fs from 'fs';
import path from 'path';

const schemaDir = path.resolve('electron-app/src/features/calculations/schemas');
const files = fs.readdirSync(schemaDir).filter(f => f.endsWith('.js') && f !== 'index.js');

const all = {};

for (const file of files) {
    const fullPath = path.join(schemaDir, file);
    let content = fs.readFileSync(fullPath, 'utf-8');
    
    // Replace imports with mock
    content = content.replace(/^import\s+.*?;\s*$/gm, '');
    content = 'const SOIL_PROFILE_DOCS = {}; const CALCULATION_GRID_DOCS = {};
' + content;
    
    const tmpPath = path.resolve('tests/_tmp_' + file);
    fs.writeFileSync(tmpPath, content);
    try {
        const mod = await import('file:///' + tmpPath.replace(/\\/g, '/'));
        for (const [expKey, expVal] of Object.entries(mod)) {
            if (expVal && typeof expVal === 'object') {
                for (const [funcName, schema] of Object.entries(expVal)) {
                    all[funcName] = {
                        sourceFile: file,
                        ...schema
                    };
                }
            }
        }
    } catch (e) {
        console.error('Error importing ' + file + ':', e.message);
    } finally {
        if (fs.existsSync(tmpPath)) fs.unlinkSync(tmpPath);
    }
}

fs.writeFileSync('tests/frontend_schemas_dump.json', JSON.stringify(all, null, 2));
console.log('Successfully exported ' + Object.keys(all).length + ' frontend schemas.');