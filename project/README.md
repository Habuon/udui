## **MiniMax - Reversi**
###### **Daniel Trizna**
##
### Zadanie
Zadaním tejto úlohy bolo zostrojiť MiniMax agenta, ktorý bude schopný hrať hru reversi.

### Implementácia
Tento agent je reprezentovaný pomocou triedy MyPlayer, ktorá sa nachádza v súbore minimax.py. 

Táto trieda obsahuje niekoľko funkcií a 3 parametre, _self.depth_ určuje maximálnu hĺbku do akej sa 
bude minimax vzkonávať pred tým ako sa zavolá heuristika. _Self.game_ a _self.my_player_ sa viažu na aktuálnu hru a na
hráča, za ktorého tento agent hrá.

Algoritmus minimax obsahuje aj Alpha-Beta orezávanie, kde sa na začiatku posiela -nekonečno ako alpha a nekonečno ako beta
a následne sa tieto premenné upravujú za účelom vylúčenia zbytočných prehľadávaní. 

Funkcia _self.heuristic_ dostáva ako argument stav hry hráča pre ktorého má daný stav vyhodnotiť a koeficient, ktorý určuje
koľkonásobne väčšiu hodnotu majú dobré políčka. Za dobré políčko sa považuje také, pre ktoré platí, že je na kraji. Nakoniec
táto funkcia vráti sumu políčok ktoré daný hráč má obsadené ale nie sú dobré a políčok ktoré sú dobré prenásobené koeficientom.
v prípade, že je hráč rovnaký ako ten náš tak vráti výsledok ako kladné číslo inak ako záporné.

Funkcie _self.min_ a _self.max_ sú generickými funkciami vykonávajúcimi algoritmus minimax tak ako sme sa ho učili v rámci predmetu.

### Výsledky

Tento agent vo svojej hre proti náhodnému agentovi dosahoval vysokú úspešnosť. Zo 100 hier moj agent vyhral 97 krát, 2 krát 
prehral a raz remízoval, čím dosiahol celkové skóre 0,95. Príčinou prehier môže byť fakt, že mnou zvolená heuristika rovnako ako
väčšina heuristík nie je dokonalá a teda môžu nastať situácie kedy sa môj agent nerozhodne úplne korektne.