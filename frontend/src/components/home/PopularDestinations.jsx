import { MapPin, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const PopularDestinations = () => {
  const destinations = [
    {
      city: 'Mumbai',
      code: 'BOM',
      image: 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=400&h=300&fit=crop',
      description: 'The City of Dreams',
      priceFrom: 2499,
    },
    {
      city: 'Delhi',
      code: 'DEL',
      image: 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=400&h=300&fit=crop',
      description: "India's Capital",
      priceFrom: 2299,
    },
    {
      city: 'Bangalore',
      code: 'BLR',
      image: 'https://images.unsplash.com/photo-1596176530529-78163a4f7af2?w=400&h=300&fit=crop',
      description: 'Silicon Valley of India',
      priceFrom: 2699,
    },
    {
      city: 'Goa',
      code: 'GOI',
      image: 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=400&h=300&fit=crop',
      description: 'Beach Paradise',
      priceFrom: 3199,
    },
    {
      city: 'Jaipur',
      code: 'JAI',
      image: 'https://images.unsplash.com/photo-1477587458883-47145ed94245?w=400&h=300&fit=crop',
      description: 'The Pink City',
      priceFrom: 2899,
    },
    {
      city: 'Kolkata',
      code: 'CCU',
      image: 'https://images.unsplash.com/photo-1558431382-27e303142255?w=400&h=300&fit=crop',
      description: 'City of Joy',
      priceFrom: 2599,
    },
  ];

  return (
    <section className="destinations-section">
      <div className="destinations-container">
        <div className="section-header">
          <h2>Popular Destinations</h2>
          <p>Discover amazing places with our best flight deals</p>
        </div>

        <div className="destinations-grid">
          {destinations.map((destination, index) => (
            <Link 
              key={index}
              to={`/flights?destination=${destination.code}`}
              className="destination-card"
            >
              <div className="destination-image">
                <img src={destination.image} alt={destination.city} />
                <div className="destination-overlay">
                  <span className="view-flights">
                    View Flights <ArrowRight size={16} />
                  </span>
                </div>
              </div>
              <div className="destination-info">
                <div className="destination-header">
                  <h3>{destination.city}</h3>
                  <span className="destination-code">{destination.code}</span>
                </div>
                <p className="destination-desc">
                  <MapPin size={14} />
                  {destination.description}
                </p>
                <div className="destination-price">
                  <span className="price-label">From</span>
                  <span className="price-value">₹{destination.priceFrom.toLocaleString()}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PopularDestinations;
