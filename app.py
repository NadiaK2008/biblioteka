import streamlit as st
import os
from biblioteka import Ksiazka, Czytelnik, Biblioteka

# ============================================================
# Konfiguracja strony
# ============================================================

st.set_page_config(
    page_title="📚 Biblioteka",
    page_icon="📚",
    layout="wide"
)

# ============================================================
# Inicjalizacja — wczytujemy dane tylko raz (przy pierwszym
# uruchomieniu). Potem dane trzymamy w session_state.
# To jest odpowiednik naszego bib.wczytaj() z wersji konsolowej.
# ============================================================

if "bib" not in st.session_state:
    bib = Biblioteka()
    sciezka = os.path.dirname(os.path.abspath(__file__))
    bib.wczytaj(
        os.path.join(sciezka, "ksiazki.txt"),
        os.path.join(sciezka, "czytelnicy.txt")
    )
    st.session_state.bib = bib

bib = st.session_state.bib

# ============================================================
# Nagłówek
# ============================================================

st.title("📚 Biblioteka — Zarządzanie Wypożyczalnią")
st.caption("Program do zarządzania małą biblioteką. Wersja webowa.")

# ============================================================
# Menu w bocznym panelu (sidebar) — odpowiednik naszego menu
# z wersji konsolowej, ale zamiast wpisywać cyfry, klikamy.
# ============================================================

st.sidebar.title("📋 Menu")
opcja = st.sidebar.radio("Wybierz operację:", [
    "📚 Pokaż książki",
    "👥 Pokaż czytelników",
    "➕ Dodaj książkę",
    "👤 Zarejestruj czytelnika",
    "📖 Wypożycz książkę",
    "↩️ Zwróć książkę",
    "🔍 Szukaj książki"
])

st.sidebar.divider()
st.sidebar.info(f"📊 Książek: {len(bib.ksiazki)} | Czytelników: {len(bib.czytelnicy)}")

# ============================================================
# Treść strony — zależy od wybranej opcji w menu
# ============================================================

# --- POKAŻ KSIĄŻKI ---
if opcja == "📚 Pokaż książki":
    st.header("📚 Lista książek")

    if len(bib.ksiazki) == 0:
        st.warning("Brak książek w bibliotece.")
    else:
        for ksiazka in bib.ksiazki:
            if ksiazka.dostepna:
                st.success(f"📗 **{ksiazka.tytul}** — {ksiazka.autor}  ·  ✅ dostępna")
            else:
                st.error(f"📕 **{ksiazka.tytul}** — {ksiazka.autor}  ·  ❌ wypożyczona, zwrot do: {ksiazka.data_zwrotu}")

# --- POKAŻ CZYTELNIKÓW ---
elif opcja == "👥 Pokaż czytelników":
    st.header("👥 Lista czytelników")

    if len(bib.czytelnicy) == 0:
        st.warning("Brak zarejestrowanych czytelników.")
    else:
        for czytelnik in bib.czytelnicy:
            if czytelnik.wypozyczone:
                lista = ", ".join(czytelnik.wypozyczone)
                st.info(f"👤 **{czytelnik.imie} {czytelnik.nazwisko}** (karta: {czytelnik.numer_karty})  ·  📖 {lista}")
            else:
                st.write(f"👤 **{czytelnik.imie} {czytelnik.nazwisko}** (karta: {czytelnik.numer_karty})  ·  brak wypożyczeń")

# --- DODAJ KSIĄŻKĘ ---
elif opcja == "➕ Dodaj książkę":
    st.header("➕ Dodaj nową książkę")

    with st.form("dodaj_ksiazke"):
        tytul = st.text_input("Tytuł książki")
        autor = st.text_input("Autor")
        wyslij = st.form_submit_button("Dodaj książkę")

        if wyslij:
            if tytul != "" and autor != "":
                wynik = bib.dodaj_ksiazke(tytul, autor)
                st.success(wynik)
                st.rerun()
            else:
                st.error("❌ Tytuł i autor nie mogą być puste.")

# --- ZAREJESTRUJ CZYTELNIKA ---
elif opcja == "👤 Zarejestruj czytelnika":
    st.header("👤 Zarejestruj nowego czytelnika")

    with st.form("zarejestruj"):
        imie = st.text_input("Imię")
        nazwisko = st.text_input("Nazwisko")
        wyslij = st.form_submit_button("Zarejestruj")

        if wyslij:
            if imie != "" and nazwisko != "":
                wynik = bib.zarejestruj_czytelnika(imie, nazwisko)
                st.success(wynik)
                st.rerun()
            else:
                st.error("❌ Imię i nazwisko nie mogą być puste.")

# --- WYPOŻYCZ KSIĄŻKĘ ---
elif opcja == "📖 Wypożycz książkę":
    st.header("📖 Wypożycz książkę")

    dostepne = [k for k in bib.ksiazki if k.dostepna]
    if len(dostepne) == 0:
        st.warning("Brak dostępnych książek do wypożyczenia.")
    elif len(bib.czytelnicy) == 0:
        st.warning("Brak zarejestrowanych czytelników.")
    else:
        with st.form("wypozycz"):
            tytuly = [k.tytul for k in dostepne]
            wybrany_tytul = st.selectbox("Wybierz książkę", tytuly)

            czytelnik_opcje = [f"{c.imie} {c.nazwisko} ({c.numer_karty})" for c in bib.czytelnicy]
            wybrany_czytelnik_idx = st.selectbox("Wybierz czytelnika", range(len(czytelnik_opcje)), format_func=lambda i: czytelnik_opcje[i])

            wyslij = st.form_submit_button("Wypożycz")

            if wyslij:
                numer_karty = bib.czytelnicy[wybrany_czytelnik_idx].numer_karty
                wynik = bib.wypozycz(wybrany_tytul, numer_karty)
                if wynik.startswith("✅"):
                    st.success(wynik)
                else:
                    st.error(wynik)
                st.rerun()

# --- ZWRÓĆ KSIĄŻKĘ ---
elif opcja == "↩️ Zwróć książkę":
    st.header("↩️ Zwróć książkę")

    wypozyczone = [k for k in bib.ksiazki if not k.dostepna]
    if len(wypozyczone) == 0:
        st.warning("Brak wypożyczonych książek do zwrotu.")
    else:
        with st.form("zwroc"):
            tytuly = [k.tytul for k in wypozyczone]
            wybrany_tytul = st.selectbox("Wybierz książkę do zwrotu", tytuly)

            # Znajdź kto ma tę książkę
            czytelnicy_z_ksiazka = []
            for c in bib.czytelnicy:
                if wybrany_tytul in c.wypozyczone:
                    czytelnicy_z_ksiazka.append(c)

            if len(czytelnicy_z_ksiazka) > 0:
                czytelnik_opcje = [f"{c.imie} {c.nazwisko} ({c.numer_karty})" for c in czytelnicy_z_ksiazka]
                wybrany_idx = st.selectbox("Czytelnik zwracający", range(len(czytelnik_opcje)), format_func=lambda i: czytelnik_opcje[i])
                numer_karty = czytelnicy_z_ksiazka[wybrany_idx].numer_karty
            else:
                st.warning("Nie można ustalić kto wypożyczył tę książkę.")
                numer_karty = ""

            wyslij = st.form_submit_button("Zwróć")

            if wyslij and numer_karty != "":
                wynik = bib.zwroc(wybrany_tytul, numer_karty)
                if wynik.startswith("✅"):
                    st.success(wynik)
                else:
                    st.error(wynik)
                st.rerun()

# --- SZUKAJ KSIĄŻKI ---
elif opcja == "🔍 Szukaj książki":
    st.header("🔍 Szukaj książki")

    fraza = st.text_input("Wpisz tytuł lub autora")

    if fraza != "":
        wyniki = bib.szukaj(fraza)
        if len(wyniki) > 0:
            st.success(f"Znaleziono {len(wyniki)} wyników:")
            for ksiazka in wyniki:
                if ksiazka.dostepna:
                    st.write(f"📗 **{ksiazka.tytul}** — {ksiazka.autor}  ·  ✅ dostępna")
                else:
                    st.write(f"📕 **{ksiazka.tytul}** — {ksiazka.autor}  ·  ❌ wypożyczona, zwrot do: {ksiazka.data_zwrotu}")
        else:
            st.warning("Nie znaleziono książek pasujących do frazy.")

# ============================================================
# Stopka
# ============================================================

st.divider()
st.caption("Projekt szkolny — Zarządzanie Biblioteką | Python + Streamlit")
