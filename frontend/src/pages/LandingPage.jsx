import Hero from '../components/home/Hero';
import Features from '../components/home/Features';
import PopularDestinations from '../components/home/PopularDestinations';
import Stats from '../components/home/Stats';
import Newsletter from '../components/home/Newsletter';

const LandingPage = () => {
  return (
    <main className="landing-page">
      <Hero />
      <Stats />
      <Features />
      <PopularDestinations />
      <Newsletter />
    </main>
  );
};

export default LandingPage;
