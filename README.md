# AniXtract: tool di estrazione, classificazione e annotazione delle camera-feature

## Pacchetti Python richiesti
 - PySimpleGUI
 - pillow
 - opencv-python
 - pandas
 - keras
 - tensorflow

## Istruzioni
 - Per far partire il programma eseguire 'python main.py'
 - Nell'area in alto a sinistra, selezionare il filmato da analizzare, le camera-features da estrarre automaticamente con i modelli e la frequenza
di estrazione, da 1 a 7 secondi d'intervallo tra due frame, poi cliccare su ''Load video and settings''. Se necessario, caricare anche il file csv.
 - Una volta caricato il video, nell'area in basso a sinistra si può vedere la posizione dell'estrattore nel filmato (numero frame e minutaggio).
 - In alto a destra ci sono i controlli per il video. Cliccare su ''Play'' per avviare l'estrazioen automatica. Cliccare su ''Pause'' per mettere in pausa.
 Cliccare su ''<'' o ''>'' per scorrere il filmato all'indietro o in avanti di un frame alla volta, oppure ''<<'' o ''>>'' per saltare di un numero
 di frame pari alla frequenza di estrazione.
 - Cliccare su ''Call model prediction'' per forzare una valutazione del modello sul frame.
 - Sui bordi della schermata si trovano i bottoni per l'annotazione. Al frame scelto cliccare sul bottone corrispondente all'annotazione scelta. Ricliccare
 il bottone per annullare la scelta fatta.
 - Cliccare su ''Save annotation to CSV'' per salvare l'annotazione fino a quell'istante in un file csv.

## Download modelli
I modelli si trovano al link: https://drive.google.com/drive/folders/13LYHyYeakSYc0NaxqSCbMR5qOSOVWnxB?usp=sharing

Scaricare i modelli e metterli nella sottocartella 'predictor_net/models'
