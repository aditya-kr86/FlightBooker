import { Users, Plane, MapPin, Star } from 'lucide-react';

const Stats = () => {
  const stats = [
    {
      icon: <Users />,
      value: '50K+',
      label: 'Happy Travelers',
    },
    {
      icon: <Plane />,
      value: '1000+',
      label: 'Daily Flights',
    },
    {
      icon: <MapPin />,
      value: '100+',
      label: 'Destinations',
    },
    {
      icon: <Star />,
      value: '4.8',
      label: 'User Rating',
    },
  ];

  return (
    <section className="stats-section">
      <div className="stats-container">
        {stats.map((stat, index) => (
          <div key={index} className="stat-item">
            <div className="stat-icon">
              {stat.icon}
            </div>
            <div className="stat-content">
              <span className="stat-value">{stat.value}</span>
              <span className="stat-label">{stat.label}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Stats;
