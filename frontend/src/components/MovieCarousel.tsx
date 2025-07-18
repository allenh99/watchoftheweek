import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/effect-coverflow';
import { Autoplay, EffectCoverflow } from 'swiper/modules';

const movies = [
  { 
    title: 'Inception', 
    poster_path: '/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg',
  },
  { 
    title: 'The Matrix', 
    poster_path: '/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
  },
  { 
    title: 'Interstellar', 
    poster_path: '/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
  },
  { 
    title: 'The Godfather', 
    poster_path: '/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
  },
  { 
    title: 'Pulp Fiction', 
    poster_path: '/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg',
  },
  { 
    title: 'Another Round', 
    poster_path: '/aDcIt4NHURLKnAEu7gow51Yd00Q.jpg',
  },
  {
    title: 'Midsommar', 
    poster_path: '/vqPtSD5kJJTEFuJluj4C1J8wKKf.jpg',
  }
];

export default function MovieCarousel() {
  return (
    <div className="w-full flex justify-center py-8">
      <Swiper
        modules={[Autoplay, EffectCoverflow]}
        effect="coverflow"
        grabCursor={true}
        centeredSlides={true}
        slidesPerView={5}
        coverflowEffect={{
          rotate: 0,
          stretch: 0,
          depth: 100,
          modifier: 2.5,
          slideShadows: false,
        }}
        autoplay={{
          delay: 3000,
          disableOnInteraction: false,
        }}
        loop={true}
        className="w-[900px] h-[500px] max-w-5xl"
      >
        {movies.map((movie, idx) => (
          <SwiperSlide>
            <div className="flex flex-col items-center">
              <div className="w-64 h-96 relative overflow-hidden rounded-lg shadow-lg">
                <img
                  src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                  alt={movie.title}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Fallback to a placeholder if image fails to load
                    e.currentTarget.src = '/placeholder-movie.jpg';
                  }}
                />
              </div>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
} 