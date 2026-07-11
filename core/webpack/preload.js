const path = require('path');
const fs = require('fs-extra');

const outputPath = path.resolve(__dirname, '../assets/bundles'); // Replace with the actual public assets path
const configPath = path.resolve(__dirname, 'package-copy.json');

async function copyLibs(params) {
    try {
        const configContent = await fs.readFile(configPath, 'utf-8');
        const { packagesToCopy } = JSON.parse(configContent);
    
        for (const packageName of packagesToCopy) {
            const destPackagePath = path.join(outputPath, 'libs', packageName);
    
            const sourcePath = fs.existsSync(path.join(__dirname, '../node_modules', packageName, 'dist'))
                ? path.join(__dirname, '../node_modules', packageName, 'dist')
                : path.join(__dirname, '../node_modules', packageName);
    
            await fs.access(sourcePath, fs.constants.F_OK);
            await fs.copy(sourcePath, destPackagePath);
        }
    } catch (error) {
        console.error('Error copying and renaming packages:', error);
    }
}

copyLibs();