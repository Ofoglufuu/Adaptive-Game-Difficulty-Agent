# Adaptive Game Difficulty Agent

## Dynamische Schwierigkeitsanpassung durch Spielersimulation

### Projektidee

Das Ziel dieses Projekts ist die Entwicklung eines adaptiven Agenten, der den Schwierigkeitsgrad eines Spiels automatisch an die aktuelle Leistung des Spielers anpasst. Im Gegensatz zu einem statischen Schwierigkeitssystem bleibt der Schwierigkeitsgrad nicht während des gesamten Spiels konstant. Der Agent analysiert regelmäßig die Spielergebnisse und verändert anschließend ausgewählte Spielparameter.

Das System soll verhindern, dass ein Spiel für unerfahrene Spieler dauerhaft zu schwierig oder für erfahrene Spieler zu einfach wird. Dadurch soll eine möglichst ausgeglichene und motivierende Spielerfahrung entstehen.

### Forschungsfrage

Kann ein adaptiver Schwierigkeitsagent eine ausgewogenere Spielerfahrung erzeugen als ein statisches Schwierigkeitssystem?

### Funktionsweise des Systems

Das Projekt verwendet eine vereinfachte Spielersimulation. In mehreren Spielrunden tritt ein simulierter Spieler gegen Gegner an. Nach jeder Runde werden Leistungsdaten des Spielers erfasst.

Zu den analysierten Leistungsdaten gehören beispielsweise:

* Sieg oder Niederlage
* verbleibende Lebenspunkte
* erlittener Schaden
* Dauer der Spielrunde
* Trefferquote
* Anzahl aufeinanderfolgender Siege oder Niederlagen

Der Agent wertet die Ergebnisse der letzten Spielrunden aus und entscheidet anschließend, ob der Schwierigkeitsgrad erhöht, reduziert oder beibehalten werden soll.

### Anpassbare Spielparameter

Der Schwierigkeitsgrad wird durch mehrere Parameter beschrieben. Der Agent kann insbesondere folgende Werte verändern:

* Anzahl der Gegner
* Schaden der Gegner
* Geschwindigkeit oder Reaktionsfähigkeit der Gegner
* verfügbare Lebenspunkte oder Heilungsobjekte
* Wahrscheinlichkeit für das Auftreten von Gesundheitsboni

Wenn der Spieler mehrfach verliert, kann der Agent beispielsweise den Gegnerschaden reduzieren oder zusätzliche Heilungsobjekte bereitstellen. Gewinnt der Spieler mehrere Runden sehr deutlich, können die Gegneranzahl oder der Gegnerschaden erhöht werden.

### Modellierung der Spielerleistung

Der simulierte Spieler besitzt ein festgelegtes Fähigkeitsniveau. Dieses beeinflusst unter anderem seine Trefferwahrscheinlichkeit, Reaktionsfähigkeit und Überlebenschance.

Die Erfolgswahrscheinlichkeit des Spielers hängt sowohl von seinem Fähigkeitsniveau als auch vom aktuellen Schwierigkeitsgrad ab. Dadurch können unterschiedliche Spielertypen simuliert werden:

* Anfänger
* durchschnittlicher Spieler
* erfahrener Spieler

Zusätzlich können zufällige Schwankungen berücksichtigt werden, damit nicht jede Runde mit identischen Parametern gleich endet.

### Vergleich der Systeme

Für die Evaluation werden zwei Systeme miteinander verglichen:

1. **Statisches Schwierigkeitssystem**
   Die Spielparameter bleiben während aller Runden unverändert.

2. **Adaptives Schwierigkeitssystem**
   Der Agent verändert die Spielparameter auf Grundlage der aktuellen Spielerleistung.

Beide Systeme werden mit denselben Spielertypen und über eine größere Anzahl von Spielrunden getestet.

### Bewertungsgrößen

Zur Bewertung werden unter anderem folgende Kennzahlen verwendet:

* durchschnittliche Gewinnrate
* durchschnittliche Anzahl der Niederlagen
* Abweichung von einer gewünschten Zielgewinnrate
* durchschnittliche Rundendauer
* Entwicklung des Schwierigkeitsgrades
* Häufigkeit der Schwierigkeitsanpassungen
* Stabilität des Systems

Eine mögliche Zielgewinnrate liegt beispielsweise bei 60 Prozent. Der Agent soll den Schwierigkeitsgrad so einstellen, dass die tatsächliche Gewinnrate langfristig möglichst nahe an diesem Zielwert liegt.

### Agentenlogik

Die erste Version des Agenten soll regelbasiert arbeiten. Beispielsweise kann der Schwierigkeitsgrad reduziert werden, wenn der Spieler mehrere Runden hintereinander verliert. Bei einer sehr hohen Gewinnrate wird der Schwierigkeitsgrad erhöht.

Optional kann zusätzlich ein Sprachmodell eingesetzt werden. Das Sprachmodell übernimmt jedoch nicht die sicherheitskritische Berechnung, sondern erklärt die Entscheidung des Agenten in natürlicher Sprache.

Beispiel:

> Der Schwierigkeitsgrad wurde reduziert, weil der Spieler drei Runden hintereinander verloren und dabei durchschnittlich mehr als 80 Prozent seiner Lebenspunkte verloren hat.

### Live-Demonstration

In der Live-Demo wird eine Folge simulierter Spielrunden ausgeführt. Im Terminal werden für jede Runde der aktuelle Schwierigkeitsgrad, das Spielergebnis und die Entscheidung des Agenten angezeigt.

Beispiel:

```text
Runde 1 | Schwierigkeit 5 | Niederlage
Runde 2 | Schwierigkeit 5 | Niederlage
Agent: Schwierigkeit wird auf 4 reduziert.

Runde 3 | Schwierigkeit 4 | Sieg
Runde 4 | Schwierigkeit 4 | Sieg
Agent: Schwierigkeit bleibt unverändert.
```

Zusätzlich sollen Diagramme die Entwicklung des Schwierigkeitsgrades, die Gewinnrate und den Vergleich zwischen dem statischen und adaptiven System darstellen.

### Erwartetes Ergebnis

Es wird erwartet, dass das adaptive System die Spielerleistung langfristig näher an der gewünschten Zielgewinnrate hält. Das statische System kann dagegen für bestimmte Spielertypen dauerhaft zu leicht oder zu schwer sein.

Das Projekt zeigt, wie Agenten, Simulationen und dynamische Parameteranpassungen kombiniert werden können, um ein Spielsystem automatisch an unterschiedliche Spieler anzupassen.
