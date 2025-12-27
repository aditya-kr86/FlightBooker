import { useState } from 'react';
import { Send, CheckCircle } from 'lucide-react';

const Newsletter = () => {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setSubscribed(true);
    setLoading(false);
    setEmail('');
  };

  return (
    <section className="newsletter-section">
      <div className="newsletter-container">
        <div className="newsletter-content">
          <h2>Get Exclusive Deals</h2>
          <p>
            Subscribe to our newsletter and be the first to know about 
            amazing flight deals, special offers, and travel tips.
          </p>
        </div>

        {subscribed ? (
          <div className="newsletter-success">
            <CheckCircle size={48} />
            <h3>Thanks for subscribing!</h3>
            <p>You'll receive our best deals in your inbox soon.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="newsletter-form">
            <div className="input-group">
              <input
                type="email"
                placeholder="Enter your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <button type="submit" disabled={loading}>
                {loading ? (
                  'Subscribing...'
                ) : (
                  <>
                    Subscribe <Send size={18} />
                  </>
                )}
              </button>
            </div>
            <p className="newsletter-note">
              We respect your privacy. Unsubscribe anytime.
            </p>
          </form>
        )}
      </div>
    </section>
  );
};

export default Newsletter;
