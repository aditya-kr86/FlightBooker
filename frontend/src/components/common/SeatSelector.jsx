import { useState, useEffect } from 'react';
import { AlertCircle, Loader2, Info, User } from 'lucide-react';
import api from '../../api/config';
import './SeatSelector.css';

/**
 * SeatSelector Component - Interactive aircraft seat map for seat selection
 * 
 * Props:
 * - flightId: ID of the flight
 * - seatClass: Filter by seat class (ECONOMY, BUSINESS, etc.)
 * - passengerCount: Number of passengers to select seats for
 * - passengers: Array of passenger objects with names
 * - selectedSeats: Array of already selected seat IDs
 * - onSeatSelect: Callback when seats are selected (receives array of seat objects)
 * - basePrice: Base price per passenger (for surcharge display)
 */
const SeatSelector = ({ 
  flightId, 
  seatClass = 'ECONOMY',
  passengerCount = 1,
  passengers = [],
  selectedSeats = [],
  onSeatSelect,
  basePrice = 0
}) => {
  const [seatMap, setSeatMap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentlySelected, setCurrentlySelected] = useState(selectedSeats);
  const [activePassengerIndex, setActivePassengerIndex] = useState(0);

  // Fetch seat map on mount
  useEffect(() => {
    const fetchSeatMap = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await api.get(`/seats/map/${flightId}`, {
          params: { seat_class: seatClass }
        });
        setSeatMap(response.data);
      } catch (err) {
        console.error('Failed to fetch seat map:', err);
        setError('Failed to load seat map. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (flightId) {
      fetchSeatMap();
    }
  }, [flightId, seatClass]);

  // Initialize selected seats from props
  useEffect(() => {
    if (selectedSeats.length > 0) {
      setCurrentlySelected(selectedSeats);
    }
  }, [selectedSeats]);

  // Handle seat click
  const handleSeatClick = (seat) => {
    if (!seat.is_available) return;

    setCurrentlySelected(prev => {
      const isAlreadySelected = prev.some(s => s.id === seat.id);
      
      if (isAlreadySelected) {
        // Deselect this seat
        const newSelection = prev.filter(s => s.id !== seat.id);
        // Move to first unassigned passenger
        const nextIndex = newSelection.length < passengerCount ? newSelection.length : passengerCount - 1;
        setActivePassengerIndex(Math.max(0, nextIndex));
        return newSelection;
      } else if (prev.length < passengerCount) {
        // Select this seat for current passenger
        const newSelection = [...prev, seat];
        // Move to next passenger
        if (activePassengerIndex < passengerCount - 1) {
          setActivePassengerIndex(activePassengerIndex + 1);
        }
        return newSelection;
      }
      
      return prev;
    });
  };

  // Notify parent of selection changes
  useEffect(() => {
    if (onSeatSelect) {
      onSeatSelect(currentlySelected);
    }
  }, [currentlySelected, onSeatSelect]);

  // Get seat status class
  const getSeatClass = (seat) => {
    const isSelected = currentlySelected.some(s => s.id === seat.id);
    const selectedIndex = currentlySelected.findIndex(s => s.id === seat.id);
    
    if (!seat.is_available) return 'seat unavailable';
    if (isSelected) return `seat selected passenger-${selectedIndex + 1}`;
    return `seat available ${seat.seat_position}`;
  };

  // Calculate total surcharge for selected seats
  const getTotalSurcharge = () => {
    return currentlySelected.reduce((sum, seat) => sum + (seat.surcharge || 0), 0);
  };

  // Get surcharge label
  const getSurchargeLabel = (position) => {
    if (!seatMap?.surcharge_info) return '';
    const rate = seatMap.surcharge_info[position] || 0;
    if (rate === 0) return 'No extra charge';
    return `+${(rate * 100).toFixed(0)}% surcharge`;
  };

  if (loading) {
    return (
      <div className="seat-selector-loading">
        <Loader2 className="spinner" size={32} />
        <p>Loading seat map...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="seat-selector-error">
        <AlertCircle size={32} />
        <p>{error}</p>
      </div>
    );
  }

  if (!seatMap || !seatMap.rows || seatMap.rows.length === 0) {
    return (
      <div className="seat-selector-error">
        <AlertCircle size={32} />
        <p>No seats available for this flight.</p>
      </div>
    );
  }

  return (
    <div className="seat-selector">
      {/* Legend */}
      <div className="seat-legend">
        <div className="legend-item">
          <div className="legend-seat available"></div>
          <span>Available</span>
        </div>
        <div className="legend-item">
          <div className="legend-seat selected"></div>
          <span>Selected</span>
        </div>
        <div className="legend-item">
          <div className="legend-seat unavailable"></div>
          <span>Booked</span>
        </div>
        <div className="legend-divider"></div>
        <div className="legend-item">
          <div className="legend-seat available window"></div>
          <span>Window {getSurchargeLabel('window')}</span>
        </div>
        <div className="legend-item">
          <div className="legend-seat available aisle"></div>
          <span>Aisle {getSurchargeLabel('aisle')}</span>
        </div>
        <div className="legend-item">
          <div className="legend-seat available middle"></div>
          <span>Middle {getSurchargeLabel('middle')}</span>
        </div>
      </div>

      {/* Passenger Selection Guide */}
      <div className="passenger-selection-guide">
        <Info size={16} />
        <span>
          Select {passengerCount} seat{passengerCount > 1 ? 's' : ''} for your passengers. 
          Selected: {currentlySelected.length}/{passengerCount}
        </span>
      </div>

      {/* Passenger List with Seat Assignment */}
      <div className="passenger-seat-list">
        {passengers.map((passenger, index) => (
          <div 
            key={index}
            className={`passenger-seat-item ${index === activePassengerIndex ? 'active' : ''} ${currentlySelected[index] ? 'assigned' : ''}`}
            onClick={() => setActivePassengerIndex(index)}
          >
            <div className={`passenger-marker passenger-${index + 1}`}>
              <User size={14} />
            </div>
            <div className="passenger-details">
              <span className="passenger-name">
                {passenger.passenger_name || `Passenger ${index + 1}`}
              </span>
              <span className="seat-assignment">
                {currentlySelected[index] 
                  ? `Seat ${currentlySelected[index].seat_number} (${currentlySelected[index].seat_position})`
                  : 'Click a seat to assign'
                }
              </span>
            </div>
            {currentlySelected[index] && (
              <span className="seat-surcharge">
                {currentlySelected[index].surcharge > 0 
                  ? `+₹${currentlySelected[index].surcharge.toFixed(0)}`
                  : 'No extra'
                }
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Aircraft Seat Map */}
      <div className="aircraft-container">
        {/* Aircraft nose */}
        <div className="aircraft-nose">
          <div className="nose-shape"></div>
          <span className="aircraft-label">{seatMap.aircraft_model || 'Aircraft'}</span>
        </div>

        {/* Seat Grid */}
        <div className="seat-grid">
          {/* Column Headers */}
          <div className="seat-row header-row">
            <div className="row-number"></div>
            {seatMap.config.seat_letters.map((letter, idx) => (
              <div key={letter} className="seat-header">
                {letter}
                {seatMap.config.aisle_after.includes(idx + 1) && (
                  <div className="aisle-spacer"></div>
                )}
              </div>
            ))}
          </div>

          {/* Seat Rows */}
          {seatMap.rows.map((row) => (
            <div key={row.row_number} className="seat-row">
              <div className="row-number">{row.row_number}</div>
              {seatMap.config.seat_letters.map((letter, colIdx) => {
                const seat = row.seats.find(s => s.seat_letter === letter);
                const afterAisle = seatMap.config.aisle_after.includes(colIdx + 1);
                
                return (
                  <div key={letter} className="seat-cell">
                    {seat ? (
                      <button
                        className={getSeatClass(seat)}
                        onClick={() => handleSeatClick(seat)}
                        disabled={!seat.is_available}
                        title={`${seat.seat_number} - ${seat.seat_position}${seat.surcharge > 0 ? ` (+₹${seat.surcharge})` : ''}`}
                      >
                        {currentlySelected.findIndex(s => s.id === seat.id) >= 0 && (
                          <span className="seat-passenger-num">
                            {currentlySelected.findIndex(s => s.id === seat.id) + 1}
                          </span>
                        )}
                      </button>
                    ) : (
                      <div className="seat empty"></div>
                    )}
                    {afterAisle && <div className="aisle"></div>}
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        {/* Aircraft tail */}
        <div className="aircraft-tail">
          <div className="tail-shape"></div>
        </div>
      </div>

      {/* Selection Summary */}
      {currentlySelected.length > 0 && (
        <div className="selection-summary">
          <div className="summary-row">
            <span>Selected Seats:</span>
            <span className="seats-list">
              {currentlySelected.map(s => s.seat_number).join(', ')}
            </span>
          </div>
          {getTotalSurcharge() > 0 && (
            <div className="summary-row surcharge">
              <span>Seat Selection Surcharge:</span>
              <span>+₹{getTotalSurcharge().toFixed(2)}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SeatSelector;
