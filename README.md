# Adaptive Game Difficulty Agent

Ein agentenbasiertes System, das den Schwierigkeitsgrad einer Spielsimulation automatisch an die Leistung des Spielers anpasst.

Zusätzlich enthält das Projekt einen optionalen **Reaktionstest-Modus**: Der Nutzer misst seine Reaktionszeit im Terminal, der gemessene Median wird in einen Reaktionswert zwischen 0,0 und 1,0 umgerechnet, und daraus wird ein personalisiertes Spielerprofil erstellt, das direkt in der adaptiven Live-Demo verwendet werden kann.

---

## Projektidee

Viele Spiele verwenden einen fixen Schwierigkeitsgrad, der entweder zu einfach oder zu schwer ist.
Dieses Projekt untersucht, ob ein adaptiver Agent – der die letzten Spielergebnisse beobachtet und die Schwierigkeit entsprechend anpasst – eine ausgewogenere Spielerfahrung erzeugen kann als ein statisches System.

Das System wird mit einem statischen Schwierigkeitssystem verglichen, bei dem die Schwierigkeit über alle Runden konstant bleibt.

---

## Forschungsfrage

**Kann ein adaptiver Schwierigkeitsagent eine ausgewogenere Spielerfahrung erzeugen als ein statisches Schwierigkeitssystem?**

---

## Funktionsweise

Jede Spielrunde läuft in folgendem Ablauf:

1. **Spielerprofil auswählen** – ein Profil mit definierten Stärke- und Schwächewerten.
2. **Schwierigkeit in Spielparameter umwandeln** – aus dem aktuellen Schwierigkeitsgrad werden konkrete Werte für Gegner und Heilung abgeleitet.
3. **Runde simulieren** – das Ergebnis (Sieg oder Niederlage) wird probabilistisch bestimmt.
4. **Auswertung der letzten Runden** – der Agent analysiert ein Fenster der jüngsten Ergebnisse.
5. **Entscheidung des Agenten** – er wählt eine der drei Aktionen:
   - `increase` – Schwierigkeit erhöhen
   - `decrease` – Schwierigkeit reduzieren
   - `keep` – Schwierigkeit beibehalten
6. **Neue Schwierigkeit anwenden** – gilt ab der nächsten Runde.

### Optionaler Reaktionstest-Pfad

Als zusätzliches interaktives Demo-Feature kann das Spielerprofil aus einer Reaktionszeitenmessung abgeleitet werden:

1. **Reaktionstest starten** – der Nutzer startet den Test im Terminal.
2. **Messungen durchführen** – mehrere Reaktionszeiten werden nacheinander gemessen.
3. **Median berechnen** – aus allen gültigen Messungen wird der Medianwert ermittelt.
4. **Reaktionswert ableiten** – der Median wird in einen Wert zwischen 0,0 und 1,0 umgerechnet.
5. **Persönliches Profil erstellen** – ein Profil mit dem gemessenen Reaktionswert wird erzeugt.
6. **Adaptive Demo starten** – die Demo läuft automatisch mit diesem Profil weiter.

Dabei wird ausschließlich `reaction_speed` aus der Messung abgeleitet. Die übrigen Profilwerte bleiben auf dem Niveau eines durchschnittlichen Spielers:

- `skill_level` bleibt **0,60**
- `accuracy` bleibt **0,60**
- `survival_factor` bleibt **0,65**
- nur `reaction_speed` wird aus dem Reaktionstest personalisiert

---

## Spielerprofile

Drei vordefinierte Profile stehen zur Verfügung:

| Profil                   | skill level | accuracy | reaction speed | survival factor |
|--------------------------|-------------|----------|----------------|-----------------|
| Anfänger                 | 0.35        | 0.30     | 0.25           | 0.40            |
| durchschnittlicher Spieler | 0.60      | 0.60     | 0.55           | 0.65            |
| erfahrener Spieler       | 0.85        | 0.85     | 0.80           | 0.90            |

**Bedeutung der Eigenschaften:**

- **skill level** – allgemeine Spielstärke, beeinflusst die Angriffseffektivität.
- **accuracy** – Trefferquote bei Angriffen.
- **reaction speed** – Geschwindigkeit der Reaktion, reduziert Rundendauer und Schaden.
- **survival factor** – Überlebensfähigkeit, erhöht die Chance, Runden zu überstehen.

---

## Schwierigkeitsparameter

Der Schwierigkeitsgrad liegt zwischen **1** (einfach) und **10** (sehr schwer).
Aus dem Schwierigkeitsgrad werden folgende konkrete Spielparameter abgeleitet:

| Parameter        | Schwierigkeit 1 | Schwierigkeit 5 | Schwierigkeit 10 |
|------------------|-----------------|-----------------|------------------|
| enemy count      | 3               | 7               | 12               |
| enemy damage     | 5               | 9               | 14               |
| health pack rate | 0.40            | 0.28            | 0.13             |

- **Höhere Schwierigkeit** → mehr Gegner, höherer Schaden.
- **Höhere Schwierigkeit** → niedrigere Heilungswahrscheinlichkeit.

---

## Adaptive Agentenlogik

Der `AdaptiveDifficultyAgent` wertet die letzten Spielrunden aus und passt die Schwierigkeit an.

**Standardwerte:**

- Zielgewinnrate: **60 %**
- Fenstergröße: **letzte 5 Runden**

**Entscheidungsregeln (in dieser Reihenfolge):**

1. Mindestens **3 Niederlagen in Folge** → Schwierigkeit reduzieren.
2. Mindestens **3 Siege in Folge** und Gewinnrate über Zielwert → Schwierigkeit erhöhen.
3. Gewinnrate deutlich **unter** dem Zielbereich (≤ 40 %) → Schwierigkeit reduzieren.
4. Gewinnrate deutlich **über** dem Zielbereich (≥ 80 %) → Schwierigkeit erhöhen.
5. Sonst → Schwierigkeit beibehalten.

**Nebenbedingungen:**

- Pro Entscheidung wird die Schwierigkeit um höchstens **eine Stufe** verändert.
- Die Schwierigkeit bleibt immer im Bereich **1 bis 10**.
- Wenn eine Grenze erreicht ist und eine Änderung eigentlich vorgesehen wäre, gilt die Entscheidung als `keep`.

---

## Projektstruktur

```text
.
├── main.py                        # Live-Demo (Terminal-Ausführung)
├── README.md
├── requirements.txt
├── pyrefly.toml
├── src/
│   ├── __init__.py
│   ├── player.py                  # Spielerprofile und Validierung
│   ├── game_simulation.py         # Simulation einer einzelnen Runde
│   ├── difficulty_agent.py        # Schwierigkeitsmodell und adaptiver Agent
│   ├── experiment.py              # Statische und adaptive Experimentläufe
│   ├── reaction_test.py           # Interaktiver Reaktionstest und Erstellung eines persönlichen Profils
│   └── visualization.py          # Diagrammerstellung
├── tests/
│   └── test_simulation.py         # Automatisierte Pytest-Tests (113 Tests)
├── docs/
│   ├── project_scope.md
│   └── project_documentation.md
├── results/
│   ├── data/                      # CSV-Ergebnisdateien
│   │   └── comparison_results.csv
│   └── figures/                   # Exportierte Diagramme (PNG)
│       ├── win_rate_comparison.png
│       ├── target_deviation.png
│       ├── difficulty_progression.png
│       └── moving_win_rate.png
└── .vscode/
    └── settings.json
```

---

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Live-Demo

Die Demo simuliert mehrere Spielrunden und zeigt, wie sich der Schwierigkeitsgrad automatisch anpasst.

**Standardausführung (15 Runden, durchschnittlicher Spieler, Startschwierigkeit 5):**

```bash
python main.py
```

**Beispiele mit CLI-Parametern:**

```bash
python main.py --player beginner --rounds 10 --difficulty 7 --seed 42
python main.py --player expert --rounds 10 --difficulty 3 --seed 42
```

**CLI-Parameter:**

| Parameter            | Beschreibung                                         | Standard  | Gültige Werte                    |
|----------------------|------------------------------------------------------|-----------|----------------------------------|
| `--player`           | Spielerprofil                                        | `average` | `beginner`, `average`, `expert`  |
| `--rounds`           | Anzahl der Spielrunden                               | `15`      | Ganzzahl > 0                     |
| `--difficulty`       | Startschwierigkeit                                   | `5`       | 1 bis 10                         |
| `--seed`             | Zufallsseed für Reproduzierbarkeit                   | `42`      | Beliebige Ganzzahl               |

Ungültige Eingaben werden mit verständlichen Fehlermeldungen abgewiesen.

**Beispiel-Ausgabe (einzelne Runde):**

```
Runde 04 | Schwierigkeit 4 | Gegner 6 | Schaden 8 | Heilung 31 % | Sieg | HP 100 | Trefferquote 47 % | Agent: increase | Nächste Schwierigkeit 5
  Gesamtgewinnrate 75.0 % | Letzte 4 Runden 75.0 %
```

---

## Reaktionstest-Modus

Der Reaktionstest ist ein optionaler interaktiver Modus. Er misst die Reaktionszeit des Nutzers im Terminal und erstellt daraus ein personalisiertes Spielerprofil für die adaptive Demo.
Das Ergebnis ist eine **reaktionsbasierte Profileinschätzung** – keine wissenschaftliche Bewertung der vollständigen Spielfähigkeit.

**Einfacher Start:**

```bash
python main.py --reaction-test
```

**Beispiele mit weiteren Parametern:**

```bash
python main.py --reaction-test --reaction-attempts 5 --rounds 10 --difficulty 5 --seed 42
python main.py --reaction-test --reaction-attempts 7 --rounds 20 --difficulty 6 --seed 123
```

**Neue CLI-Parameter:**

| Parameter              | Beschreibung                                                          | Standard | Gültige Werte  |
|------------------------|-----------------------------------------------------------------------|----------|----------------|
| `--reaction-test`      | Aktiviert den interaktiven Reaktionstest-Modus                        | –        | Flag (kein Wert) |
| `--reaction-attempts`  | Anzahl der gültigen Reaktionszeitenmessungen                          | `5`      | Ganzzahl ≥ 3   |

**Verhalten:**

- `--player` wird im Reaktionstest-Modus ignoriert; das Profil wird aus der Messung erzeugt.
- `--rounds`, `--difficulty` und `--seed` wirken wie gewohnt auf die nachfolgende adaptive Demo.
- Der `--seed` steuert zusätzlich die zufällige Wartesequenz vor jedem `JETZT!`-Signal.
- Die tatsächliche menschliche Reaktionszeit ist von Natur aus nicht reproduzierbar.

---

### Reaktionstest-Logik

Der Test erfordert mindestens **3 gültige Messungen**; der Standardwert sind **5 Messungen**.
Zur Auswertung wird der **Median** der Messungen verwendet (nicht der Durchschnitt), da dieser robuster gegenüber Ausreißern ist.

**Ungültige Messungen:**

Messungen unter **80 ms** werden als implausibel frühe oder gepufferte Tastendrücke abgelehnt.
Die entsprechende Ausgabe lautet: `Zu früh gedrückt. Der Versuch wird wiederholt.`
Abgelehnte Messungen werden nicht in das Ergebnis aufgenommen und der Versuch wird automatisch wiederholt, bis die gewünschte Anzahl gültiger Messungen vorliegt.

**Reaktionswert-Berechnung:**

| Reaktionszeit          | Reaktionswert |
|------------------------|:-------------:|
| ≤ 150 ms               | 1,00          |
| 325 ms (Mittelpunkt)   | ≈ 0,50        |
| ≥ 500 ms               | 0,00          |

Zwischen 150 ms und 500 ms wird linear interpoliert. Der Wert wird auf den Bereich \[0,0 – 1,0\] begrenzt.

**Profilkategorien:**

| Reaktionszeit           | Kategorie   |
|-------------------------|:-----------:|
| unter 220 ms            | `expert`    |
| 220 ms bis < 350 ms     | `average`   |
| 350 ms und darüber      | `beginner`  |

> **Hinweis:** Diese Kategorien sind projektspezifische Schwellenwerte für die Demo. Sie stellen keine wissenschaftliche Bewertung der allgemeinen Spielfähigkeit dar.

---

### Persönliches Profil

Aus dem gemessenen Medianwert wird ein Spielerprofil nach folgendem Schema erstellt:

| Eigenschaft      | Wert                    |
|------------------|------------------------:|
| Name             | Reaktionstest-Spieler   |
| skill level      | 0,60                    |
| accuracy         | 0,60                    |
| reaction speed   | aus Reaktionstest       |
| survival factor  | 0,65                    |

Nur `reaction_speed` wird aus der Nutzermessung abgeleitet. Alle anderen Werte entsprechen dem Niveau eines durchschnittlichen Spielers und bleiben fest. Das Ergebnis ist eine **reaktionsbasierte Profileinschätzung**, keine umfassende Bewertung der Spielfähigkeit.

---

## Tests

Die automatisierten Tests werden mit pytest ausgeführt:

```bash
python -m pytest -v
```

oder mit dem Venv direkt:

```bash
./.venv/bin/python -m pytest -v
```

**Aktueller Teststand: 113 Tests bestanden**

Abgedeckte Bereiche:

- `PlayerProfile` – Erstellung, Validierung, Grenzwerte
- `simulate_round` – Reproduzierbarkeit, Wertebereiche, Fehlerpfade
- `get_difficulty_settings` – Monotonie, Identität, Grenzen
- `AdaptiveDifficultyAgent` – alle Entscheidungsregeln, Grenzen, Fehlerpfade
- `run_static_experiment` – Rundenzahl, keine Änderungen, Reproduzierbarkeit
- `run_adaptive_experiment` – Entscheidungen, Grenzen, Reproduzierbarkeit
- `run_comparison_experiments` – CSV-Ausgabe, Fehlerpfade, Reproduzierbarkeit
- `main.py`-Hilfsfunktionen – Spielerauswahl, Gewinnratenberechnung
- Reaktionswert-Berechnung (`calculate_reaction_score`) – Grenzwerte, Clamping, Fehlerpfade
- Schwellenwert-Klassifikation (`classify_reaction_time`) – alle Kategoriegrenzen
- Median-Auswertung (`evaluate_reaction_times`) – Korrektheit, Fehlerpfade
- Persönliche Profilerstellung (`create_reaction_profile`) – Werte, Typen
- Interaktiver Reaktionstest (`run_reaction_test`) – gemockter Input und Timing
- Ablehnung von Messungen unter 80 ms und Wiederholungsverhalten
- Verarbeitung eines festen Seeds für die Wartesequenz

---

## Experimente und Ergebnisse

Das System unterstützt zwei Experimenttypen, die automatisch verglichen werden:

- **Statisches System** – Die Schwierigkeit bleibt über alle Runden konstant.
- **Adaptives System** – Der Agent passt die Schwierigkeit nach jeder Runde an.

Beide Systeme werden für:
- alle drei Spielerprofile,
- mehrere feste Seeds

ausgeführt. Die Ergebnisse sind vollständig reproduzierbar.

**Ausgabe:**

- Zusammenfassende Statistiken werden als CSV unter `results/data/comparison_results.csv` gespeichert.
- Diagramme werden unter `results/figures/` als PNG-Dateien exportiert.

---

## Visualisierungen

| Datei                        | Inhalt                                                                                     |
|------------------------------|--------------------------------------------------------------------------------------------|
| `win_rate_comparison.png`    | Vergleich der mittleren Gewinnraten beider Systeme je Spielerprofil.                       |
| `target_deviation.png`       | Abweichung der Gewinnrate vom Zielwert (60 %) für statisches und adaptives System.         |
| `difficulty_progression.png` | Verlauf der Schwierigkeitsstufe über alle Runden für ein ausgewähltes adaptives Experiment.       |
| `moving_win_rate.png`        | Gleitende Gewinnrate im Zeitverlauf – zeigt, wie schnell sich das System einpendelt.       |

---

## Aktuelle Kernergebnisse

Die Experimente zeigen folgende Tendenzen:

- Das adaptive System hilft besonders **Anfängern** und **erfahrenen Spielern**, näher an die Zielgewinnrate von 60 % zu kommen, da der Agent die Schwierigkeit aktiv anpasst.
- Beim **durchschnittlichen Spieler** kann das statische System bei gut gewählter Ausgangsschwierigkeit bereits ausreichend nah am Zielwert liegen.
- Das adaptive System ist **nicht automatisch in jedem einzelnen Fall besser** als das statische – die Wirkung hängt vom Spielerprofil und der gewählten Ausgangsschwierigkeit ab.
- Die Ergebnisse zeigen, dass die Effektivität der Anpassung von **Ausgangsbedingungen** (Spielerprofil, Startschwierigkeit, Seed) abhängt.

---

## Reproduzierbarkeit

Simulationen mit einem festen Seed sind vollständig reproduzierbar:

- Bei Verwendung eines festen Seeds wird für jede Runde ein deterministischer Rundenseed verwendet (`seed + Rundennummer - 1`).
- Gleiche Eingaben (Spielerprofil, Startschwierigkeit, Seed) erzeugen **identische Ausgaben**.
- CSV-Dateien können bei gleichen Parametern byte-identisch erzeugt werden; dies wird im manuellen Reproduzierbarkeitstest von `src/experiment.py` geprüft.
- Die Pytest-Suite prüft zusätzlich die Reproduzierbarkeit zentraler Simulationsergebnisse.

**Reaktionstest:**

- Die zufällige Wartesequenz vor jedem `JETZT!`-Signal ist mit einem festen `--seed` reproduzierbar.
- Die tatsächlichen Reaktionszeitenmessungen sind **nicht reproduzierbar**, da sie von menschlichem Input abhängen.
- Die adaptive Simulation nach der Profilerstellung bleibt für dasselbe erzeugte Profil und denselben Simulationsseed reproduzierbar.

---

## Grenzen des Modells

Das Modell vereinfacht die Realität an mehreren Stellen:

- Die Spielsimulation ist **probabilistisch und stark vereinfacht** – keine echte Game Engine.
- Die drei Standardprofile sind synthetisch. Im Reaktionstest-Modus wird lediglich der Wert `reaction_speed` aus einer realen Nutzermessung abgeleitet; die übrigen Profilwerte bleiben vordefiniert.
- Der Agent verwendet **keine lernenden Verfahren** (kein Reinforcement Learning, kein neuronales Netz).
- Es gibt **keine komplexe Gegner-KI** – Gegner werden durch einzelne Parameter beschrieben.
- Die **Gewinnrate** dient als vereinfachter Näherungswert für „Spielspaß" und bildet die tatsächliche Spielerfahrung nur grob ab.
- Die Reaktionszeit im Terminal wird durch Display-Latenz, Tastatur-Latenz, Fingerposition, Aufmerksamkeit und Terminal-Verhalten beeinflusst und ist kein präzises Labor-Messinstrument.
- Reaktionszeit allein repräsentiert **nicht die vollständige Spielfähigkeit** eines Nutzers.
- Die Kategorien `expert`, `average` und `beginner` sind vereinfachte projektspezifische Labels für die Demo und stellen **keine wissenschaftliche Bewertung** dar.
