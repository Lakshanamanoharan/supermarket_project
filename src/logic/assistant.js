import productsData from '../data/products.json';
import Fuse from 'fuse.js';

class SupermarketAssistant {
  constructor() {
    this.inventory = productsData;
    this.cart = [];
    this.state = 'idle'; // idle, confirming_add, confirming_checkout
    this.pendingItem = null;
    this.preferredLanguage = null; // null means auto-detect
    
    this.initFuse();
  }

  initFuse() {
    const options = {
      keys: ['name', 'tamil_name'],
      threshold: 0.4, // Increased from 0.3 to be more forgiving of typos
      includeScore: true,
      ignoreLocation: true // Search anywhere in the string
    };
    this.fuse = new Fuse(this.inventory, options);
  }

  setInventory(newInventory) {
    this.inventory = newInventory;
    this.initFuse();
  }

  processMessage(message) {
    let text = message.toLowerCase().trim();
    const isTamil = this.preferredLanguage === 'ta' || (this.preferredLanguage === null && /[^\x00-\x7F]/.test(text));

    // 1. Handle Greetings
    if (this.isGreeting(text)) {
      return {
        text: isTamil ? "வணக்கம்! நான் உங்கள் சூப்பர் மார்க்கெட் உதவியாளர். நான் உங்களுக்கு எப்படி உதவ முடியும்?" : "Hello! I am your supermarket assistant. How can I help you today?"
      };
    }

    // 2. Handle Gratitude
    if (this.isGratitude(text)) {
      return {
        text: isTamil ? "மிக்க மகிழ்ச்சி! உங்களுக்கு வேறு ஏதேனும் உதவி தேவையா?" : "You're very welcome! Do you need anything else?"
      };
    }

    // 3. Handle Confirmation Flow
    if (this.state === 'confirming_add') {
      if (text.includes('yes') || text.includes('ஆம்') || text.includes('சரி') || text.includes('add')) {
        return this.confirmAddToCart(isTamil);
      } else if (text.includes('no') || text.includes('இல்லை') || text.includes('வேண்டாம்')) {
        this.state = 'idle';
        this.pendingItem = null;
        return { text: isTamil ? "சரி, நான் அதைச் சேர்க்கவில்லை. வேறு ஏதேனும் வேண்டுமா?" : "Okay, I won't add that. Anything else?" };
      }
    }

    if (this.state === 'confirming_checkout') {
      if (text.includes('yes') || text.includes('ஆம்') || text.includes('சரி') || text.includes('confirm')) {
        return this.confirmCheckout(isTamil);
      } else {
        this.state = 'idle';
        return { text: isTamil ? "சரி, ஆர்டர் ரத்து செய்யப்பட்டது. வேறு ஏதேனும் வேண்டுமா?" : "Okay, order cancelled. Anything else?" };
      }
    }


    // 4. Handle Removal Request
    if (text.includes('remove') || text.includes('delete') || text.includes('நீக்கு') || text.includes('வேண்டாம்')) {
      const cleanText = text.replace(/remove|delete|நீக்கு|வேண்டாம்|please|தயவுசெய்து/g, '').trim();
      return this.handleRemoval(cleanText, isTamil);
    }

    // 5. Handle Checkout Request
    if (text.includes('checkout') || text.includes('payment') || text.includes('பணம்') || text.includes('செக் அவுட்') || 
        text.includes("that's all") || text.includes("finished") || text.includes("எல்லாம்") || text.includes("முடிந்தது")) {
      return this.handleCheckoutRequest(isTamil);
    }

    // 5b. Handle Stock Inquiry (Verification)
    if (text.includes('stock') || text.includes('இருப்பு')) {
      const searchResult = this.fuse.search(text.replace(/stock|இருப்பு/g, '').trim());
      if (searchResult.length > 0) {
        const product = searchResult[0].item;
        return { 
          text: isTamil 
            ? `${product.tamil_name || product.name} இப்போது ${product.stock} ${product.unit} இருப்பில் உள்ளது.`
            : `We have ${product.stock} ${product.unit} of ${product.name} in stock.`
        };
      }
    }



    // 6. Handle Product Search & Quantity
    const quantityMatch = text.match(/(\d+)\s*(kg|kilo|pkt|packet|லிட்டர்|லி|கிலோ)/i) || text.match(/(\d+)/);
    const quantity = quantityMatch ? quantityMatch[1] : 1;
    
    // Strip common filler words before searching
    const searchTerm = text.replace(/add|want|need|please|வாங்க|வேண்டும்|சேர்/g, '').trim();
    
    // Fuzzy search for product
    const searchResult = this.fuse.search(searchTerm || text);
    if (searchResult.length > 0) {
      const product = searchResult[0].item;
      return this.initiateAddToCart(product, quantity, isTamil);
    }


    // Default response for unhandled queries
    return {
      text: isTamil ? "மன்னிக்கவும், எனக்குப் புரியவில்லை. நான் தக்காளி, வெங்காயம் போன்ற பொருட்களைச் சேர்க்க அல்லது நீக்க உங்களுக்கு உதவ முடியும்." : "I'm sorry, I didn't catch that. I can help you add or remove items like tomatoes, onions, etc.",
      cart: this.cart
    };
  }

  isGreeting(text) {
    const greetings = ['hi', 'hello', 'hey', 'vanakkam', 'வணக்கம்'];
    return greetings.some(g => text.includes(g));
  }

  isGratitude(text) {
    const gratitude = ['thanks', 'thank you', 'thankyou', 'nandri', 'நன்றி'];
    return gratitude.some(g => text.includes(g));
  }

  initiateAddToCart(product, quantity, isTamil) {
    if (product.stock <= 0) {
      return {
        text: isTamil 
          ? `மன்னிக்கவும், ${product.tamil_name || product.name} தற்போது கைவசம் இல்லை (Out of stock).`
          : `I'm sorry, ${product.name} is currently out of stock.`
      };
    }

    if (quantity > product.stock) {
      return {
        text: isTamil 
          ? `மன்னிக்கவும், எங்களிடம் ${product.stock} ${product.unit} ${product.tamil_name || product.name} மட்டுமே உள்ளது. தயவுசெய்து இந்த அளவிற்குக் குறைவாக ஆர்டர் செய்யவும்.`
          : `I'm sorry, we only have ${product.stock} ${product.unit} of ${product.name} in stock. Please order within this quantity.`
      };
    }

    const totalCost = product.price_per_unit * quantity;
    this.pendingItem = { ...product, quantity, totalCost };
    this.state = 'confirming_add';

    const productName = isTamil && product.tamil_name ? product.tamil_name : product.name;
    const unit = isTamil ? (product.unit === 'kg' ? 'கிலோ' : 'பாக்கெட்') : product.unit;

    return {
      text: isTamil 
        ? `${quantity} ${unit} ${productName} விலை ₹${totalCost}. நான் இதை உங்கள் கூடையில் (cart) சேர்க்கவா?`
        : `${quantity} ${unit} of ${productName} costs ₹${totalCost}. Shall I add it to your cart?`
    };
  }


  confirmAddToCart(isTamil) {
    const existingIndex = this.cart.findIndex(item => item.id === this.pendingItem.id);
    if (existingIndex > -1) {
      this.cart[existingIndex].quantity = parseInt(this.cart[existingIndex].quantity) + parseInt(this.pendingItem.quantity);
    } else {
      this.cart.push(this.pendingItem);
    }

    this.state = 'idle';
    this.pendingItem = null;

    return {
      text: isTamil ? "நிச்சயமாக, உங்கள் கூடையில் சேர்க்கப்பட்டது. உங்களுக்கு வேறு ஏதேனும் வேண்டுமா?" : "Sure, added to your cart. Do you need anything else?",
      cart: this.cart
    };
  }

  handleRemoval(text, isTamil) {
    if (this.cart.length === 0) {
      return {
        text: isTamil ? "உங்கள் கூடை காலியாக உள்ளது." : "Your cart is empty.",
        cart: this.cart
      };
    }

    // Fuzzy search within the cart
    const cartFuse = new Fuse(this.cart, {
      keys: ['name', 'tamil_name'],
      threshold: 0.4
    });

    const searchResult = cartFuse.search(text);

    if (searchResult.length > 0) {
      const cartItem = searchResult[0].item;
      this.cart = this.cart.filter(item => item.id !== cartItem.id);
      const itemName = isTamil && cartItem.tamil_name ? cartItem.tamil_name : cartItem.name;
      return {
        text: isTamil ? `சரி, ${itemName} உங்கள் கூடையில் இருந்து நீக்கப்பட்டது.` : `Ok, ${itemName} removed from your cart.`,
        cart: this.cart
      };
    }

    return {
      text: isTamil ? "மன்னிக்கவும், அந்தப் பொருள் உங்கள் கூடையில் இல்லை." : "Sorry, I couldn't find that item in your cart.",
      cart: this.cart
    };
  }


  handleCheckoutRequest(isTamil) {
    if (this.cart.length === 0) {
      return {
        text: isTamil ? "உங்கள் கூடை காலியாக உள்ளது. தயவுசெய்து சில பொருட்களைச் சேர்க்கவும்." : "Your cart is empty. Please add some items first."
      };
    }

    const total = this.cart.reduce((sum, item) => sum + (item.price_per_unit * item.quantity), 0);
    this.state = 'confirming_checkout';
    
    return {
      text: isTamil 
        ? `உங்கள் மொத்தத் தொகை ₹${total}. நான் பணப்பரிவர்த்தனையை உறுதிப்படுத்தலாமா?`
        : `Your total is ₹${total}. Shall I confirm your purchase?`
    };
  }

  confirmCheckout(isTamil) {
    // Deduct stock from inventory
    this.cart.forEach(cartItem => {
      const inventoryItem = this.inventory.find(item => item.id === cartItem.id);
      if (inventoryItem) {
        inventoryItem.stock -= cartItem.quantity;
      }
    });

    const summary = this.cart.map(item => `${item.quantity} ${item.unit} ${isTamil ? (item.tamil_name || item.name) : item.name}`).join(', ');
    this.cart = [];
    this.state = 'idle';

    return {
      text: isTamil 
        ? `மிக்க நன்றி! உங்கள் ஆர்டர் (${summary}) உறுதிப்படுத்தப்பட்டது. இருப்புகள் (stock) புதுப்பிக்கப்பட்டுள்ளன.`
        : `Thank you! Your order for ${summary} is confirmed. Stock levels have been updated.`,
      cart: [],
      action: 'checkout_success'
    };
  }
}



export default new SupermarketAssistant();

