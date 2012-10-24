-- It turned out that several people are posting under different names
-- This is fixed for active posters to keep the stats clean

UPDATE listarchive SET author = 'Ralf Gesellensetter'    WHERE project = 'edu' AND author LIKE 'Ralf%setter';
UPDATE listarchive SET author = 'Vagrant Cascadian'      WHERE author LIKE '%vagrant%';
UPDATE listarchive SET author = 'Francesco P. Lovergine' WHERE author LIKE 'Francesco%Lovergine' OR author = 'frankie';
UPDATE listarchive SET author = 'Christian Perrier'      WHERE author = 'bubulle' OR author = 'Christian PERRIER';
UPDATE listarchive SET author = 'Steve Langasek'         WHERE author = 'vorlon';
UPDATE listarchive SET author = 'Adrian von Bidder'      WHERE author like 'Adrian % von Bidder';
UPDATE listarchive SET author = 'Thomas Bushnell BSG'    WHERE author like 'Thomas Bushnell%BSG';
UPDATE listarchive SET author = 'Martin-Éric Racine'     WHERE author like 'Martin-%ric% Racine';
UPDATE listarchive SET author = 'Eddy Petrisor'          WHERE author like 'Eddy Petri%or';
UPDATE listarchive SET author = 'Linas Zvirblis'         WHERE author like 'Linas %virblis';
UPDATE listarchive SET author = 'Nicolas Évrard'         WHERE author like 'Nicolas %vrard';
UPDATE listarchive SET author = 'Piotr Ozarowski'        WHERE author like 'Piotr O%arowski';
UPDATE listarchive SET author = 'Charles Plessy'         WHERE author like 'charles-debian-nospam' OR author = 'plessy';
UPDATE listarchive SET author = 'Jean Luc COULON'        WHERE author like 'Jean-Luc Coulon%';
UPDATE listarchive SET author = 'Jérôme Warnier'         WHERE author like 'Jerome Warnier';
UPDATE listarchive SET author = 'Sven LUTHER'            WHERE project = 'ocaml-maint' AND author = 'Sven';
UPDATE listarchive SET author = 'Sven LUTHER'            WHERE author = 'Sven Luther';
UPDATE listarchive SET author = 'Steffen Möller'         WHERE author = 'smoe-guest'  OR author = 'moeller' OR author = 'Steffen Moeller';
UPDATE listarchive SET author = 'Steven M. Robbins'      WHERE author = 'smr' or author like 'Steve%Robbins';
UPDATE listarchive SET author = 'Charles Plessy'         WHERE author = 'plessy' OR author = 'charles-guest' ;
UPDATE listarchive SET author = 'David Paleino'          WHERE author = 'hanska-guest';
UPDATE listarchive SET author = 'Nelson A. de Oliveira'  WHERE author = 'naoliv';
UPDATE listarchive SET author = 'Andreas Tille'          WHERE author = 'tille' OR author = 'tillea' OR author = 'TilleA';
UPDATE listarchive SET author = 'Thijs Kinkhorst'        WHERE author = 'thijs';
UPDATE listarchive SET author = 'Mathieu Malaterre'      WHERE author = 'malat-guest';
UPDATE listarchive SET author = 'Morten Kjeldgaard'      WHERE author = 'mok0-guest';
UPDATE listarchive SET author = 'Tobias Quathamer'       WHERE author = 'Tobias Toedter';
UPDATE listarchive SET author = 'J.H.M. Dassen'          WHERE author = 'J.H.M.Dassen';
UPDATE listarchive SET author = 'L. V. Gandhi'           WHERE author = 'L . V . Gandhi' OR author = 'L.V.Gandhi';
UPDATE listarchive SET author = 'Jelmer Vernooij'        WHERE author = 'ctrlsoft-guest' OR author = 'jelmer';
UPDATE listarchive SET author = 'Mathieu Parent'         WHERE author = 'mparent-guest' OR author = 'Mathieu PARENT' or author = 'sathieu';
UPDATE listarchive SET author = 'Noèl Köthe'             WHERE author = 'Noel Koethe' OR author = 'noel';
UPDATE listarchive SET author = 'Dominique Belhachemi'   WHERE author = 'domibel-guest';
UPDATE listarchive SET author = 'Philipp Benner'         WHERE author = 'pbenner-guest';
UPDATE listarchive SET author = 'Sylvestre Ledru'        WHERE author = 'sylvestre-guest' OR author = 'sylvestre' OR author = 'sylvestre.ledru' ;
UPDATE listarchive SET author = 'Christophe Prud_homme'  WHERE author = 'prudhomm' OR author = 'prudhomm-guest' ;
UPDATE listarchive SET author = 'Torsten Werner'         WHERE author = 'twerner';
UPDATE listarchive SET author = 'Jan Beyer'              WHERE author = 'beathovn-guest' OR author = 'jan@beathovn.de';
UPDATE listarchive SET author = 'Filippo Rusconi'        WHERE author = 'Filippo Rusconi (Debian Maintainer)' OR author = 'rusconi';
UPDATE listarchive SET author = 'Daniel Leidert'         WHERE author = 'Daniel Leidert (dale)' OR author = 'dleidert-guest';
UPDATE listarchive SET author = 'Michael Banck'          WHERE author = 'mbanck';
UPDATE listarchive SET author = 'Guido Günther'          WHERE author = 'Guido G&#252;nther' OR author = 'Guido Guenther';
UPDATE listarchive SET author = 'Ahmed El-Mahmoudy'      WHERE author like '%Ahmed El-Mahmoudy%' OR author = 'aelmahmoudy-guest';
UPDATE listarchive SET author = 'Branden Robinson'       WHERE author like 'Branden Robinson%' ;
UPDATE listarchive SET author = 'LI Daobing'             WHERE author = 'lidaobing-guest' ;
UPDATE listarchive SET author = 'Egon Willighagen'       WHERE author = 'egonw-guest' ;
UPDATE listarchive SET author = 'Jordan Mantha'          WHERE author = 'laserjock-guest' ;
UPDATE listarchive SET author = 'Eric Sharkey'           WHERE author = 'sharkey' ;
UPDATE listarchive SET author = 'Fabio Tranchitella'     WHERE author = 'kobold' ;
UPDATE listarchive SET author = 'Petter Reinholdtsen'    WHERE author = 'pere' ;
UPDATE listarchive SET author = 'Andreas Putzo'          WHERE author = 'nd-guest' ;
UPDATE listarchive SET author = 'Giovanni Mascellani'    WHERE author = 'gmascellani-guest' ;
UPDATE listarchive SET author = 'Paul Wise'              WHERE author = 'pabs' OR author = 'pabs-guest' ;
UPDATE listarchive SET author = 'Alan Boudreault'        WHERE author = 'aboudreault-guest' ;
UPDATE listarchive SET author = 'Reinhard Tartler'       WHERE author = 'siretart' ;
UPDATE listarchive SET author = 'Alessio Treglia'        WHERE author = 'quadrispro-guest' OR author = 'alessio';
UPDATE listarchive SET author = 'M. Christophe Mutricy'  WHERE author = 'xtophe-guest' ;
UPDATE listarchive SET author = 'Jonas Smedegaard'       WHERE author = 'js' ;
UPDATE listarchive SET author = 'Jaromír Mikeš'          WHERE author = 'mira-guest' ;
UPDATE listarchive SET author = 'Adrian Knoth'           WHERE author = 'adiknoth-guest' ;
UPDATE listarchive SET author = 'Andres Mejia'           WHERE author = 'ceros-guest' ;
UPDATE listarchive SET author = 'Fabian Greffrath'       WHERE author = 'fabian-guest' ;
UPDATE listarchive SET author = 'Loïc Minier'            WHERE author = 'lool-guest' OR author = 'lool' ;
UPDATE listarchive SET author = 'Benjamin Drung'         WHERE author = 'bdrung-guest' ;
UPDATE listarchive SET author = 'Yaroslav Halchenko'     WHERE author = 'yoh-guest' OR author = 'yoh' ;
UPDATE listarchive SET author = 'Samuel Thibault'        WHERE author = 'sthibaul-guest' OR author = 'sthibault';
UPDATE listarchive SET author = 'Andrew Lee'             WHERE author = 'ajqlee' ;
UPDATE listarchive SET author = 'David Bremner'          WHERE author = 'bremner-guest' ;
UPDATE listarchive SET author = 'Christian Kastner'      WHERE author = 'chrisk' ;
UPDATE listarchive SET author = 'Christopher Walker'     WHERE author = 'cjw1006-guest' ;
-- see below in <new></new>
UPDATE listarchive SET author = 'Alastair McKinstry'     WHERE author = 'mckinstry' ;
UPDATE listarchive SET author = 'Otavio Salvador'        WHERE author = 'otavio' ;
UPDATE listarchive SET author = 'Frederic Lehobey'       WHERE author = 'fdl-guest' or author = 'Frederic Daniel Luc Lehobey' ;
UPDATE listarchive SET author = 'Sylvain Le Gall'        WHERE author = 'Sylvain LE GALL' ;
UPDATE listarchive SET author = 'Hans-Christoph Steiner' WHERE author = 'eighthave-guest' ;
UPDATE listarchive SET author = 'Karol Langner'          WHERE author = 'klm-guest' ;
UPDATE listarchive SET author = 'Georges Khaznadar'      WHERE author = 'georgesk' ;

-- <new>
UPDATE listarchive SET author = 'Joost van Baal'         WHERE author like 'Joost van Baal%' OR author = 'joostvb' ;
UPDATE listarchive SET author = 'Michael Hanke'          WHERE author = 'mhanke-guest' OR author = 'mih' ;
UPDATE listarchive SET author = 'Mechtilde Stehmann'     WHERE author = 'Mechtilde' AND project = 'lex' ;
UPDATE listarchive SET author = 'Gonéri Le Bouder'       WHERE author like 'Gon%ri Le Bouder' ;

--  updated at 5.1.2012
UPDATE listarchive SET author = 'Johannes Ring'          WHERE author like 'johannr-guest' ;
UPDATE listarchive SET author = 'Christophe Trophime'    WHERE author LIKE 'trophime%' OR author LIKE 'christophe.trophime' ;
UPDATE listarchive SET author = 'Frédéric-Emmanuel PICCA' WHERE author ILIKE 'Picca Fr%d%ric%' OR author ILIKE 'Fr%d%ric% PICCA' OR author like 'picca';
UPDATE listarchive SET author = 'Pierre Saramito'        WHERE author ILIKE 'saramito-guest' ;
UPDATE listarchive SET author = 'Gudjon I. Gudjonsson'   WHERE author ILIKE 'gudjon-guest' ;
UPDATE listarchive SET author = 'Ko van der Sloot'       WHERE author ILIKE 'sloot-guest' ;
UPDATE listarchive SET author = 'Sargis Dallakyan'       WHERE author ILIKE 'sargis' OR author ILIKE 'sargis-guest' ;
UPDATE listarchive SET author = 'Nicholas Breen'         WHERE author ILIKE 'nbreen%';
UPDATE listarchive SET author = 'Karol M. Langner'       WHERE author ILIKE 'kml-guest' OR author ILIKE 'Karol Langner';
UPDATE listarchive SET author = 'Ben Armstrong'          WHERE author ILIKE 'synrg';
UPDATE listarchive SET author = 'Bart Cornelis'          WHERE author ILIKE 'cobaco%' ;
UPDATE listarchive SET author = 'Jordà Polo'             WHERE author ILIKE 'Jord% Polo' ;
UPDATE listarchive SET author = 'Bruno "Fuddl" Kleinert' WHERE author ILIKE  'Bruno%Fuddl%' ;
UPDATE listarchive SET author = 'IOhannes M. Zmölnig'    WHERE author ILIKE '%zmoelnig%' ;
UPDATE listarchive SET author = 'Benjamin Drung'         WHERE author ILIKE '%bdrung%' ;
UPDATE listarchive SET author = 'Felipe Sateler'         WHERE author ILIKE 'fsateler%' ;
UPDATE listarchive SET author = 'Maia Kozheva'           WHERE author ILIKE 'lucidfox%' OR author ILIKE 'Sikon' ;
UPDATE listarchive SET author = 'Matteo F. Vescovi'      WHERE author ILIKE 'mfv%' OR author ILIKE 'Matteo%Vescovi';
UPDATE listarchive SET author = 'Alessandro Ghedini'     WHERE author ILIKE 'ghedo%' ;
UPDATE listarchive SET author = 'Alexandre Quessy'       WHERE author ILIKE 'alexandrequessy%' ;
UPDATE listarchive SET author = 'Ryan Kavanagh'          WHERE author ILIKE 'ryanakca%' ;
UPDATE listarchive SET author = 'Roman Haefeli'          WHERE author ILIKE 'rdz%' ;
UPDATE listarchive SET author = 'Free Ekanayaka'         WHERE author ILIKE 'freee%' ;
UPDATE listarchive SET author = 'Matthias Klumpp'        WHERE author ILIKE 'ximion%' ;
UPDATE listarchive SET author = 'Rosea Grammostola'      WHERE author ILIKE 'rosea-%' OR author ILIKE 'rosea%grammosto%a' OR author ILIKE 'Grammostola Rosea' OR author ILIKE 'rosea';
UPDATE listarchive SET author = 'Andriy Beregovenko'     WHERE author ILIKE 'jet-guest' ;
UPDATE listarchive SET author = 'Philippe Coval'         WHERE author ILIKE 'rzr-guest' OR author ILIKE 'Philippe COVAL' ;
UPDATE listarchive SET author = 'Miguel Colon'           WHERE author ILIKE 'micove-%' ;
UPDATE listarchive SET author = 'Sebastian Dröge'        WHERE author ILIKE 'slomo' ;
UPDATE listarchive SET author = 'Harry Rickards'         WHERE author ILIKE 'hrickards%' OR author ILIKE 'Harry RIckards' ;
UPDATE listarchive SET author = 'Jordi Gutiérrez Hermoso' WHERE author ILIKE '%Jord%G%t%rrez%Hermoso%' ;
UPDATE listarchive SET author = 'Felipe Augusto van de Wiel' WHERE author ILIKE 'Felipe Augusto van de Wiel%' ;

-- </new>

-- stupid spammers at project = 'pkg-grass-devel'.
DELETE FROM listarchive WHERE author = 'info' AND project = 'pkg-grass-devel' ;

-- delete known spammers
DELETE FROM listarchive WHERE project = 'pkg-java-maintainers' AND author = 'info' ;

-- Debian custom list was renamed to blends
UPDATE listarchive SET project = 'blends' WHERE project = 'custom' ;
