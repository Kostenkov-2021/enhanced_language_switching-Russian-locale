# Forbedret språkdeteksjon

* Forfatter: Emil-18
* NVDA -kompatibilitet: 2024.2 og utover
* Last ned: [stabil versjon] (https://github.com/emil-18/enhanced_language_switching/releases/download/v1.0/enhancedlanguagedetection-1.0.nvda-addon).

Dette tillegget  automatisk oppdager språket i teksten NVDA er i ferd med å si, og bruker NVDAs innebygde automatiske språk bytte hvis det er slått på, for å si teksten på det språket.

Dette tillegget er sterkt inspirert av [Language Ident Add-On] (https://github.com/slohmaier/languageident).
Det tillegget sluttet å fungere, og fra issues på GitHub, ser det ikke  ut som utvikleren kommer til å fikse det.

## Innstillinger

* Språktolkning:
    Dette er en kombinasjonsboks som lar deg velge når tillegget tolker språket i teksten. Valgene er:
    * Tolk alltid:
        Tillegget vil alltid tolke tekstens språk og fjerne alle tidligere instruksjoner for å endre språket. For eksempel, hvis du er på en webside, og språket på websiden er definert som engelsk, men ifølge tillegget er teksten norsk, vil den bytte til en norsk stemme. Hvis du ikke har valgt norsk som et av språkene som skal tolkes, (se nedenfor), vil ikke stemmen endre seg i det hele tatt.
    * Bare tolke hvis teksten ikke instruerer NVDA om å endre språk:
        Tillegget vil bare tolke språket hvis det ikke er instruksjoner om å endre språket i teksten. I eksemplet over vil den bytte til en engelsk stemme.
    * Aldri tolke (NVDAs standardoppførsel):
        Selvforklarende.
* Språk for å tolke:
    Dette er en liste over språkene å tolke. Hvis tillegget tolker en tekst som et språk som ikke er valgt i denne listen, gjøres ingen automatisk språk bytte basert på tolkningen. Ingen språk er valgt som standard.

## Endre log.
### v1.0

første utgivelse