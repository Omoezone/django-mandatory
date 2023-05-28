# django-mandatory
The main repo for the mandatories + eksam project

Vejledning og kommandoer i django: Sørg altid for at være i folderen hvor filen "manage.py" ligger

Hvis dette er første gang, du kører programmet, gør dette:

A. Du kan risikerer at få et problem med at installere numpy, pygame og pillow ved requirement.txt
   En løsning er at tage dem ud af requirements.txt og installere dem for sig selv. 
B. Der er sat en smtp development server op. Kør den lokalt ved kommandoen 
   "python -m aiosmtpd -n -l localhost:8025". Alt der skal gøres er sat op i settings.py.

1. Slet din nuværende database, hvis en eksisterer (kan gøres ved at slette dine migrationsfiler + filen db.sqlite3)
2. kør "python manage.py makemigrations"
3. kør "python manage.py migrate"
4. kør scriptene rankSetup & setupDemo.
   1. Dette gøre ved brug af kommando "python manage.py <navnPåScript>"
5. Lav en superuser/admin "python manage.py createsuperuser"
6. Kør service med "python manage.py runserver"

Du bør nu have adgang til funktionelt service.

pip install -r requirements.txt
pip freeze > requirements.txt