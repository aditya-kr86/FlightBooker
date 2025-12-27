import api from './config';

// Flight API endpoints
export const flightAPI = {
  // Get all flights
  getAllFlights: async (limit = 50) => {
    const response = await api.get('/flights/', { params: { limit } });
    return response.data;
  },

  // Search flights with filters
  searchFlights: async (params) => {
    const response = await api.get('/flights/search', { params });
    return response.data;
  },

  // Get single flight by ID
  getFlightById: async (flightId) => {
    const response = await api.get(`/flights/${flightId}`);
    return response.data;
  },

  // Get flight seats
  getFlightSeats: async (flightId) => {
    const response = await api.get(`/flights/${flightId}/seats`);
    return response.data;
  },
};

// Airport API endpoints
export const airportAPI = {
  // Get all airports
  getAllAirports: async () => {
    const response = await api.get('/airports/');
    return response.data;
  },

  // Get airport by ID
  getAirportById: async (airportId) => {
    const response = await api.get(`/airports/${airportId}`);
    return response.data;
  },
};

// Airline API endpoints
export const airlineAPI = {
  // Get all airlines
  getAllAirlines: async () => {
    const response = await api.get('/airlines/');
    return response.data;
  },
};

export default { flightAPI, airportAPI, airlineAPI };
