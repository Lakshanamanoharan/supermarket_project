import React, { useState } from 'react';
import { useSwipeable } from 'react-swipeable';

const SwipeableCartItem = ({ item, onRemove }) => {
  const [swiped, setSwiped] = useState(false);
  
  const handlers = useSwipeable({
    onSwipedLeft: () => {
      setSwiped(true);
      setTimeout(() => onRemove(item.name || item.tamil_name), 300);
    },
    trackMouse: true
  });

  return (
    <div className="swipe-item-container" {...handlers}>
      <div className="swipe-delete-bg">🗑️</div>
      <div className={`cart-item ${swiped ? 'swiped-left' : ''}`}>
        <div className="item-info">
          <h4>{item.name} {item.tamil_name ? `(${item.tamil_name})` : ''}</h4>
          <p>{item.quantity} {item.unit} x ₹{item.price_per_unit}</p>
        </div>
        <div className="item-price">₹{item.price_per_unit * item.quantity}</div>
      </div>
    </div>
  );
};

const Cart = ({ cart, onRemoveItem }) => {
  const total = cart.reduce((sum, item) => sum + (item.price_per_unit * item.quantity), 0);

  return (
    <div className="cart-panel">
      <h2 className="cart-header">🛒 Your Cart</h2>
      
      <div className="cart-items">
        {cart.length === 0 ? (
          <p style={{ color: '#667781', textAlign: 'center', marginTop: '2rem' }}>
            Your basket is empty.
          </p>
        ) : (
          cart.map((item, idx) => (
            <SwipeableCartItem key={item.id || idx} item={item} onRemove={onRemoveItem} />
          ))
        )}
      </div>

      <div className="cart-total">
        <div className="total-row">
          <span>Total</span>
          <span>₹{total}</span>
        </div>
        <button 
          className="checkout-btn" 
          disabled={cart.length === 0}
          onClick={() => alert("Proceeding to Secure Gateway...")}
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
};

export default Cart;
