# Projektdokumentation

## Adaptive Game Difficulty Agent – Dynamische Schwierigkeitsanpassung durch Spielersimulation

---

## 1. Einleitung

Viele Videospiele bieten Spielern einen oder mehrere vordefinierte Schwierigkeitsgrade an. Wird ein solcher Schwierigkeitsgrad zu Beginn gewählt, bleibt er häufig für die gesamte Spielsitzung konstant. Für einen unerfahrenen Spieler kann ein mittlerer Schwierigkeitsgrad bereits zu herausfordernd sein, während er einen erfahrenen Spieler nicht ausreichend fordert. Diese Diskrepanz kann dazu führen, dass das Spiel entweder frustrierend oder langweilig wirkt – beides sind Gründe, die zum Abbruch führen.

Dynamische Schwierigkeitsanpassung (*Dynamic Difficulty Adjustment*, DDA) versucht, den Schwierigkeitsgrad während des Spielens automatisch an die beobachtete Leistung des Spielers anzupassen. Ziel ist es, eine ausgewogene Spielerfahrung zu schaffen, bei der der Spieler weder überfordert noch unterfordert wird.

Dieses Projekt implementiert ein solches System in Form eines regelbasierten, agentenbasierten Ansatzes. Da der Zugang zu einer echten Spiel-Engine außerhalb des Projektumfangs liegt, wird die Spielumgebung durch eine vereinfachte probabilistische Simulation ersetzt. Diese Simulation modelliert Spielrunden mit konfigurierbaren Parametern und gibt für jede Runde ein Ergebnis aus, das von Spielerprofil und Schwierigkeitsgrad abhängt.

Das Kernstück des Systems ist ein adaptiver Agent (`AdaptiveDifficultyAgent`), der nach jeder Runde die jüngsten Spielergebnisse auswertet und den Schwierigkeitsgrad erhöht, reduziert oder beibehält. Dieses adaptive System wird einem statischen System gegenübergestellt, bei dem der Schwierigkeitsgrad über alle Runden konstant bleibt.

Als zusätzliche interaktive Erweiterung wurde ein **optionaler Reaktionstest-Modus** implementiert. Dieser Modus ermöglicht es einem Nutzer, seine Reaktionszeit im Terminal zu messen und daraus ein personalisiertes Spielerprofil zu generieren, das anschließend direkt in der adaptiven Live-Demo verwendet werden kann. Dieser Modus ist kein Teil des wissenschaftlichen Kernexperiments. Er dient als interaktives Demo-Feature und liefert eine **reaktionsbasierte Profileinschätzung** – keine umfassende wissenschaftliche Bewertung der Spielfähigkeit.

---

## 2. Forschungsfrage

**Kann ein adaptiver Schwierigkeitsagent eine ausgewogenere Spielerfahrung erzeugen als ein statisches Schwierigkeitssystem?**

Als Näherungswert für „Ausgewogenheit" wird die **Gewinnrate** herangezogen. Eine Gewinnrate nahe dem Zielwert von **60 %** gilt als ausgewogen: Der Spieler gewinnt häufig genug, um motiviert zu bleiben, verliert aber auch regelmäßig, um Herausforderung zu empfinden.

Diese Vereinfachung ist bewusst gewählt. Die tatsächliche Spielerfahrung hängt von zahlreichen weiteren Faktoren ab – etwa von der wahrgenommenen Fairness, dem Spielfluss und dem emotionalen Engagement –, die durch eine Simulationsumgebung nicht abgebildet werden können. Die Gewinnrate dient daher nur als erster, praktisch messbarer Annäherungswert.

Die Forschungsfrage wird durch Experimente mit drei synthetischen Spielerprofilen, einer konfigurierbaren Startschwierigkeit und mehreren festen Zufalls-Seeds untersucht.

---

## 3. Projektziele

Das Projekt verfolgt folgende konkrete Ziele:

- Modellierung von drei synthetischen Spielerprofilen mit definierten Stärke- und Schwächewerten
- Definition von Schwierigkeitsstufen von 1 bis 10
- Umrechnung von Schwierigkeitsstufen in konkrete Spielparameter
- Probabilistische Simulation von Spielrunden
- Implementierung eines regelbasierten adaptiven Schwierigkeitsagenten
- Vergleich des adaptiven Systems mit einem statischen System
- Reproduzierbare Experimente mit festen Seeds
- Export der Ergebnisse als CSV-Datei
- Erzeugung von Visualisierungsdiagrammen
- Bereitstellung einer interaktiven Terminal-Live-Demo
- Bereitstellung eines optionalen Reaktionstest-Modus
- Generierung eines personalisierten reaktionsbasierten Spielerprofils
- Validierung der Implementierung durch automatisierte Pytest-Tests

**Aktueller Teststand: 113 Tests bestanden**

---

## 4. Systemarchitektur

### 4.1 Hauptsystem – Adaptiver Schwierigkeitsagent

Der Datenfluss des Kernsystems folgt einer klaren Sequenz:

1. Ein Spielerprofil wird ausgewählt oder erzeugt.
2. Die aktuelle Schwierigkeitsstufe wird in konkrete Spielparameter (`DifficultySettings`) umgerechnet.
3. Eine Spielrunde wird mit diesen Parametern und dem Spielerprofil simuliert.
4. Das Ergebnis (`GameRoundResult`) wird in der Verlaufshistorie gespeichert.
5. Der adaptive Agent wertet die jüngsten Ergebnisse aus.
6. Der Agent wählt eine der drei Aktionen: `increase`, `decrease` oder `keep`.
7. Die nächste Runde verwendet die aktualisierte Schwierigkeitsstufe.
8. Nach allen Runden können Ergebnisse exportiert und visualisiert werden.

```
Spielerprofil
     │
     ▼
Schwierigkeitsstufe (1–10)
     │
     ▼
get_difficulty_settings()
     │
     ▼
DifficultySettings
(enemy_count, enemy_damage, health_pack_rate)
     │
     ▼
simulate_round()
     │
     ▼
GameRoundResult
(victory, remaining_health, accuracy, ...)
     │
     ▼
AdaptiveDifficultyAgent.decide()
     │
     ▼
DifficultyDecision
(increase / decrease / keep)
     │
     ▼
Nächste Schwierigkeitsstufe
```

### 4.2 Reaktionstest-Pfad

Der optionale Reaktionstest-Modus erzeugt ein personalisiertes Profil und startet danach die reguläre adaptive Demo:

```
Nutzer startet Reaktionstest
     │
     ▼
Mehrere Reaktionszeitenmessungen (≥ 3 gültig)
     │
     ▼
evaluate_reaction_times()
(Median, Validierung)
     │
     ▼
calculate_reaction_score()
(Median → reaction_speed ∈ [0.0, 1.0])
     │
     ▼
create_reaction_profile()
(Reaktionstest-Spielerprofil)
     │
     ▼
Adaptive Live-Demo startet mit persönlichem Profil
```

---

## 5. Modulübersicht

### 5.1 `src/player.py`

Dieses Modul definiert das Datenmodell für Spielerprofile.

**`PlayerProfile`** ist das Datenmodell für Spielerprofile und enthält folgende Felder:

| Feld | Typ | Bedeutung |
|---|---|---|
| `name` | `str` | Name des Profils; darf nicht leer oder nur aus Leerzeichen bestehen |
| `skill_level` | `float` | Allgemeine Spielstärke; beeinflusst die Angriffseffektivität |
| `accuracy` | `float` | Trefferquote; wirkt auf Rundengenauigkeit und Angriffserfolg |
| `reaction_speed` | `float` | Reaktionsgeschwindigkeit; reduziert Rundendauer und beeinflusst Schadensabwehr |
| `survival_factor` | `float` | Überlebensfähigkeit; beeinflusst die Chance, Runden zu überstehen |

Alle numerischen Felder werden beim Erstellen validiert: Sie müssen im Bereich `[0.0, 1.0]` liegen. Ein leerer oder nur aus Leerzeichen bestehender Name löst eine `ValueError`-Ausnahme aus.

**`create_default_players()`** erzeugt und gibt eine Liste mit drei vordefinierten Standardprofilen zurück:

- Anfänger
- durchschnittlicher Spieler
- erfahrener Spieler

---

### 5.2 `src/game_simulation.py`

Dieses Modul implementiert die Simulation einer einzelnen Spielrunde.

**`GameRoundResult`** ist ein Dataclass mit folgenden Ausgabefeldern:

| Feld | Typ | Bedeutung |
|---|---|---|
| `victory` | `bool` | Ob der Spieler die Runde gewonnen hat |
| `remaining_health` | `int` | Verbleibende Trefferpunkte am Ende der Runde (0–100) |
| `damage_taken` | `int` | Erlittener Schaden (0–100) |
| `accuracy` | `float` | Erzielte Trefferquote in dieser Runde (0.0–1.0) |
| `round_duration` | `float` | Simulierte Rundendauer in Sekunden |
| `difficulty_level` | `int` | Verwendete Schwierigkeitsstufe |
| `enemy_count` | `int` | Anzahl der Gegner in dieser Runde |
| `enemy_damage` | `int` | Schaden pro Gegner |
| `health_pack_rate` | `float` | Heilungswahrscheinlichkeit dieser Runde |

**`simulate_round(...)`** berechnet probabilistisch, ob der Spieler eine Runde gewinnt oder verliert. Die Gewinnwahrscheinlichkeit wird aus mehreren Faktoren zusammengesetzt:

- **Offensive Stärke** (`offensive_power`): gewichtete Kombination aus `skill_level` und `accuracy`.
- **Defensive Stärke** (`defensive_power`): gewichtete Kombination aus `reaction_speed` und `survival_factor`.
- **Bedrohungswert** (`threat_score`): Produkt aus `enemy_count` und `enemy_damage`, normiert.
- **Heilungsbonus** (`health_bonus`): proportional zur `health_pack_rate`.
- **Schwierigkeitsstrafe** (`difficulty_penalty`): wächst linear mit der Schwierigkeitsstufe.

Aus diesen Bestandteilen ergibt sich eine Gewinnwahrscheinlichkeit, die auf den Bereich `[0.05, 0.95]` begrenzt wird, sodass immer ein Zufallsanteil erhalten bleibt. Der Ausgang wird durch `rng.random() < win_probability` bestimmt.

Gesundheit, Schaden, Genauigkeit und Rundendauer werden ebenfalls probabilistisch berechnet und sind an Spielerprofil sowie Schwierigkeit gebunden.

Die Eingaben werden validiert: Schwierigkeit muss zwischen 1 und 10 liegen, `enemy_count` und `enemy_damage` müssen positiv sein, `health_pack_rate` muss im Bereich `[0.0, 1.0]` liegen.

Bei Übergabe eines festen `seed`-Werts wird intern eine lokale `random.Random(seed)`-Instanz verwendet. Identische Eingaben mit demselben Seed liefern immer identische Ergebnisse.

---

### 5.3 `src/difficulty_agent.py`

Dieses Modul enthält die Schwierigkeitsabbildung und den adaptiven Agenten.

**`DifficultySettings`** ist ein Dataclass mit den konkreten Spielparametern für eine Schwierigkeitsstufe:

- `difficulty_level`, `enemy_count`, `enemy_damage`, `health_pack_rate`

**`get_difficulty_settings(difficulty_level)`** übersetzt eine ganzzahlige Schwierigkeitsstufe (1–10) in ein `DifficultySettings`-Objekt. Die Umrechnungsformeln sind im Kapitel 7 dokumentiert.

**`DifficultyDecision`** ist ein Dataclass, das die Entscheidung des Agenten für eine Runde festhält:

- `previous_level`, `new_level`, `action` (`"increase"`, `"decrease"`, `"keep"`), `reason`, `recent_win_rate`, `consecutive_wins`, `consecutive_losses`

**`AdaptiveDifficultyAgent`** ist der Kern des Systems. Der Agent wird mit folgenden Parametern initialisiert:

- `target_win_rate` (Standard: 0.60)
- `window_size` (Standard: 5)
- `min_difficulty` (Standard: 1)
- `max_difficulty` (Standard: 10)

Die Methode `decide(current_level, recent_results)` wertet das Fenster der jüngsten Ergebnisse aus und gibt eine `DifficultyDecision` zurück. Die Entscheidungsregeln und ihre Reihenfolge sind in Kapitel 9 beschrieben.

---

### 5.4 `src/experiment.py`

Dieses Modul stellt Funktionen für strukturierte Experimentläufe bereit.

**`ExperimentResult`** fasst die Ergebnisse eines vollständigen Experiments zusammen:

- Systemtyp (`"static"` oder `"adaptive"`)
- Spielername, Startschwierigkeit, Zielgewinnrate
- Gesamtrunden, Gesamtsiege, Gesamtniederlagen
- Gesamtgewinnrate, finale Schwierigkeit, Anzahl der Schwierigkeitsänderungen
- Durchschnittliche Trefferpunkte, Schaden, Genauigkeit und Rundendauer
- Liste der Rundenresultate und Agentenentscheidungen

**`run_static_experiment(...)`** führt ein Experiment mit konstanter Schwierigkeit durch: Es werden keine Agentenentscheidungen getroffen, und `difficulty_changes` ist immer 0.

**`run_adaptive_experiment(...)`** führt ein Experiment mit dem adaptiven Agenten durch: Nach jeder Runde entscheidet der Agent, ob die Schwierigkeit angepasst wird.

**`run_comparison_experiments(...)`** kombiniert beide Systeme für alle übergebenen Spielerprofile und Seeds. Die Ergebnisse werden als CSV-Datei gespeichert. Die Funktion validiert Eingaben und wirft `ValueError` bei ungültigen Parametern.

---

### 5.5 `src/visualization.py`

Dieses Modul erzeugt auf Basis der `ExperimentResult`-Liste vier Diagramme:

| Datei | Inhalt |
|---|---|
| `win_rate_comparison.png` | Mittlere Gewinnraten im Vergleich, gruppiert nach Spielerprofil |
| `target_deviation.png` | Abweichung der Gewinnrate vom 60-%-Zielwert |
| `difficulty_progression.png` | Schwierigkeitsverlauf über Runden für einen ausgewählten adaptiven Lauf |
| `moving_win_rate.png` | Gleitende Gewinnrate im Zeitverlauf |

Alle Diagramme werden unter `results/figures/` gespeichert. Das Verzeichnis wird automatisch angelegt, wenn es noch nicht existiert.

---

### 5.6 `src/reaction_test.py`

Dieses Modul implementiert den optionalen Reaktionstest-Modus vollständig. Es verwendet ausschließlich die Python-Standardbibliothek (`random`, `statistics`, `time`). Alle nutzersichtigen Ausgaben sind auf Deutsch.

**`ReactionTestResult`** (Dataclass):

| Feld | Typ | Bedeutung |
|---|---|---|
| `reaction_times_ms` | `list[float]` | Alle gültigen Messwerte in Millisekunden |
| `median_reaction_time_ms` | `float` | Median der Messungen |
| `reaction_score` | `float` | Abgeleiteter Reaktionswert (0.0–1.0) |
| `profile_category` | `str` | Kategorie: `"expert"`, `"average"` oder `"beginner"` |

**`calculate_reaction_score(reaction_time_ms)`** rechnet eine Reaktionszeit in einen Score zwischen 0,0 und 1,0 um. Werte ≤ 0 lösen `ValueError` aus. Ergebnisse werden auf `[0.0, 1.0]` begrenzt.

**`classify_reaction_time(reaction_time_ms)`** ordnet eine Reaktionszeit einer der drei Kategorien zu. Werte ≤ 0 lösen `ValueError` aus.

**`evaluate_reaction_times(reaction_times_ms)`** validiert eine Liste von Messwerten (mindestens 3, alle > 0), berechnet den Median, den Reaktionswert und die Kategorie und gibt ein vollständiges `ReactionTestResult` zurück.

**`create_reaction_profile(median_reaction_time_ms)`** erstellt ein `PlayerProfile` mit dem Namen `"Reaktionstest-Spieler"`. Nur `reaction_speed` wird aus dem Reaktionstest abgeleitet; alle anderen Werte sind fest vorgegeben.

**`run_reaction_test(...)`** ist die interaktive Hauptfunktion. Sie:

- validiert alle Eingabeparameter (mindestens 3 Versuche, positive Wartezeiten)
- erzeugt mit `random.Random(seed)` die zufälligen Wartezeiten (reproduzierbar wenn Seed gesetzt)
- misst Reaktionszeiten mit `time.perf_counter()`
- lehnt Messungen unter 80 ms als implausibel ab und wiederholt den Versuch
- berechnet nach allen gültigen Messungen das Ergebnis
- gibt das Ergebnis auf Deutsch aus

Die tatsächlichen menschlichen Reaktionszeiten sind von Natur aus nicht reproduzierbar.

---

### 5.7 `main.py`

`main.py` ist der Einstiegspunkt für die Terminal-Live-Demo.

**Normaler Modus:**

- CLI-Argumente werden mit `argparse` eingelesen und validiert.
- Das Spielerprofil wird über `--player` ausgewählt.
- `run_demo(...)` führt die Simulation über die angegebenen Runden aus.
- Nach jeder Runde werden Schwierigkeitsstufe, Ergebnis, Trefferquote, Agent-Aktion und Gewinnrate ausgegeben.
- Falls der Agent die Schwierigkeit ändert, wird der Grund ausgegeben.
- Am Ende wird eine tabellarische Zusammenfassung gedruckt.

**Reaktionstest-Modus** (`--reaction-test`):

- `--player` wird ignoriert; ein kurzer Hinweis wird ausgegeben.
- `run_reaction_test(attempts, seed)` wird aufgerufen.
- Aus dem Ergebnis wird mit `create_reaction_profile(...)` ein persönliches Profil erstellt.
- Das Profil wird angezeigt.
- Die adaptive Demo startet automatisch mit diesem Profil.

---

### 5.8 `tests/test_simulation.py`

Die gesamte Testsuite befindet sich in einer einzelnen Datei und wird mit Pytest ausgeführt.

**Aktueller Stand: 113 Tests bestanden**

Die Tests decken folgende Bereiche ab:

- Erstellung und Validierung von `PlayerProfile`
- Grenzwerte und ungültige Eingaben
- Reproduzierbarkeit von `simulate_round`
- Wertebereiche aller Ausgabefelder
- Korrektheit von `get_difficulty_settings`
- Alle Entscheidungsregeln des `AdaptiveDifficultyAgent`
- Grenzen der Schwierigkeitsstufen
- Statische Experimentläufe
- Adaptive Experimentläufe
- Vergleichsexperimente und CSV-Ausgabe
- CLI-Hilfsfunktionen
- Reaktionswert-Berechnung mit Clamping und Fehlerpfaden
- Schwellenwert-Klassifikation
- Median-Auswertung
- Erstellung des persönlichen Profils
- Interaktiver Reaktionstest mit gemocktem `input`, `time.sleep` und `time.perf_counter`
- Ablehnung von Messungen unter 80 ms
- Wiederholungsverhalten bei ungültigen Messungen
- Verarbeitung eines festen Seeds für die Wartesequenz

Tests warten nicht auf echte Nutzereingaben und führen keine realen Mehrsekundenpausen durch.

---

## 6. Spielerprofile

### 6.1 Standardprofile

Die drei vordefinierten synthetischen Profile sind:

| Profil | skill level | accuracy | reaction speed | survival factor |
|---|---:|---:|---:|---:|
| Anfänger | 0.35 | 0.30 | 0.25 | 0.40 |
| durchschnittlicher Spieler | 0.60 | 0.60 | 0.55 | 0.65 |
| erfahrener Spieler | 0.85 | 0.85 | 0.80 | 0.90 |

Alle Profile sind synthetisch und repräsentieren keine realen Spielerdaten.

### 6.2 Bedeutung der Profileigenschaften

**`skill_level`** repräsentiert die allgemeine Spielstärke. In der Simulation geht dieser Wert mit höherem Gewicht in die offensive Stärke ein. Ein hoher Wert führt zu einer größeren Gewinnwahrscheinlichkeit.

**`accuracy`** repräsentiert die Trefferquote. Sie beeinflusst sowohl die offensive Stärke als auch die in der Runde erzielte Genauigkeit. Höhere Genauigkeit senkt ebenfalls die Rundendauer leicht.

**`reaction_speed`** repräsentiert die Reaktionsgeschwindigkeit. Sie geht in die defensive Stärke ein und beeinflusst die Rundendauer: Ein reaktionsschneller Spieler beendet Runden schneller. Im Reaktionstest-Modus ist dies der einzige aus einer Nutzermessung abgeleitete Wert.

**`survival_factor`** repräsentiert die Überlebensfähigkeit. Er geht in die defensive Stärke ein und erhöht gemeinsam mit `reaction_speed` die Chance, Schaden zu reduzieren und Runden zu überleben.

---

## 7. Schwierigkeitsmodell

Der Schwierigkeitsgrad liegt im Bereich **1** (leichteste Stufe) bis **10** (schwerste Stufe). Jede Stufe wird durch `get_difficulty_settings(difficulty_level)` in drei konkrete Parameter umgerechnet:

```
enemy_count     = 3 + (difficulty_level - 1)
enemy_damage    = 5 + (difficulty_level - 1)
health_pack_rate = max(0.0, 0.40 - 0.03 * (difficulty_level - 1))
```

Der `health_pack_rate`-Wert wird auf zwei Nachkommastellen gerundet.

**Auswirkungen:**

- Mit steigender Schwierigkeit nimmt die Anzahl der Gegner zu.
- Mit steigender Schwierigkeit nimmt der Schaden pro Gegner zu.
- Mit steigender Schwierigkeit sinkt die Heilungswahrscheinlichkeit.

**Beispielwerte:**

| Schwierigkeit | enemy count | enemy damage | health pack rate |
|---:|---:|---:|---:|
| 1 | 3 | 5 | 0.40 |
| 5 | 7 | 9 | 0.28 |
| 10 | 12 | 14 | 0.13 |

---

## 8. Rundensimulation

Die Simulation bildet eine einzelne Spielrunde probabilistisch ab. Sie ist keine realistische Spiel-Engine, sondern ein kontrolliertes Modell für reproduzierbare Experimente.

Für jede Runde werden folgende Schritte durchgeführt:

1. Aus Spielerprofil und Schwierigkeitsparametern wird eine **Gewinnwahrscheinlichkeit** berechnet. Sie berücksichtigt offensive Stärke, defensive Stärke, Heilungsbonus und Schwierigkeitsstrafe und wird auf `[0.05, 0.95]` begrenzt.
2. Ein Zufallswert entscheidet, ob die Runde gewonnen oder verloren wird.
3. Der **Schaden** ergibt sich aus dem Bedrohungswert, der defensiven Stärke und einem Zufallsanteil. Bei Niederlage beträgt der Schaden stets 100; verbleibende Trefferpunkte sind dann 0.
4. Die **Rundengenauigkeit** variiert um die Basisgenauigkeit des Spielers mit einem kleinen Zufallsanteil und wird durch die Schwierigkeit leicht gesenkt.
5. Die **Rundendauer** ergibt sich aus einer Basiszeit, einem Bonus für Gegnerzahl und Schwierigkeit sowie einer Reduzierung durch die Reaktionsgeschwindigkeit des Spielers.

Durch Verwendung eines festen Seeds wird intern eine lokale Zufallsinstanz erzeugt, die vollständige Reproduzierbarkeit garantiert. Gleiche Eingaben mit gleichem Seed liefern immer identische Ausgaben. Dies ist für die Experiment-Reproduzierbarkeit essenziell.

---

## 9. Adaptive Agentenlogik

### 9.1 Standardparameter

| Parameter | Wert |
|---|---:|
| Zielgewinnrate | 60 % |
| Fenstergröße | letzte 5 Runden |
| Minimale Schwierigkeit | 1 |
| Maximale Schwierigkeit | 10 |

### 9.2 Entscheidungsregeln

Der Agent wertet nach jeder Runde das aktuelle Fenster der jüngsten Ergebnisse aus. Die Regeln werden in dieser festen Reihenfolge geprüft:

1. **Drei aufeinanderfolgende Niederlagen** → `decrease`
2. **Drei aufeinanderfolgende Siege** und Gewinnrate im Fenster über dem Zielwert → `increase`
3. **Gewinnrate ≤ 40 %** (Ziel minus 20 Prozentpunkte) → `decrease`
4. **Gewinnrate ≥ 80 %** (Ziel plus 20 Prozentpunkte) → `increase`
5. **Sonst** → `keep`

### 9.3 Erläuterungen

Die **Reihenfolge** der Regeln ist bewusst gewählt: Aufeinanderfolgende Niederlagen oder Siege werden als stärkste Signale gewertet und erhalten Vorrang vor der allgemeinen Gewinnrate. Dadurch reagiert der Agent schnell auf eindeutige Leistungseinbrüche oder -spitzen.

Der Agent verändert die Schwierigkeit pro Entscheidung um **höchstens eine Stufe**. Dies verhindert abrupte Sprünge, die die Spielerfahrung stören würden.

**Grenzen** werden strikt eingehalten: Falls die Schwierigkeit bereits an der Unter- oder Obergrenze liegt und eine Änderung vorgesehen wäre, wird die Aktion als `keep` umgewertet und der Grund entsprechend vermerkt.

Der Agent ist **regelbasiert** und lernt nicht. Er verwendet weder Reinforcement Learning noch neuronale Netze. Er setzt lediglich explizit definierte Schwellenwerte um.

---

## 10. Reaktionstest-Modus

Der Reaktionstest-Modus ist ein optionales, interaktives Demo-Feature. Er ersetzt den vordefinierten Spielerprofilaufruf durch eine personalisierte Messung der Reaktionszeit des Nutzers.

### 10.1 Ablauf

1. Der Nutzer startet `main.py` mit dem Flag `--reaction-test`.
2. Ein einleitender Text erklärt den Test und weist darauf hin, dass das Ergebnis eine reaktionsbasierte Profileinschätzung ist.
3. Für jeden Versuch drückt der Nutzer Enter zum Starten.
4. Das Programm wartet eine zufällige Dauer zwischen 1 und 3 Sekunden.
5. Die Ausgabe `JETZT!` erscheint im Terminal.
6. Der Nutzer drückt erneut Enter so schnell wie möglich.
7. Die Reaktionszeit wird mit `time.perf_counter()` gemessen.
8. Valide Messungen werden gesammelt; invalide werden abgelehnt und wiederholt.
9. Nach Abschluss aller gültigen Messungen wird der Median berechnet.
10. Aus dem Median werden Reaktionswert und Kategorie abgeleitet.
11. Ein personalisiertes Spielerprofil wird erstellt.
12. Die adaptive Demo startet automatisch mit diesem Profil.

### 10.2 Gültige Messungen

- Es werden **mindestens 3 gültige Messungen** benötigt; der Standardwert beträgt **5**.
- Messungen unter **80 ms** werden als implausibel frühe oder gepufferte Tastendrücke abgelehnt.
- Beim Ablehnen wird die Meldung `Zu früh gedrückt. Der Versuch wird wiederholt.` ausgegeben.
- Der Versuch wird sofort wiederholt; abgelehnte Werte werden nicht in das Ergebnis aufgenommen.
- Die Gesamtanzahl gültiger Messungen entspricht immer genau dem angeforderten Wert `attempts`.

### 10.3 Median

Zur Auswertung wird der **Median** der Messungen verwendet, nicht der arithmetische Mittelwert. Der Median ist robuster gegenüber Ausreißern: Eine unbeabsichtigt langsame Messung (z. B. durch Ablenkung) beeinflusst das Gesamtergebnis weniger stark als beim Durchschnitt. Dies verbessert die praktische Verlässlichkeit des Tests, macht ihn jedoch nicht wissenschaftlich präzise.

### 10.4 Reaktionswert

Der Reaktionswert wird nach folgender Formel berechnet:

```
score = (500 - reaction_time_ms) / (500 - 150)
```

Anschließend wird der Wert auf den Bereich `[0.0, 1.0]` begrenzt (*Clamping*):

- **≤ 150 ms** → 1.0
- **≥ 500 ms** → 0.0
- **Dazwischen** → linear interpoliert

Beispiele:

| Reaktionszeit | Reaktionswert |
|---:|---:|
| 150 ms | 1,00 |
| 325 ms | ≈ 0,50 |
| 500 ms | 0,00 |
| 80 ms | 1,00 (Clamping) |
| 600 ms | 0,00 (Clamping) |

### 10.5 Kategorien

Aus dem Median der Reaktionszeiten wird eine Kategorie abgeleitet:

| Median-Reaktionszeit | Kategorie |
|---|---|
| unter 220 ms | `expert` |
| 220 ms bis unter 350 ms | `average` |
| 350 ms und darüber | `beginner` |

> **Wichtiger Hinweis:** Diese Schwellenwerte sind projektspezifisch und ausschließlich für die Demo-Klassifikation definiert. Sie stellen keine wissenschaftliche Bewertung der allgemeinen Spielfähigkeit dar. Reaktionszeit allein repräsentiert keine Spielerfahrung, kein Spielverständnis, keine strategische Kompetenz, keine Entscheidungsqualität und keine Treffergenauigkeit. Die Kategorien dienen nur der interaktiven Einordnung im Rahmen dieses Projekts.

### 10.6 Persönliches Profil

Das erzeugte Spielerprofil hat folgende Werte:

| Eigenschaft | Wert |
|---|---:|
| Name | Reaktionstest-Spieler |
| skill level | 0.60 |
| accuracy | 0.60 |
| reaction speed | aus Reaktionstest |
| survival factor | 0.65 |

Nur `reaction_speed` wird aus der Nutzermessung abgeleitet. Alle anderen Werte entsprechen dem Niveau des durchschnittlichen Standardprofils und bleiben fest. Diese Entscheidung ist bewusst: Es wäre eine Fehlinterpretation, aus der Reaktionszeit allein auf den gesamten Spielerskill zu schließen. Das Profil liefert eine reaktionsbasierte Profileinschätzung innerhalb des Demosystems – nicht mehr und nicht weniger.

---

## 11. CLI-Nutzung

### 11.1 Normaler Modus

**Standardausführung:**

```bash
python main.py
```

**Beispiele:**

```bash
python main.py --player beginner --rounds 10 --difficulty 7 --seed 42
python main.py --player expert --rounds 10 --difficulty 3 --seed 42
```

### 11.2 Reaktionstest-Modus

**Einfacher Start:**

```bash
python main.py --reaction-test
```

**Erweiterte Beispiele:**

```bash
python main.py --reaction-test --reaction-attempts 5 --rounds 10 --difficulty 5 --seed 42
python main.py --reaction-test --reaction-attempts 7 --rounds 20 --difficulty 6 --seed 123
```

### 11.3 CLI-Parameter

| Parameter | Bedeutung | Standard |
|---|---|---:|
| `--player` | Standard-Spielerprofil | `average` |
| `--rounds` | Anzahl der Simulationsrunden | 15 |
| `--difficulty` | Startschwierigkeit | 5 |
| `--seed` | Basis-Seed | 42 |
| `--reaction-test` | Aktiviert den Reaktionstest | deaktiviert |
| `--reaction-attempts` | Anzahl gültiger Reaktionsmessungen | 5 |

**Verhalten im Reaktionstest-Modus:**

- `--player` wird ignoriert; ein kurzer Hinweis wird ausgegeben.
- `--rounds`, `--difficulty` und `--seed` wirken wie gewohnt auf die nachfolgende adaptive Demo.
- Der `--seed` steuert zusätzlich die zufällige Wartesequenz vor jedem `JETZT!`-Signal.
- Die tatsächlichen menschlichen Reaktionszeitmessungen bleiben stets nicht reproduzierbar.

Ungültige Parameterwerte werden von `argparse` mit verständlichen Fehlermeldungen abgewiesen. Für `--reaction-attempts` wird zusätzlich geprüft, dass der Wert mindestens 3 beträgt.

---

## 12. Experimentdesign

### 12.1 Statisches System

Im statischen System wird die Schwierigkeit vor Beginn des Experiments festgelegt und bleibt für alle Runden konstant. Der Agent trifft keine Entscheidungen; `difficulty_changes` ist immer 0. Dieses System dient als Kontrollbedingung.

### 12.2 Adaptives System

Im adaptiven System entscheidet der Agent nach jeder Runde, ob die Schwierigkeit erhöht, reduziert oder beibehalten wird. Die Entscheidungshistorie und die Anzahl der Schwierigkeitsänderungen werden vollständig erfasst.

### 12.3 Vergleichsbedingungen

Beide Systeme werden unter identischen Bedingungen ausgeführt:

- drei Standardspielerprofile (Anfänger, durchschnittlicher Spieler, erfahrener Spieler)
- mehrere feste Seeds zur Verringerung der Abhängigkeit von einzelnen Zufallsverläufen
- gleiche Startschwierigkeit
- gleiche Rundenzahl

Die Ergebnisse werden als CSV gespeichert und mittels Visualisierungen verglichen.

### 12.4 Messgrößen

Für jedes Experiment werden folgende Größen erfasst:

- Gesamtsiege und -niederlagen
- Gesamtgewinnrate
- Abweichung vom 60-%-Zielwert
- Finale Schwierigkeit
- Anzahl der Schwierigkeitsänderungen
- Durchschnittliche verbleibende Trefferpunkte
- Durchschnittlicher erlittener Schaden
- Durchschnittliche Trefferquote
- Durchschnittliche Rundendauer
- Rundenweise Ergebnisse und Agentenentscheidungen

Der optionale Reaktionstest-Pfad ist kein Teil des Standard-Vergleichsexperiments. Er dient als personalisierter Demo-Einstiegspunkt und beeinflusst die wissenschaftliche Auswertung nicht.

---

## 13. Ergebnisse

Die Experimente zeigen innerhalb des vereinfachten Simulationsmodells folgende Tendenzen:

- Das adaptive System hilft besonders **Anfängern**, wenn die Startschwierigkeit zu hoch gewählt wurde: Der Agent reduziert die Schwierigkeit, sobald aufeinanderfolgende Niederlagen auftreten.
- **Erfahrene Spieler** profitieren, wenn die Startschwierigkeit zu niedrig liegt: Der Agent erhöht sie schrittweise, bis die Gewinnrate näher an den Zielwert rückt.
- Für **durchschnittliche Spieler** kann eine gut gewählte statische Startschwierigkeit (z. B. 5) bereits ausreichend nah am Zielwert liegen, sodass der Vorteil des adaptiven Systems geringer ausfällt.
- Das adaptive System ist **nicht in jedem Einzelfall besser** als das statische. Der Nutzen hängt stark von Spielerprofil, Startschwierigkeit und Seed ab.
- Insgesamt liefern die Ergebnisse eine differenzierte Antwort auf die Forschungsfrage: Das adaptive System kann für unterschiedliche Spielertypen eine ausgewogenere Erfahrung erzeugen, garantiert diese aber nicht unter allen Bedingungen.

Konkrete numerische Vergleichswerte (z. B. Abweichungen in Prozentpunkten) sind in der exportierten CSV-Datei (`results/data/comparison_results.csv`) und den erzeugten Diagrammen einsehbar.

---

## 14. Visualisierungen

### 14.1 `win_rate_comparison.png`

Vergleicht die mittleren Gewinnraten beider Systeme (statisch und adaptiv) für alle drei Spielerprofile als gruppiertes Balkendiagramm. Eine horizontale Linie markiert den Zielwert von 60 %. Das Diagramm ermöglicht eine direkte Sichtbarkeit, welches System näher am Ziel liegt.

### 14.2 `target_deviation.png`

Zeigt den absoluten Abstand der mittleren Gewinnrate vom Zielwert für jedes Profil und System. Kleinere Werte bedeuten eine ausgewogenere Erfahrung gemäß der Projektmetrik. Dieses Diagramm ist besonders für den direkten Systemvergleich geeignet.

### 14.3 `difficulty_progression.png`

Zeigt den Verlauf der Schwierigkeitsstufe über alle Runden für einen ausgewählten adaptiven Experimentlauf. Anhand dieser Kurve lässt sich ablesen, wann der Agent die Schwierigkeit erhöht, reduziert oder beibehält. Das Diagramm repräsentiert einen spezifischen Lauf und nicht alle Kombinationen.

### 14.4 `moving_win_rate.png`

Stellt die gleitende Gewinnrate im Zeitverlauf dar. Dadurch wird sichtbar, wie sich die Spielerleistung im Laufe der Runden entwickelt und ob das System sich in Richtung des Zielbereichs einpendelt.

Alle Diagramme werden unter `results/figures/` gespeichert.

---

## 15. Tests und Qualitätssicherung

### 15.1 Ausführung

```bash
python -m pytest -v
# oder mit virtuellem Environment:
./.venv/bin/python -m pytest -v
```

**Aktueller Teststand: 113 Tests bestanden**

### 15.2 Abgedeckte Bereiche

**Spielerprofile:**
- Gültige Erstellung mit Grenzwerten
- Ablehnung ungültiger Werte und leerer Namen

**Rundensimulation:**
- Reproduzierbarkeit mit festem Seed
- Wertebereiche aller Ausgabefelder (Gesundheit, Schaden, Genauigkeit, Dauer)
- Validierungsfehler bei ungültigen Eingaben

**Schwierigkeitsmodell:**
- Korrekte Parameterumrechnung für alle Stufen 1–10
- Monotonie der Parameter (Enemy Count und Damage steigen, Health Pack Rate sinkt)
- Fehler bei ungültigen Stufen

**Adaptiver Agent:**
- Alle fünf Entscheidungsregeln
- Einhaltung der Schwierigkeitsgrenzen
- Maximale Änderung von einer Stufe
- Verhalten bei leerer Ergebnishistorie

**Experimente:**
- Korrekte Rundenzahlen
- Keine Schwierigkeitsänderungen im statischen System
- Reproduzierbarkeit mit gleichem Seed
- CSV-Erstellung und Tabellenköpfe
- Fehlerpfade (leere Spielerliste, ungültige Parameter)

**CLI-Hilfsfunktionen:**
- Spielerauswahl und Gewinnratenberechnung

**Reaktionstest:**
- Reaktionswert-Berechnung mit Clamping und Fehlerpfaden
- Schwellenwert-Klassifikation (alle Kategoriegrenzen)
- Median-Berechnung und Validierung der Messungen
- Erstellung des persönlichen Profils
- Interaktiver Testablauf mit gemocktem `input`, `time.sleep` und `time.perf_counter`
- Ablehnung von Messungen unter 80 ms
- Wiederholungsverhalten und korrekte Endanzahl
- Verarbeitung eines festen Seeds für die Wartesequenz

Tests verwenden `monkeypatch` (Pytest-Fixture), um Nutzereingaben, Wartezeiten und Zeitmessungen zu ersetzen. Es findet keine echte Wartezeit und kein echtes Tastatureingabe-Lesen statt.

---

## 16. Reproduzierbarkeit

### 16.1 Simulation

Alle Simulationen mit einem festen Seed sind vollständig reproduzierbar. Für jede Runde wird ein deterministischer Rundenseed verwendet (`seed + Rundennummer - 1`). Identische Eingaben (Spielerprofil, Startschwierigkeit, Seed, Rundenzahl) erzeugen identische Ausgaben. CSV-Dateien können bei gleichen Parametern byte-identisch neu erzeugt werden. Die Pytest-Suite prüft die Reproduzierbarkeit zentraler Simulationsergebnisse explizit.

### 16.2 Reaktionstest

Die **zufällige Wartesequenz** vor jedem `JETZT!`-Signal ist mit einem festen `--seed` reproduzierbar, da `random.Random(seed)` verwendet wird.

Die **tatsächlichen Reaktionszeitenmessungen** des Nutzers sind nicht reproduzierbar. Sie hängen von menschlicher Reaktion, Display-Latenz, Tastatur-Latenz, Fingerposition, Aufmerksamkeit und dem Verhalten des Terminals ab.

Sobald ein Profil aus einer Messung erstellt wurde, ist die anschließende **adaptive Simulation** für dasselbe Profil und denselben Simulationsseed reproduzierbar.

---

## 17. Grenzen des Systems

Das vorliegende System vereinfacht die Realität an mehreren wichtigen Stellen:

- Die **Spielsimulation** ist probabilistisch und stark vereinfacht. Sie enthält keine echte Game Engine, keine reale Spielmechanik und keine komplexe Gegner-KI.
- Die **Standardprofile** sind synthetisch. Im Reaktionstest-Modus wird lediglich `reaction_speed` aus einer realen Nutzermessung abgeleitet; alle anderen Profilwerte bleiben vordefiniert.
- Es werden **keine realen Telemetriedaten** eingesetzt. Spielerverhalten und -präferenzen werden nicht modelliert.
- Der **adaptive Agent** ist regelbasiert und lernt nicht. Er verbessert sich nicht durch Erfahrung und passt seine Regeln nicht an.
- Die **Gewinnrate** ist nur ein grober Näherungswert für Spielspaß und Spielerfahrung.
- Die **Terminal-Reaktionsmessung** ist unpräzise: Display-Latenz, Tastatur-Latenz, Enter-Puffer, Fingerposition und Aufmerksamkeit des Nutzers beeinflussen die Messung. Die 80-ms-Ablehnungsschwelle ist eine heuristische Maßnahme, keine wissenschaftlich validierte Grenze.
- Die **Reaktionskategorien** (`expert`, `average`, `beginner`) sind projektspezifische Demo-Labels ohne wissenschaftliche Grundlage.
- **Reaktionszeit allein** repräsentiert keine vollständige Spielfähigkeit. Spielkenntnisse, Entscheidungsqualität, strategisches Denken und Erfahrung werden nicht erfasst.

---

## 18. Fazit

Innerhalb des vereinfachten Simulationsmodells kann der adaptive Agent eine ausgewogenere Spielerfahrung erzeugen als ein statisches System – insbesondere wenn das Spielerprofil stark von einem mittleren Niveau abweicht oder die gewählte Startschwierigkeit nicht zu den Fähigkeiten des Spielers passt.

Für Spieler mit mittlerem Niveau kann eine gut gewählte statische Schwierigkeit bereits ausreichend nah am Zielwert liegen, sodass der Vorteil des adaptiven Systems geringer ausfällt. Adaptivität ist demnach vor allem dann wertvoll, wenn Spieler unterschiedliche Fähigkeitsniveaus mitbringen oder die Ausgangskalibrierung unsicher ist.

Die Ergebnisse sind innerhalb des Modells vielversprechend, belegen jedoch nicht die Wirksamkeit des Ansatzes in echten kommerziellen Spielen. Für eine belastbarere Aussage wären reale Spielerdaten, eine echte Spielumgebung und statistische Auswertungen mit Konfidenzintervallen erforderlich.

Der **Reaktionstest-Modus** verbessert die Interaktivität und Personalisierbarkeit der Demo erheblich. Er ist jedoch kein Teil des wissenschaftlichen Kernexperiments und sollte entsprechend eingeordnet werden: als reaktionsbasierte Profileinschätzung im Rahmen eines Demonstrationssystems.

---

## 19. Ausblick

Mögliche Erweiterungen des Projekts in absteigender Priorität:

- **Integration in ein echtes Spiel** – Einbindung in eine tatsächliche Spielumgebung mit realen Spielerinteraktionen
- **Reale Telemetriedaten** – Nutzung echter Spielerstatistiken anstelle synthetischer Profile
- **Weitere Spielerprofile** – Erweiterung um mehr als drei Profile für differenziertere Vergleiche
- **Mehr Schwierigkeitsparameter** – z. B. Gegnerbewegungsgeschwindigkeit, Rüstungswerte oder Rundenzeit
- **Personalisierte Zielgewinnraten** – unterschiedliche Zielwerte je nach Spielerpräferenz
- **Längere Experimentreihen** – mehr Runden und Seeds für statistisch belastbarere Ergebnisse
- **Konfidenzintervalle und statistische Analyse** – formale Auswertung der Unterschiede zwischen den Systemen
- **Lernender Agent** – Einsatz von Reinforcement Learning für kontextbewusstere und selbstverbessernde Entscheidungen
- **Browser-basierter visueller Reaktionstest** – visuelle Reize statt Terminal-Prompts, ohne Enter-Puffer-Problematik
- **Direkte Tastatur- oder Mausereignisse** – Messung ohne Enter-Buffering für präzisere Latenzwerte
- **Geräte-Kalibrierung** – Anpassung der Schwellenwerte für unterschiedliche Display- und Tastaturlatenzen
- **Messung von Genauigkeit oder Entscheidungszeit** – Erweiterung des reaktionsbasierten Profils um weitere Messwerte
- **Vollständigeres personalisiertes Profil** – Kombination mehrerer Messwerte für eine umfassendere Profileinschätzung
- **Grafische Benutzeroberfläche** – interaktive Steuerung der Demo-Parameter ohne CLI
