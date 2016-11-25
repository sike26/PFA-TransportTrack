## Version

1.0

## Prérequis d'installation

* Un système Unix


* Python avec le gestionnaire de modules python `pip` : `sudo apt-get install python-pip`

  Si besoin, une procédure d'installation plus détaillée de pip peut être trouvée ici : http://pip.readthedocs.org/en/stable/installing/

## Installation

Placez vous dans un nouveau dossier dédié au PFA. Nous l'appellerons `projet_pfa` dans la suite.

Décompressez l'archive du projet dans un sous-dossier `pfa` ou clonez le dépôt du projet (privé pour l'instant) : `git clone https://github.com/piroux/pfa29_server.git`

Installer toutes les dépendances dans l'environnement virtuel : `pip install -r pfa/requirements.txt` (il est possible que les droits d'administrateur soient requis pour cela)

Notre application en plus du framework Flask se base sur Celery. Pour pouvoir l'utiliser il vous faut intaller RabbitMQ. Si vous utilisez ubuntu ou debian vou pourrez l'installer en tapant la commande :

`sudo apt-get install rabbitmq-server`

Sinon http://www.rabbitmq.com/download.html

Pour lancer Celery : `python pfa/runcelery.py worker -B`

Puis lancer le serveur : `python pfa/runserver.py` (Utilisez Ctrl+C pour le quitter)

Le site pfa est maintenant disponible à l'adresse http://localhost:8000

## Architecture

Le micro-framework flask a été utilisé. De fait, aucune architecture de base n'était en place. Nous avons voulu nous rapprocher du modèle MVC et avons donc classer nos fichiers selon leur fonction dans ce modèle.

* *controllers* contient l'ensemble des controlleurs du projet et donc les fonctions de l'API réparties dans les fichiers suivant leur fonction

* *models* contient l'ensemble des objets de la base de données ainsi que les méthodes qui permettent d'intéragir avec ces objets

* *libraries* contient toutes les bibliothèques permettant la collecte et le traitement des données, ainsi que les routines de génération de la base de données

* *server.config* contient surtout la configuration des taches Celery

Pour ouvrir l'interface au format .yaml (format swagger), http://editor.swagger.io/ 