from flask import Flask, request
import requests
import itertools
app = Flask(__name__)
# Tutaj wklej swój klucz Google Maps API
GOOGLE_API_KEY = "TU_WKLEJ_SWÓJ_KLUCZ"
def odleglosc_między(adres1, adres2):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": adres1,
        "destinations": adres2,
        "key": GOOGLE_API_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params).json()
    try:
        return response['rows'][0]['elements'][0]['distance']['value']
    except:
        return float('inf')
def optymalna_trasa(adresy):
    # Bruteforce dla małych zestawów (max ~6-7 adresów na kierowcę)
    min_dystans = float('inf')
    najlepsza = adresy
    for perm in itertools.permutations(adresy):
        dystans = sum(odleglosc_między(perm[i], perm[i+1]) for i in range(len(perm)-1))
        if dystans < min_dystans:
            min_dystans = dystans
            najlepsza = perm
    return list(najlepsza)
def podziel_trasy(adresy):
    kierowcy = {1: [], 2: [], 3: []}
    for i, adres in enumerate(adresy):
        kierowca = (i % 3) + 1
        kierowcy[kierowca].append(adres)
    # Optymalizujemy kolejność dla każdego kierowcy
    for k in kierowcy:
        if len(kierowcy[k]) > 1:
            kierowcy[k] = optymalna_trasa(kierowcy[k])
    return kierowcy
@app.route('/', methods=['GET', 'POST'])
def index():
    trasy = None
    if request.method == 'POST':
        adresy = [a.strip() for a in request.form['adresy'].split('\n') if a.strip()]
        trasy = podziel_trasy(adresy)
    html = """
    <h1>Inteligentne trasy dla 3 kierowców</h1>
    <form method="post">
        <textarea name="adresy" rows="10" cols="50" placeholder="Wpisz każdy adres w nowej linii"></textarea><br>
        <button type="submit">Generuj trasy</button>
    </form>
    """
    if trasy:
        for k, adresy in trasy.items():
            html += f"<h2>Kierowca {k}</h2><ul>"
            for a in adresy:
                html += f"<li>{a}</li>"
            html += "</ul>"
    return html
if __name__ == "__main__":
    app.run(debug=True)
