import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/effect-coverflow';
import { Autoplay, EffectCoverflow } from 'swiper/modules';

const movies = [
  { title: 'Inception', image: '/inception.jpg' },
  { title: 'The Matrix', image: '/matrix.jpg' },
  { title: 'Interstellar', image: '/interstellar.jpg' },
  { title: 'The Godfather', image: '/godfather.jpg' },
  { title: 'Pulp Fiction', image: '/pulpfiction.jpg' },
];

export default function MovieCarousel() {
  return (
    <div className="w-full flex justify-center py-8">
      <Swiper
        modules={[Autoplay, EffectCoverflow]}
        effect="coverflow"
        grabCursor={true}
        centeredSlides={true}
        slidesPerView={3}
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
        className="w-[600px] h-[400px]"
      >
        {movies.map((movie, idx) => (
          <SwiperSlide key={idx}>
            <img
              src={movie.image}
              alt={movie.title}
              className="rounded-lg shadow-lg object-cover w-full h-80"
            />
            <div className="text-center mt-2 font-montserrat text-lg text-white drop-shadow">
              {movie.title}
            </div>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
} 