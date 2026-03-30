import React from 'react';
import * as XLSX from 'xlsx';

function InventoryManager({ onInventoryUpdate }) {
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (evt) => {
      const bstr = evt.target.result;
      const wb = XLSX.read(bstr, { type: 'binary' });
      const wsname = wb.SheetNames[0];
      const ws = wb.Sheets[wsname];
      const data = XLSX.utils.sheet_to_json(ws);
      
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

      onInventoryUpdate(standardizedData);
      alert(`Success! Loaded ${standardizedData.length} products from Excel.`);
    };
    reader.readAsBinaryString(file);
  };

  return (
    <div className="inventory-manager">
      <label className="upload-btn">
        📂 Upload Excel Inventory
        <input 
          type="file" 
          accept=".xlsx, .xls" 
          onChange={handleFileUpload} 
          style={{ display: 'none' }}
        />
      </label>
      <div className="inventory-hint">
        Supports .xlsx files with columns: id, name, tamil_name, price_per_unit, unit, stock
      </div>
    </div>
  );
}

export default InventoryManager;
