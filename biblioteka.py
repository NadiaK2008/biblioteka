# ============================================================
# PROGRAM: Zarządzanie Biblioteką / Wypożyczalnią
# WERSJA: Streamlit Cloud (webowa)
# OPIS: Te same klasy co w wersji konsolowej.
#       Jedyna różnica: metody zwracają tekst zamiast
#       wyświetlać go przez print() — bo na stronie
#       internetowej nie ma konsoli.
# ============================================================

from datetime import datetime, timedelta
import os


# ============================================================
# KLASA 1: Ksiazka
# Opisuje jedną książkę w bibliotece.
# Każda książka ma: tytuł, autora, informację czy jest
# dostępna, oraz daty wypożyczenia i planowanego zwrotu.
# ============================================================

class Ksiazka:

    def __init__(self, tytul, autor, dostepna=True, data_wypozyczenia="", data_zwrotu=""):
        self.tytul = tytul
        self.autor = autor
        self.dostepna = dostepna
        self.data_wypozyczenia = data_wypozyczenia
        self.data_zwrotu = data_zwrotu

    def __str__(self):
        if self.dostepna:
            return f"'{self.tytul}' - {self.autor} [dostępna]"
        else:
            return f"'{self.tytul}' - {self.autor} [wypożyczona, zwrot do: {self.data_zwrotu}]"


# ============================================================
# KLASA 2: Czytelnik
# Opisuje jednego czytelnika biblioteki.
# Każdy czytelnik ma: imię, nazwisko, numer karty
# bibliotecznej oraz listę tytułów wypożyczonych książek.
# ============================================================

class Czytelnik:

    def __init__(self, imie, nazwisko, numer_karty, wypozyczone=None):
        self.imie = imie
        self.nazwisko = nazwisko
        self.numer_karty = numer_karty
        if wypozyczone is None:
            self.wypozyczone = []
        else:
            self.wypozyczone = wypozyczone

    def __str__(self):
        if self.wypozyczone:
            lista = ", ".join(self.wypozyczone)
            return f"{self.imie} {self.nazwisko} (karta: {self.numer_karty}) — wypożyczone: {lista}"
        else:
            return f"{self.imie} {self.nazwisko} (karta: {self.numer_karty}) — brak wypożyczeń"


# ============================================================
# KLASA 3: Biblioteka
# To główna klasa programu — "mózg" całej aplikacji.
# Przechowuje listę książek i czytelników.
# Ma metody do wszystkich operacji: dodawanie, wypożyczanie,
# zwracanie, wyświetlanie, szukanie, zapis i odczyt z plików.
# ============================================================

class Biblioteka:

    def __init__(self):
        self.ksiazki = []
        self.czytelnicy = []
        self.licznik_kart = 0

    # --- DODAWANIE KSIĄŻKI ---
    def dodaj_ksiazke(self, tytul, autor):
        ksiazka = Ksiazka(tytul, autor)
        self.ksiazki.append(ksiazka)
        return f"✅ Dodano książkę: '{tytul}' - {autor}"

    # --- REJESTRACJA CZYTELNIKA ---
    def zarejestruj_czytelnika(self, imie, nazwisko):
        self.licznik_kart = self.licznik_kart + 1
        numer = "CZ-" + str(self.licznik_kart).zfill(3)
        czytelnik = Czytelnik(imie, nazwisko, numer)
        self.czytelnicy.append(czytelnik)
        return f"✅ Zarejestrowano: {imie} {nazwisko}, numer karty: {numer}"

    # --- SZUKANIE KSIĄŻKI PO TYTULE ---
    def znajdz_ksiazke(self, tytul):
        for ksiazka in self.ksiazki:
            if ksiazka.tytul.lower() == tytul.lower():
                return ksiazka
        return None

    # --- SZUKANIE CZYTELNIKA PO NUMERZE KARTY ---
    def znajdz_czytelnika(self, numer_karty):
        for czytelnik in self.czytelnicy:
            if czytelnik.numer_karty == numer_karty:
                return czytelnik
        return None

    # --- WYPOŻYCZANIE KSIĄŻKI ---
    def wypozycz(self, tytul, numer_karty):
        ksiazka = self.znajdz_ksiazke(tytul)
        if ksiazka is None:
            return "❌ Nie znaleziono książki o takim tytule."

        if not ksiazka.dostepna:
            return f"❌ Książka '{ksiazka.tytul}' jest już wypożyczona. Planowany zwrot: {ksiazka.data_zwrotu}"

        czytelnik = self.znajdz_czytelnika(numer_karty)
        if czytelnik is None:
            return "❌ Nie znaleziono czytelnika o takim numerze karty."

        dzis = datetime.now()
        za_30_dni = dzis + timedelta(days=30)

        ksiazka.dostepna = False
        ksiazka.data_wypozyczenia = dzis.strftime("%d.%m.%Y")
        ksiazka.data_zwrotu = za_30_dni.strftime("%d.%m.%Y")
        czytelnik.wypozyczone.append(ksiazka.tytul)

        return f"✅ Wypożyczono '{ksiazka.tytul}' dla {czytelnik.imie} {czytelnik.nazwisko}. Zwrot do: {ksiazka.data_zwrotu}"

    # --- ZWRACANIE KSIĄŻKI ---
    def zwroc(self, tytul, numer_karty):
        ksiazka = self.znajdz_ksiazke(tytul)
        if ksiazka is None:
            return "❌ Nie znaleziono książki o takim tytule."

        if ksiazka.dostepna:
            return "❌ Ta książka nie jest wypożyczona."

        czytelnik = self.znajdz_czytelnika(numer_karty)
        if czytelnik is None:
            return "❌ Nie znaleziono czytelnika o takim numerze karty."

        if ksiazka.tytul not in czytelnik.wypozyczone:
            return "❌ Ten czytelnik nie ma wypożyczonej tej książki."

        ksiazka.dostepna = True
        ksiazka.data_wypozyczenia = ""
        ksiazka.data_zwrotu = ""
        czytelnik.wypozyczone.remove(ksiazka.tytul)

        return f"✅ Zwrócono '{ksiazka.tytul}'. Książka jest znów dostępna."

    # --- SZUKANIE KSIĄŻKI PO FRAZIE ---
    def szukaj(self, fraza):
        wyniki = []
        for ksiazka in self.ksiazki:
            if fraza.lower() in ksiazka.tytul.lower():
                wyniki.append(ksiazka)
            elif fraza.lower() in ksiazka.autor.lower():
                wyniki.append(ksiazka)
        return wyniki

    # --- ODCZYT DANYCH Z PLIKÓW TEKSTOWYCH ---
    def wczytaj(self, sciezka_ksiazki="ksiazki.txt", sciezka_czytelnicy="czytelnicy.txt"):
        # Wczytujemy książki z pliku ksiazki.txt
        if os.path.exists(sciezka_ksiazki):
            plik = open(sciezka_ksiazki, "r", encoding="utf-8")
            for linia in plik:
                linia = linia.strip()
                if linia == "":
                    continue
                czesci = linia.split("|")
                tytul = czesci[0]
                autor = czesci[1]
                dostepna = czesci[2] == "tak"
                data_wyp = ""
                data_zwr = ""
                if len(czesci) > 3:
                    data_wyp = czesci[3]
                if len(czesci) > 4:
                    data_zwr = czesci[4]
                ksiazka = Ksiazka(tytul, autor, dostepna, data_wyp, data_zwr)
                self.ksiazki.append(ksiazka)
            plik.close()

        # Wczytujemy czytelników z pliku czytelnicy.txt
        if os.path.exists(sciezka_czytelnicy):
            plik = open(sciezka_czytelnicy, "r", encoding="utf-8")
            for linia in plik:
                linia = linia.strip()
                if linia == "":
                    continue
                czesci = linia.split("|")
                imie = czesci[0]
                nazwisko = czesci[1]
                numer = czesci[2]
                wypozyczone = []
                if len(czesci) > 3 and czesci[3] != "":
                    wypozyczone = czesci[3].split(",")
                czytelnik = Czytelnik(imie, nazwisko, numer, wypozyczone)
                self.czytelnicy.append(czytelnik)
                # Aktualizujemy licznik kart
                numer_int = int(numer.split("-")[1])
                if numer_int > self.licznik_kart:
                    self.licznik_kart = numer_int
            plik.close()
