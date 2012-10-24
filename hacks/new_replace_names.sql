-- <new>
UPDATE listarchives SET name = 'Joost van Baal'         WHERE name like 'Joost van Baal%' OR name = 'joostvb' ;
UPDATE listarchives SET name = 'Michael Hanke'          WHERE name = 'mhanke-guest' OR name = 'mih' ;
UPDATE listarchives SET name = 'Mechtilde Stehmann'     WHERE name = 'Mechtilde' AND project = 'lex' ;
UPDATE listarchives SET name = 'Gonéri Le Bouder'       WHERE name like 'Gon%ri Le Bouder' ;

--  updated at 5.1.2012
UPDATE listarchives SET name = 'Johannes Ring'          WHERE name like 'johannr-guest' ;
UPDATE listarchives SET name = 'Christophe Trophime'    WHERE name LIKE 'trophime%' OR name LIKE 'christophe.trophime' ;
UPDATE listarchives SET name = 'Frédéric-Emmanuel PICCA' WHERE name ILIKE 'Picca Fr%d%ric%' OR name ILIKE 'Fr%d%ric% PICCA' OR name like 'picca';
UPDATE listarchives SET name = 'Pierre Saramito'        WHERE name ILIKE 'saramito-guest' ;
UPDATE listarchives SET name = 'Gudjon I. Gudjonsson'   WHERE name ILIKE 'gudjon-guest' ;
UPDATE listarchives SET name = 'Ko van der Sloot'       WHERE name ILIKE 'sloot-guest' ;
UPDATE listarchives SET name = 'Sargis Dallakyan'       WHERE name ILIKE 'sargis' OR name ILIKE 'sargis-guest' ;
UPDATE listarchives SET name = 'Nicholas Breen'         WHERE name ILIKE 'nbreen%';
UPDATE listarchives SET name = 'Karol M. Langner'       WHERE name ILIKE 'kml-guest' OR name ILIKE 'Karol Langner';
UPDATE listarchives SET name = 'Ben Armstrong'          WHERE name ILIKE 'synrg';
UPDATE listarchives SET name = 'Bart Cornelis'          WHERE name ILIKE 'cobaco%' ;
UPDATE listarchives SET name = 'Jordà Polo'             WHERE name ILIKE 'Jord% Polo' ;
UPDATE listarchives SET name = 'Bruno "Fuddl" Kleinert' WHERE name ILIKE  'Bruno%Fuddl%' ;
UPDATE listarchives SET name = 'IOhannes M. Zmölnig'    WHERE name ILIKE '%zmoelnig%' ;
UPDATE listarchives SET name = 'Benjamin Drung'         WHERE name ILIKE '%bdrung%' ;
UPDATE listarchives SET name = 'Felipe Sateler'         WHERE name ILIKE 'fsateler%' ;
UPDATE listarchives SET name = 'Maia Kozheva'           WHERE name ILIKE 'lucidfox%' OR name ILIKE 'Sikon' ;
UPDATE listarchives SET name = 'Matteo F. Vescovi'      WHERE name ILIKE 'mfv%' OR name ILIKE 'Matteo%Vescovi';
UPDATE listarchives SET name = 'Alessandro Ghedini'     WHERE name ILIKE 'ghedo%' ;
UPDATE listarchives SET name = 'Alexandre Quessy'       WHERE name ILIKE 'alexandrequessy%' ;
UPDATE listarchives SET name = 'Ryan Kavanagh'          WHERE name ILIKE 'ryanakca%' ;
UPDATE listarchives SET name = 'Roman Haefeli'          WHERE name ILIKE 'rdz%' ;
UPDATE listarchives SET name = 'Free Ekanayaka'         WHERE name ILIKE 'freee%' ;
UPDATE listarchives SET name = 'Matthias Klumpp'        WHERE name ILIKE 'ximion%' ;
UPDATE listarchives SET name = 'Rosea Grammostola'      WHERE name ILIKE 'rosea-%' OR name ILIKE 'rosea%grammosto%a' OR name ILIKE 'Grammostola Rosea' OR name ILIKE 'rosea';
UPDATE listarchives SET name = 'Andriy Beregovenko'     WHERE name ILIKE 'jet-guest' ;
UPDATE listarchives SET name = 'Philippe Coval'         WHERE name ILIKE 'rzr-guest' OR name ILIKE 'Philippe COVAL' ;
UPDATE listarchives SET name = 'Miguel Colon'           WHERE name ILIKE 'micove-%' ;
UPDATE listarchives SET name = 'Sebastian Dröge'        WHERE name ILIKE 'slomo' ;
UPDATE listarchives SET name = 'Harry Rickards'         WHERE name ILIKE 'hrickards%' OR name ILIKE 'Harry RIckards' ;
UPDATE listarchives SET name = 'Jordi Gutiérrez Hermoso' WHERE name ILIKE '%Jord%G%t%rrez%Hermoso%' ;
UPDATE listarchives SET name = 'Felipe Augusto van de Wiel' WHERE name ILIKE 'Felipe Augusto van de Wiel%' ;

-- </new>
