from django.core.management.base import BaseCommand
from django.utils import timezone
from movies.models import Movie, Theater, Showtime, Screen, Seat, Genre
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Populates the database with movies, theaters, screens and seats'

    def handle(self, *args, **options):
        Genre.objects.all().delete()
        genres_data = [
            {'code': 'AC', 'name': 'Action'},
            {'code': 'CO', 'name': 'Comedy'},
            {'code': 'DR', 'name': 'Drama'},
            {'code': 'HO', 'name': 'Horror'},
            {'code': 'SF', 'name': 'Sci-Fi'},
            {'code': 'RO', 'name': 'Romance'},
            {'code': 'TH', 'name': 'Thriller'},
            {'code': 'FA', 'name': 'Fantasy'},
            {'code': 'HI', 'name': 'Historical'},
            {'code': 'AD', 'name': 'Adventure'}
        ]
        for genre_data in genres_data:
            Genre.objects.get_or_create(**genre_data)

        Movie.objects.all().delete()
        Theater.objects.all().delete()
        Showtime.objects.all().delete()
        Screen.objects.all().delete()
        Seat.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted all existing movie data'))

        # Create theaters
        theaters_data = [
            {'name': 'Savoy Colombo', 'location': 'Colombo 3', 'contact': '0112 345 678', 'screen_type': 'imax'},
            {'name': 'Majestic Cineplex', 'location': 'Colombo 4', 'contact': '0112 987 654', 'screen_type': 'dolby'},
            {'name': 'Regal Cinema', 'location': 'Colombo 1', 'contact': '0112 567 890', 'screen_type': 'standard'},
            {'name': 'Liberty by Scope', 'location': 'Kandy', 'contact': '0812 345 678', 'screen_type': 'standard'}
        ]

        for theater_data in theaters_data:
            theater, created = Theater.objects.get_or_create(
                name=theater_data['name'],
                defaults={
                    'location': theater_data['location'],
                    'contact': theater_data['contact'],
                    'image': f'theaters/{theater_data["name"].lower().replace(" ", "_")}.jpg'
                }
            )

            # Create single screen for each theater
            screen, _ = Screen.objects.get_or_create(
                theater=theater,
                screen_number=1,  # Always screen number 1
                defaults={
                    'capacity': 150 if theater_data['screen_type'] == 'standard' else 100,
                    'screen_type': theater_data['screen_type']
                }
            )

            # Create seats for the screen (10 rows x 15 seats)
            for row in 'ABCDEFGHIJ':
                for seat_num in range(1, 16):
                    Seat.objects.get_or_create(
                        screen=screen,
                        row=row,
                        seat_number=str(seat_num),
                        defaults={'is_booked': False}
                    )
        self.stdout.write(self.style.SUCCESS(f'Created {len(theaters_data)} theaters with screens and seats'))

        # All movies data with multiple genres
        movies_data = [
            # Sinhala Movies
            {
                'title': 'Aba',
                'poster': 'images/aba.jpeg',
                'description': 'Historical drama about King Pandukabhaya',
                'duration': 150,
                'genres': ['HI', 'DR'],
                'language': 'SI',
                'price': 800
            },
            {
                'title': 'Nelum Kuluna',
                'poster': 'images/nelum_kuluna.jpeg',
                'description': 'Contemporary Sri Lankan drama',
                'duration': 120,
                'genres': ['DR'],
                'language': 'SI',
                'price': 800
            },
            {
                'title': 'Walampoori',
                'poster': 'images/walampoori.jpg',
                'description': 'Classic Sinhalese comedy-drama',
                'duration': 135,
                'genres': ['CO', 'DR'],
                'language': 'SI',
                'price': 800
            },

            # English Action/Sci-Fi
            {
                'title': 'Avengers: Endgame',
                'poster': 'images/avengers.jpg',
                'description': 'Epic conclusion to the Infinity Saga',
                'duration': 181,
                'genres': ['AC', 'SF', 'AD'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Black Widow',
                'poster': 'images/blackwidow.jpg',
                'description': 'Marvel film about Natasha Romanoff',
                'duration': 134,
                'genres': ['AC', 'TH'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'The Matrix',
                'poster': 'images/Matrix1.jpg',
                'description': 'Sci-fi classic about simulated reality',
                'duration': 136,
                'genres': ['SF', 'AC'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'The Matrix Reloaded',
                'poster': 'images/Matrix2.jpg',
                'description': 'Second installment of the Matrix trilogy',
                'duration': 138,
                'genres': ['SF', 'AC'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'The Matrix Revolutions',
                'poster': 'images/Matrix3.jpg',
                'description': 'Final chapter of the Matrix trilogy',
                'duration': 129,
                'genres': ['SF', 'AC'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'The Matrix Resurrections',
                'poster': 'images/Matrix4.jpg',
                'description': 'Return to the world of the Matrix',
                'duration': 148,
                'genres': ['SF', 'AC'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Inception',
                'poster': 'images/inception.jpg',
                'description': 'Sci-fi thriller about dream-sharing technology',
                'duration': 148,
                'genres': ['SF', 'TH'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Interstellar',
                'poster': 'images/interstellar.jpg',
                'description': 'Epic sci-fi about space travel and love',
                'duration': 169,
                'genres': ['SF', 'DR'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Tenet',
                'poster': 'images/tenet.jpg',
                'description': 'Mind-bending spy thriller about time inversion',
                'duration': 150,
                'genres': ['SF', 'TH'],
                'language': 'EN',
                'price': 1200
            },

            # English Comedy/Romance
            {
                'title': 'Barbie',
                'poster': 'images/barbie.jpg',
                'description': 'Live-action adventure about the iconic doll',
                'duration': 114,
                'genres': ['CO', 'AD'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Cruella',
                'poster': 'images/cruella.jpeg',
                'description': 'Origin story of the iconic Disney villain',
                'duration': 134,
                'genres': ['CO', 'DR'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'The Devil Wears Prada',
                'poster': 'images/devil_wears_prada.jpg',
                'description': 'Comedy-drama about fashion magazine industry',
                'duration': 109,
                'genres': ['CO', 'DR'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Legally Blonde',
                'poster': 'images/legally_blonde.jpg',
                'description': 'Comedy about a sorority girl at Harvard Law',
                'duration': 96,
                'genres': ['CO'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Me Before You',
                'poster': 'images/mebeforeyou.jpg',
                'description': 'Romantic drama about a caregiver and her patient',
                'duration': 110,
                'genres': ['RO', 'DR'],
                'language': 'EN',
                'price': 1200
            },

            # English Horror/Thriller
            {
                'title': 'Friday the 13th',
                'poster': 'images/fridaythe13th.jpg',
                'description': 'Classic slasher horror film',
                'duration': 95,
                'genres': ['HO'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Scream',
                'poster': 'images/scream.jpg',
                'description': 'Meta horror film about horror movie rules',
                'duration': 111,
                'genres': ['HO', 'TH'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'The Silence of the Lambs',
                'poster': 'images/thesilenceofthelambs.jpg',
                'description': 'Psychological thriller about FBI and serial killer',
                'duration': 118,
                'genres': ['TH', 'DR'],
                'language': 'EN',
                'price': 1200
            },

            # Other English Films
            {
                'title': 'Oppenheimer',
                'poster': 'images/oppenheimer.jpg',
                'description': 'Biographical thriller about the atomic bomb',
                'duration': 180,
                'genres': ['TH', 'DR'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Spider-Man: No Way Home',
                'poster': 'images/spiderman.jpg',
                'description': 'Marvel superhero film with multiverse concept',
                'duration': 148,
                'genres': ['AC', 'SF'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Lord of the Rings: Fellowship of the Ring',
                'poster': 'images/lotr1.jpg',
                'description': 'Fantasy epic about the One Ring',
                'duration': 178,
                'genres': ['FA', 'AD'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Lord of the Rings: The Two Towers',
                'poster': 'images/lotr2.jpg',
                'description': 'Second part of the LOTR trilogy',
                'duration': 179,
                'genres': ['FA', 'AD'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Lord of the Rings: Return of the King',
                'poster': 'images/lotr3.jpg',
                'description': 'Final part of the LOTR trilogy',
                'duration': 201,
                'genres': ['FA', 'AD'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'The Chronicles of Narnia: The Lion, the Witch and the Wardrobe',
                'poster': 'images/narnia1.jpg',
                'description': 'Fantasy adventure in the magical land of Narnia',
                'duration': 143,
                'genres': ['FA', 'AD'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'The Chronicles of Narnia: Prince Caspian',
                'poster': 'images/narnia2.jpg',
                'description': 'Second Narnia film about the Telmarine conquest',
                'duration': 150,
                'genres': ['FA', 'AD'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'The Chronicles of Narnia: The Voyage of the Dawn Treader',
                'poster': 'images/narnia3.jpg',
                'description': 'Third Narnia film about a sea voyage',
                'duration': 113,
                'genres': ['FA', 'AD'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': "Ocean's 8",
                'poster': 'images/oceans8.jpg',
                'description': 'Heist comedy about a Met Gala robbery',
                'duration': 110,
                'genres': ['CO', 'TH'],
                'language': 'EN',
                'price': 1200
            },
            {
                'title': 'Minecraft: The Movie',
                'poster': 'images/minecraft.jpg',
                'description': 'Adventure film based on the popular game',
                'duration': 105,
                'genres': ['AD', 'FA'],
                'language': 'EN',
                'price': 1200,
                'coming_soon': True
            },
            {
                'title': 'Flow',
                'poster': 'images/flow.jpg',
                'description': 'Environmental documentary about water',
                'duration': 90,
                'genres': ['DR'],
                'language': 'EN',
                'price': 1000,
                'coming_soon': True
            }
        ]

        # MOVIE DATA AND SCHEDULING STRATEGY
        today = timezone.now().date()
        all_theaters = list(Theater.objects.all())

        # Explicitly select 6 coming soon movies
        coming_soon_movies = random.sample(movies_data, 6)
        remaining_movies = [m for m in movies_data if m not in coming_soon_movies]

        # Select 5 past movies
        past_movies = random.sample(remaining_movies, 5)
        remaining_movies = [m for m in remaining_movies if m not in past_movies]

        # Select 4 mid-May ending movies
        mid_may_movies = random.sample(remaining_movies, 4)
        remaining_movies = [m for m in remaining_movies if m not in mid_may_movies]

        # The rest will be normal current movies ending after May 14th
        normal_movies = remaining_movies

        theater_movie_map = {t.id: [] for t in all_theaters}

        for movie_data in movies_data:
            coming_soon = movie_data in coming_soon_movies
            past = movie_data in past_movies
            mid_may = movie_data in mid_may_movies

            # Set release dates
            if coming_soon:
                release_date = today + timedelta(days=30)
                end_date = None
            elif past:
                release_date = today - timedelta(days=30)
                end_date = today - timedelta(days=random.randint(3, 20))
            elif mid_may:
                release_date = today - timedelta(days=7)
                end_date = today + timedelta(days=random.randint(1, 5))  # Between May 5-9
            else:  # normal movies
                release_date = today - timedelta(days=7)
                end_date = today + timedelta(days=random.randint(15, 30))  # After May 14

            movie, created = Movie.objects.update_or_create(
                title=movie_data['title'],
                defaults={
                    'description': movie_data['description'],
                    'duration': movie_data['duration'],
                    'language': movie_data.get('language', 'EN'),
                    'release_date': release_date,
                    'poster': movie_data['poster'],
                    'rating': movie_data.get('rating', 0.0)
                }
            )
            movie.genres.clear()
            for genre_code in movie_data['genres']:
                genre = Genre.objects.get(code=genre_code)
                movie.genres.add(genre)

            if coming_soon:
                self.stdout.write(self.style.WARNING(f'Coming Soon movie: {movie.title}'))
                continue
            if past and end_date and end_date < today:
                self.stdout.write(self.style.WARNING(f'Past movie: {movie.title}'))
            elif mid_may:
                self.stdout.write(self.style.WARNING(f'Mid-May ending movie: {movie.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Now Showing movie: {movie.title}'))

            # Assign to theaters with specified distribution
            if not (coming_soon or (past and end_date < today)):
                num_theaters = random.choices([1, 2, 3], [0.7, 0.25, 0.05])[0]  # 70% 1 theater, 25% 2, 5% 3
                assigned_theaters = random.sample(all_theaters, num_theaters)

                for theater in assigned_theaters:
                    theater_movie_map[theater.id].append(movie)

                    show_date = today
                    while show_date <= end_date:
                        Showtime.objects.get_or_create(
                            movie=movie,
                            theater=theater,
                            date=show_date,
                            time='18:00:00',
                            defaults={'price': movie_data.get('price', 1200)}
                        )
                        show_date += timedelta(days=1)

        # Ensure each theater has at least 6 movies (at least 5 current)
        for theater in all_theaters:
            current_movies = [m for m in theater_movie_map[theater.id]
                              if m.release_date <= today and (not hasattr(m, 'end_date') or m.end_date >= today)]

            while len(current_movies) < 5 or len(theater_movie_map[theater.id]) < 6:
                # Find movies not already in this theater
                candidates = Movie.objects.filter(
                    release_date__lte=today
                ).exclude(
                    id__in=[m.id for m in theater_movie_map[theater.id]]
                )

                if not candidates.exists():
                    break

                extra_movie = random.choice(candidates)
                theater_movie_map[theater.id].append(extra_movie)
                current_movies.append(extra_movie)

                # Set end date 1-2 weeks from today for these additional movies
                extra_end_date = today + timedelta(days=random.randint(7, 14))

                show_date = today
                while show_date <= extra_end_date:
                    Showtime.objects.get_or_create(
                        movie=extra_movie,
                        theater=theater,
                        date=show_date,
                        time='20:30:00',
                        defaults={'price': 1200}
                    )
                    show_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Successfully populated movie database!'))