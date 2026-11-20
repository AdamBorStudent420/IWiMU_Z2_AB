from pathlib import Path

from silnik import wczytaj_baze, wnioskuj_w_przod, wnioskuj_wstecz

baza = wczytaj_baze(Path(__file__).parent.parent / "wiedza" / "rowery.json")
cel = baza["cel"]

PRZYPADKI = [
    # 1. Granica przedziału: dokładnie 20 km -> warunek <= 20 (klasyczny, nie elektryczny)
    (
        "Granica przedziału (20 km)",
        {"przeznaczenie": "dojazdy do pracy", "ile_km": 20, "duzo_miejsca": "tak"},
        "rower miejski",
        ["R2", "R11"],
    ),
    # 2. Granica przedziału: dokładnie 100 km, bez trudnego terenu -> warunek <= 100
    (
        "Granica przedziału (100 km)",
        {"przeznaczenie": "jazda rekreacyjna", "ile_km": 100, "trudny_teren": "nie"},
        "rower mtb elektryczny",
        ["R4", "R16"],
    ),
    # 3. Konflikt reguł: pasują zarówno R15 (fatbike), jak i R16 (mtb elektryczny) — wygrywa R15
    (
        "Konflikt reguł (R15 przed R16)",
        {"przeznaczenie": "jazda rekreacyjna", "ile_km": 50, "trudny_teren": "tak"},
        "rower fatbike",
        ["R4", "R15"],
    ),
    # 4. Brak wyniku (luka w bazie): jazda wyczynowa po asfalcie nie ma reguły
    (
        "Brak wyniku (luka)",
        {"przeznaczenie": "jazda wyczynowa", "teren_jazdy": "jazda po asfalcie"},
        None,
        [],
    ),
    # 5. Typowy przypadek (dalekie trasy z bagażem)
    (
        "Dalekie trasy z bagażem",
        {"przeznaczenie": "dalekie trasy", "spory_bagaz": "tak"},
        "rower trekkingowy",
        ["R5", "R17"],
    ),
    # 6. Typowy przypadek (jazda sportowa, trening w lesie)
    (
        "Jazda sportowa treningowa",
        {"przeznaczenie": "jazda sportowa", "wyscigi": "nie", "teren_sport": "jazda po lesie"},
        "rower gravelowy",
        ["R8", "R21"],
    ),
    # 7. Typowy przypadek (jazda wyczynowa w skateparku)
    (
        "Jazda wyczynowa w skateparku",
        {"przeznaczenie": "jazda wyczynowa", "teren_wyczynowy": "jazda w skateparku"},
        "rower bmx",
        ["R24"],
    ),
]

ok = 0
for opis, wejscie, oczekiwane, oczekiwany_slad in PRZYPADKI:
    fakty, slad = wnioskuj_w_przod(baza, wejscie)
    w_przod_ok = fakty.get(cel) == oczekiwane and (oczekiwany_slad is None or slad == oczekiwany_slad)

    zadane = []
    def zapytaj(atrybut, powod):
        zadane.append(atrybut)
        return wejscie.get(atrybut)

    wstecz = wnioskuj_wstecz(baza, cel, {}, zapytaj, [])
    wstecz_ok = wstecz == oczekiwane and len(zadane) == len(set(zadane))

    status = "OK " if w_przod_ok and wstecz_ok else "BŁĄD"
    ok += w_przod_ok and wstecz_ok
    print(f"[{status}] {opis}: w przód={fakty.get(cel)}, wstecz={wstecz}, ślad={slad}, pytań={len(zadane)}")

print(f"\nZaliczone przypadki: {ok}/{len(PRZYPADKI)}")