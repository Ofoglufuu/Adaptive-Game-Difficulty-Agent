# Adaptive Game Difficulty Agent

Ein agentenbasiertes System, das den Schwierigkeitsgrad einer Spielsimulation automatisch an die Leistung des Spielers anpasst.

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
│   └── visualization.py          # Diagrammerstellung
├── tests/
│   └── test_simulation.py         # Automatisierte Pytest-Tests (74 Tests)
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

| Parameter      | Beschreibung                                  | Standard  | Gültige Werte                |
|----------------|-----------------------------------------------|-----------|------------------------------|
| `--player`     | Spielerprofil                                 | `average` | `beginner`, `average`, `expert` |
| `--rounds`     | Anzahl der Spielrunden                        | `15`      | Ganzzahl > 0                 |
| `--difficulty` | Startschwierigkeit                            | `5`       | 1 bis 10                     |
| `--seed`       | Zufallsseed für Reproduzierbarkeit            | `42`      | Beliebige Ganzzahl           |

Ungültige Eingaben werden mit verständlichen Fehlermeldungen abgewiesen.

**Beispiel-Ausgabe (einzelne Runde):**

```
Runde 04 | Schwierigkeit 4 | Gegner 6 | Schaden 8 | Heilung 31 % | Sieg | HP 100 | Trefferquote 47 % | Agent: increase | Nächste Schwierigkeit 5
  Gesamtgewinnrate 75.0 % | Letzte 4 Runden 75.0 %
```

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

**Aktueller Teststand: 74 Tests bestanden**

Abgedeckte Bereiche:

- `PlayerProfile` – Erstellung, Validierung, Grenzwerte
- `simulate_round` – Reproduzierbarkeit, Wertebereiche, Fehlerpfade
- `get_difficulty_settings` – Monotonie, Identität, Grenzen
- `AdaptiveDifficultyAgent` – alle Entscheidungsregeln, Grenzen, Fehlerpfade
- `run_static_experiment` – Rundenzahl, keine Änderungen, Reproduzierbarkeit
- `run_adaptive_experiment` – Entscheidungen, Grenzen, Reproduzierbarkeit
- `run_comparison_experiments` – CSV-Ausgabe, Fehlerpfade, Reproduzierbarkeit
- `main.py`-Hilfsfunktionen – Spielerauswahl, Gewinnratenberechnung

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

---

## Grenzen des Modells

Das Modell vereinfacht die Realität an mehreren Stellen:

- Die Spielsimulation ist **probabilistisch und stark vereinfacht** – keine echte Game Engine.
- Es werden **keine realen Spielerdaten** verwendet; alle Profile sind synthetisch.
- Der Agent verwendet **keine lernenden Verfahren** (kein Reinforcement Learning, kein neuronales Netz).
- Es gibt **keine komplexe Gegner-KI** – Gegner werden durch einzelne Parameter beschrieben.
- Die **Gewinnrate** dient als vereinfachter Näherungswert für „Spielspaß" und bildet die tatsächliche Spielerfahrung nur grob ab.

---

## Ausblick

Mögliche Erweiterungen des Projekts:

- **Echte Spielintegration** – Einbindung in eine tatsächliche Spielumgebung.
- **Reale Telemetriedaten** – Nutzung echter Spielerstatistiken statt synthetischer Profile.
- **Lernender Agent** – Einsatz von Reinforcement Learning für kontextbewusstere Entscheidungen.
- **Personalisierte Zielbereiche** – unterschiedliche Zielgewinnraten je nach Spielerpräferenz.
- **Grafische Benutzeroberfläche** – interaktive Steuerung der Demo-Parameter.
- **Längere Experimente** – mehr Runden und Seeds für statistisch belastbarere Ergebnisse.
