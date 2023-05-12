# django-mandatory
The main repo for the mandatories + eksam project

Vejledning og kommandoer i django: Sørg altid for at være i folderen hvor filen "manage.py" ligger

Hvis dette er første gang, du kører programmet, gør dette:

1. Slet din nuværende database, hvis en eksisterer (kan gøres ved at slette dine migrationsfiler + filen db.sqlite3)
2. kør "python manage.py makemigrations"
3. kør "python manage.py migrate"
4. kør scriptene rankSetup & setupDemo.
   1. Dette gøre ved brug af kommando "python manage.py <navnPåScript>"
5. Lav en superuser/admin "python manage.py createsuperuser"
6. Kør service med "python manage.py runserver"
7. Som det første, gå ind i admin portal og lav en customer til den superuser du lige har lavet.

Du bør nu have adgang til funktionelt service.