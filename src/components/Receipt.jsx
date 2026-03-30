import React from 'react';

const Receipt = ({ data, onClose }) => {
  if (!data) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="receipt-overlay">
      <div className="receipt-card">
        <div className="receipt-header">
          <h2>🧾 Supermarket Receipt</h2>
          <p>Order #{Math.floor(Math.random() * 100000)}</p>
          <p>{new Date().toLocaleString()}</p>
          <div className="receipt-delivery-badge" style={{
            marginTop: '0.5rem',
            padding: '0.4rem 0.8rem',
            borderRadius: '20px',
            background: data.delivery_mode === 'delivery' ? '#e8f5e9' : '#fff8e1',
            color: data.delivery_mode === 'delivery' ? '#2e7d32' : '#f57f17',
            fontWeight: '600',
            display: 'inline-block'
          }}>
            {data.delivery_mode === 'delivery' ? '🚚 Delivery' : '🏪 Store Pickup'}
          </div>
          {data.delivery_mode === 'delivery' && data.delivery_address && (
            <p style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#555' }}>
              📍 {data.delivery_address}
            </p>
          )}
        </div>
        
        <div className="receipt-items">
          {data.receipt_items.map((item, idx) => (
            <div key={idx} className="receipt-item-row">
              <span className="receipt-item-name">{item.name} x {item.quantity} {item.unit}</span>
              <span className="receipt-item-price">₹{item.price_per_unit * item.quantity}</span>
            </div>
          ))}
        </div>

        <div className="receipt-total">
          <h3>Total Paid</h3>
          <h3>₹{data.total_amount}</h3>
        </div>

        <div className="receipt-actions no-print">
          <button className="print-btn" onClick={handlePrint}>🖨️ Save PDF</button>
          <button className="close-btn" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default Receipt;
