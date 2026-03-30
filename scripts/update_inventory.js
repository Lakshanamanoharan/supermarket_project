import XLSX from 'xlsx';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const EXCEL_PATH = path.join(__dirname, '../inventory.xlsx');
const JSON_OUTPUT = path.join(__dirname, '../src/data/products.json');

console.log('--- Supermarket Inventory Updater ---');

if (!fs.existsSync(EXCEL_PATH)) {
  console.error(`Error: inventory.xlsx not found at ${EXCEL_PATH}`);
  console.log('Please place your Excel file in the project root named "inventory.xlsx"');
  process.exit(1);
}

try {
  const workbook = XLSX.readFile(EXCEL_PATH);
  const sheetName = workbook.SheetNames[0];
  const worksheet = workbook.Sheets[sheetName];
  const data = XLSX.utils.sheet_to_json(worksheet);

  // Standardize data format
  const standardizedData = data.map((item, index) => ({
    id: item.id || index + 1,
    name: item.name || item.ProductName || 'Unknown Product',
    tamil_name: item.tamil_name || item.TamilName || '',
    price_per_unit: parseFloat(item.price_per_unit || item.Price || 0),
    unit: item.unit || item.Unit || 'unit',
    stock: parseInt(item.stock || item.Stock || 0),
    category: item.category || 'General'
  }));

  fs.writeFileSync(JSON_OUTPUT, JSON.stringify(standardizedData, null, 2));

  console.log(`Successfully updated inventory!`);
  console.log(`Loaded ${standardizedData.length} products to ${JSON_OUTPUT}`);
} catch (err) {
  console.error('Error processing Excel file:', err.message);
}
