import XLSX from 'xlsx';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const OUTPUT_PATH = path.join(__dirname, '../inventory.xlsx');

const sampleData = [
  { id: 1, name: 'Apple', tamil_name: 'ஆப்பிள்', price_per_unit: 180, unit: 'kg', stock: 50, category: 'Fruits' },
  { id: 2, name: 'Banana', tamil_name: 'வாழைப்பழம்', price_per_unit: 50, unit: 'kg', stock: 100, category: 'Fruits' },
  { id: 3, name: 'Carrot', tamil_name: 'கேரட்', price_per_unit: 60, unit: 'kg', stock: 80, category: 'Vegetables' },
  { id: 4, name: 'Potato', tamil_name: 'உருளைக்கிழங்கு', price_per_unit: 40, unit: 'kg', stock: 200, category: 'Vegetables' },
  { id: 5, name: 'Rice', tamil_name: 'அரிசி', price_per_unit: 55, unit: 'kg', stock: 500, category: 'Grains' }
];

const worksheet = XLSX.utils.json_to_sheet(sampleData);
const workbook = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(workbook, worksheet, 'Products');

XLSX.writeFile(workbook, OUTPUT_PATH);

console.log(`Created sample inventory at: ${OUTPUT_PATH}`);
