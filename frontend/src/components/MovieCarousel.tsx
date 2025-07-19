import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/effect-coverflow';
import { Autoplay, EffectCoverflow } from 'swiper/modules';
import { carouselMovies } from '../data/movies';


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
          delay: 10000,
          disableOnInteraction: false,
        }}
        loop={true}
        className="w-[900px] h-[300px] max-w-5xl"
      >
        {carouselMovies.map((movie, idx) => (
          <SwiperSlide>
            <div className="flex flex-col items-center">
              <div className="w-48 h-72 relative overflow-hidden rounded-lg shadow-lg">
                <img
                  src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                  alt={movie.title}
                  className="w-full h-full object-cover"
                  onError={(e) => {
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